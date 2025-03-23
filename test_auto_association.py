import requests
import json
import time
from datetime import datetime, timedelta
import pymysql

BASE_URL = "http://localhost:5000/api"

def login():
    """登录系统获取token"""
    login_data = {
        "username": "bo1",
        "password": "bo123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        user_id = response.json().get('user_id')
        
        # 如果user_id为None，使用默认值2（bo1）
        if user_id is None:
            user_id = 2
            print(f"服务器未返回用户ID，使用默认ID: {user_id}")
        else:
            print(f"登录成功，用户ID: {user_id}")
            
        return token, user_id
    else:
        print(f"登录失败: {response.text}")
        return None, None

def get_file_ids(user_id=2):
    """获取最近上传的文件ID"""
    # 连接数据库直接查询
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='l10n_management',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, originalName, uploadTime 
                FROM files 
                WHERE uploaded_by = %s AND isDeleted = FALSE
                ORDER BY id DESC
                LIMIT 2
            """, (user_id,))
            
            files = cursor.fetchall()
            
            if files:
                file_ids = [file['id'] for file in files]
                print(f"找到最近的文件:")
                for file in files:
                    print(f"  ID: {file['id']}, 名称: {file['originalName']}, 上传时间: {file['uploadTime']}")
                return file_ids
            else:
                print("未找到任何文件")
                return []
    finally:
        conn.close()

def create_request(file_ids, user_id=2):
    """创建包含文件的请求"""
    token, _ = login()
    
    if not token:
        print("无法创建请求，登录失败")
        return None
        
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    request_url = f"{BASE_URL}/requests"
    
    # 设置预期交付日期为7天后
    expected_delivery_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    request_data = {
        "requestName": "自动测试请求-修复后",
        "requestBackground": "这是一个测试请求，用于测试修复后的文件自动关联功能",
        "sourceLanguage": "en",
        "targetLanguages": ["zh", "ja"],
        "wordCount": 1200,
        "additionalRequirements": ["lqa"],
        "expectedDeliveryDate": expected_delivery_date,
        "fileIds": file_ids  # 包含文件ID
    }
    
    print(f"准备创建请求，数据: {json.dumps(request_data, ensure_ascii=False)}")
    
    response = requests.post(request_url, json=request_data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"请求创建成功，ID: {result.get('id')}, 项目ID: {result.get('project_id')}")
        
        # 检查项目文件关联是否成功
        check_project_files(result.get('project_id'), token)
        return result
    else:
        print(f"创建请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None

def check_project_files(project_id, token=None):
    """检查项目文件关联情况"""
    if not project_id:
        print("无法检查项目文件，项目ID为空")
        return
    
    # 如果没有提供token，重新登录    
    if not token:
        token, _ = login()
        if not token:
            print("登录失败，无法检查项目文件")
            return
            
    project_files_url = f"{BASE_URL}/project-files/{project_id}"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(project_files_url, headers=headers)
        
        if response.status_code == 200:
            files = response.json()
            if files:
                print(f"\n获取到项目 {project_id} 的文件组，共 {len(files)} 个文件组:")
                
                for file_group in files:
                    print(f"文件组ID: {file_group['id']}, 类型: {file_group['fileType']}, 描述: {file_group['description']}")
                    
                    for f in file_group.get('fileList', []):
                        print(f"  - 文件ID: {f['id']}, 名称: {f['name']}")
            else:
                print(f"项目 {project_id} 没有关联的文件")
        else:
            print(f"获取项目文件失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"检查项目文件时出错: {str(e)}")

def check_db_file_association(project_id):
    """直接从数据库检查文件关联"""
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='l10n_management',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            print(f"\n===== 数据库中项目 {project_id} 的文件关联 =====")
            
            # 检查项目文件表
            cursor.execute("""
                SELECT id, projectId, fileType, notes, created_by
                FROM project_files
                WHERE projectId = %s
            """, (project_id,))
            
            project_files = cursor.fetchall()
            
            if project_files:
                print(f"找到 {len(project_files)} 个项目文件组:")
                
                for pf in project_files:
                    print(f"项目文件ID: {pf['id']}, 项目ID: {pf['projectId']}, 类型: {pf['fileType']}, 创建者: {pf['created_by']}")
                    
                    # 检查项目文件映射
                    cursor.execute("""
                        SELECT pfm.id, pfm.file_id, f.originalName
                        FROM project_file_mappings pfm
                        JOIN files f ON pfm.file_id = f.id
                        WHERE pfm.project_file_id = %s
                    """, (pf['id'],))
                    
                    mappings = cursor.fetchall()
                    
                    if mappings:
                        print(f"  关联的文件 ({len(mappings)} 个):")
                        for m in mappings:
                            print(f"  - 映射ID: {m['id']}, 文件ID: {m['file_id']}, 文件名: {m['originalName']}")
                    else:
                        print("  没有关联的文件")
            else:
                print(f"项目 {project_id} 没有任何项目文件记录")
                
            # 检查请求表
            cursor.execute("""
                SELECT id, requestName, project_id
                FROM requests
                WHERE project_id = %s
            """, (project_id,))
            
            requests = cursor.fetchall()
            
            if requests:
                print(f"\n关联的请求:")
                for req in requests:
                    print(f"请求ID: {req['id']}, 名称: {req['requestName']}, 项目ID: {req['project_id']}")
            else:
                print(f"\n没有找到与项目 {project_id} 关联的请求")
    finally:
        conn.close()

def main():
    # 1. 登录
    token, user_id = login()
    if not token:
        return
    
    # 2. 获取最近上传的文件ID
    file_ids = get_file_ids(user_id)
    if not file_ids:
        print("未找到文件，无法继续测试")
        return
    
    # 3. 创建请求并关联文件
    request_result = create_request(file_ids, user_id)
    
    if request_result:
        project_id = request_result.get('project_id')
        
        if project_id:
            # 4. 从数据库检查文件关联
            time.sleep(2)  # 稍等片刻确保数据已更新
            check_db_file_association(project_id)

if __name__ == "__main__":
    main() 