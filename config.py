import os

class Config:
    """Flask 애플리케이션 설정을 위한 기본 클래스"""
    # SECRET_KEY: 세션 관리 및 보안을 위한 키.
    # .env 파일에서 불러오거나, 없으면 기본값 사용
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-should-be-changed'

    # SQLALCHEMY_DATABASE_URI: 데이터베이스 연결 설정.
    # 인메모리 SQLite DB를 사용하여, 앱 실행 중에만 데이터를 유지
    DATABASE = 'test.db'

    # MAX_CONTENT_LENGTH: 파일 업로드 최대 크기 제한 (5MB)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024