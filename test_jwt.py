import jwt
import sys

def decode_jwt(token):
    try:
        # 使用与app.py中相同的密钥
        secret_key = 'lingoflows_secret_key'
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        print("JWT解码成功！")
        print("Payload:", payload)
        print("User ID:", payload.get('user_id'))
        print("Username:", payload.get('username'))
        print("Role:", payload.get('role'))
        print("Expiration:", payload.get('exp'))
        return payload
    except jwt.ExpiredSignatureError:
        print("错误：JWT令牌已过期")
        return None
    except jwt.InvalidTokenError as e:
        print(f"错误：无效的JWT令牌 - {e}")
        return None
    except Exception as e:
        print(f"错误：{e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        token = sys.argv[1]
        decode_jwt(token)
    else:
        print("请提供JWT令牌作为命令行参数")
        print("用法：python test_jwt.py <token>") 