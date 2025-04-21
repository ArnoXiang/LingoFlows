<template>
  <a-layout class="layout-demo">
    <a-layout-sider
      theme="dark"
      breakpoint="lg"
      :width="220"
      collapsible
      :collapsed="collapsed"
      @collapse="onCollapse"
    >
      <div class="logo-placeholder" @click="goToHome">
        <!-- 展开状态下的logo显示 -->
        <div class="logo-content" v-if="!collapsed">
          <div class="logo-icon">
            <IconLanguage />
          </div>
          <div class="logo-text">
            <span class="logo-name">Lingo<span class="logo-highlight">Flows</span></span>
            <span class="logo-tagline">Localization Platform</span>
          </div>
        </div>
        <!-- 折叠状态下的logo显示 -->
        <div class="logo-content-collapsed" v-else>
          <div class="logo-icon-collapsed">
            <IconLanguage />
          </div>
        </div>
      </div>
      <a-menu
        :defaultOpenKeys="['1']"
        :selectedKeys="[selectedMenuKey]"
        @menuItemClick="onClickMenuItem"
      >
        <!-- Home - 所有用户可见，包括未登录用户 -->
        <a-menu-item key="0">
          <IconHome />
          Home
        </a-menu-item>
        
        <!-- 本地化管理 - 根据权限显示子菜单 -->
        <a-sub-menu key="1" v-if="filteredMenuItems.some(item => item.startsWith('1_'))">
          <template #title>
            <span><IconApps />本地化管理 / L10n Management</span>
          </template>
          
          <!-- 请求管理 - 所有登录用户可见 -->
          <a-menu-item key="1_1" v-if="filteredMenuItems.includes('1_1')">
            请求管理 / Request Management
          </a-menu-item>
          
          <!-- 项目管理 - LM和BO可见 -->
          <a-menu-item key="1_2" v-if="filteredMenuItems.includes('1_2')">
            项目管理 / Project Management
          </a-menu-item>
          
          <!-- 财务管理 - 仅LM和FT可见 -->
          <a-menu-item key="1_3" v-if="filteredMenuItems.includes('1_3')">
            财务管理 / Financial Management
          </a-menu-item>
        </a-sub-menu>
        
        <!-- 系统设置 - 仅LM可见 -->
        <a-menu-item key="2" v-if="filteredMenuItems.includes('2')">
          <IconSettings />
          系统设置 / Settings
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header>
        <div class="header-content">
          <div class="header-left">
            <!-- 左侧内容已移除 -->
          </div>
          
          <div class="header-right">
            <!-- 登录/登出按钮 -->
            <a-button 
              v-if="!isLoggedIn" 
              type="primary" 
              @click="toggleLogin" 
              class="login-button"
            >
              登录 / Login
            </a-button>
            <a-button 
              v-else 
              type="outline" 
              @click="toggleLogin" 
              class="logout-button"
            >
              登出 / Logout
            </a-button>
            
            <div class="user-avatar">
              <!-- 未登录状态显示空白头像 -->
              <a-avatar v-if="!isLoggedIn" :style="{ backgroundColor: '#f0f2f5', color: '#ccc' }">
                <template #icon><IconUser /></template>
              </a-avatar>
              
              <!-- 登录状态下显示用户信息 -->
              <a-dropdown v-else trigger="click">
                <a-avatar :style="{ backgroundColor: '#3c9ae8' }">
                  {{ userName.charAt(0).toUpperCase() }}
                </a-avatar>
                <template #content>
                  <a-doption>
                    <div class="user-dropdown-item">
                      <span>{{ userName }}</span>
                      <span class="user-role">{{ userRole === 'LM' ? '本地化经理 / LM' : userRole === 'FT' ? '财务团队 / FT' : '业务负责人 / BO' }}</span>
                    </div>
                  </a-doption>
                </template>
              </a-dropdown>
            </div>
          </div>
        </div>
      </a-layout-header>
      <a-layout style="padding: 0 24px">
        <a-breadcrumb :style="{ margin: '16px 0' }">
          <a-breadcrumb-item>首页 / Home</a-breadcrumb-item>
          <a-breadcrumb-item>{{ getBreadcrumbText() }}</a-breadcrumb-item>
        </a-breadcrumb>
        <a-layout-content style="color: black;">
          <!-- Home页面 -->
          <div v-if="currentPage === 'home'" class="home-container">
            <h1 class="home-title">Welcome to LingoFlows</h1>
            <h2 class="home-subtitle">Collaborative Localization Management Platform</h2>
            
            <div class="home-content">
              <div class="home-section">
                <h3>About LingoFlows</h3>
                <p>
                  LingoFlows is a comprehensive localization management platform designed to streamline the translation 
                  and localization process for businesses of all sizes. Our platform provides powerful tools for request 
                  management, project tracking, and financial reporting in a collaborative environment.
                </p>
              </div>
              
              <div class="home-section">
                <h3>Key Features</h3>
                <ul>
                  <li><strong>Request Management:</strong> Submit and track localization requests</li>
                  <li><strong>Project Management:</strong> Monitor localization projects from start to finish</li>
                  <li><strong>Financial Management:</strong> Track costs, quotes, and invoices</li>
                  <li><strong>Team Collaboration:</strong> Connect business owners, project managers, LSPs, and procurement teams</li>
                </ul>
              </div>
              
              <div class="home-section home-login-info">
                <h3>Getting Started</h3>
                <p>To access the platform features, please log in using the credentials provided by your administrator.</p>
                
                <div class="demo-accounts">
                  <h4>Demo Accounts</h4>
                  <div class="account-card">
                    <div class="account-type">Project Manager (PM)</div>
                    <div class="account-creds">
                      <span>Username: admin</span>
                      <span>Password: admin123</span>
                    </div>
                    <div class="account-desc">Full access to all platform features</div>
                  </div>
                  
                  <div class="account-card">
                    <div class="account-type">Business Owner (BO)</div>
                    <div class="account-creds">
                      <span>Username: bo</span>
                      <span>Password: bo123</span>
                    </div>
                    <div class="account-desc">Access to request and personal project management</div>
                  </div>
                  
                  <div class="account-card">
                    <div class="account-type">Finance Team (FT)</div>
                    <div class="account-creds">
                      <span>Username: ft</span>
                      <span>Password: ft123</span>
                    </div>
                    <div class="account-desc">Access to financial reports, quotes, and invoicing</div>
                  </div>
                </div>
              </div>
              
              <div class="home-section">
                <h3>Contact Support</h3>
                <p>
                  For assistance with the platform, please contact our support team at:
                  <a href="mailto:support@lingoflows.com">support@lingoflows.com</a>
                </p>
              </div>
            </div>
          </div>
          
          <!-- 请求管理页面 -->
          <div v-if="currentPage === 'request_management'">
            <RequestForm />
          </div>
          
          <!-- 项目管理页面 -->
          <div v-if="currentPage === 'project_management'">
            <ProjectManagement :userRole="userRole" :userId="userId" :projectData="projectData" />
          </div>
          
          <!-- 财务管理页面 -->
          <div v-if="currentPage === 'financial_management'">
            <FinancialManagement :userRole="userRole" :userId="userId" />
          </div>
          
          <!-- 系统设置页面 -->
          <div v-if="currentPage === 'settings'">
            <h1>系统设置 / System Settings</h1>
            <p>系统设置页面正在开发中... / System settings page is under development...</p>
          </div>
        </a-layout-content>
        <a-layout-footer>
          <div class="footer-content">
            <p style="color: black;">© 2025 LingoFlows - Collaborative Localization Management Platform</p>
            <p style="color: black;">Developed by Yizhuo Xiang</p>
          </div>
        </a-layout-footer>
      </a-layout>
    </a-layout>

    <!-- 登录弹窗 -->
    <a-modal v-model:visible="visible" title="登录 / Login" @cancel="handleCancel" @ok="handleBeforeOk" :ok-loading="loginLoading">
      <a-form :model="form">
        <a-form-item field="username" label="用户名 / Username">
          <a-input v-model="form.username" />
        </a-form-item>
        <a-form-item field="password" label="密码 / Password">
          <a-input type="password" v-model="form.password" />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-space>
          <a-button @click="handleCancel">取消 / Cancel</a-button>
          <a-button type="primary" @click="handleBeforeOk" :loading="loginLoading">登录 / Login</a-button>
        </a-space>
      </template>
    </a-modal>

    <!-- 返回顶部按钮 -->
    <a-back-top :style="{ position: 'absolute', right: '20px', bottom: '20px' }" />
  </a-layout>
