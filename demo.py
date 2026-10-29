#!/usr/bin/env python3
"""从任意工作目录运行的原创样例演示。"""
from pathlib import Path
from inspect_csv import inspect
import json
p=Path(__file__).resolve().parent/'examples'/'catalog.csv'
before=p.read_bytes()
r=inspect(p)
assert r['rows']==5 and r['columns']==4
assert r['exact_duplicate_rows']==1 and r['formula_prefix_rows']==1
assert r['column_checks'][0]['leading_zero_digit_cells']==5
assert r['column_checks'][2]['leading_zero_digit_cells']==5
assert r['column_checks'][1]['outer_whitespace_cells']==2
assert p.read_bytes()==before
print('原创模拟目录：5 条记录，SKU 和邮编均含前导零。')
print('诊断：1 条完整重复行，1 条潜在公式行，商品名 2 格有两端空白。')
print('不修改数据；前导零并不代表错误，而是提醒下游按文本导入。')
print(json.dumps(r,ensure_ascii=False,indent=2))
print('DEMO PASS: 实际检查结果符合原创样例预期，原文件字节未改动。')
