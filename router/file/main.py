import json
import os
from flask import Blueprint, flash, render_template, jsonify, request, send_file, session, url_for
from flask import redirect
from werkzeug.utils import secure_filename

from auth import login_required
import src.utils as utils

bp = Blueprint('file', __name__, url_prefix='/file')

@bp.route('/', methods=['GET'])
@login_required
def home():
    usage = utils.get_upload_folder_useage()
    max_usage = utils.MAX_STORAGE
    
    f_usage = utils.convert_file_fsize(usage)
    f_max_usage = utils.convert_file_fsize(max_usage)
    usage_per = round((usage / max_usage) * 100, 2) if max_usage != 0 else 0
    
    return render_template('file/index.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                           client_name=session.get('username'), files=utils.get_file_infos(), usage=f_usage, max_usage=f_max_usage, usage_per=usage_per), 200

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if session.get('userlevel', -1) != 0:
        flash("권한이 없습니다.", 'error')
        return redirect(url_for('router.file.home'), 401)
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('router.file.home'), 400)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('파일을 선택해주세요.', 'error')
            return redirect(url_for('router.file.home'), 400)

        if (file.filename.split('.')[-1] not in utils.ALLOWED_EXTENSIONS):
            flash(f'지원하지 않는 파일입니다. 지원 확장자: {', '.join(utils.ALLOWED_EXTENSIONS)}', 'error')
            return redirect(url_for('router.file.home'), 400)
        
        file_size = len(file.read())
        if utils.MAX_STORAGE < (utils.get_upload_folder_useage() + file_size):
            flash('저장공간이 부족합니다.', 'error')
            return redirect(url_for('router.file.home'), 400)
        
        file_info = {
            'orgName': file.filename,
            'ext': file.filename.split('.')[-1],
            'size': file_size,
            'fSize': utils.convert_file_fsize(file_size),
            "status": "idle",
            'uploadTime': utils.get_now_ftime(),
            'uploadFTime': utils.get_now_ftime('%Y년 %m월 %d일 %H:%M:%S'),
            'uploader_id': session.get('userid'),
            'uploader_name': session.get('username')
        }
        file.seek(0)
        
        while True:
            file_info['saveName'] = os.path.join(utils.gen_hash() + "." + file_info['ext'])
            file_save_path = os.path.join(utils.UPLOAD_FOLDER_PATH, file_info['saveName'])
            if not os.path.exists(file_save_path):
                break
        
        file.save(file_save_path)
        
        try:
            if os.path.exists(utils.FILE_INFO_PATH):
                with open(utils.FILE_INFO_PATH, 'r', encoding='utf-8') as json_file:
                    file_infos = json.load(json_file)
            else:
                file_infos = []
        except (json.JSONDecodeError, FileNotFoundError):
            file_infos = []

        file_infos.append(file_info)
        
        with open(utils.FILE_INFO_PATH, 'w', encoding='utf-8') as json_file:
            json.dump(file_infos, json_file, ensure_ascii=False, indent=4)
        
        flash('파일 업로드에 성공하였습니다.', 'success')
        return redirect(url_for('router.file.home'), 302)
    
    return render_template('file/upload.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                           client_name=session.get('username')), 200

@bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if session.get('userlevel', -1) != 0:
        flash("권한이 없습니다.", 'error')
        return redirect(url_for('router.file.home'), 401)
    
    if request.method == 'POST':
        file_name = request.form.get('del_file')
        
        try:
            with open(utils.FILE_INFO_PATH, 'r', encoding='utf-8') as json_file:
                file_infos = json.load(json_file)
        except (json.JSONDecodeError, FileNotFoundError):
            file_infos = []
        
        sel_file_info = None
        for file_info in file_infos:
            if file_info['saveName'] == file_name:
                sel_file_info = file_info
                break
        
        if sel_file_info == None:
            flash('파일 삭제 실패: 파일이 없습니다.', 'warning')
            return redirect(url_for('router.file.home'), 400)
            
        if sel_file_info['status'] != 'idle':
            flash('파일 삭제 실패: 삭제 가능한 상태가 아닙니다.', 'warning')
            return redirect(url_for('router.file.home'), 400)
        
        file_infos.remove(sel_file_info)
        os.remove(sel_file_info['path'])
        
        with open(utils.FILE_INFO_PATH, 'w', encoding='utf-8') as json_file:
            json.dump(file_infos, json_file, ensure_ascii=False, indent=4)
        
        flash('파일 삭제에 성공하였습니다.', 'success')
        return redirect(url_for('router.file.home'), 200)
    
    return render_template('file/delete.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                           client_name=session.get('username'), files=utils.get_file_infos()), 200

@bp.route('/view/<string:FILENAME>', methods=['GET'])
@login_required
def view(FILENAME):
    file_name = secure_filename(FILENAME)
    
    try:
        with open(utils.FILE_INFO_PATH, 'r', encoding='utf-8') as json_file:
            file_infos = json.load(json_file)
    except (json.JSONDecodeError, FileNotFoundError):
        file_infos = []
    
    same_file_infos = None
    for file_info in file_infos:
        if file_info['saveName'] == file_name:
            same_file_infos = file_info
            break
    
    if same_file_infos == None:
        flash('존재하지 않는 파일입니다.', 'warning')
        return render_template('file/index.html', 400)
    
    return send_file(os.path.join(utils.UPLOAD_FOLDER_PATH, same_file_infos['saveName']), as_attachment=True, download_name=same_file_infos['orgName'])

@bp.route('/download/<string:FILENAME>', methods=['GET'])
@login_required
def download(FILENAME):
    file_name = secure_filename(FILENAME)
    
    try:
        with open(utils.FILE_INFO_PATH, 'r', encoding='utf-8') as json_file:
            file_infos = json.load(json_file)
    except (json.JSONDecodeError, FileNotFoundError):
        file_infos = []
    
    file_path = None
    for file_info in file_infos:
        if file_info['saveName'] == file_name:
            file_path = file_info['path']
            file_org_name = file_info['orgName']
            break
    
    if file_path == None:
        flash('존재하지 않는 파일입니다.', 'warning')
        return redirect(url_for('router.file.home'), 400)
    
    return send_file(file_path, as_attachment=True, download_name=file_org_name)