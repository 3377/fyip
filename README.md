# FYIP - 专业的 IP 地理位置查询服务

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10-blue.svg)

</div>

FYIP 是一个基于 Python Flask 的专业 IP 地理位置信息查询服务，提供高性能的 RESTful API 接口和友好的 Web 界面，支持 IPv4/IPv6 地址查询。

## 目录

- [主要特性](#主要特性)
- [快速开始](#快速开始)
- [部署方法](#部署方法)
- [环境配置](#环境配置)
- [API 文档](#api-文档)
- [项目结构](#项目结构)
- [技术架构](#技术架构)
- [安全特性](#安全特性)
- [维护指南](#维护指南)
- [依赖说明](#依赖说明)
- [更新日志](#更新日志)
- [开源协议](#开源协议)

## 主要特性

- ✨ 高性能 IP 地理位置查询
- 🌐 友好的 Web 界面
- 🔒 内置访问频率限制
- 📝 详细的访问日志记录
- 🔑 支持域名和 IP 白名单
- 🐳 Docker 容器化部署
- 🏗️ 内置健康检查
- ⚡ 异步处理优化

## 快速开始

### 前置条件

- Python 3.10+
- Docker（可选）
- Git

### 本地开发环境

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/fyip.git
cd fyip
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置环境变量：

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

4. 启动服务：

```bash
python -m flask run
```

### Docker 快速启动

```bash
docker-compose up -d
```

服务将在 http://localhost:5000 启动

## 部署方法

### 方法一：Docker 部署（推荐）

1. 准备环境变量文件：

```bash
cp .env.example .env
```

2. 修改环境变量：

```env
TENCENT_MAP_KEY=your_key_here
DAILY_LIMIT=100
ALLOWED_DOMAINS=example.com,api.example.com
```

3. 构建并启动容器：

```bash
# 构建镜像
docker build -t fyip:latest .

# 启动容器
docker run -d \
  --name fyip \
  -p 5000:5000 \
  --env-file .env \
  --restart unless-stopped \
  fyip:latest
```

### 方法二：使用 Docker Compose

1. 修改 docker-compose.yml（可选）：

```yaml
version: "3.8"
services:
  fyip:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/current"]
      interval: 30s
      timeout: 10s
      retries: 3
```

2. 启动服务：

```bash
docker-compose up -d
```

### 方法三：直接部署

1. 安装系统依赖：

```bash
# Ubuntu/Debian
apt-get update && apt-get install -y python3 python3-pip curl

# CentOS/RHEL
yum install -y python3 python3-pip curl
```

2. 创建虚拟环境：

```bash
python3 -m venv venv
source venv/bin/activate
```

3. 安装项目依赖：

```bash
pip install -r requirements.txt
```

4. 配置 Supervisor：

```ini
[program:fyip]
directory=/path/to/fyip
command=/path/to/fyip/venv/bin/python -m flask run --host=0.0.0.0
autostart=true
autorestart=true
stderr_logfile=/var/log/fyip/err.log
stdout_logfile=/var/log/fyip/out.log
environment=
    FLASK_APP=app.main,
    FLASK_ENV=production,
    PYTHONPATH=/path/to/fyip
```

5. 配置 Nginx：

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

6. 启动服务：

```bash
supervisorctl reread
supervisorctl update
supervisorctl start fyip
```

## 环境配置

| 变量名           | 说明              | 默认值              |
| ---------------- | ----------------- | ------------------- |
| FLASK_APP        | Flask 应用入口    | app.main            |
| FLASK_ENV        | 运行环境          | production          |
| DAILY_LIMIT      | 访问限制次数      | 5                   |
| ALLOWED_DOMAINS  | 允许的域名        | \*                  |
| ALLOWED_IPS      | 允许的 IP         | 127.0.0.1,localhost |
| TZ               | 时区设置          | Asia/Shanghai       |
| PYTHONPATH       | Python 路径       | /app                |
| PYTHONUNBUFFERED | Python 输出缓冲   | 1                   |
| TENCENT_MAP_KEY  | 腾讯地图 API 密钥 | -                   |

## API 接口

### 1. 获取当前 IP

```
GET /api/current

响应示例：
{
    "ip": "1.2.3.4"
}
```

### 2. 查询 IP 信息

```
GET /api/{ip_address}

响应示例：
{
    "accuracy": "高精度",
    "adcode": "330106",
    "asn": "4134",
    "city": "杭州市",
    "continent": "亚洲",
    "country": "中国",
    "district": "西湖区",
    "ip": "115.204.76.218",
    "isp": "中国电信",
    "lat": "30.307869",
    "lng": "120.100527",
    "location_a": "高新文教区-西城年华",
    "location_b": "城西银泰城-赛丽绿城·慧园",
    "location_c": "西湖区申花西城年华(申花路北)",
    "location_d": "浙江省杭州市西湖区申花路388",
    "prov": "浙江省",
    "timezone": "UTC+8"
}
```

### 3. 响应字段说明

| 字段       | 说明           | 示例值                       |
| ---------- | -------------- | ---------------------------- |
| accuracy   | 定位精度       | 高精度                       |
| adcode     | 行政区划代码   | 330106                       |
| asn        | 自治系统编号   | 4134                         |
| city       | 城市名称       | 杭州市                       |
| continent  | 所属大洲       | 亚洲                         |
| country    | 国家名称       | 中国                         |
| district   | 区县名称       | 西湖区                       |
| ip         | 查询的 IP 地址 | 115.204.76.218               |
| isp        | 网络服务商     | 中国电信                     |
| lat        | 纬度           | 30.307869                    |
| lng        | 经度           | 120.100527                   |
| location_a | 位置描述一级   | 高新文教区-西城年华          |
| location_b | 位置描述二级   | 城西银泰城-赛丽绿城·慧园     |
| location_c | 位置描述三级   | 西湖区申花西城年华(申花路北) |
| location_d | 详细地址       | 浙江省杭州市西湖区申花路 388 |
| prov       | 省份名称       | 浙江省                       |
| timezone   | 时区           | UTC+8                        |

### 4. 使用的第三方 API

本服务整合了多个数据源以提供准确的 IP 地理位置信息：

1. **腾讯地图 API**

   - 地理编码服务
   - 标准地址解析
   - 行政区划代码
   - 时区信息

2. **美团移动 API**

   - 经纬度定位
   - 区域信息
   - POI 详情

3. **MaxMind GeoIP2**

   - IP 基础信息
   - 大洲和国家信息
   - ASN 信息
   - ISP 信息

4. **IPInfo.io**
   - 备用 ISP 信息
   - 组织信息

### 5. API 调用流程

1. **基础信息获取**

   - 通过 MaxMind API 获取 IP 的基础地理信息
   - 包括大洲、国家、省份、城市、ISP、ASN 等

2. **精确定位**

   - 通过美团移动 API 获取精确经纬度
   - 提供高精度的位置坐标

3. **位置详情**

   - 并发请求多个位置信息：
     - 位置 A：美团 API (tag=0)
     - 位置 B：美团 API (tag=1)
     - 位置 C 和 D：腾讯地图 API
   - 获取多层次的位置描述

4. **ISP 信息补充**
   - 如果基础信息中 ISP 缺失
   - 使用 IPInfo.io 作为备用数据源

### 6. API 响应状态码

| 状态码 | 说明                             |
| ------ | -------------------------------- |
| 200    | 请求成功                         |
| 400    | 请求参数错误（如无效的 IP 地址） |
| 401    | 未授权访问                       |
| 403    | 访问受限（如超出每日限制）       |
| 404    | 未找到资源                       |
| 429    | 请求过于频繁                     |
| 500    | 服务器内部错误                   |

### 7. 错误响应格式

```json
{
  "error": "错误描述信息",
  "code": "错误代码",
  "message": "详细错误说明",
  "timestamp": "2023-12-20T10:00:00+08:00"
}
```

## 项目结构

```
fyip/
├── app/
│   ├── __init__.py
│   ├── main.py      # 主应用
│   └── api.py       # API实现
├── static/          # 静态文件
│   ├── css/
│   ├── js/
│   └── index.html
├── Dockerfile       # Docker配置
├── docker-compose.yml
├── requirements.txt # 项目依赖
└── README.md
```

## 安全特性

1. **访问控制**

   - 每日访问次数限制
   - 域名白名单
   - IP 白名单
   - 非 root 用户运行

2. **日志记录**
   - 访问日志
   - 错误追踪
   - 用户代理记录
   - 来源追踪

## 部署建议

1. **生产环境**

   - 使用 Nginx 反向代理
   - 配置 SSL 证书
   - 设置访问限制
   - 配置日志轮转

2. **监控**
   - 使用内置健康检查（30 秒间隔）
   - 监控系统资源
   - 检查访问日志
   - 设置告警机制

## 依赖版本

- Flask==2.3.3
- Werkzeug==2.3.7
- Requests==2.31.0
- Python-dotenv==1.0.0
- Flask-cors==4.0.0
- Pytz==2023.3
- Aiohttp==3.9.1

## Docker 镜像特性

- 基础镜像：python:3.10-slim
- 时区设置：Asia/Shanghai
- 非 root 用户运行
- 健康检查机制
- 系统依赖优化
- 多阶段构建
- 镜像体积优化

## 开源协议

MIT License

## 更新日志

### v1.0.0

- 初始版本发布
- 基础查询功能
- Docker 容器化支持
- 访问限制机制
- 健康检查功能
- 安全性增强

## 维护指南

### 日志管理

1. 配置日志轮转：

```bash
# /etc/logrotate.d/fyip
/var/log/fyip/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 fyip fyip
}
```

2. 监控日志：

```bash
# 实时查看访问日志
tail -f /var/log/fyip/out.log

# 查看错误日志
tail -f /var/log/fyip/err.log
```

### 性能优化

1. 使用 Gunicorn 作为 WSGI 服务器：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

2. 启用 Nginx 缓存：

```nginx
proxy_cache_path /path/to/cache levels=1:2 keys_zone=fyip_cache:10m max_size=10g inactive=60m use_temp_path=off;

location / {
    proxy_cache fyip_cache;
    proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
    proxy_cache_valid 200 1h;
}
```
