"""建冲突图、找环、渲染报告。"""


class Counter:
    """记录建图时比较过的操作对数。"""

    def __init__(self):
        self.scanned = 0


def conflicts(ops, counter):
    """返回冲突边集合，元素是 (先, 后) 事务号。"""
    edges = set()
    by_item = {}
    for index, op in enumerate(ops):
        by_item.setdefault(op["item"], []).append(index)
    for group in by_item.values():
        for pos_i in range(len(group)):
            for pos_j in range(pos_i + 1, len(group)):
                counter.scanned += 1
                a = ops[group[pos_i]]
                b = ops[group[pos_j]]
                if a["txn"] == b["txn"]:
                    continue
                if a["kind"] == "r" and b["kind"] == "r":
                    continue
                edges.add((a["txn"], b["txn"]))
    return edges


def find_cycle(edges):
    """返回一条环上的事务路径，找不到返回 None。"""
    graph = {}
    nodes = set()
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
        nodes.add(a)
        nodes.add(b)
    state = {}
    stack = []
    for start in sorted(nodes):
        if state.get(start) == "done":
            continue
        work = [(start, iter(sorted(graph.get(start, ()))))]
        state[start] = "active"
        stack.append(start)
        while work:
            node, neighbors = work[-1]
            advanced = False
            for nxt in neighbors:
                if state.get(nxt) == "active":
                    cycle_start = stack.index(nxt)
                    return stack[cycle_start:] + [nxt]
                if state.get(nxt) != "done":
                    state[nxt] = "active"
                    stack.append(nxt)
                    work.append((nxt, iter(sorted(graph.get(nxt, ())))))
                    advanced = True
                    break
            if not advanced:
                state[node] = "done"
                stack.pop()
                work.pop()
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
