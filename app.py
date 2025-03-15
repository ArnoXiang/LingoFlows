from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql
import os
import uuid
from datetime import datetime, timedelta
import jwt
from src.api.chatGPT import get_chat_response
import re

app = Flask(__name__)

# 配置上传文件存储路径
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# JWT配置
app.config['SECRET_KEY'] = 'lingoflows_secret_key'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=1)

# 正确配置CORS，允许所有来源
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# 配置 MySQL 数据库连接
db = pymysql.connect(
    host='localhost',
    user='root',  
    password='root',  
    database='l10n_management',
    cursorclass=pymysql.cursors.DictCursor
)

# 用户认证相关接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    print(f"尝试登录 - 用户名: {username}")
    
    if not username or not password:
        print("错误: 用户名和密码是必需的")
        return jsonify({"error": "Username and password are required"}), 400
    
    with db.cursor() as cur:
        # 查询用户
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if not user or user['password'] != password:  
            print("错误: 无效的用户名或密码")
            return jsonify({"error": "Invalid username or password"}), 401
        
        print(f"登录成功 - 用户ID: {user['id']}, 角色: {user['role']}")
        
        # 生成JWT令牌
        payload = {
            'id': user['id'],  # 使用'id'作为键名，与其他地方保持一致
            'user_id': user['id'],  # 同时保留'user_id'键名以兼容可能的旧代码
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        print(f"生成的令牌负载: {payload}")
        
        return jsonify({
            "token": token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role'],
                "name": user['name']
            }
        })

@app.route('/api/users/current', methods=['GET'])
def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Authorization header is missing"}), 401
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        
        with db.cursor() as cur:
            cur.execute("SELECT id, username, role, name FROM users WHERE id = %s", (payload['user_id'],))
            user = cur.fetchone()
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify(user)
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except (jwt.InvalidTokenError, IndexError):
        return jsonify({"error": "Invalid token"}), 401

# 验证令牌的装饰器
def token_required(f):
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            print("错误: 请求中缺少Authorization头")
            return jsonify({"error": "Authorization header is missing"}), 401
        
        try:
            token = auth_header.split(" ")[1]
            print(f"收到令牌: {token[:10]}...")
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            print(f"解码后的令牌负载: {payload}")
            request.user = payload
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            print("错误: 令牌已过期")
            return jsonify({"error": "Token has expired"}), 401
        except (jwt.InvalidTokenError, IndexError) as e:
            print(f"错误: 无效的令牌 - {str(e)}")
            return jsonify({"error": "Invalid token"}), 401
    
    decorated.__name__ = f.__name__
    return decorated

# 项目相关接口
@app.route('/api/projects', methods=['GET'])
@token_required
def get_projects():
    user_role = request.user.get('role')
    # 尝试从不同的键名获取用户ID
    user_id = request.user.get('user_id') or request.user.get('id')
    
    print(f"获取项目 - 用户角色: {user_role}, 用户ID: {user_id}")
    print(f"完整的用户信息: {request.user}")
    
    with db.cursor() as cur:
        if user_role == 'LM':
            # LM可以查看所有项目
            print("LM用户 - 查询所有项目")
            cur.execute("SELECT * FROM projectname")
        else:
            # BO只能查看自己提交的项目
            print(f"非LM用户 - 只查询用户ID为 {user_id} 的项目")
            cur.execute("SELECT * FROM projectname WHERE created_by = %s", (user_id,))
        
        projects = cur.fetchall()
        print(f"查询结果: 找到 {len(projects)} 个项目")
        
        # 如果是LM用户但没有找到项目，检查是否有项目的created_by为NULL
        if user_role == 'LM' and len(projects) == 0:
            print("LM用户没有找到项目，检查是否有项目的created_by为NULL")
            cur.execute("SELECT COUNT(*) as count FROM projectname WHERE created_by IS NULL")
            null_count = cur.fetchone()['count']
            print(f"created_by为NULL的项目数: {null_count}")
            
            if null_count > 0:
                print("更新created_by为NULL的项目，设置为当前用户ID")
                cur.execute("UPDATE projectname SET created_by = %s WHERE created_by IS NULL", (user_id,))
                db.commit()
                
                # 重新查询所有项目
                cur.execute("SELECT * FROM projectname")
                projects = cur.fetchall()
                print(f"更新后查询结果: 找到 {len(projects)} 个项目")
    
    return jsonify(projects)

