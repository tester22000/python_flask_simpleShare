import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """
    데이터베이스 연결을 생성하고 반환합니다.
    g 객체에 연결을 저장하여 요청당 한 번만 연결되도록 관리합니다.
    """
    if 'db' not in g:
        # DB 연결: :memory: 는 인메모리 데이터베이스를 의미합니다.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # 컬럼 이름으로 결과에 접근 가능하도록 row_factory 설정
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    g 객체에 저장된 데이터베이스 연결을 닫습니다.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    데이터베이스 테이블을 초기화합니다.
    """
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# --- 누락된 함수 추가 ---
def create_table_if_not_exists():
    """
    애플리케이션 시작 시 DB 테이블을 생성합니다.
    인메모리 DB는 앱이 시작될 때마다 초기화되므로 필수적입니다.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS share_contents (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            preview TEXT NOT NULL,
            contents BLOB NOT NULL,
            modified INTEGER NOT NULL
        );
    """)
    cursor.execute("""
        delete from share_contents
    """)
    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    데이터베이스 테이블을 초기화하는 CLI 명령어를 제공합니다.
    'flask init-db' 명령어로 실행 가능합니다.
    """
    init_db()
    click.echo('데이터베이스가 초기화되었습니다.')

def init_app(app):
    """
    Flask 애플리케이션에 데이터베이스 함수를 등록합니다.
    """
    with app.app_context():
        create_table_if_not_exists()

    # 요청 종료 후 DB 연결을 자동으로 닫도록 등록
    app.teardown_appcontext(close_db)