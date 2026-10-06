"""固定场景，用来复现题面里的锚点。"""

import json

from . import core


def _op(txn, kind, item):
    return {"txn": txn, "kind": kind, "item": item}


def run(name):
    if name == "rw":
        ops = [_op(1, "r", "x"), _op(2, "w", "x")]
        print(core.report(ops, core.Counter()))
        return 0
    if name == "reversed":
        ops = [_op(1, "w", "x"), _op(2, "w", "x")]
        print(core.report(ops, core.Counter()))
        return 0
    if name == "longcycle":
        ops = [
            _op(1, "r", "x"), _op(2, "w", "x"),
            _op(2, "r", "y"), _op(3, "w", "y"),
            _op(3, "r", "z"), _op(1, "w", "z"),
        ]
        print(core.report(ops, core.Counter()))
        return 0
    if name == "self":
        ops = [_op(1, "r", "x"), _op(1, "w", "x")]
        print(core.report(ops, core.Counter()))
        return 0
    if name == "work":
        ops = [_op(1 if i % 2 == 0 else 2, "r", "i%04d" % i) for i in range(2000)]
        counter = core.Counter()
        core.conflicts(ops, counter)
        print(json.dumps({"ops": 2000, "scanned": counter.scanned}))
        return 0
    raise SystemExit("未知场景：" + name)
