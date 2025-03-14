import requests
import json

def login_and_get_projects():
    # 登录获取令牌
    login_url = 'http://localhost:5000/api/login'
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        print("尝试登录...")
        login_response = requests.post(login_url, json=login_data)
        login_response.raise_for_status()  # 如果请求失败，抛出异常
        
        login_result = login_response.json()
        token = login_result.get('token')
        user = login_result.get('user')
        
        if not token:
            print("错误：登录成功但未获取到令牌")
            return
        
        print("登录成功！")
        print(f"用户信息: ID={user.get('id')}, 用户名={user.get('username')}, 角色={user.get('role')}")
        
        # 使用令牌获取项目
        projects_url = 'http://localhost:5000/api/projects'
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        print("\n尝试获取项目...")
        projects_response = requests.get(projects_url, headers=headers)
        projects_response.raise_for_status()  # 如果请求失败，抛出异常
        
        projects = projects_response.json()
        
        print(f"成功获取到 {len(projects)} 个项目:")
        for project in projects:
            print(f"ID: {project.get('id')}, 名称: {project.get('projectName')}, 状态: {project.get('projectStatus')}, 创建者: {project.get('created_by')}")
        
        return projects
    
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                error_data = e.response.json()
                print(f"服务器返回错误: {error_data}")
            except:
                print(f"服务器返回状态码: {e.response.status_code}")
                print(f"服务器返回内容: {e.response.text}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    login_and_get_projects() 