from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql
import os
import uuid
from datetime import datetime
from src.api.chatGPT import get_chat_response
import re

app = Flask(__name__)

# 配置上传文件存储路径
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)

# 配置 MySQL 数据库连接
db = pymysql.connect(
    host='localhost',
    user='root',  
    password='root',  
    database='l10n_management',
    cursorclass=pymysql.cursors.DictCursor
)

# 项目相关接口
@app.route('/api/projects', methods=['GET'])
def get_projects():
    with db.cursor() as cur:
        cur.execute("SELECT * FROM projectname")
        projects = cur.fetchall()
    return jsonify(projects)

@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM projectname WHERE id = %s", (project_id,))
        project = cur.fetchone()
        if not project:
            return jsonify({"error": "Project not found"}), 404
    return jsonify(project)

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    
    # 从请求中提取项目数据
    project_name = data.get('projectName')
    request_name = data.get('requestName')
    project_manager = data.get('projectManager', 'Yizhuo Xiang')  # 默认项目经理
    project_status = data.get('projectStatus', 'pending')  # 默认状态为待处理
    
    # 其他项目数据
    source_language = data.get('sourceLanguage')
    target_languages = ','.join(data.get('targetLanguages', []))
    word_count = data.get('wordCount', 0)
    expected_delivery_date = data.get('expectedDeliveryDate')
    additional_requirements = ','.join(data.get('additionalRequirements', []))
    
    # 创建项目记录
    with db.cursor() as cur:
        sql = """
        INSERT INTO projectname (
            projectName, projectStatus, requestName, projectManager, createTime,
            sourceLanguage, targetLanguages, wordCount, expectedDeliveryDate, additionalRequirements,
            taskTranslation, taskLQA, taskTranslationUpdate, taskLQAReportFinalization
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_name, project_status, request_name, project_manager, datetime.now(),
            source_language, target_languages, word_count, expected_delivery_date, additional_requirements,
            'not_started', 'not_started', 'not_started', 'not_started'
        ))
        db.commit()
        project_id = cur.lastrowid
    
    return jsonify({"id": project_id, "message": "Project created successfully"}), 201

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.json
    
    # 从请求中提取项目数据
    update_fields = []
    update_values = []
    
    # 检查并添加更新字段
    if 'projectName' in data:
        update_fields.append("projectName = %s")
        update_values.append(data['projectName'])
    
    if 'projectStatus' in data:
        update_fields.append("projectStatus = %s")
        update_values.append(data['projectStatus'])
    
    if 'requestName' in data:
        update_fields.append("requestName = %s")
        update_values.append(data['requestName'])
    
    if 'projectManager' in data:
        update_fields.append("projectManager = %s")
        update_values.append(data['projectManager'])
    
    if 'taskTranslation' in data:
        update_fields.append("taskTranslation = %s")
        update_values.append(data['taskTranslation'])
    
    if 'taskLQA' in data:
        update_fields.append("taskLQA = %s")
        update_values.append(data['taskLQA'])
    
    if 'taskTranslationUpdate' in data:
        update_fields.append("taskTranslationUpdate = %s")
        update_values.append(data['taskTranslationUpdate'])
    
    if 'taskLQAReportFinalization' in data:
        update_fields.append("taskLQAReportFinalization = %s")
        update_values.append(data['taskLQAReportFinalization'])
    
    # 如果没有要更新的字段，返回错误
    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400
    
    # 构建更新SQL
    sql = "UPDATE projectname SET " + ", ".join(update_fields) + " WHERE id = %s"
    update_values.append(project_id)
    
    # 执行更新
    with db.cursor() as cur:
        cur.execute(sql, update_values)
        db.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Project not found or no changes made"}), 404
    
    return jsonify({"message": "Project updated successfully"})

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    with db.cursor() as cur:
        cur.execute("DELETE FROM projectname WHERE id = %s", (project_id,))
        db.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Project not found"}), 404
    
    return jsonify({"message": "Project deleted successfully"})

# 请求相关接口
@app.route('/api/requests', methods=['GET'])
def get_requests():
    with db.cursor() as cur:
        cur.execute("SELECT * FROM requests")
        requests = cur.fetchall()
    return jsonify(requests)

@app.route('/api/requests', methods=['POST'])
def create_request():
    data = request.json
    
    # 从请求中提取数据
    request_name = data.get('requestName')
    request_background = data.get('requestBackground')
    source_language = data.get('sourceLanguage')
    target_languages = ','.join(data.get('targetLanguages', []))
    word_count = data.get('wordCount', 0)
    additional_requirements = ','.join(data.get('additionalRequirements', []))
    expected_delivery_date = data.get('expectedDeliveryDate')
    files = ','.join(data.get('files', []))
    
    # 创建请求记录
    with db.cursor() as cur:
        sql = """
        INSERT INTO requests (
            requestName, requestBackground, sourceLanguage, targetLanguages,
            wordCount, additionalRequirements, expectedDeliveryDate, files, status, createTime
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            request_name, request_background, source_language, target_languages,
            word_count, additional_requirements, expected_delivery_date, files, 'pending', datetime.now()
        ))
        db.commit()
        request_id = cur.lastrowid
    
    return jsonify({"id": request_id, "message": "Request created successfully"}), 201

