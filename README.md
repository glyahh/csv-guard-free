# CSV Guard Free 1.0：免费检查 CSV 前导零、重复行与空白

本地命令行工具，帮助你在把 CSV 交给表格软件前发现应特别检查的列。免费、无账号、无第三方 Python 依赖；不上传数据、不收集邮箱或个人资料。本仓库提供免费源码、原创虚构样例与可重复测试。

## 适合谁：商品 SKU、邮编等编号的 CSV 导入前检查

适合能运行 Python 命令的商品目录维护者、数据整理人员和开发者：手里已有逗号分隔 CSV，希望在交给 Excel 或下游程序前，检查纯数字前导零、完整重复记录、两端空白与潜在公式前缀。

这不是 Excel 插件、在线上传网站或自动清洗器；不需要注册。不会替你决定哪些重复记录应删除，也不能恢复源文件里已经丢失的零。只想双击操作、需要 XLSX 或超过 20 MiB 文件处理的用户，请先看下方限制，不要把本工具当作现成解决方案。

**开始使用：**在仓库上方选择 **Code → Download ZIP**，解压后进入含 `demo.py` 的目录，运行下方演示。所有数据处理在本地进行，MIT 许可允许修改和商用；无需购买其他资料包。

## 为什么 CSV 编号 000123 打开后可能变成 123？

编号 `000123` 若被软件作为数值解析，可能变成 `123`。CSV 不保存列类型，仅用引号包住数字也不能阻止所有表格软件自动推断。pandas 用户的真实公开问题 [#54665](https://github.com/pandas-dev/pandas/issues/54665) 记录过这种需求，并已通过显式文本类型解决，不是本工具宣称发现了当前漏洞。

## 英文实测教程 / English walkthrough

[Keep `000123` intact: a reproducible CSV identifier check before spreadsheet import](docs/csv-leading-zero-check.md) 用同一份虚构样例说明不下载工具也能进行的人工检查、Python 实测结果和局限；文中明确披露 AI 协助，Excel 指引未原生实测。

## 先看可重复演示

需要 Python 3.10+（实测 Linux / Python 3.12.14）。解压后在目录内执行：

```bash
python demo.py
python -m unittest discover -s tests -v
```

Linux/macOS 若 `python` 不可用，可用 `python3`；Windows 有 Python Launcher 时可用 `py`。Windows/macOS 未实测。不需要 pip 安装，不改变安全设置。

原创 `examples/catalog.csv` 只有 5 条虚构商品记录。真实运行预期：

- 第 1 列 SKU 有 5 格纯数字前导零，第 3 列邮编也有 5 格；这不是错误，是按文本导入的提醒。
- 1 条完整重复行；不等于一定该删，可能有业务含义。
- 1 条潜在公式行；不会执行公式。
- 第 2 列商品名有 2 格两端空白。

例如样例第一条记录的 SKU 是 `000123`、邮编是 `010001`，商品名两端有空白。报告不会打印这些字段值，而是给出列号汇总；下面摘录的是运行结果中的部分字段，不是完整 JSON：

```text
rows: 5
exact_duplicate_rows: 1
formula_prefix_rows: 1
column_number: 1 → leading_zero_digit_cells: 5
column_number: 2 → outer_whitespace_cells: 2
column_number: 3 → leading_zero_digit_cells: 5
```

下一步应核对编号列是否按文本导入，并按自己的业务规则复核重复记录；看到公式前缀提示也不要直接认定为恶意。**这是虚构样例的实测结果，不是客户案例。**

`demo.py` 会对上述结果和源文件未变作断言。结果不符会失败，而不是显示假成功。`evidence/` 中保存本次运行日志。

## 检查自己的 CSV

对你有权处理的本地副本运行：

```bash
python inspect_csv.py "你的文件.csv"
python inspect_csv.py "你的GB18030文件.csv" --encoding gb18030
```

只向终端打印 JSON 汇总，不生成或覆盖业务文件。若需自己保存汇总，可使用终端重定向，但不要将输出路径指向输入文件。报告只用列号，不输出表头或字段内容；仍含文件 SHA-256 和汇总数量，不建议把敏感数据报告公开上传。

## 看懂报告

- `leading_zero_digit_cells`：第一个字符为 0、长度大于 1 的 ASCII 纯数字字符串数量。带空格、符号或字母的编号不计入，不是通用编号识别器。
- `exact_duplicate_rows`：逐字段完全一致的重复记录数，保留第一条后其余数量；本工具不删除。
- `formula_prefix_rows`：忽略前置空白后以 `= + - @` 开头的字段所在记录数。负数也会被提示，不是恶意判定。
- `outer_whitespace_cells`、`blank_cells`、`literal_NA_cells`：两端空白、空字符串、字面 `NA` 数量；三者不混同。
- `formula_prefix_headers`：表头出现潜在公式前缀的数量。请勿未经复核在可执行公式的环境中打开。

## 免费即可采取的处理

无需购买清洗包，也可以用 CSV 文本编辑器检查编号是否仍有零，通过下方方法按文本导入 Excel，并根据业务规则人工决定是否保留重复行。始终保留原始文件。本工具也允许按 MIT 许可自行修改和商用，详见 [MIT 许可证](LICENSE)。

## Excel 导入（官方依据，未原生实测）

通过“数据 → 从文本/CSV”导入，选择 UTF-8、逗号分隔；若提供数据类型检测选项，可关闭推断，让各列按文本读取。进“转换数据/编辑”后确认编号列为文本，再加载，并核对 `000123`。如先前的类型转换已经丢零，应撤销转换从源文件重新导入，事后将 123 改为文本不会恢复 000123。

微软官方说明：[保留前导零和大数](https://support.microsoft.com/en-au/excel/keeping-leading-zeros-and-large-numbers)、[Text/CSV 连接器](https://learn.microsoft.com/en-us/power-query/connectors/text-csv)。菜单可能随版本不同，本次未操作 Excel，不保证双击 CSV 不转换。

## 限制

仅逗号分隔、UTF-8/UTF-8 BOM 或显式 GB18030；20 MiB 输入上限，不接受符号链接、目录、设备或 FIFO。先检查大小再有界读取，解析内存仍可能显著高于文件大小，不是流式大数据工具。标准库可能拒绝超长字段；不处理 XLSX、分号 CSV、日期/金额转换、修复损坏文件或恢复丢失前导零。错误编码、缺表头、重复表头、字段数不齐或畸形引号会返回退出码 2，不静默跳行。

不是完整安全扫描器，也不承诺面对恶意同机并发修改者的数据一致性。没有真实客户数据、销量、节省时间或收益验证。脚本不联网；Python 自身生成的 __pycache__ 缓存不包含输入 CSV 字段值。

## 免费版与付费候选的差别

见 [免费版与付费候选边界](FREE_VS_CANDIDATE.md)。本包不含支付、注册、邮箱表单、追踪代码或销售链接，也不开始销售。

## 下载与反馈

在 GitHub 仓库页面选择 **Code → Download ZIP**，解压后进入含 `demo.py` 的目录，再执行上面的命令。也可使用 Git 克隆本仓库。

若发现问题，可在本仓库 [Issues](https://github.com/glyahh/csv-guard-free/issues) 描述操作系统、Python 版本、文件编码、预期与实际结果。仅提交自己编写的虚构最小样例；不要上传真实订单、客户资料、账号、凭据、原始业务文件或敏感报告。反馈不构成服务购买或交付承诺。