@app.route('/api/projects/<int:project_id>', methods=['GET'])
@token_required
def get_project(project_id):
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    with db.cursor() as cur:
        if user_role == 'LM':
            # LM可以查看任何项目
            cur.execute("SELECT * FROM projectname WHERE id = %s", (project_id,))
        else:
            # BO只能查看自己的项目
            cur.execute("SELECT * FROM projectname WHERE id = %s AND created_by = %s", (project_id, user_id))
        
        project = cur.fetchone()
        if not project:
            return jsonify({"error": "Project not found or you don't have permission"}), 404
    return jsonify(project)

@app.route('/api/projects', methods=['POST'])
@token_required
def create_project():
    data = request.json
    user_id = request.user.get('user_id')
    
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
            taskTranslation, taskLQA, taskTranslationUpdate, taskLQAReportFinalization, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_name, project_status, request_name, project_manager, datetime.now(),
            source_language, target_languages, word_count, expected_delivery_date, additional_requirements,
            'not_started', 'not_started', 'not_started', 'not_started', user_id
        ))
        db.commit()
        project_id = cur.lastrowid
    
    return jsonify({"id": project_id, "message": "Project created successfully"}), 201

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@token_required
def update_project(project_id):
    data = request.json
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    print(f"更新项目 - 项目ID: {project_id}, 用户角色: {user_role}, 用户ID: {user_id}")
    print(f"更新数据: {data}")
    
    # 检查用户是否有权限更新此项目
    with db.cursor() as cur:
        if user_role == 'LM':
            # LM可以更新任何项目
            cur.execute("SELECT id FROM projectname WHERE id = %s", (project_id,))
        else:
            # BO只能更新自己的项目
            cur.execute("SELECT id FROM projectname WHERE id = %s AND created_by = %s", (project_id, user_id))
        
        project = cur.fetchone()
        if not project:
            return jsonify({"error": "Project not found or you don't have permission"}), 404
    
    try:
        # 从请求中提取项目数据
        update_fields = []
        update_values = []
        
        # 检查并添加更新字段 - 基本信息
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
        
        # 检查并添加更新字段 - 任务状态
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
        
        # 检查并添加更新字段 - 任务详细信息
        if 'translationAssignee' in data:
            update_fields.append("translationAssignee = %s")
            update_values.append(data['translationAssignee'])
        
        if 'translationDeadline' in data:
            update_fields.append("translationDeadline = %s")
            try:
                if data['translationDeadline']:
                    if isinstance(data['translationDeadline'], str):
                        date_str = data['translationDeadline'].split('T')[0] if 'T' in data['translationDeadline'] else data['translationDeadline']
                        update_values.append(date_str)
                    else:
                        update_values.append(data['translationDeadline'])
                else:
                    update_values.append(None)
            except Exception as e:
                print(f"处理翻译截止日期时出错: {e}")
                update_values.append(None)
        
        if 'translationNotes' in data:
            update_fields.append("translationNotes = %s")
            update_values.append(data['translationNotes'])
        
        if 'lqaAssignee' in data:
            update_fields.append("lqaAssignee = %s")
            update_values.append(data['lqaAssignee'])
        
        if 'lqaDeadline' in data:
            update_fields.append("lqaDeadline = %s")
            try:
                if data['lqaDeadline']:
                    if isinstance(data['lqaDeadline'], str):
                        date_str = data['lqaDeadline'].split('T')[0] if 'T' in data['lqaDeadline'] else data['lqaDeadline']
                        update_values.append(date_str)
                    else:
                        update_values.append(data['lqaDeadline'])
                else:
                    update_values.append(None)
            except Exception as e:
                print(f"处理LQA截止日期时出错: {e}")
                update_values.append(None)
        
        if 'lqaNotes' in data:
            update_fields.append("lqaNotes = %s")
            update_values.append(data['lqaNotes'])
        
        # 检查并添加更新字段 - 其他信息
        if 'sourceLanguage' in data:
            update_fields.append("sourceLanguage = %s")
            update_values.append(data['sourceLanguage'])
        
        if 'targetLanguages' in data:
            update_fields.append("targetLanguages = %s")
            update_values.append(data['targetLanguages'])
        
        if 'wordCount' in data:
            update_fields.append("wordCount = %s")
            update_values.append(data['wordCount'])
        
        if 'expectedDeliveryDate' in data:
            update_fields.append("expectedDeliveryDate = %s")
            # 确保日期格式正确
            try:
                # 尝试解析日期
                if data['expectedDeliveryDate']:
                    # 如果是日期对象的字符串表示，尝试转换为日期对象
                    if isinstance(data['expectedDeliveryDate'], str):
                        # 移除可能的时区信息
                        date_str = data['expectedDeliveryDate'].split('T')[0] if 'T' in data['expectedDeliveryDate'] else data['expectedDeliveryDate']
                        update_values.append(date_str)
                    else:
                        update_values.append(data['expectedDeliveryDate'])
                else:
                    update_values.append(None)
            except Exception as e:
                print(f"处理日期时出错: {e}")
                update_values.append(None)
        
        if 'additionalRequirements' in data:
            update_fields.append("additionalRequirements = %s")
            update_values.append(data['additionalRequirements'])
        
        # 如果没有要更新的字段，返回错误
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        # 构建更新SQL
        sql = "UPDATE projectname SET " + ", ".join(update_fields) + " WHERE id = %s"
        update_values.append(project_id)
        
        print(f"更新SQL: {sql}")
        print(f"更新值: {update_values}")
        
        # 执行更新
        with db.cursor() as cur:
            # 首先检查表是否有必要的字段
            try:
                cur.execute("SHOW COLUMNS FROM projectname LIKE 'translationAssignee'")
                has_translation_assignee = cur.fetchone() is not None
                
                if not has_translation_assignee:
                    # 添加必要的字段
                    print("添加任务详细信息字段到projectname表")
                    cur.execute("""
                        ALTER TABLE projectname 
                        ADD COLUMN translationAssignee VARCHAR(100),
                        ADD COLUMN translationDeadline DATE,
                        ADD COLUMN translationNotes TEXT,
                        ADD COLUMN lqaAssignee VARCHAR(100),
                        ADD COLUMN lqaDeadline DATE,
                        ADD COLUMN lqaNotes TEXT
                    """)
                    db.commit()
                    print("成功添加字段")
            except Exception as e:
                print(f"检查或添加字段时出错: {e}")
                # 继续执行，即使添加字段失败
            
            # 执行更新
            cur.execute(sql, update_values)
            db.commit()
            if cur.rowcount == 0:
                return jsonify({"error": "Project not found or no changes made"}), 404
        
        return jsonify({"message": "Project updated successfully"})
    except Exception as e:
        print(f"更新项目时出错: {e}")
        db.rollback()
        return jsonify({"error": f"Failed to update project: {str(e)}"}), 500

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@token_required
def delete_project(project_id):
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    # 只有LM可以删除项目
    if user_role != 'LM':
        return jsonify({"error": "Only LM can delete projects"}), 403
    
    with db.cursor() as cur:
        cur.execute("DELETE FROM projectname WHERE id = %s", (project_id,))
        db.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Project not found"}), 404
    
    return jsonify({"message": "Project deleted successfully"})

