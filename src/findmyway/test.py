from itertools import permutations
from functools import lru_cache

def solve_tsp_from_tuples(data, start):
    """
    解决非对称TSP问题
    
    参数:
        data: set或list，元素格式为 (from_node, to_node, duration)
        start: 起始节点地址
    返回:
        (最佳路径列表, 最短总时间)
    """
    # 1. 构建距离字典
    distances = {}
    nodes = set()
    
    for from_node, to_node, duration in data:
        distances[(from_node, to_node)] = duration
        nodes.add(from_node)
        nodes.add(to_node)
    

    nodes = list(nodes)
    if start not in nodes:
        raise ValueError(f"起点 '{start}' 不在节点集合中")
    
    # 确保起点在第一个位置
    nodes.remove(start)
    other_nodes = nodes
    all_nodes = [start] + other_nodes
    n = len(all_nodes)
    
    print(f"找到 {n} 个节点: {all_nodes}")
    
    # 2. 使用动态规划 (Held-Karp算法)
    # 将节点映射到索引
    idx = {node: i for i, node in enumerate(all_nodes)}
    
    # 快速距离查询函数
    def get_dist(a, b):
        return distances.get((a, b), float('inf'))
    
    @lru_cache(maxsize=None)
    def dp(visited_mask, last_idx):
        """
        visited_mask: 已访问节点的位掩码（不包括起点，因为起点总是已访问）
        last_idx: 最后访问的节点在 all_nodes 中的索引（不会是起点）
        """
        if visited_mask == 0:
            # 刚从起点出发，到达 last_idx
            return get_dist(start, all_nodes[last_idx])
        
        min_cost = float('inf')
        # 枚举上一个节点
        for prev_idx in range(1, n):  # 排除起点（索引0）
            if prev_idx == last_idx:
                continue
            if visited_mask & (1 << (prev_idx - 1)):  # 注意位偏移
                prev_mask = visited_mask & ~(1 << (last_idx - 1))
                cost = dp(prev_mask, prev_idx) + get_dist(all_nodes[prev_idx], all_nodes[last_idx])
                if cost < min_cost:
                    min_cost = cost
        return min_cost
    
    # 3. 计算最终结果（回到起点）
    full_mask = (1 << (n - 1)) - 1  # 所有其他节点都已访问
    best_cost = float('inf')
    best_last_idx = None
    
    for last_idx in range(1, n):
        cost = dp(full_mask, last_idx) + get_dist(all_nodes[last_idx], start)
        if cost < best_cost:
            best_cost = cost
            best_last_idx = last_idx
    
    # 4. 重构路径
    path = [start]
    mask = full_mask
    last_idx = best_last_idx
    
    while mask != 0:
        # 找到上一个节点
        for prev_idx in range(1, n):
            if prev_idx == last_idx:
                continue
            if mask & (1 << (prev_idx - 1)):
                prev_mask = mask & ~(1 << (last_idx - 1))
                # 验证这个转移是否是最优的
                if prev_mask == 0:
                    prev_cost = get_dist(start, all_nodes[prev_idx])
                else:
                    prev_cost = dp(prev_mask, prev_idx)
                
                current_cost = prev_cost + get_dist(all_nodes[prev_idx], all_nodes[last_idx])
                if abs(current_cost - dp(mask, last_idx)) < 1e-6:
                    path.insert(1, all_nodes[prev_idx])  # 插入到起点后
                    mask = prev_mask
                    last_idx = prev_idx
                    break
    
    path.append(start)  # 回到起点
    return path, best_cost


# 如果你的节点数 ≤ 10，可以用更简单的暴力法
def solve_tsp_bruteforce(data, start):
    """暴力枚举（适用于节点数 ≤ 10）"""
    # 构建距离字典和节点列表
    distances = {}
    nodes = set()
    for from_node, to_node, duration in data:
        distances[(from_node, to_node)] = duration
        nodes.add(from_node)
        nodes.add(to_node)
    
    if start not in nodes:
        raise ValueError(f"起点 '{start}' 不在节点集合中")
    
    nodes.remove(start)
    other_nodes = list(nodes)
    
    best_path = None
    best_duration = float('inf')
    
    for perm in permutations(other_nodes):
        path = [start] + list(perm) + [start]
        total = 0
        valid = True
        for i in range(len(path) - 1):
            d = distances.get((path[i], path[i+1]))
            if d is None:
                valid = False
                break
            total += d
        if valid and total < best_duration:
            best_duration = total
            best_path = path
    
    return best_path, best_duration


# ========== 使用示例 ==========
if __name__ == "__main__":
    # 你的数据示例
    data = {
        ('东钱湖', '天一广场', 1944),
        ('天一广场', '东钱湖', 1670),
        ('东钱湖', '老外滩', 1500),
        ('老外滩', '东钱湖', 1450),
        ('天一广场', '老外滩', 800),
        ('老外滩', '天一广场', 850),
        ('东钱湖', '南塘老街', 2000),
        ('南塘老街', '东钱湖', 1950),
        ('天一广场', '南塘老街', 600),
        ('南塘老街', '天一广场', 620),
        ('老外滩', '南塘老街', 900),
        ('南塘老街', '老外滩', 880),
    }
    
import numpy as np
import elkai

def solve_tsp_with_elkai(data, start_point):
    """使用 elkai 库求解最短回路（适合大数据量）"""
    # 1. 提取所有节点
    nodes = set()
    for from_node, to_node, _ in data:
        nodes.add(from_node)
        nodes.add(to_node)
    nodes = list(nodes)
    
    # 确保起点是第一个节点
    if start_point not in nodes:
        raise ValueError(f"起点 {start_point} 不在节点中")
    nodes.remove(start_point)
    nodes = [start_point] + nodes
    n = len(nodes)
    
    # 2. 构建索引和距离矩阵
    idx = {node: i for i, node in enumerate(nodes)}
    dist_matrix = np.zeros((n, n), dtype=np.int32)  # elkai 要求整数
    
    for from_node, to_node, duration in data:
        i, j = idx[from_node], idx[to_node]
        dist_matrix[i, j] = int(round(duration))  # 转为整数
        # 注意：不对称矩阵，双向都要设置
        # 但你的数据本身不对称，按原样填充即可
    
    # 3. 求解
    permutation = elkai.solve_int_matrix(dist_matrix, runs=10)
    
    # 4. 恢复路径
    path = [nodes[i] for i in permutation] + [start_point]
    
    # 计算实际总距离（用原始数据）
    total = 0
    for k in range(len(permutation) - 1):
        total += dist_matrix[permutation[k], permutation[k+1]]
    total += dist_matrix[permutation[-1], permutation[0]]
    
    return path, total