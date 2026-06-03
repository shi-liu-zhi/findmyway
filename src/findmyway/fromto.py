#%%
import requests
from IPython.display import display, Image
import qrcode
import hashlib
import urllib.parse
from typing import Dict, Any
import itertools
import time

#%% 构建一个字典进行送货节点的保存
start_dict = {
    "origin": "闵行区浦江镇昌林路985弄"
}
pods_dict = {
    "OE": "浦江镇联航路1188号25幢",
    "上海戏剧学院": "闵行区昌林路800号",
    "欢乐颂": "闵行区浦锦街道陈行公路2688号"
}

ningbo = "0574" 

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

#%% 简单的两点路径规划
def twopoints_management(
        origin: str = '', 
        destination: str = '',
        strategy: int = 0
) -> int:
    
    # API的基础URL (注意：这是GET请求，不是POST)
    url = "https://restapi.amap.com/v5/direction/driving"

    # 将参数放在params字典里
    params = {
        "origin": origin,
        "destination": destination,
        "key": "0d5c74a803fdba8397aa08e6d047d128",  # 请替换为你的真实KEY
        "show_fields": "cost",
        "strategy": strategy
    }

    sig = generate_signature(
        params=params,
        private_key='9cab683bc6b3f097e00bde8bb871113d'
    )

    params['sig'] = sig

    # 发送GET请求
    time.sleep(1)
    response = requests.get(url = url, params=params).json()
    paths = response['route']['paths'][0]
    duration:int = int(paths['cost']['duration'])

    return duration


# %% 生成可直接调起高德App的导航链接 
def generate_amap_navigation_link(origin, destination, mode='car'):
    """
    生成高德地图导航链接
    mode: car（驾车）, bus（公交）, walk（步行）, bike（骑行）
    """
    base_url = "https://uri.amap.com/navigation" 
    params = {
        "origin": origin,
        "destination": destination,
        "intelligent_sorting": 1,
        "policy": "1"  # 1: 速度优先, 2: 费用优先, 3: 距离优先
    }
    
    param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{base_url}?{param_str}"
    
    return full_url


# %% 多点规划
def mulpoints_management(
    origin: str = '', 
    destination: str = '', 
    pods_dict: dict = {},
    strategy: int = 0
) -> str:
    
    origin = point_getcode(start_dict['origin'])
    waypoints = []
    for i in pods_dict.values():
        waypoints += [point_getcode(i)]


    waypoints_list = list(itertools.permutations(waypoints))

    all_points = [[origin] + list(i) + [origin] for i in waypoints_list]
    
    all_delay = {}
    for mark, i in enumerate(all_points):
        all_delay[mark] = 0
        for j in itertools.pairwise(i):
            all_delay[mark] += twopoints_management(origin=j[0], destination=j[1])

    url = 0 
    return url


# %% 测试用例
origin = point_getcode(start_dict['origin'])
waypoints = [point_getcode(i) for i in pods_dict.values()]

waypoints_list = list(itertools.permutations(waypoints))

all_points = [[origin] + list(i) + [origin] for i in waypoints_list]

all_delay = {}
for mark, i in enumerate(all_points):
    all_delay[mark] = 0
    for j in itertools.pairwise(i):

        all_delay[mark] += twopoints_management(origin=j[0], destination=j[1])



# origin = "116.434307,39.90909"
# destination = "116.434446,39.90816"
# nav_link = generate_amap_navigation_link(origin, destination)
# print(f"高德导航链接：{nav_link}")
# final_qr = qrcode.make(nav_link)
# final_qr.save('test.png')




# %%
