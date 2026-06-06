from functools import lru_cache


class _TspSolver:
    """TSP求解器，封装距离矩阵和DP求解"""

    def __init__(self, distances, all_nodes, start):
        self.distances = distances
        self.all_nodes = all_nodes
        self.start = start
        self.n = len(all_nodes)

    @classmethod
    def from_data(cls, data, start):
        """从原始数据构建求解器"""
        distances = {}
        nodes = set()

        for pairedNodes, duration in data:
            from_node, to_node = pairedNodes
            distances[pairedNodes] = duration
            nodes.add(from_node)
            nodes.add(to_node)

        nodes = list(nodes)
        if start not in nodes:
            raise ValueError(f"起点 '{start}' 不在节点集合中")

        nodes.remove(start)
        all_nodes = [start] + nodes

        print(f"找到 {len(all_nodes)} 个节点: {all_nodes}")
        return cls(distances, all_nodes, start)

    def get_dist(self, a, b):
        return self.distances.get((a, b), float('inf'))

    @lru_cache(maxsize=None)
    def dp(self, visited_mask, last_idx):
        """
        visited_mask: 已访问节点的位掩码（不包括起点）
        last_idx: 最后访问的节点在 all_nodes 中的索引
        """
        if visited_mask == (1 << (last_idx - 1)):
            return self.get_dist(self.start, self.all_nodes[last_idx])

        if visited_mask == 0:
            return self.get_dist(self.start, self.all_nodes[last_idx])

        min_cost = float('inf')
        for prev_idx in range(1, self.n):
            if prev_idx == last_idx:
                continue
            if visited_mask & (1 << (prev_idx - 1)):
                prev_mask = visited_mask & ~(1 << (last_idx - 1))
                cost = (
                    self.dp(prev_mask, prev_idx)
                    + self.get_dist(self.all_nodes[prev_idx], self.all_nodes[last_idx])
                )
                if cost < min_cost:
                    min_cost = cost
        return min_cost

    def solve(self):
        """
        求解非对称TSP问题（环形，需回到起点）
        返回:
            (最佳路径列表, 最短总时间)
        """
        n = self.n
        all_nodes = self.all_nodes
        start = self.start

        # 1. 计算最终结果（回到起点）
        full_mask = (1 << (n - 1)) - 1
        best_cost = float('inf')
        best_last_idx = None

        for last_idx in range(1, n):
            cost = self.dp(full_mask, last_idx) + self.get_dist(all_nodes[last_idx], start)
            if cost < best_cost:
                best_cost = cost
                best_last_idx = last_idx

        # 2. 重构路径（反向回溯）
        rev_path = [all_nodes[best_last_idx]]
        mask = full_mask
        last_idx = best_last_idx

        while True:
            if mask == (1 << (last_idx - 1)):
                break

            found = False
            for prev_idx in range(1, n):
                if prev_idx == last_idx:
                    continue
                if mask & (1 << (prev_idx - 1)):
                    prev_mask = mask & ~(1 << (last_idx - 1))
                    if prev_mask == 0:
                        prev_cost = self.get_dist(start, all_nodes[prev_idx])
                    else:
                        prev_cost = self.dp(prev_mask, prev_idx)

                    current_cost = prev_cost + self.get_dist(all_nodes[prev_idx], all_nodes[last_idx])
                    if abs(current_cost - self.dp(mask, last_idx)) < 1e-6:
                        rev_path.append(all_nodes[prev_idx])
                        mask = prev_mask
                        last_idx = prev_idx
                        found = True
                        break

            if not found:
                break

        path = [start] + rev_path[::-1] + [start]
        return path, best_cost

    MAX_WAYPOINTS = 16  # 每个导航链接最多支持的途经点数量

    def _get_coord_list(self, path):
        """从路径中提取坐标列表（去掉末尾重复起点）"""
        coord_list = []
        for node in path[:-1]:
            if hasattr(node, 'latlon'):
                coord_list.append(node.latlon)
            else:
                for n in self.all_nodes:
                    if hasattr(n, 'address') and n.address == node:
                        coord_list.append(n.latlon)
                        break
                else:
                    coord_list.append(str(node))
        return coord_list

    def to_link(self, path, mode='car'):
        """
        将solve()输出的路径转为高德地图导航链接
        如果途经点超过 limit，自动分段生成多个首尾相连的链接
        返回: 导航链接列表
        """
        coords = self._get_coord_list(path)
        n = len(coords)  # 总节点数（不包含末尾重复起点）
        from manage_path import generate_amap_navigation_link

        # 每个链接最多容纳: 1个起点 + MAX_WAYPOINTS个途经点 + 1个终点 = MAX_WAYPOINTS + 2
        chunk_size = self.MAX_WAYPOINTS + 2

        links = []
        for i in range(0, n - 1, chunk_size - 1):
            seg = coords[i:i + chunk_size]
            origin = seg[0]
            destination = seg[-1]
            waypoints = ';'.join(seg[1:-1])
            links.append(generate_amap_navigation_link(
                origin=origin,
                destination=destination,
                waypoint=waypoints,
                mode=mode,
            ))

        return links


# ========== 使用示例 ==========
if __name__ == "__main__":
    # 你的数据示例
    data = {
        (('东钱湖', '天一广场'), 1944),
        (('天一广场', '东钱湖'), 1670),
        (('东钱湖', '老外滩'), 1500),
        (('老外滩', '东钱湖'), 1450),
        (('天一广场', '老外滩'), 800),
        (('老外滩', '天一广场'), 850),
        (('东钱湖', '南塘老街'), 2000),
        (('南塘老街', '东钱湖'), 1950),
        (('天一广场', '南塘老街'), 600),
        (('南塘老街', '天一广场'), 620),
        (('老外滩', '南塘老街'), 900),
        (('南塘老街', '老外滩'), 880),
    }

    path, total_time = _TspSolver.from_data(data, start='东钱湖').solve()
    # print(f"\n最佳路径: {' -> '.join(path)}")
    print(f"总耗时: {total_time} 秒 ≈ {total_time / 60:.1f} 分钟")