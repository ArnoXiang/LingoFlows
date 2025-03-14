import pymysql

try:
    # 连接数据库
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='l10n_management',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("Database connection successful!")
    
    # 查询项目表
    with db.cursor() as cur:
        # 检查项目表是否存在
        cur.execute("SHOW TABLES LIKE 'projectname'")
        if cur.fetchone():
            print("Projects table exists!")
            
            # 查询项目
            cur.execute("SELECT * FROM projectname")
            projects = cur.fetchall()
            
            if projects:
                print(f"Found {len(projects)} projects:")
                for project in projects:
                    print(f"ID: {project['id']}, Name: {project['projectName']}, Status: {project['projectStatus']}, Created By: {project['created_by']}")
                
                # 更新项目的created_by字段
                print("\nUpdating projects to set created_by to admin user (ID: 1)...")
                cur.execute("UPDATE projectname SET created_by = 1")
                db.commit()
                print("Projects updated successfully!")
                
                # 再次查询项目
                cur.execute("SELECT * FROM projectname")
                updated_projects = cur.fetchall()
                print("\nAfter update:")
                for project in updated_projects:
                    print(f"ID: {project['id']}, Name: {project['projectName']}, Status: {project['projectStatus']}, Created By: {project['created_by']}")
            else:
                print("No projects found in the table.")
        else:
            print("Projects table does not exist!")
    
    # 关闭数据库连接
    db.close()
    
except Exception as e:
    print(f"Error: {e}") 