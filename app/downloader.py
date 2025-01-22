import os
import yt_dlp
import requests
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
from utils import normalize_filename
from flask import current_app
import json





def progress_hook(d):

    """回調函數來更新下載進度"""
    if d['status'] == 'downloading':
        # 計算下載進度百分比
        if 'total_bytes' in d:
            percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
        elif 'total_bytes_estimate' in d:
            percentage = (d['downloaded_bytes'] /
                          d['total_bytes_estimate']) * 100
        else:
            percentage = 0

        progress_data = {
            'status': 'downloading',
            'percentage': round(percentage, 1),
            'speed': d.get('speed', 0),
            'eta': d.get('eta', 0),
            'filename': d.get('filename', '')
        }
        print(progress_data)
        # 將進度寫入臨時文件
        with open(os.path.join(current_app.config['UPLOAD_FOLDER'], 'progress.json'), 'w') as f:
            print(progress_data)
            json.dump(progress_data, f)


def download_single_video(url, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'writethumbnail': True,
        'progress_hooks': [progress_hook],
        # 修改下載配置
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        },
        'nocheckcertificate': True,
        'no_check_certificate': True,
        'ignoreerrors': True,
        'quiet': False,
        'no_warnings': False,
        'verbose': True,
        'retries': 3,
        'fragment_retries': 3,
        'skip_unavailable_fragments': True,
        'abort_on_unavailable_fragment': False,
        'keepvideo': False,
        'prefer_ffmpeg': True,

    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            progress_file = os.path.join(
                current_app.config['UPLOAD_FOLDER'], 'progress.json')
            with open(progress_file, 'w') as f:
                print(f"Progress file: {progress_file}")
                json.dump({'status': 'starting', 'percentage': 0}, f)
            # 先獲取信息
            info = ydl.extract_info(url, download=False)
            title = info['title']
            normalized_title = normalize_filename(title)
            safe_title = normalize_filename(title)

            # 然後下載
            ydl.download([url])

            downloaded_file = None
            for file in os.listdir(output_dir):
                if normalize_filename(file.replace('.mp3', '')) == normalized_title:
                    downloaded_file = file
                    break

            if not downloaded_file:
                raise Exception("找不到下載的 MP3 檔案")

            original_mp3_path = os.path.join(output_dir, downloaded_file)
            mp3_path = os.path.join(output_dir, f"{safe_title}.mp3")

            if os.path.exists(original_mp3_path) and original_mp3_path != mp3_path:
                os.rename(original_mp3_path, mp3_path)

            # 添加 metadata
            try:
                audio = ID3(mp3_path)
            except:
                audio = ID3()

            audio.add(TIT2(encoding=3, text=title))
            audio.add(TPE1(encoding=3, text=info.get(
                'artist', info['uploader'])))
            audio.add(TALB(encoding=3, text=title))

            if 'thumbnail' in info:
                try:
                    response = requests.get(
                        info['thumbnail'],
                        headers={'User-Agent': 'Mozilla/5.0'},
                        verify=False,
                        timeout=30
                    )
                    if response.status_code == 200:
                        img_data = response.content
                        audio.add(APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,
                            desc='Cover',
                            data=img_data
                        ))
                except Exception as e:
                    print(f"無法下載縮圖: {str(e)}")

            audio.save(mp3_path)
            return {
                'status': 'success',
                'title': safe_title,
                'filename': f"{safe_title}.mp3"
            }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


