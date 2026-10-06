"""建冲突图、找环、渲染报告。"""


class Counter:
    """记录建图时比较过的操作对数。"""

    def __init__(self):
        self.scanned = 0


def conflicts(ops, counter):
    """返回冲突边集合，元素是 (先, 后) 事务号。"""
    by_item = {}
    for op in ops:
        by_item.setdefault(op["item"], []).append(op)
    edges = set()
    for group in by_item.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                counter.scanned += 1
                a, b = group[i], group[j]
                if a["txn"] == b["txn"]:
                    continue
                if a["kind"] == "w" or b["kind"] == "w":
                    edges.add((a["txn"], b["txn"]))
    return edges


def find_cycle(edges):
    """返回一条环上的事务路径，找不到返回 None。"""
    graph = {}
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    for root in sorted(graph):
        if color[root] != WHITE:
            continue
        color[root] = GRAY
        path = [root]
        stack = [(root, iter(sorted(graph[root])))]
        while stack:
            node, it = stack[-1]
            advanced = False
            for nxt in it:
                if color.get(nxt, WHITE) == GRAY:
                    return path[path.index(nxt):] + [nxt]
                if color.get(nxt, WHITE) == WHITE:
                    color[nxt] = GRAY
                    path.append(nxt)
                    stack.append((nxt, iter(sorted(graph.get(nxt, ())))))
                    advanced = True
                    break
            if not advanced:
                color[node] = BLACK
                stack.pop()
                path.pop()
    return None


def report(ops, counter):
    """渲染文本报告。"""
    edges = conflicts(ops, counter)
    cycle = find_cycle(edges)
    lines = ["conflicts:"]
    for a, b in sorted(edges):
        lines.append("  %s -> %s" % (a, b))
    lines.append("conflicts=%d" % len(edges))
    lines.append("serializable=%s" % ("false" if cycle else "true"))
    if cycle:
        lines.append("cycle=%s" % " -> ".join(str(t) for t in cycle))
    return "\n".join(lines)
