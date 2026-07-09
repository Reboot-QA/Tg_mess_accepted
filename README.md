# Telegram → 微信 消息推送

监听 Telegram 新消息，推送到 **企业微信 / Server酱 / PushPlus**。

支持 **Linux 服务器** 部署。

---

## Docker 部署（推荐）

### 1. 准备配置

```bash
chmod +x docker/setup.sh
./docker/setup.sh
vim data/config.yaml   # 填写 api_id、api_hash、企业微信 webhook
```

`setup.sh` 会自动把 session 和日志路径设为 `data/sessions`、`data/logs`。

### 2. 构建镜像

```bash
docker compose build
```

### 3. 首次 Telegram 登录

**方式 A**：复制已有 session

```bash
mkdir -p data/sessions
cp telegram_session.session data/sessions/telegram_session.session
```

**方式 B**：容器内交互登录

```bash
docker compose --profile login run --rm login
# 输入手机号、验证码、两步验证密码
```

### 4. 测试推送

```bash
docker compose --profile test run --rm test
```

### 5. 启动服务（后台运行 + 自动重启）

```bash
docker compose up -d
docker compose logs -f
```

### 6. 常用命令

```bash
docker compose ps
docker compose restart
docker compose down
docker compose logs -f monitor
```

### 7. 代理（国内服务器）

编辑 `data/config.yaml`：

```yaml
telegram:
  proxy:
    enabled: true
    type: "socks5"
    host: "host.docker.internal"   # Docker Desktop
    port: 1080
```

Linux 宿主机代理可改用宿主机内网 IP，或在 `docker-compose.yml` 取消注释：

```yaml
network_mode: host
```

---

## Linux 服务器部署（非 Docker）

### 1. 上传项目

```bash
# 示例：放到 /opt/telegram-wechat-push
scp -r 监控telegeram user@your-server:/opt/telegram-wechat-push
ssh user@your-server
cd /opt/telegram-wechat-push
```

### 2. 安装

```bash
chmod +x install.sh start.sh test_push.sh install_service.sh
./install.sh
nano config.yaml   # 或 vim config.yaml
```

填写：
- `telegram.api_id` / `api_hash`
- `push.provider` 和对应 webhook / sendkey

### 3. 首次登录 Telegram（需交互）

```bash
./start.sh
```

按提示输入手机号、验证码、两步验证密码。  
成功后生成 `telegram_session.session`。

> **免交互技巧**：若已在其他环境登录过，把 `telegram_session.session` 复制到服务器同目录即可跳过验证码。

### 4. 测试推送

```bash
./test_push.sh
```

### 5. 安装 systemd 服务（开机自启 + 崩溃重启）

```bash
sudo ./install_service.sh
```

常用命令：

```bash
sudo systemctl status telegram-wechat-push
sudo journalctl -u telegram-wechat-push -f
sudo systemctl restart telegram-wechat-push
```

### 6. 代理（国内服务器连 Telegram）

编辑 `config.yaml`：

```yaml
telegram:
  proxy:
    enabled: true
    type: "socks5"
    host: "127.0.0.1"
    port: 1080
```

服务器上可先部署本地代理（如 sing-box、v2ray），再指向 `127.0.0.1`。

---

## 推送方式

| provider | 说明 | 费用 |
|----------|------|------|
| `wecom` | 企业微信群机器人 Webhook | 免费 |
| `serverchan` | Server酱 SendKey | 免费 5 条/天 |
| `pushplus` | PushPlus Token | 需实名 |

`config.yaml` 示例：

```yaml
push:
  provider: "wecom"
  wecom:
    webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
```

---

## 文件说明

| 文件 | Docker | Linux |
|------|--------|-------|
| `Dockerfile` | 镜像构建 | - |
| `docker-compose.yml` | 编排配置 | - |
| `docker/setup.sh` | 初始化 data 目录 | - |
| `monitor.py` | 主程序 | 主程序 |
| `install.sh` | - | 安装依赖 |
| `start.sh` | - | 启动 |
| `test_push.sh` | `docker compose --profile test` | 测试推送 |
| `install_service.sh` | - | systemd 自启 |
| `list_chats.py` | 查看群 ID | 查看群 ID |

---

## 安全

- 不要提交 `config.yaml`、`data/config.yaml`、`*.session` 到 Git
- Webhook / SendKey 泄露后请立即重置
