#!/usr/bin/env python3
"""免费 CSV 编号体检：只读、本地、汇总输出，不清理文件。"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys

MAX_BYTES = 20 * 1024 * 1024

def read_local(path):
    path = Path(path)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('只接受普通文件，不接受目录、链接或特殊文件')
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0)
    fd = os.open(path, flags)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('只接受普通文件')
        if before.st_size > MAX_BYTES:
            raise ValueError('输入超过 20 MiB')
        with os.fdopen(fd, 'rb') as f:
            fd = None
            raw = f.read(MAX_BYTES + 1)
            after = os.fstat(f.fileno())
        if len(raw) > MAX_BYTES or after.st_size > MAX_BYTES:
            raise ValueError('输入超过 20 MiB')
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('读取期间输入发生变化')
        return raw
    finally:
        if fd is not None: os.close(fd)

def inspect(path, encoding='utf-8-sig'):
    raw = read_local(path)
    text = raw.decode(encoding, errors='strict')
    if '\x00' in text: raise ValueError('输入包含 NUL 字符')
    rows = list(csv.reader(io.StringIO(text, newline=''), strict=True))
    if not rows or not rows[0] or any(not v.strip() for v in rows[0]):
        raise ValueError('缺少表头或空表头')
    headers, data = rows[0], rows[1:]
    if len(set(headers)) != len(headers): raise ValueError('重复表头')
    if any(len(r) != len(headers) for r in data): raise ValueError('记录字段数不一致')
    def formula(v): return v.lstrip().startswith(('=', '+', '-', '@'))
    columns = []
    for index, _ in enumerate(headers):
        values = [row[index] for row in data]
        columns.append({'column_number': index+1,
            'leading_zero_digit_cells': sum(len(v)>1 and v.startswith('0') and v.isascii() and v.isdigit() for v in values),
            'outer_whitespace_cells': sum(v != v.strip() for v in values),
            'blank_cells': sum(v=='' for v in values),
            'literal_NA_cells': sum(v=='NA' for v in values),
            'formula_prefix_cells': sum(formula(v) for v in values)})
    return {'mode':'read_only', 'input_sha256': hashlib.sha256(raw).hexdigest(),
            'rows':len(data), 'columns':len(headers),
            'exact_duplicate_rows':len(data)-len({tuple(r) for r in data}),
            'formula_prefix_rows':sum(any(formula(v) for v in r) for r in data),
            'formula_prefix_headers':sum(formula(v) for v in headers),
            'column_checks':columns,
            'note':'列号从 1 开始；不输出字段值或表头；不是完整安全扫描；不修改输入'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('--encoding',choices=['utf-8-sig','gb18030'],default='utf-8-sig')
    args=parser.parse_args()
    try: result=inspect(args.input,args.encoding)
    except (OSError,ValueError,UnicodeError,csv.Error) as e:
        print('失败：'+str(e),file=sys.stderr); return 2
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': sys.exit(main())
