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
    
    # 查询用户表
    with db.cursor() as cur:
        # 检查users表是否存在
        cur.execute("SHOW TABLES LIKE 'users'")
        if cur.fetchone():
            print("Users table exists! Dropping it...")
            
            # 删除旧的用户表
            cur.execute("DROP TABLE users")
            db.commit()
            print("Users table dropped successfully!")
        
        # 创建新的用户表
        print("Creating new users table...")
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
        print("Adding default users...")
        cur.execute("""
            INSERT INTO users (username, password, name, role, email)
            VALUES 
            ('admin', 'admin123', 'Admin User', 'LM', 'admin@example.com'),
            ('bo1', 'bo123', 'Business Owner 1', 'BO', 'bo1@example.com'),
            ('bo2', 'bo123', 'Business Owner 2', 'BO', 'bo2@example.com')
        """)
        
        db.commit()
        print("Default users added successfully!")
        
        # 查询新的用户
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        
        if users:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"ID: {user['id']}, Username: {user['username']}, Password: {user['password']}, Role: {user['role']}")
        else:
            print("No users found in the table.")
    
    # 关闭数据库连接
    db.close()
    
except Exception as e:
    print(f"Error: {e}") 