# 请求相关接口
@app.route('/api/requests', methods=['GET'])
@token_required
def get_requests():
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    with db.cursor() as cur:
        if user_role == 'LM':
            # LM可以查看所有请求
            cur.execute("SELECT * FROM requests")
        else:
            # BO只能查看自己的请求
            cur.execute("SELECT * FROM requests WHERE created_by = %s", (user_id,))
        
        requests = cur.fetchall()
    return jsonify(requests)

@app.route('/api/requests', methods=['POST'])
@token_required
def create_request():
    data = request.json
    user_id = request.user.get('user_id')
    
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
            wordCount, additionalRequirements, expectedDeliveryDate, files, status, createTime, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            request_name, request_background, source_language, target_languages,
            word_count, additional_requirements, expected_delivery_date, files, 'pending', datetime.now(), user_id
        ))
        db.commit()
        request_id = cur.lastrowid
        
        # 自动创建项目
        project_name = f"{request_name} 项目"
        project_manager = 'Yizhuo Xiang'  # 默认项目经理
        project_status = 'pending'  # 默认状态为待处理
        
        # 创建项目记录
        project_sql = """
        INSERT INTO projectname (
            projectName, projectStatus, requestName, projectManager, createTime,
            sourceLanguage, targetLanguages, wordCount, expectedDeliveryDate, additionalRequirements,
            taskTranslation, taskLQA, taskTranslationUpdate, taskLQAReportFinalization, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(project_sql, (
            project_name, project_status, request_name, project_manager, datetime.now(),
            source_language, target_languages, word_count, expected_delivery_date, additional_requirements,
            'not_started', 'not_started', 'not_started', 'not_started', user_id
        ))
        db.commit()
        project_id = cur.lastrowid
        
        # 更新请求记录，关联项目ID
        cur.execute("UPDATE requests SET project_id = %s WHERE id = %s", (project_id, request_id))
        db.commit()
    
    return jsonify({
        "id": request_id, 
        "project_id": project_id,
        "message": "Request submitted and project created successfully"
    }), 201

# 文件上传接口
@app.route('/api/upload', methods=['POST'])
@token_required
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
@token_required
def get_file(filename):
    # 这里可以添加文件权限检查，但需要知道文件与项目的关联
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 项目文件接口
@app.route('/api/project-files', methods=['POST'])
@token_required
def create_project_file():
    data = request.json
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    project_id = data.get('projectId')
    
    # 检查用户是否有权限操作此项目
    with db.cursor() as cur:
        if user_role == 'LM':
            # LM可以操作任何项目
            cur.execute("SELECT id FROM projectname WHERE id = %s", (project_id,))
        else:
            # BO只能操作自己的项目
            cur.execute("SELECT id FROM projectname WHERE id = %s AND created_by = %s", (project_id, user_id))
        
        project = cur.fetchone()
        if not project:
            return jsonify({"error": "Project not found or you don't have permission"}), 404
    
    file_type = data.get('fileType')
    notes = data.get('notes', '')
    files = ','.join(data.get('files', []))
    
    # 创建项目文件记录
    with db.cursor() as cur:
        sql = """
        INSERT INTO project_files (
            projectId, fileType, notes, files, uploadTime, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_id, file_type, notes, files, datetime.now(), user_id
        ))
        db.commit()
        file_id = cur.lastrowid
    
    return jsonify({"id": file_id, "message": "Project files uploaded successfully"}), 201

