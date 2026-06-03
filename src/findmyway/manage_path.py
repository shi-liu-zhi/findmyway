#%%
import requests
from IPython.display import display, Image
import qrcode
import hashlib
import urllib.parse
from typing import Dict, Any
import itertools
import time
import Node
from Amap_request import generate_signature

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
    time.sleep(0.35)
    response = requests.get(url = url, params=params).json()
    paths = response['route']['paths'][0]
    duration:int = int(paths['cost']['duration'])

    return duration

# %% 两个点返回一个元组
def twoNodes_management(
    node1: Node,
    node2: Node,
    strategy: int = 0 
):
    duration = twopoints_management(
        origin=node1.latlon, 
        destination=node2.latlon, 
        strategy=strategy
    )
    return (node1.address, node2.address, duration)

# %% 多点返回一个字典
def mulNodes_management(
        *args
) -> set:
    all_two_Nodes = itertools.permutations(args)
    all_two_Nodes = list(itertools.permutations(args))

    tuples = {twoNodes_management(i[0], i[1]) for i in all_two_Nodes}

    return tuples


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

# %% 多点规划 Lagecy
# def mulpoints_management(
#     origin: str = '', 
#     destination: str = '', 
#     pods_dict: dict = {},
#     strategy: int = 0
# ) -> str:
    
#     origin = point_getcode(start_dict['origin'])
#     waypoints = []
#     for i in pods_dict.values():
#         waypoints += [point_getcode(i)]


#     waypoints_list = list(itertools.permutations(waypoints))

#     all_points = [[origin] + list(i) + [origin] for i in waypoints_list]
    
#     all_delay = {}
#     for mark, i in enumerate(all_points):
#         all_delay[mark] = 0
#         for j in itertools.pairwise(i):
#             all_delay[mark] += twopoints_management(origin=j[0], destination=j[1])

#     url = 0 
#     return url
