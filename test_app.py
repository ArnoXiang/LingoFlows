import unittest
from app import app  # 确保导入您的 Flask 应用

class ChatApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()  # 创建测试客户端
        self.app.testing = True

    def test_chat_response(self):
        # 模拟 POST 请求
        response = self.app.post('/api/chat', json={'message': 'Hello, world!'})
        self.assertEqual(response.status_code, 200)  # 检查状态码
        self.assertIn('response', response.get_json())  # 检查返回的 JSON 中是否有 'response' 键

if __name__ == '__main__':
    unittest.main()