# AlphaOsu! Download Tool

基于 [AlphaOsu](https://alphaosu.keytoix.vip/) 机器学习推荐的 osu! 谱面批量下载工具。

自动获取 PP 推荐谱面，按星数、Mod、上榜概率等条件筛选，批量下载 .osz 文件。

## 功能

- 🔐 osu! 用户名登录，自动获取个人推荐
- ⭐ 难度星级范围筛选（双滑块）
- 📊 上榜概率 / 破纪录概率筛选
- 🎮 Mod 筛选（NM/HD/HR/DT 及组合）
- 🚫 隐藏已玩过的谱面
- 🖼️ 谱面封面图预览
- ☑️ 多选 + 批量下载
- 📁 自定义下载目录
- ⬇️ 通过 Sayobot 镜像下载，双击 .osz 导入 osu!

## 截图

<!-- TODO: 添加截图 -->
<!-- ![主界面](screenshots/main.png) -->
<!-- ![筛选](screenshots/filter.png) -->
<!-- ![下载中](screenshots/downloading.png) -->

## 使用方式

### 下载 EXE

从 [Releases](../../releases) 下载最新版 `AlphaOsuDownloadTool.exe`，双击运行。

### 从源码运行

```bash
pip install pywebview
python main.py
```

### 打包 EXE

```bash
pip install pyinstaller pywebview
pyinstaller --onefile --windowed --icon=icon.ico --name "AlphaOsuDownloadTool" main.py
```

EXE 生成在 `dist/` 目录下。

## 工作原理

1. **登录**：调用 AlphaOsu API（`POST /api/v1/login`），传入 osu! 用户名获取 UID
2. **获取推荐**：调用 `GET /api/v1/self/maps/recommend`，自动翻页获取全部推荐（每页 20 个）
3. **筛选**：客户端按星数、Mod、概率等条件过滤，自动去重同一 beatmapset
4. **下载**：通过 Sayobot 镜像（`https://dl.sayobot.cn/beatmaps/download/{set_id}`）下载 .osz 文件

## 技术栈

- **Python** + **PyWebView** — 桌面 GUI（系统浏览器引擎渲染 HTML/CSS）
- **HTML/CSS/JS** — 现代化暗色界面
- **AlphaOsu API** — ML 推荐数据
- **Sayobot** — 国内 osu! 谱面镜像

## 致谢

- [AlphaOsu](https://alphaosu.keytoix.vip/) — 机器学习 PP 推荐引擎
- [Sayobot](https://sayobot.cn/) — osu! 谱面下载镜像

## License

MIT
