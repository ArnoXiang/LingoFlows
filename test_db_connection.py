# test_db_connection.py
import unittest
from flask import Flask
from flask_mysqldb import MySQL

class TestDatabaseConnection(unittest.TestCase):
    def setUp(self):
        # 创建 Flask 应用实例
        self.app = Flask(__name__)
        self.app.config['MYSQL_HOST'] = 'localhost'
        self.app.config['MYSQL_USER'] = 'your_username'  # 替换为您的数据库用户名
        self.app.config['MYSQL_PASSWORD'] = 'your_password'  # 替换为您的数据库密码
        self.app.config['MYSQL_DB'] = 'translation_management'
        
        # 初始化 MySQL
        self.mysql = MySQL(self.app)

    def test_connection(self):
        with self.app.app_context():
            try:
                # 尝试获取数据库连接
                cur = self.mysql.connection.cursor()
                cur.execute('SELECT 1')
                result = cur.fetchone()
                cur.close()
                self.assertIsNotNone(result, "Failed to connect to the database.")
            except Exception as e:
                self.fail(f"Database connection test failed: {e}")

if __name__ == '__main__':
    unittest.main()