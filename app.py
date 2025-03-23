from flask import Flask, request, jsonify, send_from_directory, after_this_request
from flask_cors import CORS
import pymysql
import os
import uuid
from datetime import datetime, timedelta, date
import jwt
from src.api.chatGPT import get_chat_response
import re
import tempfile
import zipfile
import shutil
from flask import send_file
import logging
import json
import traceback
import time

# 配置详细的日志记录
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'flask_app.log')),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger(__name__)

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

# 定义JSON序列化帮助函数
def json_serial(obj):
    """JSON序列化器，处理不可序列化的对象如datetime"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError (f"Type {type(obj)} not serializable")

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
        print("------- 开始验证令牌 -------")
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            print("错误: 请求中缺少Authorization头")
            print(f"请求头: {dict(request.headers)}")
            return jsonify({"error": "Authorization header is missing"}), 401
        
        print(f"收到Authorization头: {auth_header}")
        
        try:
            # 检查格式是否符合"Bearer <token>"
            if not auth_header.startswith('Bearer '):
                print("错误: Authorization头格式错误，应该以'Bearer '开头")
                return jsonify({"error": "Invalid authorization format, expected 'Bearer <token>'"}), 401
            
            token = auth_header.split(" ")[1]
            print(f"提取的令牌: {token[:10]}...")
            
            try:
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                print(f"令牌解码成功，负载: {payload}")
                
                # 检查必要的字段
                if 'user_id' not in payload:
                    print("错误: 令牌负载中缺少user_id字段")
                    return jsonify({"error": "Token payload is missing user_id field"}), 401
                
                # 查询用户是否存在
                with db.cursor() as cur:
                    cur.execute("SELECT id, username, role FROM users WHERE id = %s", (payload['user_id'],))
                    user = cur.fetchone()
                    
                    if not user:
                        print(f"错误: 令牌中的用户ID {payload['user_id']} 不存在")
                        return jsonify({"error": "User not found"}), 401
                    
                    print(f"验证用户存在: {user['username']}, 角色: {user['role']}")
                
                request.user = payload
                print("令牌验证成功")
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                print("错误: 令牌已过期")
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError as e:
                print(f"错误: 无效的令牌 - {str(e)}")
                return jsonify({"error": f"Invalid token: {str(e)}"}), 401
        except Exception as e:
            print(f"验证令牌时发生未预期的错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": "Authentication error"}), 500
    
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
    
    # 使用ASCII=False确保中文正常显示
    logger.info(f"收到创建请求: {json.dumps(data, ensure_ascii=False, default=json_serial)}")
    
    # 从请求中提取数据
    request_name = data.get('requestName')
    request_background = data.get('requestBackground')
    source_language = data.get('sourceLanguage')
    target_languages = ','.join(data.get('targetLanguages', []))
    word_count = data.get('wordCount', 0)
    additional_requirements = ','.join(data.get('additionalRequirements', []))
    expected_delivery_date = data.get('expectedDeliveryDate')
    files = ','.join(data.get('files', []))
    # 提取文件ID列表 - 这个是新增的
    file_ids = data.get('fileIds', [])
    
    # 增强日志记录，检查fileIds的内容和类型
    logger.info(f"提取的文件IDs: {file_ids}, 类型: {type(file_ids)}")
    
    if isinstance(file_ids, list):
        logger.info(f"文件ID列表长度: {len(file_ids)}")
        for i, file_id in enumerate(file_ids):
            logger.info(f"文件ID[{i}]: {file_id}, 类型: {type(file_id)}")
    else:
        logger.warning(f"fileIds不是列表类型: {type(file_ids)}")
        # 尝试转换为列表
        if isinstance(file_ids, str):
            try:
                file_ids = [int(id.strip()) for id in file_ids.split(',') if id.strip()]
                logger.info(f"从字符串转换后的fileIds: {file_ids}")
            except ValueError as e:
                logger.error(f"无法将字符串转换为文件ID列表: {str(e)}")
                file_ids = []
    
    # 确保所有的文件ID都是整数类型
    original_file_ids = file_ids.copy()
    file_ids = [int(id) if isinstance(id, str) and id.isdigit() else id for id in file_ids]
    file_ids = [id for id in file_ids if isinstance(id, int)]
    
    if file_ids != original_file_ids:
        logger.info(f"文件ID经过类型转换，原始值: {original_file_ids}, 处理后: {file_ids}")
    else:
        logger.info(f"文件ID无需类型转换，保持原样: {file_ids}")
    
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
        
        logger.info(f"请求创建成功，ID: {request_id}")
        
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
        
        logger.info(f"项目创建成功，ID: {project_id}")
        
        # 更新请求记录，关联项目ID
        cur.execute("UPDATE requests SET project_id = %s WHERE id = %s", (project_id, request_id))
        db.commit()
        
        # 如果提供了文件ID，自动创建项目文件关联 - 这部分是新增的
        if file_ids:
            logger.info(f"开始创建项目文件关联，项目ID: {project_id}, 文件IDs: {file_ids}")
            try:
                # 确认文件是否存在且属于当前用户
                file_ids_str = ','.join([str(id) for id in file_ids])
                logger.info(f"文件ID列表字符串: {file_ids_str}")
                
                # 直接构建SQL，避免参数展开问题
                file_query = f"""
                    SELECT id FROM files 
                    WHERE id IN ({file_ids_str}) AND uploaded_by = {user_id} AND isDeleted = FALSE
                """
                logger.info(f"执行查询: {file_query}")
                
                cur.execute(file_query)
                found_files = cur.fetchall()
                
                logger.info(f"查询结果 - 找到文件: {json.dumps(found_files, default=json_serial)}")
                
                # 获取找到的文件ID列表
                found_file_ids = [f['id'] for f in found_files]
                logger.info(f"找到的文件IDs: {found_file_ids}, 数量: {len(found_file_ids)}")
                
                # 只要找到任何有效文件就创建关联
                if found_file_ids:
                    # 获取文件名，用作files字段
                    file_names_query = f"""
                        SELECT id, originalName FROM files 
                        WHERE id IN ({file_ids_str})
                    """
                    logger.info(f"查询文件名: {file_names_query}")
                    
                    cur.execute(file_names_query)
                    file_names_result = cur.fetchall()
                    file_names = [f['originalName'] for f in file_names_result]
                    files_str = ', '.join(file_names) if file_names else 'files from request'
                    
                    logger.info(f"获取到的文件名: {files_str}")
                    
                    # 检查project_files表是否有files字段
                    try:
                        cur.execute("SHOW COLUMNS FROM project_files LIKE 'files'")
                        has_files_column = cur.fetchone() is not None
                        logger.info(f"project_files表是否有files列: {has_files_column}")
                    except Exception as e:
                        logger.error(f"检查project_files表结构时出错: {str(e)}")
                        has_files_column = True  # 假设存在，避免中断流程
                    
                    # 创建项目文件记录
                    if has_files_column:
                        # 如果有files字段，正常插入
                        sql = """
                        INSERT INTO project_files (
                            projectId, fileType, notes, files, uploadTime, created_by
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cur.execute(sql, (
                            project_id, 'source', '请求提交时上传的文件 / Files uploaded with request submission', 
                            files_str, datetime.now(), user_id
                        ))
                    else:
                        # 如果没有files字段，忽略它
                        sql = """
                        INSERT INTO project_files (
                            projectId, fileType, notes, uploadTime, created_by
                        ) VALUES (%s, %s, %s, %s, %s)
                        """
                        cur.execute(sql, (
                            project_id, 'source', '请求提交时上传的文件 / Files uploaded with request submission', 
                            datetime.now(), user_id
                        ))
                    
                    db.commit()
                    project_file_id = cur.lastrowid
                    
                    logger.info(f"创建项目文件记录成功，ID: {project_file_id}")
                    
                    # 创建项目文件与原始文件的关联
                    inserted_mappings = 0
                    for file_id in found_file_ids:
                        try:
                            sql = """
                            INSERT INTO project_file_mappings (
                                project_file_id, file_id
                            ) VALUES (%s, %s)
                            """
                            cur.execute(sql, (project_file_id, file_id))
                            logger.info(f"创建文件映射: 项目文件ID {project_file_id} -> 文件ID {file_id}")
                            inserted_mappings += 1
                        except Exception as mapping_err:
                            logger.error(f"创建单个文件映射时出错 (文件ID {file_id}): {str(mapping_err)}")
                    
                    if inserted_mappings > 0:
                        db.commit()
                        logger.info(f"已为请求 {request_id} 创建项目文件关联，关联了 {inserted_mappings} 个文件")
                    else:
                        logger.warning(f"尝试关联 {len(found_file_ids)} 个文件，但全部失败")
                else:
                    logger.warning(f"没有找到有效的文件 - 请求的文件IDs: {file_ids}, 用户ID: {user_id}")
                    
                    # 再次查询这些文件存在但可能不属于当前用户的情况
                    check_query = f"""
                        SELECT id, uploaded_by, isDeleted FROM files 
                        WHERE id IN ({file_ids_str})
                    """
                    logger.info(f"执行额外查询验证文件存在性: {check_query}")
                    
                    cur.execute(check_query)
                    check_results = cur.fetchall()
                    
                    if check_results:
                        logger.warning(f"找到文件但不符合条件: {json.dumps(check_results, default=json_serial)}")
                        for file in check_results:
                            if file['uploaded_by'] != user_id:
                                logger.warning(f"文件ID {file['id']} 属于用户 {file['uploaded_by']}，而不是当前用户 {user_id}")
                            if file['isDeleted']:
                                logger.warning(f"文件ID {file['id']} 已被标记为删除")
                    else:
                        logger.warning(f"找不到任何ID在 {file_ids_str} 中的文件记录")
                        
                    # 检查用户是否有权限访问这些文件
                    user_query = f"""
                        SELECT id, username, role FROM users 
                        WHERE id = {user_id}
                    """
                    logger.info(f"查询用户信息: {user_query}")
                    
                    cur.execute(user_query)
                    user_info = cur.fetchone()
                    
                    if user_info:
                        logger.info(f"用户信息: {json.dumps(user_info, default=json_serial)}")
                    else:
                        logger.warning(f"找不到ID为 {user_id} 的用户")
            except Exception as e:
                logger.error(f"创建项目文件关联时出错: {str(e)}")
                logger.error(f"文件IDs: {file_ids}")
                logger.error(f"项目ID: {project_id}")
                logger.error(f"用户ID: {user_id}")
                # 详细记录异常信息
                logger.error(traceback.format_exc())
                # 不阻止请求创建，仅记录错误
        else:
            logger.info("未提供文件IDs，跳过创建项目文件关联")
    
    return jsonify({
        "id": request_id, 
        "project_id": project_id,
        "message": "Request submitted and project created successfully"
    }), 201

# 文件上传接口
@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file():
    logger.info(f"收到文件上传请求，用户: {request.user.get('username')}, ID: {request.user.get('user_id')}")
    
    # 检查请求中是否包含'file'部分
    if 'file' not in request.files:
        logger.error("错误: 请求中没有'file'部分")
        logger.debug(f"请求files字典内容: {request.files}")
        logger.debug(f"请求form字典内容: {request.form}")
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    logger.info(f"获取到文件: {file.filename}, 类型: {file.content_type if hasattr(file, 'content_type') else '未知类型'}")
    
    if file.filename == '':
        logger.error("错误: 未选择文件或文件名为空")
        return jsonify({"error": "No selected file"}), 400
    
    user_id = request.user.get('user_id')
    logger.info(f"上传者ID: {user_id}")
    
    try:
        # 确保上传目录存在
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            logger.info(f"上传目录不存在，正在创建: {app.config['UPLOAD_FOLDER']}")
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # 生成唯一文件名
        unique_filename = str(uuid.uuid4()) + '_' + file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        logger.info(f"生成的唯一文件名: {unique_filename}")
        logger.debug(f"文件将保存到: {file_path}")
        
        # 保存文件
        file.save(file_path)
        logger.info(f"文件成功保存到磁盘")
        
        # 获取文件大小和类型
        file_size = os.path.getsize(file_path)
        file_type = file.content_type if hasattr(file, 'content_type') else None
        logger.info(f"文件大小: {file_size} 字节, 类型: {file_type}")
        
        # 将文件信息存储到数据库
        with db.cursor() as cur:
            sql = """
            INSERT INTO files (
                filename, originalName, fileType, fileSize, filePath, 
                uploadTime, uploaded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                unique_filename, file.filename, file_type, file_size, file_path,
                datetime.now(), user_id
            ))
            db.commit()
            file_id = cur.lastrowid
            logger.info(f"文件信息已保存到数据库，ID: {file_id}")
            
            # 确认文件记录是否成功创建
            cur.execute("SELECT * FROM files WHERE id = %s", (file_id,))
            file_record = cur.fetchone()
            logger.debug(f"验证文件记录: {json.dumps(file_record, default=json_serial) if file_record else 'Not found'}")
        
        response_data = {
            "file_id": file_id,
            "filename": unique_filename,
            "originalName": file.filename,
            "url": f"/api/files/{unique_filename}"
        }
        logger.info(f"返回上传响应: {json.dumps(response_data)}")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"文件上传处理过程中发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Error processing file upload: {str(e)}"}), 500

# 文件下载接口
@app.route('/api/files/<filename>', methods=['GET'])
@token_required
def get_file(filename):
    user_id = request.user.get('user_id')
    user_role = request.user.get('role')
    
    # 检查文件是否存在并获取文件信息
    with db.cursor() as cur:
        cur.execute("SELECT * FROM files WHERE filename = %s AND isDeleted = FALSE", (filename,))
        file_info = cur.fetchone()
        
        if not file_info:
            return jsonify({"error": "File not found"}), 404
        
        # 检查权限 - LM 可以访问所有文件，BO 只能访问自己上传的或有权限的文件
        if user_role != 'LM' and file_info['uploaded_by'] != user_id:
            # 检查是否有显式权限
            cur.execute("""
                SELECT * FROM file_permissions 
                WHERE file_id = %s AND user_id = %s AND can_view = TRUE
            """, (file_info['id'], user_id))
            permission = cur.fetchone()
            
            if not permission:
                # 检查是否是项目文件，且用户属于该项目
                cur.execute("""
                    SELECT pf.* FROM project_file_mappings pfm
                    JOIN project_files pf ON pfm.project_file_id = pf.id
                    JOIN projectname p ON pf.projectId = p.id
                    WHERE pfm.file_id = %s AND p.created_by = %s
                """, (file_info['id'], user_id))
                project_file = cur.fetchone()
                
                if not project_file:
                    return jsonify({"error": "You don't have permission to access this file"}), 403
    
    # 用户有权访问文件，返回文件
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 项目文件接口
@app.route('/api/project-files', methods=['POST'])
@token_required
def create_project_file():
    data = request.json
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    project_id = data.get('projectId')
    file_ids = data.get('fileIds', [])  # 现在接收文件ID列表而不是文件名
    
    if not file_ids:
        return jsonify({"error": "No files provided"}), 400
    
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
        
        # 检查文件是否存在且属于当前用户
        file_ids_str = ','.join(['%s'] * len(file_ids))
        cur.execute(f"""
            SELECT id FROM files 
            WHERE id IN ({file_ids_str}) AND uploaded_by = %s AND isDeleted = FALSE
        """, (*file_ids, user_id))
        found_files = cur.fetchall()
        
        if len(found_files) != len(file_ids):
            return jsonify({"error": "Some files not found or you don't have permission"}), 400
    
    file_type = data.get('fileType')
    notes = data.get('notes', '')
    
    # 创建项目文件记录
    with db.cursor() as cur:
        # 1. 创建项目文件主记录
        sql = """
        INSERT INTO project_files (
            projectId, fileType, notes, files, uploadTime, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_id, file_type, notes, ','.join([str(id) for id in file_ids]), datetime.now(), user_id
        ))
        db.commit()
        project_file_id = cur.lastrowid
        
        # 2. 创建项目文件与原始文件的关联
        for file_id in file_ids:
            sql = """
            INSERT INTO project_file_mappings (
                project_file_id, file_id
            ) VALUES (%s, %s)
            """
            cur.execute(sql, (project_file_id, file_id))
        
        db.commit()
    
    return jsonify({"id": project_file_id, "message": "Project files uploaded successfully"}), 201

