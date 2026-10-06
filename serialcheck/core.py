"""建冲突图、找环、渲染报告。"""


class Counter:
    """记录建图时比较过的操作对数。"""

    def __init__(self):
        self.scanned = 0


def conflicts(ops, counter):
    """返回冲突边集合，元素是 (先, 后) 事务号。"""
    edges = set()
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            counter.scanned += 1
            a, b = ops[i], ops[j]
            if a["item"] != b["item"]:
                continue
            if a["txn"] == b["txn"]:
                edges.add((a["txn"], a["txn"]))
                continue
            if a["kind"] == "w" and b["kind"] == "w":
                edges.add((b["txn"], a["txn"]))
    return edges


def find_cycle(edges):
    """返回一条环上的事务路径，找不到返回 None。"""
    for a, b in edges:
        if (b, a) in edges:
            return [a, b, a]
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
