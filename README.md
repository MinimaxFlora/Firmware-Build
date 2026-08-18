<div align="center">

# 📡 Firmware-Build

### OpenWrt 定制固件一键构建 · 云端编译 · 开箱即用

![GitHub release](https://img.shields.io/github/v/release/MinimaxFlora/Firmware-Build?style=for-the-badge&logo=github&color=blue)
![GitHub stars](https://img.shields.io/github/stars/MinimaxFlora/Firmware-Build?style=for-the-badge&color=yellow)
![OpenWrt](https://img.shields.io/badge/OpenWrt-24.10%20%7C%2025.12-00A98F?style=for-the-badge&logo=openwrt&logoColor=white)
![Platform](https://img.shields.io/badge/平台-GitHub%20Actions-8A2BE2?style=for-the-badge)

</div>

---

## ✨ 特性

| | | |
| :--- | :--- | :--- |
| 🚀 **云端编译** | 🔄 **版本自动检测** | 🧩 **第三方插件** |
| GitHub Actions 构建，无需本地环境 | 自动拉取 OpenWrt 官方最新稳定版 | 自动导入 Extras_Paclages 插件 |
| 📦 **多架构支持** | 🌐 **Web 服务器可选** | 🎨 **LuCI 主题定制** |
| x86 全系 + Rockchip | uhttpd / nginx 自由切换 | 默认 argon 主题，6 种预设可选 |
| 🔌 **PPPoE 拨号** | 🖥️ **预设后台 IP** | 📤 **自动发布 Release** |
| 构建时写入宽带账号密码 | 首次启动自动设置管理地址 | 固件 + 后台信息自动发布 |

---

## 📥 使用方法

1. 打开本仓库 **Actions** 页面
2. 选择 **Build OpenWrt Firmware** 工作流
3. 点击 **Run workflow**，填写参数
4. 等待构建完成（约 10-30 分钟）
5. 在 **Releases** 页面下载固件

> 💡 构建完成后固件自动发布到 Releases，包含完整的刷机镜像和后台信息说明。
> 另有 **Build OpenWrt Firmware (Private)** 工作流，使用自建 runner 加速构建。

---

## ⚙️ 构建参数

| 参数 | 必填 | 默认值 | 说明 |
| :--- | :---: | :--- | :--- |
| **arch** | ✅ | `x86-64` | 设备架构：x86-64 / x86-generic / x86-geode / x86-legacy / rockchip-armv8 |
| **series** | ✅ | `25` | OpenWrt 系列：`24`（24.10 ipk）或 `25`（25.12 apk） |
| **profile** | ❌ | `generic` | 设备 PROFILE（rockchip 填型号，如 `friendlyarm_nanopi-r4s`） |
| **custom_router_ip** | ✅ | `192.168.100.1` | 路由器管理地址（仅多网口路由器有效） |
| **rootfs_partsize** | ✅ | `1G` | 软件包分区大小：1G / 2G / 3G / 4G |
| **web_server** | ✅ | `uhttpd` | Web 服务器：`uhttpd`（装 luci）或 `nginx`（装 luci-nginx + 自动配置） |
| **theme** | ✅ | `argon` | LuCI 主题预设：`argon` / `kucat` / `aurora` / `design` / `shadcn` / `fluent`（不设置默认 argon） |
| **packages** | ❌ | *(空)* | 额外插件，空格分隔（如 `luci-app-openclash luci-app-passwall`） |
| **root_password** | ❌ | *(空)* | 固件 root 密码（留空则保持默认空密码） |

---

## 🔑 Secrets（仓库密钥）

在仓库 **Settings → Secrets and variables → Actions** 中配置：

| Secret | 必填 | 说明 |
| :--- | :---: | :--- |
| `PPPOE_ACCOUNT` | ❌ | 宽带账号；与 `PPPOE_PASSWORD` **同时设置**才启用 PPPoE 拨号 |
| `PPPOE_PASSWORD` | ❌ | 宽带密码；不填则 WAN 保持 DHCP |

---

## 🧭 架构选择

| 架构 | 适用设备 |
| :--- | :--- |
| `x86-64` | 主流 x86 软路由（J4125 / N5105 / 倍控 / R86S 等） |
| `x86-generic` | 通用 x86 设备 |
| `x86-geode` | Geode 平台工控机 |
| `x86-legacy` | 老款 x86 设备（不支持 UEFI） |
| `rockchip-armv8` | 瑞芯微 ARM 设备（R4S / R2S / NanoPi 等） |

---

## 🌐 Web 服务器选择

| 选项 | 安装包 | 说明 |
| :--- | :--- | :--- |
| `uhttpd`（默认） | `luci` | 系统默认 Web 服务器，轻量稳定 |
| `nginx` | `luci-nginx` | 高性能 Nginx，首次启动自动写入监听 80 / conf.d 包含等配置 |

> 选 nginx 时固件首次开机自动执行完整的 nginx uci 配置并重启服务，无需手动设置。

---

## 🎨 LuCI 主题定制

预设主题（默认 `argon`，不设置即 argon），下拉选择即可：

| 预设 | 安装包 |
| :--- | :--- |
| `argon`（默认） | `luci-theme-argon` + `luci-i18n-argon-config-zh-cn` |
| `kucat` | `luci-theme-kucat` + `luci-i18n-kucat-config-zh-cn` |
| `aurora` | `luci-theme-aurora` + `luci-i18n-aurora-config-zh-cn` |
| `design` | `luci-theme-design` |
| `shadcn` | `luci-theme-shadcn` |
| `fluent` | `luci-theme-fluent` + `luci-i18n-fluent-zh-cn` |

---

## 📦 构建产物

固件发布在 **Releases** 页面，tag 格式：

```
Autobuild-<架构>          # 云端构建
Private-<架构>            # 自建 runner 构建
```

每个 Release 包含：
- 📥 刷机镜像（`.img.gz` / `.bin`）
- 📋 后台信息说明（管理地址 / 账号密码 / Web 服务器 / 主题 / 已装插件）

---

## 🛠️ 工作原理

```
workflow_dispatch 手动触发
        │
        ▼
检测 OpenWrt 官方最新版本（24.x / 25.x）
        │
        ▼
官方下载 ImageBuilder ──▶ 解压
        │
        ▼
写入 uci-defaults（LAN IP / PPPoE / nginx / root 密码 / 作者信息）
        │
        ▼
组装软件包（默认包 + Web 服务器 + 主题 + 额外插件）
        │
        ▼
导入 Extras_Paclages 第三方插件（ipk / apk / .run）
        │
        ▼
make image ──▶ 生成固件 ──▶ 发布 Release
```

> 底层由 [gh-action-imagebuilder](https://github.com/MinimaxFlora/gh-action-imagebuilder) 驱动，
> ImageBuilder 直接从 OpenWrt 官方下载，自动检测最新版本，无需手动维护。

---

<div align="center">

**Made with ❤️ by [MinimaxFlora](https://github.com/MinimaxFlora)**

</div>
