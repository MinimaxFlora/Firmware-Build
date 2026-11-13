# Firmware-Build

用官方 **ImageBuilder** 一键产出定制 OpenWrt 固件的 GitHub Actions 工程：选架构、选系列、勾主题、填插件，点一次 `Run workflow` 就出可刷机镜像。

底层构建由 [`MinimaxFlora/gh-action-imagebuilder`](https://github.com/MinimaxFlora/gh-action-imagebuilder) 完成（免 Docker，直接下载 `downloads.openwrt.org` 的 ImageBuilder），第三方插件来自 [`MinimaxFlora/Extras_Paclages`](https://github.com/MinimaxFlora/Extras_Paclages)（24.x → `ipk` 分支，25.x → `apk` 分支）。

---

## 工作流结构

```
.github/
├── scripts/
│   ├── check_feed_packages.py   # 构建前：插件是否真的在 feed 里
│   └── verify_manifest.py       # 构建后：插件是否真的进了固件
└── workflows/
    ├── _firmware-build.yml        # 可复用主流程（workflow_call），所有逻辑都在这里
    ├── build-release.yml          # GitHub 托管 runner 入口（tag 前缀 Autobuild）
    └── build-private-release.yml  # self-hosted runner 入口（tag 前缀 Private）
```

两个入口只负责输入表单，构建逻辑共用一份，避免两套流程各改各的漂移。

### 主流程做了什么

| 阶段 | 说明 |
|---|---|
| 1. 校验输入 | x86 必须 `profile=generic`、rockchip 必须填具体型号、主题/Web 服务器在允许列表内、管理地址格式合法 —— 几秒内失败，不浪费一次构建 |
| 2. 校验插件 | 拉 `Extras_Paclages` 索引（`apk/<arch>/index.json` 或 `ipk/<arch>/Packages`），逐个确认请求的插件真的存在；拼错的包名在这里就点名报错 |
| 3. 构建 | 调 ImageBuilder：自动取该系列最新稳定版，套用 Web 服务器、主题、默认管理地址、root 密码、PPPoE |
| 4. 产物断言 | 读 ImageBuilder 生成的 `.manifest`，逐个确认插件、主题包、Web 服务器包**真的进了固件**（不是"编译成功"就算数） |
| 5. 校验和 + 摘要 | 生成 `SHA256SUMS`，并把架构 / 系列 / 主题 / 插件 / 镜像体积 / sha256 写进 Job Summary |
| 6. 交付 | 先上传 artifact（构建失败也能下载来查），再发 Release |

---

## 使用

`Actions → Build OpenWrt Firmware → Run workflow`

| 输入 | 取值 | 说明 |
|---|---|---|
| `arch` | `x86-64` / `x86-generic` / `x86-geode` / `x86-legacy` / `rockchip-armv8` | 目标架构 |
| `series` | `24` / `25` | 24 = 24.10（opkg/ipk）、25 = 25.12（apk），自动取该系列最新稳定版 |
| `profile` | `generic`（x86）/ `friendlyarm_nanopi-r4s` 等 | ImageBuilder 的设备 PROFILE |
| `custom_router_ip` | `192.168.100.1` 等 | 首启写入的管理地址 |
| `rootfs_partsize` | `1G` / `2G` / `3G` / `4G` | 软件包分区大小 |
| `web_server` | `uhttpd` / `nginx` | `nginx` 装 `luci-nginx` 并在首启写好 nginx 配置；插件含 `quickfile` 时会自动切 nginx |
| `theme` | `argon` / `vantage` / `aurora` / `design` / `shadcn` / `fluent` | LuCI 主题 |
| `packages` | 空格分隔 | 必须是 `Extras_Paclages` 里已发布的包名 |
| `root_password` | 留空 = 空密码 | 设置了密码则**只上传 artifact、不发 Release**，避免带密码的固件公开分发 |

### 例子：x86_64 / 25.12 / Argon / nginx

```
arch              x86-64
series            25
profile           generic
custom_router_ip  192.168.100.1
rootfs_partsize   2G
web_server        nginx
theme             argon
packages          luci-app-homeproxy luci-app-nikki luci-app-mosdns luci-app-socat luci-app-ramfree luci-app-quickfile luci-app-diskman luci-app-adguardhome
```

> `luci-app-quickfile` 依赖 nginx，所以这里显式选 `nginx`；即使忘了选，构建脚本也会自动切换并打印提示。

### Secrets

| Secret | 说明 |
|---|---|
| `PPPOE_ACCOUNT` / `PPPOE_PASSWORD` | 两个都配置才会写入 PPPoE 拨号，否则 WAN 保持 DHCP |

---

## 产物

- **Release**：`Autobuild-<arch>`（托管）/ `Private-<arch>`（自建 runner），附 `*.img.gz`、`*.bin`、`SHA256SUMS` 和一份后台信息说明
- **Artifact**：`firmware-<arch>-<series>`，含镜像、`SHA256SUMS`、`.manifest`，保留 14 天
- **Job Summary**：镜像清单 + sha256 + 固件内包数量，不下载也能核对

烧录后可自查完整性：

```bash
sha256sum -c SHA256SUMS
```

---

## 常见问题

**插件名写错 / 还没发布** —— 第 2 步就失败，日志里写明 `feed 里没有这个插件：xxx`。去 `Extras_Paclages` 的 `Build OpenWrt Packages` 把包编出来并同步后再来。

**构建成功但固件里没这个包** —— 第 4 步用 `.manifest` 断言并列出缺失项，通常是依赖冲突（比如被 `CONFLICTS` 顶掉）。

**想换插件源（CDN）** —— 主流程支持 `feed_host` 输入，默认 `https://raw.githubusercontent.com/MinimaxFlora/Extras_Paclages`，可换成 jsDelivr 之类镜像。

**想跑在自建 runner** —— 用 `Build OpenWrt Firmware (Private)`，它复用同一套流程，只是 `runs-on: self-hosted` 且跳过依赖安装。