</template>

<script>
import { defineComponent, ref, reactive, computed, watch } from 'vue';
import { Message } from '@arco-design/web-vue';
import {
  IconHome,
  IconCalendar,
  IconSettings,
  IconApps,
  IconEdit,
  IconExport,
  IconLanguage,
  IconUser,
} from '@arco-design/web-vue/es/icon';
import { Avatar } from '@arco-design/web-vue';
import RequestForm from './components/RequestForm.vue';
import ProjectManagement from './components/ProjectManagement.vue';
import FinancialManagement from './components/FinancialManagement.vue';
import axios from 'axios';

export default defineComponent({
  components: {
    IconHome,
    IconCalendar,
    IconSettings,
    IconApps,
    IconEdit,
    IconExport,
    IconLanguage,
    IconUser,
    Avatar,
    RequestForm,
    ProjectManagement,
    FinancialManagement,
  },
  setup() {
    const collapsed = ref(false);
    const isLoggedIn = ref(false);
    const userName = ref('');
    const userRole = ref('');
    const userId = ref(null);
    const visible = ref(false);
    const form = reactive({
      username: '',
      password: ''
    });
    const currentPage = ref('home'); // 将初始值设置为'home'
    const selectedMenuKey = ref('0'); // 将初始选中菜单项设置为'0'
    const columns = ref([
      { title: 'Project Name', dataIndex: 'projectName', key: 'projectName' },
      { title: 'Project Status', dataIndex: 'projectStatus', key: 'projectStatus' },
      { title: 'Request Name', dataIndex: 'requestName', key: 'requestName' },
      { title: 'Project Manager', dataIndex: 'projectManager', key: 'projectManager' },
      { title: 'Create Time', dataIndex: 'createTime', key: 'createTime' },
      { title: 'Task - Translation', dataIndex: 'taskTranslation', key: 'taskTranslation' },
      { title: 'Task - LQA', dataIndex: 'taskLQA', key: 'taskLQA' },
      { title: 'Task - Translation Update', dataIndex: 'taskTranslationUpdate', key: 'taskTranslationUpdate' },
      { title: 'Task - LQA Report Finalization', dataIndex: 'taskLQAReportFinalization', key: 'taskLQAReportFinalization' },
    ]);
    const projectData = ref([]);
    const loginLoading = ref(false);

    // 检查用户是否有权限访问某个页面
    const hasPermission = (page) => {
      // 所有用户都可以访问Home页面
      if (page === 'home') return true;
      
      // 未登录用户只能访问Home页面
      if (!isLoggedIn.value) return false;
      
      // 所有用户都可以访问的页面
      const commonPages = ['request_management'];
      if (commonPages.includes(page)) return true;
      
      // LM可以访问所有页面
      if (userRole.value === 'LM') return true;
      
      // BO只能访问特定页面
      if (userRole.value === 'BO') {
        const boPages = ['request_management', 'project_management'];
        return boPages.includes(page);
      }
      
      // FT可以访问财务管理页面
      if (userRole.value === 'FT') {
        const ftPages = ['financial_management'];
        return ftPages.includes(page);
      }
      
      return false;
    };

    // 根据用户角色过滤菜单项
    const filteredMenuItems = computed(() => {
      if (!isLoggedIn.value) {
        // 未登录用户只能看到Home
        return [];
      }
      
      if (userRole.value === 'LM') {
        // LM可以看到所有菜单项
        return ['1_1', '1_2', '1_3', '2'];
      }
      
      if (userRole.value === 'BO') {
        // BO只能看到请求管理和项目管理
        return ['1_1', '1_2'];
      }
      
      if (userRole.value === 'FT') {
        // FT只能看到财务管理
        return ['1_3'];
      }
      
      return [];
    });

    const onCollapse = (val) => {
      collapsed.value = val;
    };

    const toggleLogin = () => {
      if (!isLoggedIn.value) {
        visible.value = true;
      } else {
        // 登出
        isLoggedIn.value = false;
        userName.value = '';
        userRole.value = '';
        userId.value = null;
        
        // 清除令牌
        localStorage.removeItem('token');
        axios.defaults.headers.common['Authorization'] = '';
        
        // 重定向到Home页面
        currentPage.value = 'home';
        selectedMenuKey.value = '0';
        
        Message.info({
          content: '已退出登录 / Logged out',
          duration: 2000,
        });
      }
    };

    // 检查本地存储的令牌并自动登录
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // 设置默认请求头
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // 获取当前用户信息
          const response = await axios.get('http://localhost:5000/api/users/current');
          
          // 更新用户信息
          userId.value = Number(response.data.id); // 确保转换为数字类型
          userName.value = response.data.name;
          userRole.value = response.data.role;
          isLoggedIn.value = true;
          
          Message.success({
            content: '自动登录成功 / Auto login successful',
            duration: 2000,
          });
          
          // 自动登录成功后获取项目数据
          fetchProjectData();
          
          // 如果是FT角色，直接进入财务管理页面
          if (response.data.role === 'FT') {
            currentPage.value = 'financial_management';
            selectedMenuKey.value = '1_3';
          } else {
            // 其他角色默认进入请求管理页面
            currentPage.value = 'request_management';
            selectedMenuKey.value = '1_1';
          }
        } catch (error) {
          console.error('自动登录失败:', error);
          // 清除无效令牌
          localStorage.removeItem('token');
          axios.defaults.headers.common['Authorization'] = '';
          // 确保未登录用户回到Home页面
          currentPage.value = 'home';
          selectedMenuKey.value = '0';
        }
      }
    };

    // 页面加载时检查认证状态
    checkAuth();

    const handleBeforeOk = async (done) => {
      if (!form.username || !form.password) {
        Message.error('请输入用户名和密码 / Please enter username and password');
        return;
      }
      
      loginLoading.value = true;
      
      try {
        // 调用登录API
        const response = await axios.post('http://localhost:5000/api/login', {
          username: form.username,
          password: form.password
        });
        
        // 保存令牌到本地存储
        const token = response.data.token;
        localStorage.setItem('token', token);
        
        // 设置默认请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // 更新用户信息
        const user = response.data.user;
        userId.value = Number(user.id); // 确保转换为数字类型
        userName.value = user.name;
        userRole.value = user.role;
        isLoggedIn.value = true;
        
        // 清空表单并关闭弹窗
        form.username = '';
        form.password = '';
        visible.value = false;
        
        Message.success({
          content: '登录成功 / Login successful',
          duration: 2000,
        });
        
        // 登录成功后获取项目数据
        fetchProjectData();
        
        // 如果是FT角色，直接进入财务管理页面
        if (user.role === 'FT') {
          currentPage.value = 'financial_management';
          selectedMenuKey.value = '1_3';
        } else {
          // 其他角色默认进入请求管理页面
          currentPage.value = 'request_management';
          selectedMenuKey.value = '1_1';
        }
      } catch (error) {
        console.error('登录失败:', error);
        
        // 构建错误消息
        let errorMsg = '登录失败 / Login failed';
        
        if (error.response) {
          if (error.response.status === 401) {
            errorMsg = '用户名或密码错误 / Invalid username or password';
          } else if (error.response.status >= 500) {
            errorMsg = '服务器错误，请稍后再试 / Server error, please try again later';
          } else if (error.response.data && error.response.data.error) {
            errorMsg = error.response.data.error;
          }
        } else if (error.request) {
          errorMsg = '无法连接到服务器，请检查网络 / Cannot connect to server, please check your network';
        }
        
        Message.error({
          content: errorMsg,
          duration: 3000,
        });
      } finally {
        loginLoading.value = false;
      }
    };

    const handleCancel = () => {
      visible.value = false;
      form.username = '';
      form.password = '';
    };

    const onClickMenuItem = (key) => {
      selectedMenuKey.value = key; // 更新选中的菜单项
      
      // 根据菜单项切换页面
      let targetPage = '';
      
      switch (key) {
        case '0':
          targetPage = 'home';
          break;
        case '1_1':
          targetPage = 'request_management'; 
          break;
        case '1_2':
          targetPage = 'project_management'; 
          break;
        case '1_3':
          targetPage = 'financial_management'; 
          break;
        case '2':
          targetPage = 'settings'; 
          break;
        default:
          targetPage = 'home';
      }
      
      // 检查权限
      if (hasPermission(targetPage)) {
        currentPage.value = targetPage;
        Message.info({ content: `You select ${key}`, showIcon: true });
        
        // 如果切换到项目管理页面，刷新项目数据
        if (targetPage === 'project_management' && isLoggedIn.value) {
          console.log('切换到项目管理页面，刷新项目数据');
          fetchProjectData();
        }
      } else {
        Message.error('您没有权限访问此页面 / You do not have permission to access this page');
      }
    };
    
    const getBreadcrumbText = () => {
      switch (currentPage.value) {
        case 'home':
          return 'Home';
        case 'request_management':
          return '请求管理 / Request Management';
        case 'project_management':
          return '项目管理 / Project Management';
        case 'financial_management':
          return '财务管理 / Financial Management';
        case 'settings':
          return '系统设置 / Settings';
        default:
          return '';
      }
    };

    const fetchProjectData = async () => {
      try {
        // 获取存储的令牌
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('未找到令牌，无法获取项目数据');
          return;
        }
        
        // 设置请求头
        const headers = {
          'Authorization': `Bearer ${token}`
        };
        
        console.log(`正在获取项目数据，用户角色: ${userRole.value}`);
        
        // 使用标准API接口，后端已经处理FT角色的权限
        const url = 'http://localhost:5000/api/projects';
        console.log(`发送请求到: ${url}`);
        
        const response = await axios.get(url, { headers });
        
        console.log(`获取到项目数据: ${response.data.length} 条记录`);
        
        // 处理原始响应数据
        if (Array.isArray(response.data)) {
          // 处理项目数据，确保created_by字段是数字类型
          const processedData = response.data.map(project => {
            return {
              ...project,
              created_by: project.created_by ? Number(project.created_by) : null
            };
          });
          projectData.value = processedData;
          console.log(`成功处理 ${projectData.value.length} 条项目数据`);
          
          // 如果是FT角色且获取到了数据，检查是否需要切换到财务管理页面
          if (userRole.value === 'FT' && projectData.value.length > 0) {
            console.log('FT角色已获取项目数据，确保正确显示在财务管理页面');
            currentPage.value = 'financial_management';
            selectedMenuKey.value = '1_3';
          }
        } else {
          console.error('返回的数据不是数组:', response.data);
          projectData.value = [];
          
          // 如果是FT角色且没有获取到数据，尝试备用请求
          if (userRole.value === 'FT') {
            try {
              console.log('FT角色未获取到数据，尝试备用请求');
              const fallbackResponse = await axios.get('http://localhost:5000/api/projects?all=true', { headers });
              
              if (Array.isArray(fallbackResponse.data) && fallbackResponse.data.length > 0) {
                const processedData = fallbackResponse.data.map(project => {
                  return {
                    ...project,
                    created_by: project.created_by ? Number(project.created_by) : null
                  };
                });
                projectData.value = processedData;
                console.log(`备用请求成功: ${projectData.value.length} 条记录`);
              }
            } catch (fallbackError) {
              console.error('备用请求失败:', fallbackError);
            }
          }
        }
      } catch (error) {
        console.error('Error fetching project data:', error);
        Message.error({
          content: '获取项目数据失败，请刷新页面重试',
          duration: 3000
        });
      }
    };

    // 添加检查FT访问页面时项目列表的函数
    const checkFTProjectData = () => {
      if (userRole.value === 'FT' && currentPage.value === 'financial_management' && projectData.value.length === 0) {
        console.log('FT角色访问财务管理页面，但项目数据为空，尝试重新获取');
        fetchProjectData();
      }
    };

    // 监听页面切换
    watch(currentPage, (newPage) => {
      if (newPage === 'financial_management') {
        // 如果进入财务管理页面，确保项目数据已加载
        checkFTProjectData();
      }
    });

    // 监听用户角色变化
    watch(userRole, () => {
      // 如果用户角色改变，重新获取项目数据
      if (isLoggedIn.value) {
        fetchProjectData();
      }
    });

    const goToHome = () => {
      currentPage.value = 'home';
      selectedMenuKey.value = '0';
    };

    return {
      collapsed,
      onCollapse,
      toggleLogin,
      isLoggedIn,
      userName,
      userRole,
      visible,
      form,
      handleBeforeOk,
      handleCancel,
      currentPage,
      onClickMenuItem,
      selectedMenuKey,
      columns,
      projectData,
      fetchProjectData,
      getBreadcrumbText,
      filteredMenuItems,
      hasPermission,
      loginLoading,
      userId,
      goToHome,
    };
  }
});
</script>

