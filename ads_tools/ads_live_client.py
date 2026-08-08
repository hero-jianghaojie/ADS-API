# -*- coding: utf-8 -*-
"""
ADS Live Client — 在 VS Code 终端运行，驱动 ADS 里的 Live Server 逐步构建版图。

用法：
    python ads_live_client.py --seed 42     # 指定随机种子（可复现）
    python ads_live_client.py               # 随机种子（每次不同）

前置条件：
    用户需先在 ADS 中启动 ads_live_server.py（见该文件顶部说明）。
    本脚本通过 XML RPC (127.0.0.1:8765) 调用服务器，逐批添加图形，
    你在 ADS 的 layout 窗口里可以实时看到每一步变化。
"""
import argparse
import random
import xmlrpc.client

PORT = 8765


def connect():
    return xmlrpc.client.ServerProxy(f"http://127.0.0.1:{PORT}/", allow_none=True)


def build_layout(seed=None, region_size=20, square_size=1, rect_w=3, rect_h=1.6):
    proxy = connect()
    print(">> ping:", proxy.ping())
    print(">> open_layout:", proxy.open_layout("BT"))
    print(">> clear_layout:", proxy.clear_layout())

    if seed is not None:
        random.seed(seed)
    else:
        random.seed()

    rect_y = (region_size - rect_h) / 2
    rect_y_end = rect_y + rect_h

    # ---------- 与 layout.py 相同的随机连通方块生成逻辑 ----------
    left_starts = [(0, y) for y in range(region_size) if rect_y < y + 1 and y < rect_y_end]
    right_starts = [(region_size - 1, y) for y in range(region_size) if rect_y < y + 1 and y < rect_y_end]

    selected = set()
    left_set = set(random.sample(left_starts, random.randint(1, len(left_starts))))
    right_set = set(random.sample(right_starts, random.randint(1, len(right_starts))))
    selected.update(left_set, right_set)

    def get_frontier(cells_set):
        f = set()
        for (cx, cy) in cells_set:
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nb = (cx + dx, cy + dy)
                if 0 <= nb[0] < region_size and 0 <= nb[1] < region_size and nb not in selected:
                    f.add(nb)
        return f

    def adjacent_to_set(cell, other_set):
        cx, cy = cell
        return any((cx + dx, cy + dy) in other_set for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)])

    left_frontier = get_frontier(left_set)
    right_frontier = get_frontier(right_set)

    max_steps = region_size * region_size * 2
    connected = False
    step = 0
    while step < max_steps and not connected:
        if left_set & right_set or any(adjacent_to_set(c, right_set) for c in left_set):
            connected = True
            break
        left_speed = random.randint(1, 5)
        right_speed = random.randint(1, 5)
        for _ in range(left_speed):
            if not left_frontier:
                break
            if random.random() < 0.3 and right_set:
                biased = [c for c in left_frontier if adjacent_to_set(c, right_set)]
                chosen = random.choice(biased) if biased else random.choice(list(left_frontier))
            else:
                chosen = random.choice(list(left_frontier))
            left_frontier.discard(chosen)
            selected.add(chosen)
            left_set.add(chosen)
        left_frontier = get_frontier(left_set)
        for _ in range(right_speed):
            if not right_frontier:
                break
            if random.random() < 0.3 and left_set:
                biased = [c for c in right_frontier if adjacent_to_set(c, left_set)]
                chosen = random.choice(biased) if biased else random.choice(list(right_frontier))
            else:
                chosen = random.choice(list(right_frontier))
            right_frontier.discard(chosen)
            selected.add(chosen)
            right_set.add(chosen)
        right_frontier = get_frontier(right_set)
        step += 1

    print(f">> connected={connected}, squares={len(selected)}")

    # ---------- 逐批添加方块（每批 20 个，方便你实时观看生长） ----------
    squares = sorted(selected)
    batch = 0
    for i in range(0, len(squares), 20):
        batch += 1
        chunk = squares[i:i + 20]
        for (x, y) in chunk:
            pts = [
                [x, y],
                [x + square_size, y],
                [x + square_size, y + square_size],
                [x, y + square_size],
            ]
            proxy.add_polygon(pts)
        print(f">> batch {batch}: +{len(chunk)} squares")

    # ---------- 左右矩形 ----------
    proxy.add_polygon([[-rect_w, rect_y], [0, rect_y], [0, rect_y + rect_h], [-rect_w, rect_y + rect_h]])
    print(">> left rect added")
    proxy.add_polygon([[region_size, rect_y], [region_size + rect_w, rect_y],
                       [region_size + rect_w, rect_y + rect_h], [region_size, rect_y + rect_h]])
    print(">> right rect added")

    # ---------- 端口 ----------
    port_y = rect_y + rect_h / 2
    proxy.add_port("P1", -rect_w, port_y)
    print(">> port P1 added")
    proxy.add_port("P2", region_size + rect_w, port_y)
    print(">> port P2 added")

    proxy.view_all()
    print(">> show_all_layers:", proxy.show_all_layers())
    print(">> save:", proxy.save_layout())
    print("== DONE: 请到 ADS 中查看 BT:layout ==")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="驱动 ADS Live Server 构建版图")
    parser.add_argument("--seed", type=int, default=None, help="随机种子（可复现）")
    parser.add_argument("--region-size", type=int, default=20, help="区域大小，默认 20")
    args = parser.parse_args()
    build_layout(seed=args.seed, region_size=args.region_size)
