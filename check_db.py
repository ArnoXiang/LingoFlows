import pymysql
import json

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    database='l10n_management',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        print("查询项目表")
        cursor.execute('SELECT id, projectName FROM projectname')
        projects = cursor.fetchall()
        print(json.dumps(projects, indent=2, default=str))
        
        print("\n查询文件表")
        cursor.execute('SELECT id, filename, originalName FROM files WHERE isDeleted = FALSE')
        files = cursor.fetchall()
        print(json.dumps(files, indent=2, default=str))
        
        print("\n查询项目文件表")
        cursor.execute('SELECT id, projectId, fileType FROM project_files')
        project_files = cursor.fetchall()
        print(json.dumps(project_files, indent=2, default=str))
        
        print("\n查询项目文件映射表")
        cursor.execute('SELECT id, project_file_id, file_id FROM project_file_mappings')
        mappings = cursor.fetchall()
        print(json.dumps(mappings, indent=2, default=str))
        
        # 关键信息：检查项目ID为最近项目的文件关联
        print("\n项目文件关联检查")
        cursor.execute('''
            SELECT 
                p.id as project_id,
                p.projectName as project_name,
                pf.id as project_file_id,
                f.id as file_id,
                f.originalName as original_name
            FROM projectname p
            LEFT JOIN project_files pf ON p.id = pf.projectId
            LEFT JOIN project_file_mappings pfm ON pf.id = pfm.project_file_id
            LEFT JOIN files f ON pfm.file_id = f.id
            WHERE p.id > 15
            ORDER BY p.id DESC
        ''')
        related_files = cursor.fetchall()
        print(json.dumps(related_files, indent=2, default=str))
        
finally:
    conn.close() 