#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_feed_packages.py — 构建前确认请求的插件真的在 Extras_Paclages 里

用法:
    check_feed_packages.py <series 24|25> <feed_host> <folder> <package...>

    series=25 → <feed_host>/apk/<folder>/index.json
    series=24 → <feed_host>/ipk/<folder>/Packages

退出码: 0 全部存在；1 有缺失（会逐个 ::error:: 点名）；2 用法错误；3 网络/解析失败
"""
import json
import sys
import urllib.request


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "firmware-build/check"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def names_apk(url):
    idx = json.loads(fetch(url).decode("utf-8", "replace"))
    items = idx["packages"] if isinstance(idx, dict) and "packages" in idx else idx
    names = set()
    for it in items:
        n = it.get("name") if isinstance(it, dict) else it
        if n:
            names.add(n)
    return names


def names_ipk(url):
    text = fetch(url).decode("utf-8", "replace")
    return {line.split(":", 1)[1].strip()
            for line in text.splitlines() if line.startswith("Package:")}


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        return 2
    series, feed_host, folder = sys.argv[1], sys.argv[2].rstrip("/"), sys.argv[3]
    want = [p for p in sys.argv[4:] if p]

    url = ""
    try:
        if series == "25":
            url = f"{feed_host}/apk/{folder}/index.json"
            names = names_apk(url)
        else:
            url = f"{feed_host}/ipk/{folder}/Packages"
            names = names_ipk(url)
    except Exception as e:
        print(f"::error::读不到 feed 索引 {url}: {e}")
        return 3

    print(f"索引 {url}")
    print(f"feed 里有 {len(names)} 个包，本次请求 {len(want)} 个")
    missing = []
    for p in want:
        bare = p.lstrip("-")
        ok = bare in names
        print(f"  {'OK  ' if ok else '缺少'} {p}")
        if not ok:
            missing.append(bare)
    for m in missing:
        print(f"::error::feed 里没有这个插件：{m}（检查拼写，或它还没被编译发布）")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
