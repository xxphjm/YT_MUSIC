from flask import Flask
import os

def create_app():
    # 使用專案根目錄的 templates
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    # 設置下載目錄
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'downloads')

    # 確保下載目錄存在
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # 註冊路由
    from route.routes import bp
    app.register_blueprint(bp)

    return app