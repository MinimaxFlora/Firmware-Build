#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_manifest.py — 用 ImageBuilder 的 .manifest 断言包真的进了固件

manifest 每行形如:   luci-app-homeproxy - 20261111-r1
本脚本检查：请求的每个插件、主题包、Web 服务器包都在里面。

用法:
    verify_manifest.py <manifest 路径> <packages 空格分隔> <theme> <web_server>

退出码: 0 全在；1 有缺失（逐个 ::error:: 点名）；2 用法错误
"""
import os
import sys


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        return 2
    manifest, packages, theme, web = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    if not os.path.isfile(manifest):
        print(f"::error::找不到 manifest：{manifest}")
        return 1

    present = set()
    with open(manifest, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.split()
            if parts:
                present.add(parts[0])
    total_lines = sum(1 for _ in open(manifest, encoding="utf-8", errors="replace"))

    want = [p for p in packages.split() if p]
    want.append(f"luci-theme-{theme}")
    want.append("luci-nginx" if web == "nginx" else "luci")

    print(f"manifest {manifest}（{total_lines} 行，{len(present)} 个包）")
    missing = []
    for p in want:
        bare = p.lstrip("-")
        ok = bare in present
        print(f"  {'OK  ' if ok else 'MISS'} {bare}")
        if not ok:
            missing.append(bare)

    for m in missing:
        print(f"::error::固件里没有这个包：{m}")
    if missing:
        return 1
    print("断言通过：请求的插件、主题、Web 服务器都在固件里")
    return 0


if __name__ == "__main__":
    sys.exit(main())
