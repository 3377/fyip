FROM python:3.10-slim

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd -m -s /bin/bash fyip

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录并设置权限
RUN mkdir -p /app/logs && \
    chown -R fyip:fyip /app

# 复制应用代码
COPY . .
RUN chown -R fyip:fyip /app

# 切换到非root用户
USER fyip

# 设置环境变量
ENV FLASK_APP=app.main
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV DAILY_LIMIT=5
ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/current || exit 1

# 启动命令
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"] 