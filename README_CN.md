<div align="center">

> 🇨🇳 中文 | 🇬🇧 [English](README.md)

<img src="https://alphaosu.keytoix.vip/assets/favicon.0d142200.ico" width="72" style="border-radius:16px">

# AlphaOsu! Download Tool

**基于机器学习推荐的 osu! 谱面批量下载桌面工具**

<img src="https://img.shields.io/badge/osu!-PP%20Farming-pink?style=for-the-badge&logo=osu" alt="osu!">
<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/PyWebView-GUI-6c8cff?style=for-the-badge" alt="PyWebView">
<img src="https://img.shields.io/badge/License-MIT-4cdb8a?style=for-the-badge" alt="MIT">

<br><br>

<img src="https://raw.githubusercontent.com/zureealLV/AlphaOsu-Download-Tool/master/screenshots/main.png" width="80%" alt="主界面">

<br>

> 输入 osu! 用户名 → ML 推荐谱面 → 筛选 → 批量下载 .osz → 双击导入游戏

<br>
</div>

---

## ✨ 功能一览

| 功能 | 说明 |
|:---|:---|
| 🎯 **ML 推荐** | 基于 AlphaOsu 机器学习，推荐你最有可能拿 PP 的谱面 |
| ⭐ **多维筛选** | 星数范围、Mod 类型、上榜概率、破纪录概率 |
| 🖼️ **封面预览** | 每首歌显示 beatmap 封面，一眼认出 |
| ☑️ **多选下载** | 勾选想要的谱面，批量下载 |
| 📁 **自定义目录** | 选择保存位置，直接下到 osu! Songs 文件夹 |
| ⬇️ **Sayobot 镜像** | 国内高速下载源，免登录 |
| 🚫 **隐藏已玩** | 自动过滤已打过的谱面 |

## 📸 截图

<div align="center">

<img src="https://raw.githubusercontent.com/zureealLV/AlphaOsu-Download-Tool/master/screenshots/main.png" width="80%" alt="主界面">

<br><br>

<img src="https://raw.githubusercontent.com/zureealLV/AlphaOsu-Download-Tool/master/screenshots/filter.png" width="80%" alt="筛选条件">

<br><br>

<img src="https://raw.githubusercontent.com/zureealLV/AlphaOsu-Download-Tool/master/screenshots/downloading.png" width="80%" alt="下载中">

</div>

## 🚀 快速开始

### 下载 EXE（推荐）

前往 [**Releases**](../../releases) 页面下载 `AlphaOsuDownloadTool.exe`，双击即用。

### 从源码运行

```bash
git clone https://github.com/zureealLV/AlphaOsu-Download-Tool.git
cd AlphaOsu-Download-Tool
pip install pywebview
python main.py
```

### 打包为 EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name "AlphaOsuDownloadTool" main.py
```

## 🏗️ 技术架构

```
┌───────────────────────────────────────────┐
│         PyWebView Native Window           │
│  ┌─────────────────────────────────────┐  │
│  │       HTML / CSS / JavaScript       │  │
│  │  filters · table · covers · UI      │  │
│  └──────────────┬──────────────────────┘  │
│                 │ pywebview.api           │
│  ┌──────────────▼──────────────────────┐  │
│  │        Python Backend               │  │
│  │ login · get_page · choose_dir       │  │
│  │ download                            │  │
│  └──────────────┬──────────────────────┘  │
└─────────────────┼─────────────────────────┘
                  │ HTTPS
       ┌──────────▼──────────┐
       │   AlphaOsu API      │  ← ML 推荐数据
       └─────────────────────┘
       ┌─────────────────────┐
       │  Sayobot Mirror     │  ← .osz 下载
       └─────────────────────┘
```

## 🎮 使用方法

1. **输入用户名** — 填入你的 osu! 用户名，点击「获取推荐」
2. **调整筛选** — 拖动滑块选择星数范围、概率阈值，勾选 Mod
3. **选择谱面** — 逐个勾选或全选
4. **开始下载** — 点击「下载选中」或「全部下载」
5. **导入游戏** — 双击 .osz 文件自动导入 osu!

## 🙏 致谢

- [**AlphaOsu**](https://alphaosu.keytoix.vip/) — 机器学习 PP 推荐引擎
- [**Sayobot**](https://sayobot.cn/) — 国内 osu! 谱面镜像
- [**PyWebView**](https://pywebview.flowrl.com/) — 跨平台桌面 GUI 框架

---

<div align="center">
<sub>Made with 💜 for the osu! community</sub>
<br><br>
</div>
