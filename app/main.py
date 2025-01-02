from flask import Flask, request, send_from_directory, url_for, jsonify
from flask_cors import CORS
from app.api import get_ip_info
import os
from functools import wraps
import requests
import logging
from datetime import datetime
import json
import pytz
from collections import defaultdict
import time

# 配置日志
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__, static_folder='../static')
CORS(app)

# 设置时区为中国上海
TIMEZONE = pytz.timezone('Asia/Shanghai')

# 访问限制配置
DAILY_LIMIT = int(os.getenv('DAILY_LIMIT', '5'))  # 默认每日访问限制次数
access_counts = defaultdict(lambda: {'count': 0, 'reset_time': 0})

def reset_daily_count():
    """重置每日访问计数"""
    current_time = time.time()
    for ip in list(access_counts.keys()):
        if current_time - access_counts[ip]['reset_time'] >= 86400:  # 24小时
            del access_counts[ip]

def check_access_limit(ip):
    """检查访问限制"""
    current_time = time.time()
    
    # 如果是新的一天，重置计数
    if current_time - access_counts[ip]['reset_time'] >= 86400:
        access_counts[ip] = {'count': 1, 'reset_time': current_time}
        return True
    
    # 检查是否超过限制
    if access_counts[ip]['count'] >= DAILY_LIMIT:
        return False
    
    # 增加计数
    access_counts[ip]['count'] += 1
    return True

def log_request(ip, endpoint, result=None, error=None):
    """记录请求日志"""
    current_time = datetime.now(TIMEZONE)
    log_data = {
        'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S %z'),
        'client_ip': request.remote_addr,
        'query_ip': ip,
        'endpoint': endpoint,
        'user_agent': request.headers.get('User-Agent', '-'),
        'referer': request.headers.get('Referer', '-')
    }
    
    if error:
        log_data['error'] = str(error)
        logger.error(json.dumps(log_data))
    else:
        if result:
            log_data['result'] = {k: v for k, v in result.items() if k in ['country', 'city', 'isp']}
        logger.info(json.dumps(log_data))

def get_real_ip():
    """获取真实IP地址"""
    # 优先从请求头获取
    ip = request.headers.get('X-Real-IP') or \
         request.headers.get('X-Forwarded-For') or \
         request.remote_addr
    
    # 如果是本地IP，尝试使用备用服务
    if ip in ['127.0.0.1', 'localhost']:
        try:
            # 备用IP获取服务
            response = requests.get('https://ipv4_cm.itdog.cn', timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('type') == 'success':
                    return data.get('ip')
        except Exception as e:
            logger.error(f"Error getting IP from backup API: {str(e)}")
            return None
    
    return ip

def check_auth(f):
    """验证域名和IP授权的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取允许的域名列表
        allowed_domains = os.getenv('ALLOWED_DOMAINS', '*').split(',')
        # 获取允许的IP列表
        allowed_ips = os.getenv('ALLOWED_IPS', '127.0.0.1,localhost').split(',')
        
        # 获取请求的域名和IP
        origin = request.headers.get('Origin', '')
        client_ip = request.remote_addr
        
        # 检查是否是本地IP
        is_local = client_ip in ['127.0.0.1', 'localhost']
        
        # 检查域名是否在允许列表中（'*' 表示允许所有域名）
        domain_allowed = '*' in [d.strip() for d in allowed_domains] or \
                        any(domain.strip() in origin for domain in allowed_domains if domain.strip())
        
        # 检查IP是否在允许列表中
        ip_allowed = client_ip in [ip.strip() for ip in allowed_ips]
        
        # 如果是本地IP或在允许列表中，直接通过
        if is_local or domain_allowed or ip_allowed:
            return f(*args, **kwargs)
            
        # 对于未授权的请求，应用访问限制
        reset_daily_count()  # 清理过期的计数
        if not check_access_limit(client_ip):
            error_msg = '您今日的免费使用次数已达上限'
            log_request(None, request.endpoint, error=error_msg)
            return jsonify({
                'error': error_msg,
                'message': '请联系管理员获取授权'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/current')
@check_auth
def current_ip():
    """获取当前访问者的IP地址"""
    ip = get_real_ip()
    if not ip:
        error_msg = '无法获取真实IP地址'
        log_request(None, 'current_ip', error=error_msg)
        return jsonify({'error': error_msg}), 400
    
    log_request(ip, 'current_ip')
    return jsonify({'ip': ip})

@app.route('/api/<ip_address>')
@check_auth
def ip_info(ip_address):
    try:
        result = get_ip_info(ip_address)
        # 移除ASN信息
        if 'asnumber' in result:
            del result['asnumber']
        
        log_request(ip_address, 'ip_info', result=result)
        return jsonify(result)
    except Exception as e:
        error_msg = str(e)
        log_request(ip_address, 'ip_info', error=error_msg)
        error_response = {
            'error': error_msg,
            'ip': ip_address
        }
        return jsonify(error_response), 500

@app.errorhandler(404)
def not_found(error):
    log_request(None, '404_error', error='Not found')
    return jsonify({'error': 'Not found', 'status_code': 404}), 404

@app.errorhandler(500)
def internal_error(error):
    log_request(None, '500_error', error=str(error))
    return jsonify({'error': 'Internal server error', 'status_code': 500}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 