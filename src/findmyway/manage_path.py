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
def generate_amap_navigation_link(origin, destination, waypoint, mode='car',
                                  origin_name='', dest_name='', waypoint_names=''):
    """
    生成高德地图导航链接
    基于高德分享链接格式: https://m.amap.com/navigation/carmap/
    mode: car（驾车）, bus（公交）, walk（步行）, bike（骑行）
    """
    # 解析坐标
    ori_lon, ori_lat = origin.split(',')
    dest_lon, dest_lat = destination.split(',')

    # 构建途经点数据
    via_lats, via_lons, via_names = '', '', ''
    if waypoint:
        coords = waypoint.split(';')
        names = waypoint_names.split('|') if waypoint_names else ['']
        lons, lats, nms = [], [], []
        for i, coord in enumerate(coords):
            lon, lat = coord.split(',')
            lons.append(lon)
            lats.append(lat)
            nms.append(names[i] if i < len(names) else '')
        via_lats = '|'.join(lats)
        via_lons = '|'.join(lons)
        via_names = '|'.join(nms)

    # __r 参数（核心路由数据，格式参照高德分享链接）
    r_parts = [
        ori_lat, ori_lon, origin_name,       # 0, 1, 2: 起点 lat, lon, name
        dest_lat, dest_lon, dest_name,        # 3, 4, 5: 终点 lat, lon, name
        '', '0', '0', '', '', '',              # 6-11: 占位
        '',                                    # 12: 路由编码数据（留空）
        via_lats, via_lons, via_names,        # 13, 14, 15: 途经点
    ]

    full_url = (
        f"https://m.amap.com/navigation/carmap/"
        f"__r={','.join(r_parts)}"
        f"&saddr={ori_lon},{ori_lat},{origin_name}"
        f"&daddr={dest_lon},{dest_lat},{dest_name}"
        f"&viaaddr={via_lons},{via_lats},{via_names}"
        f"&src=app_share&callnative=1"
    )

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
        Node(address='海底捞天一广场店', city='宁波'),
        Node(address='海底捞江北万达店', city='宁波'),
        Node(address='海底捞鄞州万达店', city='宁波'),
        Node(address='肯德基天一广场店', city='宁波'),
        Node(address='肯德基宁波来福士', city='宁波'),
        Node(address='肯德基鄞州万达店', city='宁波'),
        Node(address='星巴克天一广场店', city='宁波'),
        Node(address='星巴克宁波来福士', city='宁波'),
        Node(address='星巴克鄞州万达店', city='宁波'),
        Node(address='外婆家天一广场店', city='宁波'),
        Node(address='外婆家宁波来福士', city='宁波'),
        Node(address='绿茶餐厅天一广场店', city='宁波'),
        Node(address='绿茶餐厅鄞州万达店', city='宁波'),
        Node(address='必胜客天一广场店', city='宁波'),
        Node(address='必胜客鄞州万达店', city='宁波'),
        Node(address='老娘舅天一广场店', city='宁波'),
        Node(address='老娘舅宁波来福士', city='宁波'),
        Node(address='真功夫天一广场店', city='宁波'),
        Node(address='真功夫宁波火车站店', city='宁波'),
        Node(address='张亮麻辣烫城隍庙店', city='宁波'),
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