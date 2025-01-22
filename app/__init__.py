from flask import Flask
import os
import requests
import subprocess

def setup_ffmpeg():
    """下載並設置 FFmpeg"""
    ffmpeg_url = "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4.0/ffmpeg-linux-x64"
    ffmpeg_path = "/tmp/ffmpeg"
    
    if not os.path.exists(ffmpeg_path):
        try:
            response = requests.get(ffmpeg_url)
            with open(ffmpeg_path, 'wb') as f:
                f.write(response.content)
            # 設置執行權限
            os.chmod(ffmpeg_path, 0o755)
        except Exception as e:
            print(f"Error setting up FFmpeg: {str(e)}")

def create_app():
    # 使用專案根目錄的 templates
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    
    # 修改：使用 /tmp 目錄而不是專案目錄
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'tmp/downloads')
    # 確保下載目錄存在
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # 設置 FFmpeg
    setup_ffmpeg()

    # 註冊路由
    from route.routes import bp
    app.register_blueprint(bp)

    return app