<style scoped>
.layout-demo {
  height: 100vh;
  background: var(--color-fill-2);
  border: 1px solid var(--color-border);
  /* 确保整个布局容器只有一个滚动条 */
  overflow: hidden;
}
.layout-demo :deep(.arco-layout-sider) {
  height: 100%;
  overflow-y: hidden;
}

/* 覆盖Arco Design侧边栏内边距 */
.layout-demo :deep(.arco-layout-sider-children) {
  padding: 0 !important;
}

.layout-demo :deep(.arco-layout-header)  {
  height: 64px;
  line-height: 64px;
  background: var(--color-bg-3);
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0 16px;
}

.header-content {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 100%;
}

.header-left {
  display: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.login-button, .logout-button {
  height: 32px;
  font-size: 14px;
}

.logout-button {
  color: #fff;
  background-color: #3c9ae8;
  border-color: #3c9ae8;
}

.logout-button:hover {
  background-color: #2d8dd8;
  border-color: #2d8dd8;
}

.user-avatar {
  display: flex;
  align-items: center;
}

.user-dropdown-item {
  display: flex;
  flex-direction: column;
  padding: 4px 0;
}

.layout-demo :deep(.arco-layout-footer) {
  height: 48px;
  color: var(--color-text-2);
  font-weight: 400;
  font-size: 14px;
  line-height: 48px;
}
.layout-demo :deep(.arco-layout-content) {
  color: var(--color-text-2);
  font-weight: 400;
  font-size: 14px;
  background: var(--color-bg-3);
  display: flex;
  flex-direction: column;
  height: calc(100% - 112px);
  color: black;
  overflow-y: auto;
}

.layout-demo :deep(.arco-layout-footer) {
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: var(--color-white);
  font-size: 16px;
  font-stretch: condensed;
  text-align: center;
}
.footer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.footer-content p {
  margin: 0;
  line-height: 1.5;
}
.reply-box {
  padding: 16px;
  background: var(--color-bg-3);
  border-top: 1px solid var(--color-border);
}
.action {
  display: inline-block;
  padding: 0 4px;
  color: var(--color-text-1);
  line-height: 24px;
  background: transparent;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.1s ease;
}
.action:hover {
  background: var(--color-fill-3);
}

/* Logo占位符样式 */
.logo-placeholder {
  height: 100px; /* 减小高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  background: linear-gradient(145deg, rgba(30, 41, 59, 0.5), rgba(45, 55, 72, 0.3));
  border-radius: 8px;
  margin: 8px; /* 减少外边距 */
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  width: calc(100% - 16px); /* 确保宽度计算包含边距 */
}

.logo-placeholder::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: 0.5s;
}

