# %%
import requests
from IPython.display import display, Image
import qrcode
import hashlib
import urllib.parse
from typing import Dict, Any
import itertools
import time

# %%
def generate_signature(params: Dict[str, Any], private_key: str) -> str:
    """
    生成高德地图API签名
    
    Args:
        params: 请求参数字典（不包含sig参数本身）
        private_key: 私钥（在控制台获取）
    
    Returns:
        签名字符串（32位MD5值）
    """

    params.pop('sig', None)
    
    # 2. 按键名升序排序
    sorted_keys = sorted(params.keys())
    
    # 3. 构建参数字符串 key=value&key2=value2...
    param_parts = []
    for key in sorted_keys:
        value = params[key]
        # 确保值是字符串类型
        param_parts.append(f"{key}={value}")
    
    param_string = "&".join(param_parts)
    
    # 4. 拼接私钥（注意：直接拼接，没有&符号）
    string_to_sign = param_string + private_key
    
    # 5. 计算MD5（注意：需要UTF-8编码）
    md5_hash = hashlib.md5(string_to_sign.encode('utf-8')).hexdigest()
    
    return md5_hash

# %% 地理编码
def point_getcode(address: str = '', city:str = '') -> str:
    url = "https://restapi.amap.com/v3/geocode/geo"

    # 将参数放在params字典里
    params = {
        "key": "0d5c74a803fdba8397aa08e6d047d128",
        "address": address,
        "city" : city,
        "output": "JSON"
    }

    sig = generate_signature(
        params=params,
        private_key='9cab683bc6b3f097e00bde8bb871113d'
    )

    params['sig'] = sig
    
    time.sleep(1)
    response = requests.get(url = url, params=params).json()
    location = response['geocodes'][0]['location']
    return location

def url_to_qrcode(url: str) -> Image:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img