import pymysql
import json
from datetime import datetime

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',  
    password='root',  
    database='l10n_management',
    cursorclass=pymysql.cursors.DictCursor
)

# 自定义JSON序列化函数，处理日期对象
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

try:
    with conn.cursor() as cursor:
        print("\n============ 最近上传的文件 ============")
        cursor.execute("""
            SELECT id, filename, originalName, uploaded_by, uploadTime, isDeleted
            FROM files 
            ORDER BY id DESC
            LIMIT 10
        """)
        files = cursor.fetchall()

        for file in files:
            print(f"ID: {file['id']} | 名称: {file['originalName']} | 上传者: {file['uploaded_by']} | 删除: {file['isDeleted']}")
            
            # 检查此文件是否关联到任何项目文件
            cursor.execute("""
                SELECT pfm.project_file_id, pf.projectId, pf.fileType, pn.projectName
                FROM project_file_mappings pfm
                JOIN project_files pf ON pfm.project_file_id = pf.id
                JOIN projectname pn ON pf.projectId = pn.id
                WHERE pfm.file_id = %s
            """, (file['id'],))
            
            associations = cursor.fetchall()
            if associations:
                print(f"  关联的项目:")
                for assoc in associations:
                    print(f"  - 项目: {assoc['projectName']} (ID: {assoc['projectId']}) | 项目文件ID: {assoc['project_file_id']} | 类型: {assoc['fileType']}")
            else:
                print("  没有关联到任何项目")
        
        print("\n============ 最近创建的项目 ============")
        cursor.execute("""
            SELECT id, projectName, projectStatus, createTime, created_by
            FROM projectname 
            ORDER BY id DESC
            LIMIT 5
        """)
        projects = cursor.fetchall()

        for project in projects:
            print(f"ID: {project['id']} | 名称: {project['projectName']} | 状态: {project['projectStatus']} | 创建者: {project['created_by']}")
            
            # 查询项目的文件组
            cursor.execute("""
                SELECT id, fileType, notes, files, created_by
                FROM project_files
                WHERE projectId = %s
            """, (project['id'],))
            
            project_files = cursor.fetchall()
            if project_files:
                print(f"  项目文件组:")
                for pf in project_files:
                    print(f"  - ID: {pf['id']} | 类型: {pf['fileType']} | 描述: {pf['notes']} | 创建者: {pf['created_by']}")
                    
                    # 查询关联的原始文件
                    cursor.execute("""
                        SELECT f.id, f.originalName
                        FROM files f
                        JOIN project_file_mappings pfm ON f.id = pfm.file_id
                        WHERE pfm.project_file_id = %s
                    """, (pf['id'],))
                    
                    mapped_files = cursor.fetchall()
                    if mapped_files:
                        print(f"    关联的文件:")
                        for f in mapped_files:
                            print(f"    - ID: {f['id']} | 名称: {f['originalName']}")
                    else:
                        print("    没有关联的文件")
            else:
                print("  没有项目文件组")
                
        # 检查前端提交请求的文件ID
        print("\n============ 最近的请求 ============")
        cursor.execute("""
            SELECT id, requestName, project_id, createTime, created_by
            FROM requests
            ORDER BY id DESC
            LIMIT 5
        """)
        
        requests = cursor.fetchall()
        for req in requests:
            print(f"ID: {req['id']} | 名称: {req['requestName']} | 项目ID: {req['project_id']} | 创建者: {req['created_by']}")
            
            if req['project_id']:
                # 查询关联的项目的文件
                cursor.execute("""
                    SELECT f.id, f.originalName
                    FROM files f
                    JOIN project_file_mappings pfm ON f.id = pfm.file_id
                    JOIN project_files pf ON pfm.project_file_id = pf.id
                    WHERE pf.projectId = %s
                """, (req['project_id'],))
                
                files = cursor.fetchall()
                if files:
                    print(f"  关联的文件:")
                    for f in files:
                        print(f"  - ID: {f['id']} | 名称: {f['originalName']}")
                else:
                    print("  没有关联的文件")
            else:
                print("  没有关联的项目")

finally:
    conn.close()

print("\n检查完成! 修复验证：请检查上面的输出，确认最近创建的请求应该有关联的文件。") 