.logo-placeholder:hover {
  transform: translateY(-3px);
  box-shadow: 0 7px 14px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.logo-placeholder:hover::after {
  left: 100%;
}

.logo-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start; /* 左对齐 */
  width: 100%;
  padding: 0 12px; /* 增加内边距 */
}

.logo-icon {
  margin-right: 8px; 
  font-size: 2rem;
  color: transparent;
  background: linear-gradient(135deg, #3c9ae8, #3c9ae8);
  -webkit-background-clip: text;
  background-clip: text;  
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
  flex-shrink: 0; 
}

.logo-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  overflow: hidden; 
  max-width: calc(100% - 40px); 
}

.logo-name {
  font-size: 1.5rem; 
  font-weight: bold;
  color: white;
  letter-spacing: 0.5px; 
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  line-height: 1.2;
  white-space: nowrap; 
}

.logo-highlight {
  background: linear-gradient(90deg, #3c9ae8, #3c9ae8);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 800;
}

.logo-tagline {
  font-size: 0.6rem; 
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.5px; 
  white-space: nowrap; 
  width: 100%; 
}

/* Home页面样式 */
.home-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.home-title {
  font-size: 2.5rem;
  color: #303133;
  text-align: center;
  margin-bottom: 10px;
}

.home-subtitle {
  font-size: 1.5rem;
  color: #606266;
  text-align: center;
  margin-bottom: 40px;
  font-weight: normal;
}

.home-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.home-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.home-section h3 {
  color: #303133;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.home-section p {
  color: #606266;
  line-height: 1.6;
}

.home-section ul {
  padding-left: 20px;
}

.home-section li {
  margin-bottom: 10px;
  color: #606266;
}

.home-login-info {
  background-color: #f0f9ff;
}

.demo-accounts {
  margin-top: 20px;
}

.account-card {
  background-color: white;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.account-type {
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.account-creds {
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
  font-family: monospace;
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
}

.account-creds span {
  margin-bottom: 5px;
}

.account-desc {
  color: #909399;
  font-size: 0.9rem;
}

/* 折叠状态下的Logo样式 */
.logo-content-collapsed {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 0; /* 移除内边距 */
}

.logo-icon-collapsed {
  font-size: 2.2rem;
  color: transparent;
  background: linear-gradient(135deg, #3c9ae8, #6c5ce7);
  -webkit-background-clip: text;
  background-clip: text;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
  animation: pulse 2s infinite;
  margin: 0; 
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}
</style>