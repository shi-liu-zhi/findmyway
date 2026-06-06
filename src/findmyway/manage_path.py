#%%
import requests
from IPython.display import display, Image
import qrcode
import hashlib
import urllib.parse
from typing import Dict, Any
import itertools
import time
from Node import Node
from Amap_request import generate_signature, url_to_qrcode
import os

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
    return ((node1, node2), duration)

# %% 多点返回一个字典
def mulNodes_management(
        *args
) -> set:
    # 获取所有两两Node组合的有序排列
    all_two_Nodes = list(itertools.permutations(args, 2))

    tuples = {twoNodes_management(i, j) for i, j in all_two_Nodes}
    
    return tuples


# %% 生成可直接调起高德App的导航链接 
def generate_amap_navigation_link(origin, destination, waypoint, mode='car'):
    """
    生成高德地图导航链接
    mode: car（驾车）, bus（公交）, walk（步行）, bike（骑行）
    """
    base_url = "https://uri.amap.com/navigation" 
    params = {
        "from": origin,
        "to": destination,
        "mode": mode,
        "policy": "0"  # 0: 速度快, 1: 费用低, 2: 路程短
    }
    
    if waypoint:
        # 途经点 via 参数：多个坐标用英文分号分隔
        params["via"] = waypoint
    
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


# %% 测试：生成 mulNodes_management 的数据并传入 TSP 求解器
if __name__ == "__main__":
    from test import _TspSolver

    # 创建节点（会调用高德地理编码API获取坐标）
    nodes = [
        Node(address='东钱湖', city='宁波'),
        Node(address='天一广场', city='宁波'),
        Node(address='老外滩', city='宁波'),
        Node(address='南塘老街', city='宁波'),
        Node(address='鼓楼', city='宁波'),
        Node(address='月湖公园', city='宁波'),
        Node(address='宁波博物馆', city='宁波'),
        Node(address='城隍庙', city='宁波'),
        Node(address='梁祝文化公园', city='宁波'),
        Node(address='保国寺', city='宁波'),
        Node(address='天童寺', city='宁波'),
        Node(address='阿育王寺', city='宁波'),
        Node(address='宁波植物园', city='宁波'),
        Node(address='宁波文化广场', city='宁波'),
        Node(address='宁波海洋世界', city='宁波'),
        Node(address='宁波美术馆', city='宁波'),
        Node(address='溪口蒋氏故居', city='宁波'),
        Node(address='九龙湖', city='宁波'),
        Node(address='郑氏十七房', city='宁波'),
        Node(address='雪窦山', city='宁波'),
    ]

    # 调用 mulNodes_management 获取所有两两路径耗时（会调用驾车路径API）
    print("正在获取各节点间的驾驶耗时...")
    data_set = mulNodes_management(*nodes)

    print(f"\n生成 {len(data_set)} 条路径数据:")
    for pairedNodes, duration in data_set:
        print(f"  {pairedNodes[0].address} -> {pairedNodes[1].address}: {duration}秒")

    # 输入到 TSP 求解器
    print("\n正在求解最优环形路径...")
    solver = _TspSolver.from_data(data_set, start=nodes[0])
    path, total_time = solver.solve()
    print(f"最佳路径: {' -> '.join(n.address for n in path)}")
    print(f"总耗时: {total_time} 秒 ≈ {total_time / 60:.1f} 分钟")

    # 生成高德地图导航链接（途经点超过16个时自动分段）
    nav_links = solver.to_link(path)
    print(f"\n高德导航链接（共 {len(nav_links)} 段）:")
    for i, link in enumerate(nav_links, 1):

        print(f"  第{i}段: {link}")
        # 生成二维码
        url_to_qrcode(link).save(os.path.expanduser(f"~/Pictures/nav_link_{i}.png"))