# BIND9 Manager

BIND9 Manager 是一个轻量级的 BIND9 Web 管理面板，后端使用 FastAPI，前端使用 Vue 3，默认数据库为 SQLite。它适合在 Ubuntu 服务器上快速部署，用网页管理 DNS Zone、解析记录、ACL、View、TSIG、DNSSEC、备份和服务重载。

## 功能

- 管理 Zone 和 DNS 记录
- 生成 BIND9 配置和 Zone 文件
- 页面中执行配置检查、重载、状态查看
- 支持 ACL、View、TSIG、DNSSEC、备份和审计日志
- 默认使用 SQLite，无需额外安装 MySQL/PostgreSQL

## 快速安装

推荐使用 Ubuntu 22.04/24.04，并使用 root 或 sudo 执行：

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

首次登录后请尽快修改 `/etc/bind9-manager/backend.env` 中的密码配置。注意：这个密码只在第一次创建管理员账号时生效；如果数据库里已经有管理员账号，直接改 env 不会修改已有账号密码。

## 常用命令

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

重载 DNS 配置：

```bash
sudo rndc reload
```

也可以在 Web 页面中进入 `Monitoring`，点击 `Reload`。

## 使用方法

1. 登录 Web 面板。
2. 进入 `Zones` 创建域名，例如 `example.com`。
3. 进入 `Records` 添加记录，例如 `www`、`A`、`1.2.3.4`。
4. 进入 `Monitoring` 点击 `Reload`。
5. 使用指定 DNS 服务器测试：

```bash
dig @服务器IP www.example.com A
```

如果想让公网用户直接解析你的域名，还需要到域名注册商后台，把域名的 NS 服务器委派到你的 BIND9 服务器。只在本机创建 Zone，不会自动接管公网 DNS。

## 重要路径

- 项目目录：`/opt/bind9-manager`
- 后端环境变量：`/etc/bind9-manager/backend.env`
- SQLite 数据库：`/var/lib/bind9-manager/bind9_manager.db`
- 备份目录：`/var/lib/bind9-manager/backups`
- 生成的 BIND 配置：`/etc/bind/bind9-manager/named.conf`
- 生成的 Zone 文件：`/var/lib/bind/bind9-manager/zones`

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
