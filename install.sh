#!/usr/bin/env bash
set -euo pipefail

APP_USER="bind9-manager"
APP_DIR="/opt/bind9-manager"
DATA_DIR="/var/lib/bind9-manager"
ENV_DIR="/etc/bind9-manager"
BIND_MANAGER_CONF_DIR="/etc/bind/bind9-manager"
BIND_MANAGER_ZONE_DIR="/var/lib/bind/bind9-manager/zones"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 1
fi

apt-get update
apt-get install -y bind9 bind9utils python3 python3-venv python3-pip rsync curl ca-certificates

NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
if [[ "${NODE_MAJOR}" -lt 20 ]]; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
else
  apt-get install -y nodejs
  if ! command -v npm >/dev/null 2>&1; then
    apt-get install -y npm
  fi
fi

if ! id "${APP_USER}" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir "${DATA_DIR}" --shell /usr/sbin/nologin "${APP_USER}"
fi
usermod -a -G bind "${APP_USER}" || true

mkdir -p "${APP_DIR}" "${DATA_DIR}/backups" "${DATA_DIR}/generated" "${ENV_DIR}" "${BIND_MANAGER_CONF_DIR}" "${BIND_MANAGER_ZONE_DIR}"
rsync -a --delete \
  --exclude .git \
  --exclude backend/.venv \
  --exclude backend/.runtime \
  --exclude frontend/node_modules \
  --exclude frontend/dist \
  --exclude .runtime \
  --exclude __pycache__ \
  --exclude .pytest_cache \
  ./ "${APP_DIR}/"

python3 -m venv "${APP_DIR}/backend/.venv"
"${APP_DIR}/backend/.venv/bin/pip" install --upgrade pip
"${APP_DIR}/backend/.venv/bin/pip" install -r "${APP_DIR}/backend/requirements.txt"

cd "${APP_DIR}/frontend"
npm install
npm run build

if [[ ! -f "${ENV_DIR}/backend.env" ]]; then
  SECRET="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
  cat > "${ENV_DIR}/backend.env" <<EOF
BIND9_MANAGER_SECRET_KEY=${SECRET}
BIND9_MANAGER_DEFAULT_ADMIN_USERNAME=admin
BIND9_MANAGER_DEFAULT_ADMIN_PASSWORD=change-me-now
BIND9_MANAGER_DATABASE_URL=sqlite:////var/lib/bind9-manager/bind9_manager.db
BIND9_MANAGER_BIND_CONF_PATH=/etc/bind/named.conf
BIND9_MANAGER_BIND_ZONES_DIR=/var/lib/bind/bind9-manager/zones
BIND9_MANAGER_GENERATED_CONF_PATH=/etc/bind/bind9-manager/named.conf
BIND9_MANAGER_BACKUP_DIR=/var/lib/bind9-manager/backups
BIND9_MANAGER_CORS_ORIGINS='["*"]'
EOF
  chmod 0640 "${ENV_DIR}/backend.env"
fi
if grep -Fxq 'BIND9_MANAGER_CORS_ORIGINS=["*"]' "${ENV_DIR}/backend.env"; then
  sed -i 's|^BIND9_MANAGER_CORS_ORIGINS=.*|BIND9_MANAGER_CORS_ORIGINS='\''["*"]'\''|' "${ENV_DIR}/backend.env"
fi
if grep -Fxq 'BIND9_MANAGER_BIND_ZONES_DIR=/etc/bind/zones' "${ENV_DIR}/backend.env"; then
  sed -i 's|^BIND9_MANAGER_BIND_ZONES_DIR=.*|BIND9_MANAGER_BIND_ZONES_DIR=/var/lib/bind/bind9-manager/zones|' "${ENV_DIR}/backend.env"
fi
if grep -Fxq 'BIND9_MANAGER_GENERATED_CONF_PATH=/var/lib/bind9-manager/generated/named.conf' "${ENV_DIR}/backend.env"; then
  sed -i 's|^BIND9_MANAGER_GENERATED_CONF_PATH=.*|BIND9_MANAGER_GENERATED_CONF_PATH=/etc/bind/bind9-manager/named.conf|' "${ENV_DIR}/backend.env"
fi

chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}" "${ENV_DIR}"
chown -R "${APP_USER}:bind" "${DATA_DIR}" "${BIND_MANAGER_CONF_DIR}" "${BIND_MANAGER_ZONE_DIR}" || true
chmod 0750 "${DATA_DIR}" "${DATA_DIR}/backups" "${DATA_DIR}/generated"
chmod 0750 "${BIND_MANAGER_CONF_DIR}" "${BIND_MANAGER_ZONE_DIR}" || true

install -m 0644 "${APP_DIR}/bind9-manager-backend.service" /etc/systemd/system/bind9-manager-backend.service
install -m 0644 "${APP_DIR}/bind9-manager-frontend.service" /etc/systemd/system/bind9-manager-frontend.service

set -a
# shellcheck disable=SC1091
. "${ENV_DIR}/backend.env"
set +a

cd "${APP_DIR}/backend"
"${APP_DIR}/backend/.venv/bin/python" - <<'PY'
from core.security import ensure_default_admin
from database import SessionLocal, init_db
from services.bind_config import get_or_create_options, write_named_conf

init_db()
db = SessionLocal()
try:
    ensure_default_admin(db)
    get_or_create_options(db)
    write_named_conf(db)
finally:
    db.close()
PY
chown -R "${APP_USER}:bind" "${DATA_DIR}"
chown -R "${APP_USER}:bind" "${BIND_MANAGER_CONF_DIR}" "${BIND_MANAGER_ZONE_DIR}"
chmod 0640 "${BIND9_MANAGER_GENERATED_CONF_PATH}"

if ! grep -q 'Managed by bind9-manager' /etc/bind/named.conf; then
  cp /etc/bind/named.conf "/etc/bind/named.conf.bind9-manager.bak.$(date +%Y%m%d%H%M%S)"
fi
cat > /etc/bind/named.conf <<EOF
// Managed by bind9-manager. Previous configuration was backed up in /etc/bind.
include "${BIND9_MANAGER_GENERATED_CONF_PATH}";
EOF

named-checkconf /etc/bind/named.conf

systemctl daemon-reload
systemctl enable --now bind9-manager-backend.service bind9-manager-frontend.service
systemctl restart bind9-manager-backend.service bind9-manager-frontend.service
systemctl restart named.service || systemctl restart bind9.service || true

echo "BIND9 Manager is starting on http://SERVER_IP:8080"
echo "Default login: admin / change-me-now"