# 获取项目文件接口
@app.route('/api/project-files/<int:project_id>', methods=['GET'])
@token_required
def get_project_files(project_id):
    # 获取当前用户信息
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    logger.info(f"获取项目 {project_id} 的文件，用户ID: {user_id}, 角色: {user_role}")
    
    try:
        # 验证项目存在并且用户有权限访问
        with db.cursor() as cur:
            # 检查用户是否有权限访问此项目
            if user_role == 'LM':
                # LM可以访问任何项目
                cur.execute("SELECT id FROM projectname WHERE id = %s", (project_id,))
            else:
                # BO只能访问自己的项目
                cur.execute("SELECT id FROM projectname WHERE id = %s AND created_by = %s", (project_id, user_id))
            
            project = cur.fetchone()
            
            if not project:
                logger.warning(f"用户 {user_id} 尝试访问不存在或无权限的项目 {project_id}")
                return jsonify({"error": "项目不存在或您没有访问权限"}), 404
            
            logger.info(f"用户 {user_id} 有权限访问项目 {project_id}")
            
            # 检查project_files表结构
            try:
                cur.execute("SHOW COLUMNS FROM project_files LIKE 'files'")
                has_files_column = cur.fetchone() is not None
                logger.info(f"project_files表是否有files列: {has_files_column}")
            except Exception as e:
                logger.error(f"检查project_files表结构时出错: {str(e)}")
                has_files_column = False
            
            # 获取项目文件组
            query = """
                SELECT 
                    pf.id, pf.uploadTime as created_at, pf.notes as description, pf.fileType
                FROM project_files pf
                WHERE pf.projectId = %s
            """
            logger.info(f"执行查询项目文件组: {query.replace('%s', str(project_id))}")
            cur.execute(query, (project_id,))
            
            project_files = cur.fetchall()
            
            logger.info(f"找到 {len(project_files)} 个项目文件组")
            
            result = []
            for pf in project_files:
                project_file_id = pf['id']
                
                logger.info(f"处理项目文件组 ID: {project_file_id}, 描述: {pf['description']}")
                
                # 获取关联的原始文件
                query = """
                    SELECT f.id, f.filename, f.originalName, f.filePath as file_path, 
                           f.fileType as file_type, f.uploadTime as created_at,
                           f.uploaded_by, pfm.project_file_id
                    FROM files f
                    JOIN project_file_mappings pfm ON f.id = pfm.file_id
                    WHERE pfm.project_file_id = %s AND f.isDeleted = FALSE
                """
                logger.info(f"执行查询关联文件: {query.replace('%s', str(project_file_id))}")
                cur.execute(query, (project_file_id,))
                
                files = cur.fetchall()
                logger.info(f"找到 {len(files)} 个关联文件")
                
                # 如果没有找到关联文件通过映射表，但表中有files字段，尝试通过files字段获取文件信息
                if len(files) == 0 and has_files_column:
                    logger.info(f"映射表中未找到文件，尝试通过files字段获取")
                    cur.execute("SELECT files FROM project_files WHERE id = %s", (project_file_id,))
                    files_info = cur.fetchone()
                    if files_info and files_info.get('files'):
                        logger.info(f"从files字段获取的文件信息: {files_info['files']}")
                        # 将文件名拆分为列表
                        file_names = [name.strip() for name in files_info['files'].split(',') if name.strip()]
                        if file_names:
                            # 根据文件名查询文件记录
                            names_query = ','.join(['%s'] * len(file_names))
                            query = f"""
                                SELECT id, filename, originalName, filePath as file_path, 
                                       fileType as file_type, uploadTime as created_at,
                                       uploaded_by
                                FROM files
                                WHERE originalName IN ({names_query}) AND isDeleted = FALSE
                            """
                            logger.info(f"根据文件名查询文件: {query}")
                            cur.execute(query, tuple(file_names))
                            files = cur.fetchall()
                            logger.info(f"通过文件名找到 {len(files)} 个文件")
                
                file_list = []
                for file in files:
                    logger.debug(f"处理文件 ID: {file['id']}, 文件名: {file['filename']}, 原始名称: {file['originalName']}")
                    
                    # 构建文件URL
                    file_url = f"/api/files/{file['filename']}"
                    
                    file_list.append({
                        "id": file['id'],
                        "name": file['originalName'] or file['filename'],  # 使用originalName作为显示名称
                        "filename": file['filename'],  # 保留filename字段
                        "url": file_url,
                        "type": file['file_type'],
                        "created_at": file['created_at']
                    })
                
                result.append({
                    "id": pf['id'],
                    "created_at": pf['created_at'],
                    "fileType": pf['fileType'],
                    "description": pf['description'] or f"项目文件 {pf['id']}",
                    "fileList": file_list
                })
            
            logger.info(f"成功获取项目 {project_id} 的文件，共 {len(result)} 个文件组，总计 {sum(len(g['fileList']) for g in result)} 个文件")
            return jsonify(result)
    
    except Exception as e:
        logger.error(f"获取项目文件时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"获取项目文件失败: {str(e)}"}), 500

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
    attachment_ids = data.get('attachmentIds', [])
    
    # 检查文件是否存在并属于当前用户
    if attachment_ids:
        with db.cursor() as cur:
            attachment_ids_str = ','.join(['%s'] * len(attachment_ids))
            cur.execute(f"""
                SELECT id FROM files 
                WHERE id IN ({attachment_ids_str}) AND isDeleted = FALSE
            """, (*attachment_ids,))
            found_files = cur.fetchall()
            
            if len(found_files) != len(attachment_ids):
                return jsonify({"error": "Some attachment files not found"}), 400
    
    # 记录邮件
    with db.cursor() as cur:
        sql = """
        INSERT INTO emails (
            projectId, toRecipient, ccRecipient, subject, content, sendTime, sent_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            project_id, to, cc, subject, content, datetime.now(), user_id
        ))
        db.commit()
        email_id = cur.lastrowid
        
        # 关联附件
        if attachment_ids:
            for file_id in attachment_ids:
                cur.execute("""
                    INSERT INTO email_attachments (email_id, file_id)
                    VALUES (%s, %s)
                """, (email_id, file_id))
            db.commit()
    
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

# 获取单个邮件及其附件信息
@app.route('/api/emails/<int:email_id>', methods=['GET'])
@token_required
def get_email(email_id):
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    # 检查邮件是否存在并获取邮件信息
    with db.cursor() as cur:
        if user_role == 'LM':
            # LM可以查看任何邮件
            cur.execute("""
                SELECT e.*, p.projectName 
                FROM emails e
                JOIN projectname p ON e.projectId = p.id
                WHERE e.id = %s
            """, (email_id,))
        else:
            # BO只能查看与自己相关的项目的邮件
            cur.execute("""
                SELECT e.*, p.projectName 
                FROM emails e
                JOIN projectname p ON e.projectId = p.id
                WHERE e.id = %s AND p.created_by = %s
            """, (email_id, user_id))
        
        email_info = cur.fetchone()
        if not email_info:
            return jsonify({"error": "Email not found or you don't have permission"}), 404
        
        # 获取邮件附件
        cur.execute("""
            SELECT f.id, f.filename, f.originalName, f.fileType, f.fileSize
            FROM email_attachments ea
            JOIN files f ON ea.file_id = f.id
            WHERE ea.email_id = %s AND f.isDeleted = FALSE
        """, (email_id,))
        
        attachments = []
        for row in cur.fetchall():
            attachments.append({
                'id': row['id'],
                'filename': row['filename'],
                'originalName': row['originalName'],
                'fileType': row['fileType'],
                'fileSize': row['fileSize'],
                'url': f"/api/files/{row['filename']}"
            })
        
        # 将附件信息添加到邮件对象
        email_info['attachments'] = attachments
    
    return jsonify(email_info)

# 获取项目所有邮件
@app.route('/api/project-emails/<int:project_id>', methods=['GET'])
@token_required
def get_project_emails(project_id):
    user_role = request.user.get('role')
    user_id = request.user.get('user_id')
    
    # 检查用户是否有权限访问此项目
    with db.cursor() as cur:
        if user_role == 'LM':
            # LM可以访问任何项目
            cur.execute("SELECT id FROM projectname WHERE id = %s", (project_id,))
        else:
            # BO只能访问自己的项目
            cur.execute("SELECT id FROM projectname WHERE id = %s AND created_by = %s", (project_id, user_id))
        
        project = cur.fetchone()
        if not project:
            return jsonify({"error": "Project not found or you don't have permission"}), 404
    
    # 获取项目相关的邮件
    with db.cursor() as cur:
        cur.execute("""
            SELECT id, projectId, toRecipient, ccRecipient, subject, content, sendTime, sent_by
            FROM emails
            WHERE projectId = %s
            ORDER BY sendTime DESC
        """, (project_id,))
        
        emails = []
        for row in cur.fetchall():
            email_item = dict(row)
            
            # 获取邮件附件数量
            cur.execute("""
                SELECT COUNT(*) as attachmentCount
                FROM email_attachments
                WHERE email_id = %s
            """, (row['id'],))
            attachment_count = cur.fetchone()['attachmentCount']
            email_item['attachmentCount'] = attachment_count
            
            emails.append(email_item)
    
    return jsonify(emails)

# 批量下载文件
@app.route('/api/files/download-batch', methods=['POST'])
@token_required
def download_batch_files():
    data = request.json
    user_id = request.user.get('user_id')
    user_role = request.user.get('role')
    
    file_ids = data.get('fileIds', [])
    if not file_ids:
        return jsonify({"error": "No file IDs provided"}), 400
    
    # 检查文件是否存在并获取文件信息
    with db.cursor() as cur:
        file_ids_str = ','.join(['%s'] * len(file_ids))
        
        if user_role == 'LM':
            # LM可以访问所有文件
            query = f"""
                SELECT id, filename, originalName, filePath 
                FROM files 
                WHERE id IN ({file_ids_str}) AND isDeleted = FALSE
            """
            cur.execute(query, tuple(file_ids))
        else:
            # BO只能访问自己上传的或有权限的文件
            query = f"""
                SELECT id, filename, originalName, filePath 
                FROM files 
                WHERE id IN ({file_ids_str}) AND (uploaded_by = %s OR id IN (
                    SELECT file_id FROM file_permissions WHERE user_id = %s AND can_view = TRUE
                ) OR id IN (
                    SELECT pfm.file_id 
                    FROM project_file_mappings pfm
                    JOIN project_files pf ON pfm.project_file_id = pf.id
                    JOIN projectname p ON pf.projectId = p.id
                    WHERE p.created_by = %s
                )) AND isDeleted = FALSE
            """
            cur.execute(query, (*file_ids, user_id, user_id, user_id))
        
        files_info = cur.fetchall()
        
        if not files_info:
            return jsonify({"error": "No accessible files found"}), 404
    
    # 创建一个临时目录用于存放ZIP文件
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, 'files.zip')
    
    try:
        # 创建ZIP文件
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_info in files_info:
                file_path = file_info['filePath']
                original_name = file_info['originalName']
                
                # 添加文件到ZIP，使用原始文件名
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=original_name)
                else:
                    print(f"文件不存在: {file_path}")
        
        # 发送ZIP文件
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name='files.zip'
        )
    except Exception as e:
        print(f"创建ZIP文件时出错: {str(e)}")
        return jsonify({"error": f"Error creating ZIP file: {str(e)}"}), 500
    finally:
        # 清理临时目录（在请求完成后）
        @after_this_request
        def remove_temp_dir(response):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"清理临时目录时出错: {str(e)}")
            return response

# 软删除文件
@app.route('/api/files/<int:file_id>', methods=['DELETE'])
@token_required
def delete_file(file_id):
    user_id = request.user.get('user_id')
    user_role = request.user.get('role')
    
    # 检查文件是否存在
    with db.cursor() as cur:
        cur.execute("SELECT * FROM files WHERE id = %s AND isDeleted = FALSE", (file_id,))
        file_info = cur.fetchone()
        
        if not file_info:
            return jsonify({"error": "File not found"}), 404
        
        # 检查删除权限
        has_permission = False
        
        # LM 可以删除所有文件
        if user_role == 'LM':
            has_permission = True
        # 上传者可以删除自己的文件
        elif file_info['uploaded_by'] == user_id:
            has_permission = True
        else:
            # 检查是否有显式删除权限
            cur.execute("""
                SELECT * FROM file_permissions 
                WHERE file_id = %s AND user_id = %s AND can_delete = TRUE
            """, (file_id, user_id))
            permission = cur.fetchone()
            has_permission = permission is not None
        
        if not has_permission:
            return jsonify({"error": "You don't have permission to delete this file"}), 403
        
        # 软删除文件（将isDeleted标记为TRUE）
        cur.execute("UPDATE files SET isDeleted = TRUE WHERE id = %s", (file_id,))
        db.commit()
    
    return jsonify({"message": "File deleted successfully"}), 200

# 批量软删除文件
@app.route('/api/files/delete-batch', methods=['POST'])
@token_required
def delete_batch_files():
    data = request.json
    user_id = request.user.get('user_id')
    user_role = request.user.get('role')
    
    file_ids = data.get('fileIds', [])
    if not file_ids:
        return jsonify({"error": "No file IDs provided"}), 400
    
    # 获取有权限删除的文件
    with db.cursor() as cur:
        deleted_count = 0
        
        for file_id in file_ids:
            # 检查文件是否存在
            cur.execute("SELECT * FROM files WHERE id = %s AND isDeleted = FALSE", (file_id,))
            file_info = cur.fetchone()
            
            if not file_info:
                continue
            
            # 检查删除权限
            has_permission = False
            
            # LM 可以删除所有文件
            if user_role == 'LM':
                has_permission = True
            # 上传者可以删除自己的文件
            elif file_info['uploaded_by'] == user_id:
                has_permission = True
            else:
                # 检查是否有显式删除权限
                cur.execute("""
                    SELECT * FROM file_permissions 
                    WHERE file_id = %s AND user_id = %s AND can_delete = TRUE
                """, (file_id, user_id))
                permission = cur.fetchone()
                has_permission = permission is not None
            
            if has_permission:
                # 软删除文件
                cur.execute("UPDATE files SET isDeleted = TRUE WHERE id = %s", (file_id,))
                deleted_count += 1
        
        db.commit()
    
    return jsonify({"message": f"{deleted_count} files deleted successfully"}), 200

# 添加一个诊断路由，用于检查文件上传和关联情况
@app.route('/api/diagnostics/file-relations', methods=['GET'])
@token_required
def diagnose_file_relations():
    user_id = request.user.get('user_id')
    user_role = request.user.get('role')
    
    try:
        with db.cursor() as cur:
            # 获取用户上传的文件数量
            cur.execute("SELECT COUNT(*) as count FROM files WHERE uploaded_by = %s AND isDeleted = FALSE", (user_id,))
            file_count = cur.fetchone()['count']
            
            # 获取用户参与的项目数量
            if user_role == 'LM':
                cur.execute("SELECT COUNT(*) as count FROM projectname")
            else:
                cur.execute("SELECT COUNT(*) as count FROM projectname WHERE created_by = %s", (user_id,))
            project_count = cur.fetchone()['count']
            
            # 获取项目文件数量
            if user_role == 'LM':
                cur.execute("SELECT COUNT(*) as count FROM project_files")
            else:
                cur.execute("SELECT COUNT(*) as count FROM project_files WHERE created_by = %s", (user_id,))
            project_file_count = cur.fetchone()['count']
            
            # 获取文件映射数量
            cur.execute("""
                SELECT COUNT(*) as count FROM project_file_mappings pfm
                JOIN project_files pf ON pfm.project_file_id = pf.id
                JOIN files f ON pfm.file_id = f.id
                WHERE f.uploaded_by = %s AND f.isDeleted = FALSE
            """, (user_id,))
            mapping_count = cur.fetchone()['count']
            
            # 获取最近上传的文件
            cur.execute("""
                SELECT id, filename, originalName, uploadTime, isDeleted
                FROM files
                WHERE uploaded_by = %s
                ORDER BY uploadTime DESC
                LIMIT 5
            """, (user_id,))
            recent_files = cur.fetchall()
            
            # 获取最近创建的项目文件
            if user_role == 'LM':
                cur.execute("""
                    SELECT pf.id, pf.projectId, pf.fileType, pf.uploadTime, pf.files
                    FROM project_files pf
                    ORDER BY pf.uploadTime DESC
                    LIMIT 5
                """)
            else:
                cur.execute("""
                    SELECT pf.id, pf.projectId, pf.fileType, pf.uploadTime, pf.files
                    FROM project_files pf
                    WHERE pf.created_by = %s
                    ORDER BY pf.uploadTime DESC
                    LIMIT 5
                """, (user_id,))
            recent_project_files = cur.fetchall()
            
            # 获取文件映射详情
            cur.execute("""
                SELECT pfm.id, pfm.project_file_id, pfm.file_id,
                       pf.projectId, f.originalName
                FROM project_file_mappings pfm
                JOIN project_files pf ON pfm.project_file_id = pf.id
                JOIN files f ON pfm.file_id = f.id
                WHERE f.uploaded_by = %s AND f.isDeleted = FALSE
                ORDER BY pfm.id DESC
                LIMIT 10
            """, (user_id,))
            mapping_details = cur.fetchall()
            
            # 检查数据库表结构
            cur.execute("SHOW COLUMNS FROM project_files")
            project_files_columns = [col['Field'] for col in cur.fetchall()]
            
            cur.execute("SHOW COLUMNS FROM project_file_mappings")
            mapping_columns = [col['Field'] for col in cur.fetchall()]
            
            # 返回诊断结果
            return jsonify({
                "user_id": user_id,
                "user_role": user_role,
                "file_count": file_count,
                "project_count": project_count,
                "project_file_count": project_file_count,
                "mapping_count": mapping_count,
                "recent_files": recent_files,
                "recent_project_files": recent_project_files,
                "mapping_details": mapping_details,
                "project_files_columns": project_files_columns,
                "mapping_columns": mapping_columns,
                "database_check": "ok"
            })
            
    except Exception as e:
        logger.error(f"诊断文件关联时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

# 初始化数据库表
def init_db():
    logger.info("开始初始化数据库表...")
    
    with db.cursor() as cur:
        # 检查users表是否存在
        cur.execute("SHOW TABLES LIKE 'users'")
        if not cur.fetchone():
            # 创建users表
            logger.info("创建users表...")
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
            logger.info("添加默认用户...")
            cur.execute("""
                INSERT INTO users (username, password, name, role, email)
                VALUES 
                ('admin', 'admin123', 'Admin User', 'LM', 'admin@example.com'),
                ('bo1', 'bo123', 'Business Owner 1', 'BO', 'bo1@example.com'),
                ('bo2', 'bo123', 'Business Owner 2', 'BO', 'bo2@example.com')
            """)
            
            logger.info("Users表创建完成，添加了默认用户")
        else:
            logger.info("Users表已存在，无需创建")
        
        # 检查projectname表是否有created_by字段
        cur.execute("SHOW COLUMNS FROM projectname LIKE 'created_by'")
        if not cur.fetchone():
            # 添加created_by字段
            logger.info("向projectname表添加created_by字段...")
            cur.execute("ALTER TABLE projectname ADD COLUMN created_by INT")
            logger.info("成功添加created_by字段到projectname表")
        else:
            logger.info("projectname表已有created_by字段")
        
        # 检查requests表是否有created_by字段
        cur.execute("SHOW COLUMNS FROM requests LIKE 'created_by'")
        if not cur.fetchone():
            # 添加created_by字段
            logger.info("向requests表添加created_by字段...")
            cur.execute("ALTER TABLE requests ADD COLUMN created_by INT")
            logger.info("成功添加created_by字段到requests表")
        else:
            logger.info("requests表已有created_by字段")
        
        # 检查requests表是否有project_id字段
        cur.execute("SHOW COLUMNS FROM requests LIKE 'project_id'")
        if not cur.fetchone():
            # 添加project_id字段
            logger.info("向requests表添加project_id字段...")
            cur.execute("ALTER TABLE requests ADD COLUMN project_id INT")
            logger.info("成功添加project_id字段到requests表")
        else:
            logger.info("requests表已有project_id字段")
        
        # 检查files表是否存在
        cur.execute("SHOW TABLES LIKE 'files'")
        if not cur.fetchone():
            # 创建files表
            logger.info("创建files表...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    originalName VARCHAR(255) NOT NULL,
                    fileType VARCHAR(100),
                    fileSize INT,
                    filePath VARCHAR(255) NOT NULL,
                    fileContent LONGBLOB,
                    uploadTime DATETIME NOT NULL,
                    uploaded_by INT NOT NULL,
                    isDeleted BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (uploaded_by) REFERENCES users(id)
                )
            """)
            logger.info("Files表创建完成")
        else:
            logger.info("Files表已存在，无需创建")
        
        # 检查project_files表是否存在
        cur.execute("SHOW TABLES LIKE 'project_files'")
        if not cur.fetchone():
            # 创建project_files表
            logger.info("创建project_files表...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS project_files (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    projectId INT NOT NULL,
                    fileType ENUM('source', 'translation', 'lqa', 'other') NOT NULL,
                    notes TEXT,
                    files TEXT,
                    uploadTime DATETIME NOT NULL,
                    created_by INT NOT NULL,
                    FOREIGN KEY (projectId) REFERENCES projectname(id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            logger.info("Project_files表创建完成")
        elif not cur.execute("SHOW COLUMNS FROM project_files LIKE 'created_by'"):
            # 添加created_by字段
            logger.info("向project_files表添加created_by字段...")
            cur.execute("ALTER TABLE project_files ADD COLUMN created_by INT")
            logger.info("成功添加created_by字段到project_files表")
        else:
            logger.info("Project_files表已存在，无需创建")
        
        # 检查project_file_mappings表是否存在
        cur.execute("SHOW TABLES LIKE 'project_file_mappings'")
        if not cur.fetchone():
            # 创建project_file_mappings表
            logger.info("创建project_file_mappings表...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS project_file_mappings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_file_id INT NOT NULL,
                    file_id INT NOT NULL,
                    FOREIGN KEY (project_file_id) REFERENCES project_files(id) ON DELETE CASCADE,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            """)
            logger.info("Project_file_mappings表创建完成")
        else:
            logger.info("Project_file_mappings表已存在，无需创建")
        
        # 检查file_permissions表是否存在
        cur.execute("SHOW TABLES LIKE 'file_permissions'")
        if not cur.fetchone():
            # 创建file_permissions表
            logger.info("创建file_permissions表...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS file_permissions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    file_id INT NOT NULL,
                    user_id INT NOT NULL,
                    can_view BOOLEAN DEFAULT TRUE,
                    can_download BOOLEAN DEFAULT TRUE,
                    can_edit BOOLEAN DEFAULT FALSE,
                    can_delete BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            logger.info("File_permissions表创建完成")
        else:
            logger.info("File_permissions表已存在，无需创建")
        
        # 检查emails表是否有sent_by字段
        cur.execute("SHOW COLUMNS FROM emails LIKE 'sent_by'")
        if not cur.fetchone():
            # 添加sent_by字段
            logger.info("向emails表添加sent_by字段...")
            cur.execute("ALTER TABLE emails ADD COLUMN sent_by INT")
            logger.info("成功添加sent_by字段到emails表")
        else:
            logger.info("emails表已有sent_by字段")
        
        # 检查email_attachments表是否存在
        cur.execute("SHOW TABLES LIKE 'email_attachments'")
        if not cur.fetchone():
            # 创建email_attachments表
            logger.info("创建email_attachments表...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS email_attachments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email_id INT NOT NULL,
                    file_id INT NOT NULL, 
                    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            """)
            logger.info("Email_attachments表创建完成")
        else:
            logger.info("Email_attachments表已存在，无需创建")
        
        # 检查quotes表是否有created_by字段
        cur.execute("SHOW COLUMNS FROM quotes LIKE 'created_by'")
        if not cur.fetchone():
            # 添加created_by字段
            logger.info("向quotes表添加created_by字段...")
            cur.execute("ALTER TABLE quotes ADD COLUMN created_by INT")
            logger.info("成功添加created_by字段到quotes表")
        else:
            logger.info("quotes表已有created_by字段")
        
        db.commit()
    
    logger.info("数据库初始化完成")

# 添加一个路由，用于修复文件映射问题
@app.route('/api/fix-file-mappings', methods=['POST'])
@token_required
def fix_file_mappings():
    user_id = request.user.get('user_id')
    user_role = request.user.get('role')
    logger.info(f"用户 {user_id}({user_role}) 请求修复文件映射")
    
    try:
        with db.cursor() as cur:
            # 记录修复前的状态
            cur.execute("SELECT COUNT(*) as count FROM project_file_mappings")
            before_count = cur.fetchone()['count']
            logger.info(f"修复前有 {before_count} 个文件映射")
            
            # 1. 检查project_files表是否有files字段
            cur.execute("SHOW COLUMNS FROM project_files LIKE 'files'")
            has_files_column = cur.fetchone() is not None
            logger.info(f"project_files表是否有files列: {has_files_column}")
            
            if not has_files_column:
                logger.info("向project_files表添加files列...")
                cur.execute("ALTER TABLE project_files ADD COLUMN files TEXT AFTER notes")
                db.commit()
                logger.info("files列添加成功")
            
            # 2. 查找所有可能缺少映射的文件
            logger.info("检查当前已上传文件的映射状态...")
            cur.execute("""
                SELECT f.id, f.originalName, f.uploaded_by,
                       COUNT(pfm.id) as mapping_count
                FROM files f
                LEFT JOIN project_file_mappings pfm ON f.id = pfm.file_id
                WHERE f.isDeleted = FALSE
                GROUP BY f.id
                HAVING mapping_count = 0
                LIMIT 100
            """)
            unmapped_files = cur.fetchall()
            
            if not unmapped_files:
                logger.info("没有找到未映射的文件")
            else:
                logger.info(f"找到 {len(unmapped_files)} 个未映射的文件")
                
                # 按上传者分组文件
                files_by_uploader = {}
                for file in unmapped_files:
                    uploader_id = file['uploaded_by']
                    if uploader_id not in files_by_uploader:
                        files_by_uploader[uploader_id] = []
                    files_by_uploader[uploader_id].append(file)
                
                # 为每个上传者查找相关项目并创建映射
                fixed_count = 0
                for uploader_id, files in files_by_uploader.items():
                    logger.info(f"处理上传者 {uploader_id} 的 {len(files)} 个文件")
                    
                    # 获取该用户的项目
                    cur.execute("""
                        SELECT id, projectName 
                        FROM projectname 
                        WHERE created_by = %s OR projectManager = 'Yizhuo Xiang'
                        ORDER BY createTime DESC
                        LIMIT 5
                    """, (uploader_id,))
                    
                    projects = cur.fetchall()
                    if not projects:
                        logger.info(f"用户 {uploader_id} 没有关联的项目")
                        continue
                    
                    logger.info(f"找到 {len(projects)} 个相关项目")
                    
                    # 获取最近的项目
                    latest_project = projects[0]
                    project_id = latest_project['id']
                    
                    # 检查该项目的项目文件
                    cur.execute("""
                        SELECT id, fileType, notes, files
                        FROM project_files
                        WHERE projectId = %s
                        ORDER BY uploadTime DESC
                        LIMIT 1
                    """, (project_id,))
                    
                    project_file_record = cur.fetchone()
                    project_file_id = None
                    
                    # 如果项目已有项目文件记录，使用它；否则创建新的
                    if project_file_record:
                        project_file_id = project_file_record['id']
                        logger.info(f"使用现有项目文件记录 ID: {project_file_id}")
                        
                        # 更新files字段
                        existing_files = project_file_record['files'] or ""
                        file_names = [f['originalName'] for f in files]
                        new_files = ", ".join(file_names)
                        
                        if existing_files:
                            updated_files = f"{existing_files}, {new_files}"
                        else:
                            updated_files = new_files
                        
                        cur.execute("""
                            UPDATE project_files 
                            SET files = %s
                            WHERE id = %s
                        """, (updated_files, project_file_id))
                        logger.info(f"更新项目文件记录的files字段: {updated_files}")
                    else:
                        # 创建新的项目文件记录
                        file_names = [f['originalName'] for f in files]
                        files_str = ", ".join(file_names)
                        
                        cur.execute("""
                            INSERT INTO project_files (
                                projectId, fileType, notes, files, uploadTime, created_by
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            project_id, 'source', '自动修复创建的文件组 / Auto-fixed file group', 
                            files_str, datetime.now(), uploader_id
                        ))
                        db.commit()
                        project_file_id = cur.lastrowid
                        logger.info(f"创建新项目文件记录，ID: {project_file_id}")
                    
                    # 为每个文件创建映射
                    for file in files:
                        try:
                            # 检查映射是否已存在
                            cur.execute("""
                                SELECT id FROM project_file_mappings
                                WHERE project_file_id = %s AND file_id = %s
                            """, (project_file_id, file['id']))
                            
                            if cur.fetchone():
                                logger.info(f"映射已存在: 项目文件ID {project_file_id} -> 文件ID {file['id']}")
                                continue
                            
                            # 创建映射
                            cur.execute("""
                                INSERT INTO project_file_mappings (project_file_id, file_id)
                                VALUES (%s, %s)
                            """, (project_file_id, file['id']))
                            
                            logger.info(f"创建映射: 项目文件ID {project_file_id} -> 文件ID {file['id']} (文件名: {file['originalName']})")
                            fixed_count += 1
                        except Exception as e:
                            logger.error(f"创建映射时出错: {str(e)}")
                    
                    # 每处理一批文件后提交一次事务
                    db.commit()
                    
                    # 短暂延迟，避免数据库负载过高
                    time.sleep(0.1)  
                
                logger.info(f"修复了 {fixed_count} 个文件映射")
            
            # 3. 检查项目文件表中的files字段，确保映射一致
            logger.info("检查project_files表中的files字段与映射的一致性...")
            cur.execute("""
                SELECT pf.id, pf.projectId, pf.files
                FROM project_files pf
                WHERE pf.files IS NOT NULL AND pf.files != ''
            """)
            
            project_files_with_files = cur.fetchall()
            logger.info(f"找到 {len(project_files_with_files)} 个含有files值的项目文件记录")
            
            files_fixed = 0
            for pf in project_files_with_files:
                project_file_id = pf['id']
                files_str = pf['files']
                
                if not files_str:
                    continue
                
                file_names = [name.strip() for name in files_str.split(',') if name.strip()]
                if not file_names:
                    continue
                
                logger.info(f"项目文件 {project_file_id} 的files字段包含 {len(file_names)} 个文件名")
                
                # 1. 查找已存在的映射
                cur.execute("""
                    SELECT pfm.file_id, f.originalName
                    FROM project_file_mappings pfm
                    JOIN files f ON pfm.file_id = f.id
                    WHERE pfm.project_file_id = %s
                """, (project_file_id,))
                
                existing_mappings = cur.fetchall()
                existing_file_names = [m['originalName'] for m in existing_mappings]
                
                # 2. 找出需要添加映射的文件名
                missing_file_names = [name for name in file_names if name not in existing_file_names]
                
                if not missing_file_names:
                    continue
                
                logger.info(f"项目文件 {project_file_id} 有 {len(missing_file_names)} 个文件名缺少映射")
                
                # 3. 查找匹配的文件
                placeholders = ','.join(['%s'] * len(missing_file_names))
                query = f"""
                    SELECT id, originalName 
                    FROM files 
                    WHERE originalName IN ({placeholders}) AND isDeleted = FALSE
                """
                cur.execute(query, missing_file_names)
                found_files = cur.fetchall()
                
                if not found_files:
                    continue
                
                logger.info(f"找到 {len(found_files)} 个匹配的文件")
                
                # 4. 创建映射
                for file in found_files:
                    try:
                        cur.execute("""
                            INSERT INTO project_file_mappings (project_file_id, file_id)
                            VALUES (%s, %s)
                        """, (project_file_id, file['id']))
                        
                        logger.info(f"创建映射: 项目文件ID {project_file_id} -> 文件ID {file['id']} (文件名: {file['originalName']})")
                        files_fixed += 1
                    except Exception as e:
                        logger.error(f"创建映射时出错: {str(e)}")
                
                # 每处理一个项目文件后提交一次
                db.commit()
            
            logger.info(f"从files字段修复了 {files_fixed} 个文件映射")
            
            # 记录修复后的状态
            cur.execute("SELECT COUNT(*) as count FROM project_file_mappings")
            after_count = cur.fetchone()['count']
            
            return jsonify({
                "status": "success",
                "before_count": before_count,
                "after_count": after_count,
                "difference": after_count - before_count
            })
        
    except Exception as e:
        logger.error(f"修复文件映射时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    logger.info("==========================================")
    logger.info("LingoFlows本地化管理系统正在启动...")
    logger.info("==========================================")
    logger.info("正在初始化数据库...")
    init_db()  # 初始化数据库
    logger.info("数据库初始化完成")
    logger.info("==========================================")
    logger.info("系统启动成功，监听端口5000")
    logger.info("==========================================")
    app.run(debug=True)