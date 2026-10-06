# txn-serial-check

对一份事务调度做可串行化判定：先由冲突关系建图，再找环，最后渲染成文本报告。只用 Python 标准库。

```
python3 -m unittest discover -s tests
python3 -m serialcheck --sample=rw
python3 -m serialcheck --sample=reversed
python3 -m serialcheck --sample=longcycle
python3 -m serialcheck --sample=self
python3 -m serialcheck --sample=work
```

## 口径

- **冲突**：同一数据项上，来自不同事务的两个操作只要有一个是写，就构成冲突，先后决定边的方向（先者指向后者）。
- **图**：读读不构成冲突；同一事务内部的操作不构成冲突；边去重。
- **可串行化**：冲突图无环即可串行化，环可以任意长。

## 不变量

- 冲突列表里的边都指向不同事务，且方向与调度先后一致。
- 判定为不可串行化时报告里给出至少一个环。
- `scanned` 不随操作数平方级放大：两千个操作的 `scanned` 不超过 6000。

## 输出契约

报告文本：`conflicts:` 标题，随后每条边一行 `  <a> -> <b>`（按 a、b 排序），
再给出 `conflicts=<边数>` 与 `serializable=<true|false>`，不可串行化时再给 `cycle=<路径>`。
`--sample=work` 只打印 `{"ops": N, "scanned": N}`。