def download_playlist(url, output_dir):
    # 全局變量來追蹤播放清單進度
    playlist_info = {
        'total_items': 0,
        'current_item': 0,
        'downloaded_items': 0,
        'current_title': '',
        'entries': []
    }

    def playlist_hook(d):
        """播放清單專用的進度回調"""
        print(f"Playlist hook status: {d['status']}")  # 調試信息
        
        if d['status'] == 'downloading':
            # 計算當前檔案的下載進度
            if 'total_bytes' in d:
                file_percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d:
                file_percentage = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            else:
                file_percentage = 0

            # 計算整體進度：已完成的檔案進度 + 當前檔案進度
            overall_percentage = (playlist_info['downloaded_items'] * 100 + file_percentage) / playlist_info['total_items']

            current_info = {
                'status': 'downloading',
                'percentage': round(overall_percentage, 1),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0),
                'filename': d.get('filename', ''),
                'current_item': playlist_info['current_item'],
                'total_items': playlist_info['total_items'],
                'current_title': playlist_info['current_title']
            }
            
            print(f"Download progress: {current_info}")  # 調試信息
            
            with open(os.path.join(current_app.config['UPLOAD_FOLDER'], 'progress.json'), 'w') as f:
                json.dump(current_info, f)
                
        elif d['status'] == 'finished':
            # 當前檔案下載完成，增加計數
            playlist_info['downloaded_items'] += 1
            print(f"Finished item {playlist_info['downloaded_items']} of {playlist_info['total_items']}")  # 調試信息

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(playlist_title)s/%(title)s.%(ext)s'),
        'writethumbnail': True,
        'progress_hooks': [playlist_hook],
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'Connection': 'close',
        },
        'nocheckcertificate': True,
        'no_check_certificate': True,
        'ignoreerrors': True,
        'quiet': False,
        'no_warnings': False,
        'verbose': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 初始化進度文件
            progress_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'progress.json')
            
            # 先獲取播放清單信息
            print("Extracting playlist info...")
            result = ydl.extract_info(url, download=False)
            
            if 'entries' not in result:
                raise Exception("無效的播放清單")
            
            # 設置播放清單信息
            playlist_info['total_items'] = len(result['entries'])
            playlist_info['entries'] = result['entries']
            playlist_info['current_item'] = 0
            playlist_info['downloaded_items'] = 0
            
            # 寫入初始進度
            with open(progress_file, 'w') as f:
                json.dump({
                    'status': 'starting',
                    'percentage': 0,
                    'current_item': 0,
                    'total_items': playlist_info['total_items'],
                    'current_title': '準備下載...'
                }, f)

            # 逐個下載播放清單中的項目
            for index, entry in enumerate(playlist_info['entries'], 1):
                if entry:
                    playlist_info['current_item'] = index
                    playlist_info['current_title'] = entry.get('title', f'Item {index}')
                    
                    print(f"Downloading {index}/{playlist_info['total_items']}: {playlist_info['current_title']}")
                    
                    try:
                        ydl.download([entry['webpage_url']])
                    except Exception as e:
                        print(f"Error downloading item {index}: {str(e)}")
                        continue

            # 創建 ZIP 文件
            playlist_title = normalize_filename(result['title'])
            playlist_dir = os.path.join(output_dir, playlist_title)
            
            if os.path.exists(playlist_dir):
                print("Creating ZIP file...")
                import zipfile
                zip_path = os.path.join(output_dir, f"{playlist_title}.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, dirs, files in os.walk(playlist_dir):
                        for file in files:
                            if file.endswith('.mp3'):
                                file_path = os.path.join(root, file)
                                arcname = os.path.join(os.path.basename(root), file)
                                zipf.write(file_path, arcname)

            # 完成時更新進度
            with open(progress_file, 'w') as f:
                json.dump({
                    'status': 'finished',
                    'percentage': 100,
                    'current_item': playlist_info['total_items'],
                    'total_items': playlist_info['total_items'],
                    'current_title': '完成！'
                }, f)

            return {
                'status': 'success',
                'title': playlist_title,
                'filename': f"{playlist_title}.zip",
                'count': playlist_info['total_items']
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        # 錯誤時更新進度
        with open(progress_file, 'w') as f:
            json.dump({
                'status': 'error',
                'message': str(e),
                'current_item': playlist_info['current_item'],
                'total_items': playlist_info['total_items']
            }, f)
        return {
            'status': 'error',
            'message': str(e)
        }