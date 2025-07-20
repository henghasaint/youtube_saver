#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import random
from pathlib import Path
from yt_dlp import YoutubeDL
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download_log.txt', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class YouTubeDownloader:
    def __init__(self, cookies_file=None, output_dir='downloads', use_proxy=None):
        """
        初始化下载器
        :param cookies_file: cookies文件路径（用于下载需要登录的视频）
        :param output_dir: 输出目录
        :param use_proxy: 代理设置，格式如 'socks5://127.0.0.1:1080'
        """
        self.cookies_file = cookies_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.use_proxy = use_proxy
        
        # 创建视频和音频子目录
        self.video_dir = self.output_dir / 'videos'
        self.audio_dir = self.output_dir / 'audio'
        self.video_dir.mkdir(exist_ok=True)
        self.audio_dir.mkdir(exist_ok=True)
        
        # 反爬虫设置
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        ]
        
        # 下载延迟设置（秒）
        self.min_delay = 3
        self.max_delay = 10
        
        # 重试设置
        self.max_retries = 3
        self.retry_delay = 5
        
    def get_random_headers(self):
        """获取随机请求头"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def random_delay(self):
        """随机延迟，模拟人类行为"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logging.info(f"等待 {delay:.1f} 秒...")
        time.sleep(delay)
    
    def sanitize_filename(self, filename):
        """清理文件名，移除非法字符"""
        # Windows文件名非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        # 移除首尾空格和点
        filename = filename.strip('. ')
        # 限制文件名长度
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def get_base_ydl_opts(self):
        """获取基础的yt-dlp选项，包含反爬措施"""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'nocheckcertificate': True,
            'no_color': True,
            # 反爬虫相关设置
            'headers': self.get_random_headers(),
            'socket_timeout': 30,
            'retries': self.max_retries,
            'fragment_retries': self.max_retries,
            'sleep_interval': 1,  # 下载前等待
            'max_sleep_interval': 3,
            'sleep_interval_requests': 1,  # 请求之间的延迟
            # 限速设置（避免过快下载）
            'ratelimit': '5M',  # 限制下载速度为5MB/s
            # 其他设置
            'continuedl': True,  # 断点续传
            'noprogress': False,  # 显示进度
        }
        
        # 如果有cookies文件，添加cookies选项
        if self.cookies_file and os.path.exists(self.cookies_file):
            opts['cookiefile'] = self.cookies_file
            logging.info("使用cookies文件进行认证")
        
        # 如果有代理设置
        if self.use_proxy:
            opts['proxy'] = self.use_proxy
            logging.info(f"使用代理: {self.use_proxy}")
        
        return opts
    
    def download_with_retry(self, download_func, url, video_name, max_retries=None):
        """带重试的下载"""
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logging.info(f"重试第 {attempt} 次...")
                    time.sleep(self.retry_delay * attempt)  # 递增延迟
                
                result = download_func(url, video_name)
                if result[0]:  # 成功
                    return result
                
            except Exception as e:
                logging.error(f"下载出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    continue
                else:
                    raise
        
        return False, None
    
    def download_video(self, url, video_name):
        """下载视频"""
        try:
            safe_name = self.sanitize_filename(video_name)
            video_path = str(self.video_dir / safe_name)
            
            ydl_opts = self.get_base_ydl_opts()
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': f'{video_path}.%(ext)s',
                'merge_output_format': 'mp4',
                # 字幕选项
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['zh-Hans', 'zh-Hant', 'en'],
                'embedsubtitles': True,
                # 后处理
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
            
            with YoutubeDL(ydl_opts) as ydl:
                logging.info(f"正在下载视频: {video_name}")
                info = ydl.extract_info(url, download=True)
                logging.info(f"视频下载完成: {video_name}")
                return True, info
                
        except Exception as e:
            logging.error(f"下载视频失败 [{video_name}]: {str(e)}")
            return False, None
    
    def download_audio(self, url, video_name):
        """下载音频"""
        try:
            safe_name = self.sanitize_filename(video_name)
            audio_path = str(self.audio_dir / safe_name)
            
            ydl_opts = self.get_base_ydl_opts()
            ydl_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': f'{audio_path}.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            })
            
            with YoutubeDL(ydl_opts) as ydl:
                logging.info(f"正在下载音频: {video_name}")
                ydl.download([url])
                logging.info(f"音频下载完成: {video_name}")
                return True
                
        except Exception as e:
            logging.error(f"下载音频失败 [{video_name}]: {str(e)}")
            return False
    
    def download_item(self, video_name, video_url):
        """下载单个项目（视频和音频）"""
        logging.info(f"\n开始处理: {video_name}")
        logging.info(f"链接: {video_url}")
        
        # 随机延迟，避免过快请求
        self.random_delay()
        
        # 使用重试机制下载
        video_success = self.download_with_retry(
            self.download_video, video_url, video_name
        )[0]
        
        # 再次延迟
        self.random_delay()
        
        audio_success = self.download_with_retry(
            self.download_audio, video_url, video_name
        )
        
        return video_success and audio_success, video_name, video_url
    
    def process_videos_file(self, videos_file='videos.txt', max_workers=1):
        """处理视频列表文件"""
        if not os.path.exists(videos_file):
            logging.error(f"文件不存在: {videos_file}")
            return
        
        success_count = 0
        fail_count = 0
        failed_items = []
        
        try:
            with open(videos_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 解析有效的视频项
            video_items = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(None, 1)
                if len(parts) != 2:
                    logging.warning(f"第 {i} 行格式错误，跳过: {line}")
                    continue
                
                video_items.append(parts)
            
            total_count = len(video_items)
            logging.info(f"找到 {total_count} 个视频待下载")
            logging.info(f"使用 {max_workers} 个并发下载")
            
            # 顺序下载（为了更好的反爬）
            for i, (video_name, video_url) in enumerate(video_items, 1):
                logging.info(f"\n进度: {i}/{total_count}")
                
                success, name, url = self.download_item(video_name, video_url)
                
                if success:
                    success_count += 1
                    logging.info(f"✓ 成功下载: {name}")
                else:
                    fail_count += 1
                    failed_items.append(f"{name} {url}")
                    logging.error(f"✗ 下载失败: {name}")
                
                # 显示当前统计
                logging.info(f"当前统计 - 成功: {success_count}, 失败: {fail_count}")
        
        except Exception as e:
            logging.error(f"处理文件时出错: {str(e)}")
        
        # 最终统计
        logging.info(f"\n{'='*50}")
        logging.info(f"下载完成！")
        logging.info(f"成功: {success_count}")
        logging.info(f"失败: {fail_count}")
        
        # 保存失败的项目
        if failed_items:
            failed_file = 'failed_videos.txt'
            with open(failed_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(failed_items))
            logging.info(f"失败的视频已保存到: {failed_file}")

def create_cookie_guide():
    """创建cookies获取指南"""
    guide = """
# 🍪 YouTube Cookies 获取指南

## 方法一：使用浏览器扩展（推荐）

### Chrome/Edge 浏览器：
1. 安装扩展：Get cookies.txt LOCALLY
   - Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   - Edge: 在Edge扩展商店搜索 "Get cookies.txt"

2. 登录YouTube并加入需要的频道会员

3. 在YouTube页面点击扩展图标，选择 "Export" 或 "下载"

4. 将下载的 cookies.txt 文件放到脚本同目录

### Firefox 浏览器：
1. 安装扩展：cookies.txt
   - https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

2. 登录YouTube并加入频道会员

3. 点击扩展图标 → Current Site → Export

## 方法二：使用开发者工具（技术用户）

1. 打开YouTube并登录账号
2. 按F12打开开发者工具
3. 切换到 Application/存储 标签
4. 左侧找到 Cookies → https://www.youtube.com
5. 手动复制需要的cookies

主要需要的cookies：
- VISITOR_INFO1_LIVE
- PREF
- LOGIN_INFO
- HSID
- SSID
- APISID
- SAPISID
- SID
- SIDCC

## 方法三：使用yt-dlp直接提取

```bash
# 从Chrome浏览器提取（需要关闭浏览器）
yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download [任意YouTube链接]

# 从Firefox提取
yt-dlp --cookies-from-browser firefox --cookies cookies.txt --skip-download [任意YouTube链接]
```

## ⚠️ 注意事项：

1. **安全警告**：cookies包含登录信息，请勿分享给他人！
2. **有效期**：cookies可能过期，需要定期更新
3. **格式要求**：必须是Netscape格式的cookies.txt文件
4. **测试方法**：先用单个会员视频测试是否能正常下载

## 验证cookies是否有效：

将cookies.txt放到脚本目录后，可以用以下命令测试：
```bash
yt-dlp --cookies cookies.txt -F [会员视频链接]
```

如果能看到视频格式列表，说明cookies有效。

---
创建时间：{timestamp}
"""
    return guide.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def main():
    """主函数"""
    print("YouTube视频音频批量下载工具 v2.0")
    print("=" * 50)
    
    # 创建cookies获取指南
    if not os.path.exists('cookies_guide.txt'):
        with open('cookies_guide.txt', 'w', encoding='utf-8') as f:
            f.write(create_cookie_guide())
        logging.info("已创建 cookies_guide.txt，请查看cookies获取方法")
    
    # 检查配置文件
    config = {
        'proxy': None,
        'min_delay': 3,
        'max_delay': 10,
        'max_workers': 1,
        'rate_limit': '5M'
    }
    
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config.update(json.load(f))
            logging.info("已加载配置文件 config.json")
        except Exception as e:
            logging.warning(f"配置文件读取失败: {e}")
    else:
        # 创建默认配置文件
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logging.info("已创建默认配置文件 config.json")
    
    # 检查是否需要使用cookies
    cookies_file = None
    if os.path.exists('cookies.txt'):
        cookies_file = 'cookies.txt'
        logging.info("✓ 检测到cookies.txt文件，将用于下载会员视频")
    else:
        logging.warning("未检测到cookies.txt文件，只能下载公开视频")
        logging.info("如需下载会员视频，请查看 cookies_guide.txt")
    
    # 创建下载器实例
    downloader = YouTubeDownloader(
        cookies_file=cookies_file,
        use_proxy=config.get('proxy')
    )
    
    # 应用配置
    downloader.min_delay = config.get('min_delay', 3)
    downloader.max_delay = config.get('max_delay', 10)
    
    # 检查videos.txt文件
    videos_file = 'videos.txt'
    if not os.path.exists(videos_file):
        logging.error(f"请创建 {videos_file} 文件并添加视频信息")
        logging.info("格式: 每行一个视频，格式为 '视频名称 视频链接'")
        
        # 创建示例文件
        with open(videos_file, 'w', encoding='utf-8') as f:
            f.write("# YouTube视频批量下载列表\n")
            f.write("# 格式: 视频名称 视频链接\n")
            f.write("# 以#开头的行将被忽略\n")
            f.write("# 提示：视频名称不要包含空格，可以用下划线代替\n\n")
            f.write("# 示例：\n")
            f.write("Python教程_第1集 https://www.youtube.com/watch?v=dQw4w9WgXcQ\n")
            f.write("Python教程_第2集 https://www.youtube.com/watch?v=example123\n")
            f.write("# 会员视频示例（需要cookies.txt）：\n")
            f.write("# 会员专享内容 https://www.youtube.com/watch?v=member_only\n")
        
        logging.info(f"已创建示例文件: {videos_file}")
        logging.info("请编辑该文件后重新运行程序")
        return
    
    # 显示反爬配置
    logging.info(f"\n反爬虫配置:")
    logging.info(f"- 请求延迟: {downloader.min_delay}-{downloader.max_delay}秒")
    logging.info(f"- 下载限速: {config.get('rate_limit', '5M')}")
    logging.info(f"- 重试次数: {downloader.max_retries}")
    logging.info(f"- User-Agent池: {len(downloader.user_agents)}个")
    
    # 询问是否继续
    print("\n是否开始下载？(y/n): ", end='')
    if input().lower() != 'y':
        logging.info("用户取消下载")
        return
    
    # 开始处理
    start_time = time.time()
    downloader.process_videos_file(videos_file, max_workers=config.get('max_workers', 1))
    
    # 显示总耗时
    elapsed_time = time.time() - start_time
    logging.info(f"\n总耗时: {elapsed_time/60:.1f} 分钟")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\n用户中断下载")
    except Exception as e:
        logging.error(f"程序异常: {str(e)}")
        import traceback
        traceback.print_exc()
