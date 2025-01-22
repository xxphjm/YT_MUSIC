import re
from urllib.parse import urlparse, parse_qs

def is_valid_youtube_url(url):
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})|'
        '(https?://)?(www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)'
    )
    return bool(re.match(youtube_regex, url))

def parse_youtube_url(url):
    """
    解析 YouTube URL 並返回相關參數
    
    Args:
        url (str): YouTube URL
        
    Returns:
        dict: 包含以下鍵值的字典：
            - type: 'video' 或 'playlist'
            - id: 視頻 ID 或播放清單 ID
            - start_time: 開始時間（如果有）
            - end_time: 結束時間（如果有）
            - is_valid: URL 是否有效
            - playlist_index: 播放清單中的索引（如果有）
    """
    try:
        # 初始化返回字典
        result = {
            'type': None,
            'playlist_id': None,
            'playlist_index': None,
            'video_id': None,
            'base_url': None,
            'path': None,

        }
        
        # 檢查 URL 是否有效
        if not is_valid_youtube_url(url):
            return result
        
        # 解析 URL
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        result['base_url'] = parsed_url.scheme + '://' + parsed_url.netloc
        result['path'] = parsed_url.path
        print(parsed_url)
        # 檢查是否為播放清單
        if 'list' in query_params:
            result.update({
                'type': 'playlist',
                'playlist_id': query_params['list'][0],

            })
            
            # 檢查是否有播放清單索引
            if 'index' in query_params:
                try:
                    result['playlist_index'] = int(query_params['index'][0])
                except ValueError:
                    pass
        
            # 檢查是否同時包含視頻 ID（播放清單中的特定視頻）
            if 'v' in query_params:
                result['video_id'] = query_params['v'][0]
            
        
        # 獲取視頻 ID
        video_id = None
        
        # 從標準 watch URL 獲取
        if 'v' in query_params:
            video_id = query_params['v'][0]
        # 從短 URL 獲取 (youtu.be)
        elif 'youtu.be' in parsed_url.netloc:
            video_id = parsed_url.path.strip('/')
        # 從嵌入 URL 獲取
        elif '/embed/' in parsed_url.path:
            video_id = parsed_url.path.split('/embed/')[-1]
        
        if video_id:
            result.update({
                'type': 'video',
                'video_id': video_id,
            })
            

        
        return result
        
    except Exception as e:
        print(f"Error parsing URL: {str(e)}")
        return {
            'type': None,
            'id': None,
            'start_time': None,
            'end_time': None,
            'is_valid': False,
            'playlist_index': None
        }


    """
    解析 YouTube 時間參數
    支持格式：
    - 秒數 (例如: t=120)
    - 時分秒 (例如: t=2h1m30s)
    
    Args:
        time_str (str): 時間字符串
        
    Returns:
        int: 總秒數
    """
    try:
        # 如果是純數字，直接返回
        if time_str.isdigit():
            return int(time_str)
        
        total_seconds = 0
        # 匹配時分秒
        time_parts = re.findall(r'(\d+)([hms])', time_str.lower())
        
        for value, unit in time_parts:
            value = int(value)
            if unit == 'h':
                total_seconds += value * 3600
            elif unit == 'm':
                total_seconds += value * 60
            elif unit == 's':
                total_seconds += value
                
        return total_seconds
        
    except Exception:
        return 0