# 邮件接口
@app.route('/api/emails', methods=['POST'])
@token_required
def send_email():
    data = request.json
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    project_id = data.get('projectId')
    
    # 检查用户是否有权限操作此项目
    with db.cursor() as cur:
        if user_role == 'LM':
            # LM可以操作任何项目
            cur.execute("SELECT id FROM projectname WHERE id = %s", (project_id,))
        else:
            # BO只能操作自己的项目
            cur.execute("SELECT id FROM projectname WHERE id = %s AND created_by = %s", (project_id, user_id))
        
        project = cur.fetchone()
        if not project:
            return jsonify({"error": "Project not found or you don't have permission"}), 404
    
    to = data.get('to')
    cc = data.get('cc', '')
    subject = data.get('subject')
    content = data.get('content')
    attachments = ','.join(data.get('attachments', []))
    
    # 记录邮件
    with db.cursor() as cur:
        sql = """
        INSERT INTO emails (
            projectId, toRecipient, ccRecipient, subject, content, attachments, sendTime, sent_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_id, to, cc, subject, content, attachments, datetime.now(), user_id
        ))
        db.commit()
        email_id = cur.lastrowid
    
    # 这里可以添加实际发送邮件的代码
    # 例如使用 smtplib 发送邮件
    
    return jsonify({"id": email_id, "message": "Email sent successfully"}), 200

# 报价接口
@app.route('/api/quotes', methods=['GET'])
@token_required
def get_quotes():
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    with db.cursor() as cur:
        if user_role == 'LM':
            # LM可以查看所有报价
            cur.execute("""
                SELECT q.*, p.projectName 
                FROM quotes q 
                JOIN projectname p ON q.projectId = p.id
            """)
        else:
            # BO只能查看自己项目的报价
            cur.execute("""
                SELECT q.*, p.projectName 
                FROM quotes q 
                JOIN projectname p ON q.projectId = p.id
                WHERE p.created_by = %s
            """, (user_id,))
        
        quotes = cur.fetchall()
    return jsonify(quotes)

@app.route('/api/quotes', methods=['POST'])
@token_required
def create_quote():
    data = request.json
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    # 只有LM可以创建报价
    if user_role != 'LM':
        return jsonify({"error": "Only LM can create quotes"}), 403
    
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
            quoteDate, status, notes, createTime, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_id, lsp_name, quote_amount, currency, word_count,
            quote_date, status, notes, datetime.now(), user_id
        ))
        db.commit()
        quote_id = cur.lastrowid
    
    return jsonify({"id": quote_id, "message": "Quote created successfully"}), 201

@app.route('/api/quotes/extract', methods=['POST'])
@token_required
def extract_quote():
    user_role = request.user.get('role')
    
    # 只有LM可以提取报价
    if user_role != 'LM':
        return jsonify({"error": "Only LM can extract quotes"}), 403
    
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
@token_required
def chat():
    data = request.json
    user_message = data.get('message')
    response = get_chat_response(user_message)
    return jsonify({'response': response})

# 初始化数据库表
def init_db():
    with db.cursor() as cur:
        # 检查users表是否存在
        cur.execute("SHOW TABLES LIKE 'users'")
        if not cur.fetchone():
            # 创建users表
            cur.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(100) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    role ENUM('LM', 'BO') NOT NULL,
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 添加默认用户
            cur.execute("""
                INSERT INTO users (username, password, name, role, email)
                VALUES 
                ('admin', 'admin123', 'Admin User', 'LM', 'admin@example.com'),
                ('bo1', 'bo123', 'Business Owner 1', 'BO', 'bo1@example.com'),
                ('bo2', 'bo123', 'Business Owner 2', 'BO', 'bo2@example.com')
            """)
            
            print("Users table created and populated with default users")
        
        # 检查projectname表是否有created_by字段
        cur.execute("SHOW COLUMNS FROM projectname LIKE 'created_by'")
        if not cur.fetchone():
            # 添加created_by字段
            cur.execute("ALTER TABLE projectname ADD COLUMN created_by INT")
            print("Added created_by column to projectname table")
        
        # 检查requests表是否有created_by字段
        cur.execute("SHOW COLUMNS FROM requests LIKE 'created_by'")
        if not cur.fetchone():
            # 添加created_by字段
            cur.execute("ALTER TABLE requests ADD COLUMN created_by INT")
            print("Added created_by column to requests table")
        
        # 检查requests表是否有project_id字段
        cur.execute("SHOW COLUMNS FROM requests LIKE 'project_id'")
        if not cur.fetchone():
            # 添加project_id字段
            cur.execute("ALTER TABLE requests ADD COLUMN project_id INT")
            print("Added project_id column to requests table")
        
        # 检查project_files表是否有created_by字段
        cur.execute("SHOW COLUMNS FROM project_files LIKE 'created_by'")
        if not cur.fetchone():
            # 添加created_by字段
            cur.execute("ALTER TABLE project_files ADD COLUMN created_by INT")
            print("Added created_by column to project_files table")
        
        # 检查emails表是否有sent_by字段
        cur.execute("SHOW COLUMNS FROM emails LIKE 'sent_by'")
        if not cur.fetchone():
            # 添加sent_by字段
            cur.execute("ALTER TABLE emails ADD COLUMN sent_by INT")
            print("Added sent_by column to emails table")
        
        # 检查quotes表是否有created_by字段
        cur.execute("SHOW COLUMNS FROM quotes LIKE 'created_by'")
        if not cur.fetchone():
            # 添加created_by字段
            cur.execute("ALTER TABLE quotes ADD COLUMN created_by INT")
            print("Added created_by column to quotes table")
        
        db.commit()

if __name__ == '__main__':
    init_db()  # 初始化数据库
    app.run(debug=True)