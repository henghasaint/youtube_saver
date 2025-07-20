## 主要功能：

1. **批量下载**：从`videos.txt`文件读取视频信息，自动下载视频和音频
2. **文件格式**：`videos.txt`每行格式为：`视频名称 视频链接`
3. **自动整理**：视频保存在`downloads/videos/`，音频保存在`downloads/audio/`
4. **字幕支持**：自动下载并嵌入字幕（中文优先）
5. **错误处理**：跳过失败的下载，继续处理其他视频
6. **日志记录**：详细的下载日志，保存在`download_log.txt`
7. **失败重试**：失败的视频保存到`failed_videos.txt`，方便重新下载

## 使用方法：

### 1. 安装依赖：

```bash
pip install yt-dlp
```

### 2. 准备 videos.txt 文件：

```
Python教程第1集 https://www.youtube.com/watch?v=xxxxx
Python教程第2集 https://www.youtube.com/watch?v=yyyyy
机器学习入门 https://www.youtube.com/watch?v=zzzzz
```

### 3. （可选）准备 cookies.txt：

如果需要下载会员视频，将 cookies.txt 放在脚本同目录

### 4. 运行脚本：

```bash
python youtube_downloader.py
```

## 特色功能：

1. **智能文件名处理**：自动清理非法字符，确保在各种系统上都能正常保存
2. **进度显示**：实时显示下载进度和统计信息
3. **支持会员视频**：自动检测并使用 cookies.txt
4. **灵活配置**：
   - 视频格式：优先 MP4，自动选择最佳质量
   - 音频格式：MP3 320kbps 高质量
   - 支持注释：videos.txt 中以#开头的行会被忽略

## 输出结构：

```
downloads/
├── videos/
│   ├── Python教程第1集.mp4
│   └── Python教程第2集.mp4
├── audio/
│   ├── Python教程第1集.mp3
│   └── Python教程第2集.mp3
download_log.txt
failed_videos.txt (如果有失败的)
```

# youtube_saver
