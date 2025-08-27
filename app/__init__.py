import os
from flask import Flask
from . import database, routes


# 마크다운 필터를 위한 환경 설정
def markdown_filter(text):
    import markdown
    return markdown.markdown(text)

def create_app():
    """
    Flask 애플리케이션 팩토리 함수.
    앱을 생성하고 초기 설정 및 블루프린트를 등록합니다.
    """
    # Flask 앱 인스턴스 생성
    app = Flask(__name__, instance_relative_config=True)
    
    # 앱 설정 로드
    app.config.from_object('config.Config')

    # 인스턴스 폴더가 없으면 생성
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.jinja_env.filters['markdown'] = markdown_filter

    # DB 초기화 및 라우트 등록
    database.init_app(app)
    app.register_blueprint(routes.bp)
    
    return app