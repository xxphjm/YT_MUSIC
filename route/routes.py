from flask import Blueprint, render_template, request, jsonify, send_file, current_app
import os
from utils import is_valid_youtube_url,parse_youtube_url  # 修改導入路徑
from app.downloader import download_single_video, download_playlist
import json
bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/download', methods=['POST'])
def download():
    
    url = request.form.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({'status': 'error', 'message': '無效的 YouTube URL'})
    url_info=parse_youtube_url(url)
    if url_info['type'] == 'playlist' and url_info['playlist_index'] is  None:
        print("playlist")
        playlist_url=url_info['base_url']+url_info['path']+"?list="+url_info['playlist_id']
        result = download_playlist(playlist_url, current_app.config['UPLOAD_FOLDER'])
    else:
        print("single")
        video_url=url_info['base_url']+url_info['path']+"?v="+url_info['video_id']
        print(video_url)
        result = download_single_video(video_url, current_app.config['UPLOAD_FOLDER'])

    if result['status'] == 'success':
        return jsonify({
            'status': 'success',
            'title': result['title'],
            'download_url': f'/get_file/{result["filename"]}'
        })
    return jsonify(result)

@bp.route('/get_file/<filename>')
def get_file(filename):
    """提供檔案下載的路由"""
    try:
        return send_file(
            os.path.join(current_app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
@bp.route('/progress')
def get_progress():
    try:
        progress_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'progress.json')
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({'status': 'waiting'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})