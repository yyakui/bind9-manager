# BIND9 Manager

中文 | [English](#english)

BIND9 Manager 是一个面向 Ubuntu + BIND9 的 Web DNS 管理面板。它提供 Zone、解析记录、ACL、View、TSIG、DNSSEC、备份、审计和运行状态管理，默认使用 SQLite，适合个人服务器、小型团队、内网 DNS、实验环境和轻量级权威 DNS 管理场景。

## 功能特性

- Web 管理 BIND9 Zone 和 DNS 记录
- 自动生成 `named.conf` 和 Zone 文件
- 支持 `rndc reload`、`rndc reconfig`、状态查看和配置检查
- 支持 ACL、DNS View、TSIG、DNSSEC、备份/回滚和审计日志
- 支持中文 / English 页面切换
- 默认 SQLite，无需额外部署数据库
- 提供 systemd 服务，适合在 Ubuntu 上长期运行

## 快速安装

推荐 Ubuntu 22.04/24.04：

```bash
git clone https://github.com/yyakui/bind9-manager.git
cd bind9-manager
sudo ./install.sh
```

安装完成后访问：

```text
http://服务器IP:8080
```

默认账号：

```text
用户名：admin
密码：change-me-now
```

首次登录后请尽快修改 `/etc/bind9-manager/backend.env` 中的默认密码配置。注意：这个密码只在第一次创建管理员账号时生效；如果 SQLite 数据库中已经有管理员账号，直接修改 env 不会重置已有账号密码。

## 界面操作流程

1. 打开 `http://服务器IP:8080`，使用默认账号登录。
2. 在右上角切换 `中文` 或 `EN` 页面语言。
3. 进入 `仪表盘`，确认 `named` 状态正常，没有明显告警。
4. 进入 `域名区域`，点击 `新建 Zone`，填写域名，例如 `example.com`。
5. 填写 `主 NS`，例如 `ns1.example.com.`；如果 NS 在当前 Zone 内，建议同时添加一条 `ns1` 的 A 记录。
6. 进入 `解析记录`，选择刚创建的 Zone，点击 `新建记录`。
7. 添加记录，例如：

```text
名称：www
类型：A
记录值：1.2.3.4
```

8. 返回 `域名区域`，点击对应 Zone 的“生成 BIND 文件”按钮。
9. 进入 `监控运维`，点击 `Reload` 重载 BIND。
10. 在服务器或本机使用指定 DNS 服务器测试：

```bash
dig @服务器IP www.example.com A
```

## 常用运维命令

查看服务状态：

```bash
sudo systemctl status bind9-manager-backend
sudo systemctl status bind9-manager-frontend
sudo systemctl status named
```

重启服务：

```bash
sudo systemctl restart bind9-manager-backend
sudo systemctl restart bind9-manager-frontend
sudo systemctl restart named
```

查看日志：

```bash
sudo journalctl -u bind9-manager-backend -f
sudo journalctl -u bind9-manager-frontend -f
sudo journalctl -u named -f
```

BIND 重载：

```bash
sudo rndc reload
sudo rndc reconfig
```

`reload` 适合已有 Zone 的记录变更；`reconfig` 适合新增/删除 Zone 后重新加载配置结构。

## 重要路径

- 项目目录：`/opt/bind9-manager`
- 后端环境变量：`/etc/bind9-manager/backend.env`
- SQLite 数据库：`/var/lib/bind9-manager/bind9_manager.db`
- 备份目录：`/var/lib/bind9-manager/backups`
- 生成的 BIND 配置：`/etc/bind/bind9-manager/named.conf`
- 生成的 Zone 文件：`/var/lib/bind/bind9-manager/zones`

## 公网解析注意事项

在 BIND9 Manager 中创建 Zone，只代表你的这台 BIND9 服务器知道如何解析这个域名。若要让公网用户也能解析，需要到域名注册商后台，把域名的 NS 委派到你的 DNS 服务器。

示例：

```text
NS：ns1.example.com
Glue/A：ns1.example.com -> 你的服务器公网 IP
```

如果只是内网解析或本机测试，可以直接使用：

```bash
dig @服务器IP test.example.com A
```

## 开发运行

后端：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

开发环境默认访问：

```text
http://localhost:8080
```

API 文档：

```text
http://localhost:8000/docs
```

## 常见问题

- 登录密码修改后不生效：`BIND9_MANAGER_DEFAULT_ADMIN_PASSWORD` 只影响首次创建管理员账号，已有账号需要在数据库中重置密码。
- 记录添加后解析不到：先确认已生成 BIND 文件，再在 `监控运维` 中执行 `Reload`。
- 指定服务器能解析，公网 DNS 不能解析：通常是域名没有在注册商处完成 NS 委派。
- 新增 Zone 后解析不到：执行 `Reconfig` 或重启 `named`，让 BIND 重新读取配置结构。

---

## English

BIND9 Manager is a Web DNS management panel for Ubuntu + BIND9. It manages zones, records, ACLs, DNS views, TSIG keys, DNSSEC, backups, audit logs, and runtime status. SQLite is used by default, so no external database is required.

## Features

- Manage BIND9 zones and DNS records in a Web UI
- Generate `named.conf` and zone files automatically
- Run `rndc reload`, `rndc reconfig`, status checks, and configuration checks
- Manage ACLs, DNS views, TSIG, DNSSEC, backup/rollback, and audit logs
- Switch UI language between Chinese and English
- Use SQLite by default
- Install as systemd services on Ubuntu

## Quick Install

Ubuntu 22.04/24.04 is recommended:

```bash
git clone https://github.com/yyakui/bind9-manager.git
cd bind9-manager
sudo ./install.sh
```

Open:

```text
http://SERVER_IP:8080
```

Default login:

```text
Username: admin
Password: change-me-now
```

Change `/etc/bind9-manager/backend.env` after the first login. The default admin password only applies when the first admin user is created. If the SQLite database already has an admin user, changing the env file will not reset that existing password.

## Web UI Workflow

1. Open `http://SERVER_IP:8080` and sign in.
2. Switch the UI language from the top-right language control.
3. Go to `Dashboard` and check that `named` is healthy.
4. Go to `Zones`, click `New zone`, and enter a domain such as `example.com`.
5. Set `Primary NS`, for example `ns1.example.com.`. If the NS host is inside this zone, add an A record for `ns1` as well.
6. Go to `Records`, select the zone, and click `New record`.
7. Add a record, for example:

```text
Name: www
Type: A
Value: 1.2.3.4
```

8. Go back to `Zones` and click the “Generate BIND files” action for the zone.
9. Go to `Monitoring` and click `Reload`.
10. Verify with:

```bash
dig @SERVER_IP www.example.com A
```

## Operations

Check services:

```bash
sudo systemctl status bind9-manager-backend
sudo systemctl status bind9-manager-frontend
sudo systemctl status named
```

Restart services:

```bash
sudo systemctl restart bind9-manager-backend
sudo systemctl restart bind9-manager-frontend
sudo systemctl restart named
```

Watch logs:

```bash
sudo journalctl -u bind9-manager-backend -f
sudo journalctl -u bind9-manager-frontend -f
sudo journalctl -u named -f
```

Reload BIND:

```bash
sudo rndc reload
sudo rndc reconfig
```

Use `reload` for record changes in existing zones. Use `reconfig` after adding or removing zones.

## Important Paths

- App directory: `/opt/bind9-manager`
- Backend environment: `/etc/bind9-manager/backend.env`
- SQLite database: `/var/lib/bind9-manager/bind9_manager.db`
- Backups: `/var/lib/bind9-manager/backups`
- Generated BIND config: `/etc/bind/bind9-manager/named.conf`
- Generated zone files: `/var/lib/bind/bind9-manager/zones`

## Public DNS Delegation

Creating a zone in BIND9 Manager only configures your own BIND9 server. For public DNS resolution, delegate the domain to your DNS server at your registrar.

Example:

```text
NS: ns1.example.com
Glue/A: ns1.example.com -> your public server IP
```

For local or internal testing, query your DNS server directly:

```bash
dig @SERVER_IP test.example.com A
```

## Development

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:8080
```

API docs:

```text
http://localhost:8000/docs
```

## Troubleshooting

- Password change does not work: `BIND9_MANAGER_DEFAULT_ADMIN_PASSWORD` only initializes the first admin user. Existing users must be reset in the database.
- Record cannot be resolved: generate BIND files first, then run `Reload` in `Monitoring`.
- Direct query works but public DNS does not: the domain is probably not delegated to this DNS server at the registrar.
- New zone cannot be resolved: run `Reconfig` or restart `named` so BIND reloads the configuration structure.
