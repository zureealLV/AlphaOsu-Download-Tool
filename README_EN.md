<div align="center">

> 🇨🇳 [中文版](README.md) | 🇬🇧 English

<img src="https://alphaosu.keytoix.vip/assets/favicon.0d142200.ico" width="72" style="border-radius:16px">

# AlphaOsu! Download Tool

**ML-powered osu! beatmap batch download desktop tool**

<img src="https://img.shields.io/badge/osu!-PP%20Farming-pink?style=for-the-badge&logo=osu" alt="osu!">
<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/PyWebView-GUI-6c8cff?style=for-the-badge" alt="PyWebView">
<img src="https://img.shields.io/badge/License-MIT-4cdb8a?style=for-the-badge" alt="MIT">

<br><br>

<img src="https://raw.githubusercontent.com/zureealLV/AlphaOsu-Download-Tool/master/screenshots/main.png" width="80%" alt="Main Interface">

<br>

> Enter osu! username → ML recommendations → Filter → Batch download .osz → Double-click to import

<br>
</div>

---

## ✨ Features

| Feature | Description |
|:---|:---|
| 🎯 **ML Recommendations** | Powered by AlphaOsu machine learning — recommends maps you're most likely to gain PP on |
| ⭐ **Multi-dimensional Filters** | Star rating range, Mod type, leaderboard probability, record-breaking probability |
| 🖼️ **Cover Preview** | Beatmap cover art displayed for each song |
| ☑️ **Multi-select Download** | Check the maps you want, batch download |
| 📁 **Custom Directory** | Choose save location, download directly to osu! Songs folder |
| ⬇️ **Sayobot Mirror** | High-speed download source for China region, no login required |
| 🚫 **Hide Played** | Auto-filter maps you've already played |

## 📸 Screenshots

<div align="center">

<img src="https://raw.githubusercontent.com/zureealLV/AlphaOsu-Download-Tool/master/screenshots/main.png" width="80%" alt="Main Interface">

<br><br>

<img src="https://raw.githubusercontent.com/zureealLV/AlphaOsu-Download-Tool/master/screenshots/filter.png" width="80%" alt="Filter Settings">

<br><br>

<img src="https://raw.githubusercontent.com/zureealLV/AlphaOsu-Download-Tool/master/screenshots/downloading.png" width="80%" alt="Downloading">

</div>

## 🚀 Quick Start

### Download EXE (Recommended)

Go to the [**Releases**](../../releases) page and download `AlphaOsuDownloadTool.exe`, double-click to run.

### Run from Source

```bash
git clone https://github.com/zureealLV/AlphaOsu-Download-Tool.git
cd AlphaOsu-Download-Tool
pip install pywebview
python main.py
```

### Build as EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name "AlphaOsuDownloadTool" main.py
```

## 🏗️ Architecture

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
       │   AlphaOsu API      │  ← ML recommendation data
       └─────────────────────┘
       ┌─────────────────────┐
       │  Sayobot Mirror     │  ← .osz download
       └─────────────────────┘
```

## 🎮 How to Use

1. **Enter Username** — Type your osu! username, click "Get Recommendations"
2. **Adjust Filters** — Drag sliders for star range, probability thresholds, check Mods
3. **Select Maps** — Check individual maps or select all
4. **Start Download** — Click "Download Selected" or "Download All"
5. **Import to Game** — Double-click .osz files to auto-import into osu!

## 🙏 Credits

- [**AlphaOsu**](https://alphaosu.keytoix.vip/) — Machine learning PP recommendation engine
- [**Sayobot**](https://sayobot.cn/) — osu! beatmap mirror for China region
- [**PyWebView**](https://pywebview.flowrl.com/) — Cross-platform desktop GUI framework

---

<div align="center">
<sub>Made with 💜 for the osu! community</sub>
<br><br>
</div>
