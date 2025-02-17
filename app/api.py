import aiohttp
import asyncio
from flask import jsonify
import async_timeout
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取腾讯地图API密钥，如果环境变量不存在则使用默认值
TENCENT_MAP_KEY = os.getenv('TENCENT_MAP_KEY')

async def fetch(session, url, params=None, timeout=5):
    """通用异步请求函数"""
    try:
        async with async_timeout.timeout(timeout):
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
    return None

async def get_location_info(session, lat, lng, tag=0):
    """异步获取位置信息"""
    try:
        # 使用美团的group/v1/city/latlng API
        url = f"https://apimobile.meituan.com/group/v1/city/latlng/{lat},{lng}?tag={tag}"
        data = await fetch(session, url)
        if data and data.get('data'):
            area_name = data['data'].get('areaName', '')
            detail = data['data'].get('detail', '')
            if area_name and detail:
                return f"{area_name}-{detail}"
            return area_name or detail or "-"
    except Exception as e:
        print(f"Location API error: {str(e)}")
    return "-"

async def get_tencent_location_info(session, lat, lng):
    """异步获取腾讯地图位置信息"""
    try:
        url = "https://apis.map.qq.com/ws/geocoder/v1"
        params = {
            'location': f"{lat},{lng}",
            'key': TENCENT_MAP_KEY,
            'get_poi': '0'
        }
        data = await fetch(session, url, params=params)
        if data and data.get('status') == 0 and data.get('result'):
            result = data['result']
            return {
                'address': result.get('address', '-'),
                'standard_address': result.get('formatted_addresses', {}).get('standard_address', '-'),
                'recommend_address': result.get('formatted_addresses', {}).get('recommend', '-'),
                'adcode': result.get('ad_info', {}).get('adcode', '-'),
                'timezone': result.get('ad_info', {}).get('timezone', 'UTC+8')
            }
    except Exception as e:
        print(f"Tencent Map API error: {str(e)}")
    return {
        'address': '-', 
        'standard_address': '-',
        'recommend_address': '-',
        'adcode': '-',
        'timezone': 'UTC+8'
    }

async def get_maxmind_info(session, ip):
    """从MaxMind API获取基础IP信息"""
    try:
        async with async_timeout.timeout(5):
            async with session.get(f'https://drfy-ip.hf.space/{ip}') as response:
                if response.status == 200:
                    return await response.json()
    except Exception as e:
        print(f"MaxMind API error: {str(e)}")
    return None

async def get_public_ip(session):
    """获取公网IP地址"""
    try:
        # 主要IP获取服务
        response = await fetch(session, 'https://ipv4_cm.itdog.cn')
        if response and response.get('type') == 'success':
            return response.get('ip')

        # 备用IP获取服务
        backup_response = await fetch(session, 'https://drfy-ip.hf.space')
        if backup_response and backup_response.get('ip'):
            return backup_response.get('ip')
    except Exception as e:
        print(f"Error getting public IP: {str(e)}")
    return None

async def get_ip_info_async(ip):
    """异步获取IP信息"""
    result = {
        'ip': ip,
        'continent': '',
        'country': '',
        'timezone': 'UTC+8',
        'accuracy': '',
        'isp': '',
        'asn': '',
        'prov': '',
        'city': '',
        'district': '',
        'adcode': '',
        'lat': '',
        'lng': '',
        'location_a': '',
        'location_b': '',
        'location_c': '',
        'location_d': ''
    }

    # 设置请求头，模拟浏览器行为
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://myip.ipip.net/'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            # 1. 首先获取IP基础信息
            maxmind_data = await get_maxmind_info(session, ip)
            if maxmind_data:
                result.update({
                    'continent': maxmind_data.get('continent', {}).get('name', '亚洲'),
                    'country': maxmind_data.get('country', {}).get('name', '中国'),
                    'prov': maxmind_data.get('regions', [''])[0],
                    'city': maxmind_data.get('regions', ['', ''])[1],
                    'district': maxmind_data.get('regions', ['', '', ''])[2],
                    'isp': maxmind_data.get('as', {}).get('info', ''),
                    'asn': str(maxmind_data.get('as', {}).get('number', ''))
                })

            # 2. 获取经纬度信息
            meituan_ip_data = await fetch(session, f'https://apimobile.meituan.com/locate/v2/ip/loc?client_source=yourAppKey&rgeo=true&ip={ip}')
            if meituan_ip_data and meituan_ip_data.get('data'):
                mt_data = meituan_ip_data['data']
                lat = str(mt_data.get('lat', ''))
                lng = str(mt_data.get('lng', ''))
                if lat and lng:
                    result.update({
                        'lat': lat,
                        'lng': lng,
                        'accuracy': '高精度'
                    })

                    # 3. 获取位置信息（并发请求）
                    location_tasks = [
                        get_location_info(session, lat, lng, 0),  # 位置A
                        get_location_info(session, lat, lng, 1),  # 位置B
                        get_tencent_location_info(session, lat, lng)  # 位置C和D
                    ]
                    location_a, location_b, tencent_location = await asyncio.gather(*location_tasks)
                    result.update({
                        'location_a': location_a,
                        'location_b': location_b,
                        'location_c': tencent_location['recommend_address'],
                        'location_d': tencent_location['standard_address'],
                        'adcode': tencent_location['adcode'],
                        'timezone': tencent_location['timezone']
                    })

            # 4. 如果ISP信息缺失，尝试补充
            if not result['isp']:
                backup_data = await fetch(session, f'https://ipinfo.io/{ip}/json')
                if backup_data:
                    org = backup_data.get('org', '')
                    result['isp'] = org

        except Exception as e:
            print(f"Error in get_ip_info_async: {str(e)}")
            
        return result

def get_ip_info(ip):
    """同步包装异步函数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(get_ip_info_async(ip))
        return result
    finally:
        loop.close()