# 文件上传接口
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # 生成唯一文件名
    filename = str(uuid.uuid4()) + '_' + file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 保存文件
    file.save(file_path)
    
    return jsonify({
        "filename": filename,
        "originalName": file.filename,
        "url": f"/api/files/{filename}"
    })

# 文件下载接口
@app.route('/api/files/<filename>', methods=['GET'])
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 项目文件接口
@app.route('/api/project-files', methods=['POST'])
def create_project_file():
    data = request.json
    
    project_id = data.get('projectId')
    file_type = data.get('fileType')
    notes = data.get('notes', '')
    files = ','.join(data.get('files', []))
    
    # 创建项目文件记录
    with db.cursor() as cur:
        sql = """
        INSERT INTO project_files (
            projectId, fileType, notes, files, uploadTime
        ) VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_id, file_type, notes, files, datetime.now()
        ))
        db.commit()
        file_id = cur.lastrowid
    
    return jsonify({"id": file_id, "message": "Project files uploaded successfully"}), 201

# 邮件接口
@app.route('/api/emails', methods=['POST'])
def send_email():
    data = request.json
    
    project_id = data.get('projectId')
    to = data.get('to')
    cc = data.get('cc', '')
    subject = data.get('subject')
    content = data.get('content')
    attachments = ','.join(data.get('attachments', []))
    
    # 记录邮件
    with db.cursor() as cur:
        sql = """
        INSERT INTO emails (
            projectId, toRecipient, ccRecipient, subject, content, attachments, sendTime
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_id, to, cc, subject, content, attachments, datetime.now()
        ))
        db.commit()
        email_id = cur.lastrowid
    
    # 这里可以添加实际发送邮件的代码
    # 例如使用 smtplib 发送邮件
    
    return jsonify({"id": email_id, "message": "Email sent successfully"}), 200

# 报价接口
@app.route('/api/quotes', methods=['GET'])
def get_quotes():
    with db.cursor() as cur:
        cur.execute("""
            SELECT q.*, p.projectName 
            FROM quotes q 
            JOIN projectname p ON q.projectId = p.id
        """)
        quotes = cur.fetchall()
    return jsonify(quotes)

@app.route('/api/quotes', methods=['POST'])
def create_quote():
    data = request.json
    
    project_id = data.get('projectId')
    lsp_name = data.get('lspName')
    quote_amount = data.get('quoteAmount')
    currency = data.get('currency', 'USD')
    word_count = data.get('wordCount', 0)
    quote_date = data.get('quoteDate', datetime.now().strftime('%Y-%m-%d'))
    status = data.get('status', 'pending')
    notes = data.get('notes', '')
    
    # 创建报价记录
    with db.cursor() as cur:
        sql = """
        INSERT INTO quotes (
            projectId, lspName, quoteAmount, currency, wordCount, 
            quoteDate, status, notes, createTime
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_id, lsp_name, quote_amount, currency, word_count,
            quote_date, status, notes, datetime.now()
        ))
        db.commit()
        quote_id = cur.lastrowid
    
    return jsonify({"id": quote_id, "message": "Quote created successfully"}), 201

@app.route('/api/quotes/extract', methods=['POST'])
def extract_quote():
    data = request.json
    email_content = data.get('emailContent', '')
    
    # 使用正则表达式提取报价信息
    # 这里是一个简单的示例，实际应用中可能需要更复杂的逻辑
    project_id_match = re.search(r'Project ID: (\d+)', email_content)
    amount_match = re.search(r'Quote Amount: (\d+(\.\d+)?)', email_content)
    currency_match = re.search(r'Currency: (\w+)', email_content)
    word_count_match = re.search(r'Word Count: (\d+)', email_content)
    
    extracted_data = {}
    
    if project_id_match:
        extracted_data['projectId'] = int(project_id_match.group(1))
    
    if amount_match:
        extracted_data['quoteAmount'] = float(amount_match.group(1))
    
    if currency_match:
        extracted_data['currency'] = currency_match.group(1)
    
    if word_count_match:
        extracted_data['wordCount'] = int(word_count_match.group(1))
    
    return jsonify(extracted_data)

# 聊天接口
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    response = get_chat_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)