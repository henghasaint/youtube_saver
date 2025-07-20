# YouTube 视频音频批量下载工具

一个功能强大的 Python 脚本，支持批量下载 YouTube 视频和音频，具有反爬虫措施、会员视频下载、自动重试等特性。

## ✨ 功能特点

- 📹 **批量下载**：同时下载视频(MP4)和音频(MP3)
- 🔐 **会员视频**：支持下载需要频道会员的视频
- 🛡️ **反爬措施**：随机 UA、请求延迟、限速下载
- 📝 **字幕支持**：自动下载并嵌入字幕（中文优先）
- 🔄 **断点续传**：支持中断后继续下载
- 📊 **详细日志**：记录所有操作，便于问题排查
- 🔧 **灵活配置**：支持代理、自定义延迟等设置

## 🚀 快速开始

### 0. 创建虚拟环境
```bash
conda create -n youtube2audio python=3.12
```
### 1. 安装依赖

```bash
pip install yt-dlp
```

确保系统已安装 [ffmpeg](https://ffmpeg.org/download.html)（用于音视频处理）

### 2. 下载脚本

下载 `youtube_downloader.py` 到本地目录

### 3. 准备视频列表

创建 `videos.txt` 文件，每行格式为：`视频名称 视频链接`

```text
Python教程_第1集 https://www.youtube.com/watch?v=xxxxx
Python教程_第2集 https://www.youtube.com/watch?v=yyyyy
机器学习入门 https://www.youtube.com/watch?v=zzzzz
```

注意：视频名称中不要包含空格，可以用下划线代替

### 4. 运行脚本

```bash
python youtube_downloader.py
```

## 📁 文件结构

运行后会生成以下文件结构：

```
项目目录/
├── youtube_downloader.py    # 主脚本
├── videos.txt              # 视频列表
├── cookies.txt             # YouTube cookies（可选）
├── config.json             # 配置文件
├── cookies_guide.txt       # cookies获取指南
├── download_log.txt        # 下载日志
├── failed_videos.txt       # 失败列表（如有）
└── downloads/              # 下载目录
    ├── videos/             # 视频文件
    │   ├── Python教程_第1集.mp4
    │   └── Python教程_第2集.mp4
    └── audio/              # 音频文件
        ├── Python教程_第1集.mp3
        └── Python教程_第2集.mp3
```

## 🍪 下载会员视频

### 获取 Cookies 的方法

#### 方法 1：浏览器扩展（推荐）

**Chrome/Edge：**

1. 安装扩展 [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. 登录 YouTube 并加入频道会员
3. 点击扩展图标，导出 cookies
4. 将 `cookies.txt` 放到脚本目录

**Firefox：**

1. 安装扩展 [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. 登录 YouTube
3. 点击扩展图标 → Current Site → Export

#### 方法 2：使用 yt-dlp 命令

```bash
# 从Chrome提取
yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download https://youtube.com

# 从Firefox提取
yt-dlp --cookies-from-browser firefox --cookies cookies.txt --skip-download https://youtube.com
```

#### 方法 3：开发者工具（手动）

1. F12 打开开发者工具
2. Application → Cookies → youtube.com
3. 手动复制关键 cookies 到文本文件

### 验证 Cookies

```bash
yt-dlp --cookies cookies.txt -F [会员视频链接]
```

如果能看到视频格式列表，说明 cookies 有效。

## ⚙️ 配置选项

编辑 `config.json` 自定义设置：

```json
{
  "proxy": null, // 代理设置，如 "socks5://127.0.0.1:1080"
  "min_delay": 3, // 最小请求延迟（秒）
  "max_delay": 10, // 最大请求延迟（秒）
  "max_workers": 1, // 并发数（建议保持1）
  "rate_limit": "5M" // 下载限速（避免触发限制）
}
```

### 使用代理

如需使用代理，修改 config.json：

```json
{
  "proxy": "socks5://127.0.0.1:1080"
}
```

或使用 HTTP 代理：

```json
{
  "proxy": "http://127.0.0.1:8080"
}
```

## 🛡️ 反爬虫措施

脚本内置多种反爬措施：

1. **随机 User-Agent**：模拟不同浏览器
2. **请求延迟**：3-10 秒随机延迟
3. **限速下载**：默认 5MB/s
4. **请求头伪装**：完整浏览器请求头
5. **自动重试**：失败后延迟重试
6. **断点续传**：避免重复下载

## 📋 命令行工具对比

### 基础命令行下载

如果只需要简单下载，可以直接使用 yt-dlp：

```bash
# 下载视频
yt-dlp [URL]

# 下载音频
yt-dlp -x --audio-format mp3 [URL]

# 下载1080p视频
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best" [URL]

# 使用cookies
yt-dlp --cookies cookies.txt [URL]
```

### 脚本优势

- 批量处理多个视频
- 同时保存视频和音频
- 自动整理文件
- 详细的错误日志
- 失败自动重试
- 反爬虫保护

## ❓ 常见问题

### 1. 提示缺少 ffmpeg

Windows 用户：

- 下载 [ffmpeg](https://www.gyan.dev/ffmpeg/builds/)
- 解压并添加到系统 PATH

Mac 用户：

```bash
brew install ffmpeg
```

Linux 用户：

```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg  # CentOS/RHEL
```

### 2. 下载速度慢

- 检查网络连接
- 考虑使用代理
- 调整 `rate_limit` 设置

### 3. 频繁失败

增加请求延迟：

```json
{
  "min_delay": 5,
  "max_delay": 15
}
```

### 4. Cookies 过期

重新获取 cookies，YouTube 的 cookies 通常有效期为几周到几个月。

### 5. 地区限制

配置代理服务器访问受限内容。

## 📝 注意事项

1. **版权声明**：请仅下载有权访问的内容，遵守 YouTube 服务条款
2. **个人使用**：下载的内容仅供个人使用，不要分发
3. **Cookies 安全**：不要分享 cookies.txt 文件，包含登录信息
4. **合理使用**：避免过度下载，尊重内容创作者

## 🔧 高级用法

### 自定义下载质量

修改脚本中的 format 选项：

```python
# 4K视频
'format': 'bestvideo[height<=2160]+bestaudio/best'

# 仅720p
'format': 'bestvideo[height=720]+bestaudio/best'

# 最小文件
'format': 'worst'
```

### 下载特定语言字幕

修改 subtitleslangs 选项：

```python
'subtitleslangs': ['en', 'ja', 'ko']  # 英语、日语、韩语
```

### 批量下载播放列表

直接在 videos.txt 中添加播放列表链接：

```text
整个播放列表 https://www.youtube.com/playlist?list=PLxxxxx
```

## 🐛 问题反馈

如遇到问题，请检查：

1. `download_log.txt` 中的错误信息
2. 网络连接是否正常
3. cookies 是否有效（会员视频）
4. ffmpeg 是否正确安装

## 📄 许可证

本工具仅供学习和个人使用，使用者需自行承担相关责任。

## 🙏 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的 YouTube 下载库
- [ffmpeg](https://ffmpeg.org/) - 音视频处理工具

---

