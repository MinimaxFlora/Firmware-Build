#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""resolve_i18n.py — 为请求的 luci-app-* 自动找出对应的简体中文语言包

用法:
    resolve_i18n.py <series 24|25> <feed_host> <folder> <package...>

输出（仅标准输出最后一行）: 需要额外安装的语言包，空格分隔
其余过程信息一律写到标准错误，避免污染调用方的命令替换。
找不到对应语言包只提示，不算失败（退出码始终 0）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_feed_packages import names_apk, names_ipk  # noqa: E402

# 额外兜底：即使没请求对应插件，这几张表也补齐（LuCI 主界面 / 防火墙 / 包管理）
BASE_PACKS = ["luci-i18n-base-zh-cn", "luci-i18n-firewall-zh-cn"]


def main():
    if len(sys.argv) < 5:
        print(__doc__, file=sys.stderr)
        print("")
        return 0
    series, feed_host, folder = sys.argv[1], sys.argv[2].rstrip("/"), sys.argv[3]
    want = [p for p in sys.argv[4:] if p]

    try:
        if series == "25":
            names = names_apk(f"{feed_host}/apk/{folder}/index.json")
        else:
            names = names_ipk(f"{feed_host}/ipk/{folder}/Packages")
    except Exception as e:  # 拿不到索引就让构建继续，别在这里卡死
        print(f"::warning::读不到 feed 索引，跳过自动中文语言包: {e}", file=sys.stderr)
        print("")
        return 0

    extras = []
    for p in want:
        if not p.startswith("luci-app-"):
            continue
        app = p[len("luci-app-"):]
        cand = f"luci-i18n-{app}-zh-cn"
        if cand in names and cand not in extras:
            extras.append(cand)
            print(f"  + 中文语言包 {cand}", file=sys.stderr)
        else:
            print(f"  - 无中文语言包（跳过）: {cand}", file=sys.stderr)

    for b in BASE_PACKS:
        if b in names and b not in extras:
            extras.append(b)
            print(f"  + 基础语言包 {b}", file=sys.stderr)

    print(" ".join(extras))
    return 0


if __name__ == "__main__":
    sys.exit(main())
