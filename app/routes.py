import uuid
import time
import socket
import io
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_file, current_app
)
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from .database import get_db, create_table_if_not_exists
from markupsafe import escape

bp = Blueprint('routes', __name__)


@bp.route('/')
def index():
    """메인 페이지 (콘텐츠 목록 조회) 렌더링"""
    db = get_db()
    
    # DB에 저장된 모든 콘텐츠 유형을 조회하여 필터 드롭다운에 사용
    content_types = db.execute("SELECT DISTINCT type FROM share_contents ORDER BY type").fetchall()
    
    return render_template('index.html', content_types=content_types)

@bp.route('/api/contents')
def get_contents_api():
    """무한 스크롤 및 검색 기능을 위한 RESTful API"""
    db = get_db()
    
    # 페이지네이션 및 검색 파라미터 가져오기
    page = request.args.get('page', 0, type=int)
    query = request.args.get('q', '')
    content_type = request.args.get('type', '')
    
    limit = 10
    offset = page * limit
    
    sql_query = "SELECT id, type, preview, modified FROM share_contents WHERE 1=1"
    params = []
    
    # 검색어 필터링
    if query:
        sql_query += " AND preview LIKE ?"
        params.append(f"%{query}%")
        
    # 유형 필터링
    if content_type:
        sql_query += " AND type = ?"
        params.append(content_type)
        
    sql_query += " ORDER BY modified DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    contents = db.execute(sql_query, params).fetchall()
    
    # 결과가 없으면 빈 리스트 반환
    if not contents:
        return jsonify([])
        
    safe_contents = []
    for content in contents:
        safe_content = dict(content)
        # API 응답 시에도 preview를 이스케이프 처리하여 잠재적 XSS 방지
        safe_content['preview'] = escape(content['preview'])
        safe_contents.append(safe_content)
        
    return jsonify(safe_contents)

@bp.route('/upload', methods=['GET'])
def upload_file_form():
    """파일 업로드 페이지 렌더링"""
    return render_template('upload.html')

@bp.route('/api/upload', methods=['POST'])
def upload_file_api():
    """파일 업로드 처리 API"""
    try:
        # 파일이 요청에 포함되었는지 확인
        if 'file' not in request.files:
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
            
        file = request.files['file']
        
        # 파일명 유효성 검사
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
            
        # 파일 크기 검사는 Flask의 MAX_CONTENT_LENGTH 설정이 대신 수행
        # 이를 초과하면 RequestEntityTooLarge 예외 발생
        
        # 파일 내용 읽기
        contents = file.read()

        # DB에 저장할 메타데이터 준비
        unique_id = str(uuid.uuid4())
        file_type = file.mimetype.split('/')[-1] if file.mimetype else 'binary'
        preview = secure_filename(file.filename)
        modified_time = int(time.time())
        
        db = get_db()
        cursor = db.cursor()
        
        # 데이터베이스에 파일 정보 저장
        cursor.execute(
            "INSERT INTO share_contents (id, type, preview, contents, modified) VALUES (?, ?, ?, ?, ?)",
            (unique_id, file_type, preview, contents, modified_time)
        )
        db.commit()
        
        flash('파일이 성공적으로 업로드되었습니다.')
        return jsonify({'message': '파일 업로드 성공', 'id': unique_id})
        
    except RequestEntityTooLarge:
        return jsonify({'error': '파일 크기가 5MB를 초과했습니다.'}), 413
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/new', methods=['GET'])
def create_text_form():
    """텍스트 등록 페이지 렌더링"""
    return render_template('new.html')

@bp.route('/api/new', methods=['POST'])
def create_text_api():
    """텍스트 등록 처리 API"""
    try:
        data = request.get_json()
        contents = data.get('contents', '')
        
        if not contents or not contents.strip():
            return jsonify({'error': '내용이 입력되지 않았습니다.'}), 400
        
        # 텍스트 크기 검사 (5MB 제한)
        if len(contents.encode('utf-8')) > current_app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': '내용이 5MB를 초과했습니다.'}), 413
            
        # DB에 저장할 메타데이터 준비
        unique_id = str(uuid.uuid4())
        preview = contents[:100] + '...' if len(contents) > 100 else contents
        modified_time = int(time.time())
        
        db = get_db()
        cursor = db.cursor()
        
        # 데이터베이스에 텍스트 내용 저장
        result=cursor.execute(
            "INSERT INTO share_contents (id, type, preview, contents, modified) VALUES (?, ?, ?, ?, ?)",
            (unique_id, 'text', preview, contents, modified_time)
        )
        result = db.commit()
        
        flash('내용이 성공적으로 등록되었습니다.')
        return jsonify({'message': '내용 등록 성공', 'id': unique_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/qr')
def qr_code_page():
    """QR 코드 페이지 렌더링"""
    try:
        # 소켓을 사용해 로컬 머신의 IP 주소 가져오기
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 외부 IP(Google DNS)에 연결 시도
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"  # 외부 연결이 불가능하면 localhost 사용

    # URL 생성
    # Flask 앱의 포트를 가져와 URL에 포함
    port = current_app.config['PORT'] if 'PORT' in current_app.config else 5000
    app_host = f"http://{local_ip}:{port}"
    return render_template('qr.html', app_host=app_host)

@bp.route('/content/<uuid:content_id>')
def view_content(content_id):
    """텍스트 내용 상세 조회 페이지 렌더링"""
    db = get_db()
    content = db.execute(
        "SELECT id, contents FROM share_contents WHERE id = ?", (str(content_id),)
    ).fetchone()

    if content:
        safe_content = dict(content)
        safe_content['contents'] = escape(content['contents'])

        return render_template('content.html', content=safe_content)
    
    return "Content not found", 404

@bp.route('/download/<uuid:content_id>')
def download_content(content_id):
    """파일 다운로드 처리"""
    db = get_db()
    result = db.execute(
        "SELECT preview, contents, type FROM share_contents WHERE id = ?", (str(content_id),)
    ).fetchone()
    
    if result:
        file_name = result['preview']
        file_content = result['contents']
        file_type = result['type']
        
        byte_stream = io.BytesIO(file_content)
        return send_file(
            byte_stream,
            mimetype=f'application/{file_type}',
            as_attachment=True,
            download_name=file_name
        )
    
    return "File not found", 404

@bp.route('/api/delete/<uuid:content_id>', methods=['DELETE'])
def delete_content(content_id):
    """콘텐츠 삭제 API"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM share_contents WHERE id = ?", (str(content_id),))
    db.commit()
    
    return jsonify({'message': '콘텐츠가 삭제되었습니다.'})