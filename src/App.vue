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
      <div class="logo" />
      <a-menu
        :defaultOpenKeys="['1']"
        :selectedKeys="[selectedMenuKey]"
        @menuItemClick="onClickMenuItem"
      >
        <!-- AI助手 - 所有用户可见 -->
        <a-menu-item key="0_1" v-if="filteredMenuItems.includes('0_1')">
          <IconHome />
          AI助手 / AI Assistant
        </a-menu-item>
        
        <!-- 翻译工具 - 所有用户可见 -->
        <a-menu-item key="0_2" v-if="filteredMenuItems.includes('0_2')">
          <IconEdit />
          翻译工具 / Translator
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
        <a-menu
          :openKeys="['1']"
          :selectedKeys="[selectedMenuKey]"
          mode='horizontal'
        >
          <!-- AI助手 - 所有用户可见 -->
          <a-menu-item key="0_1" @click="onClickMenuItem('0_1')" v-if="filteredMenuItems.includes('0_1')">
            <IconHome />
            AI助手 / AI Assistant
          </a-menu-item>
          
          <!-- 翻译工具 - 所有用户可见 -->
          <a-menu-item key="0_2" @click="onClickMenuItem('0_2')" v-if="filteredMenuItems.includes('0_2')">
            <IconEdit />
            翻译工具 / Translator
          </a-menu-item>
          
          <!-- 本地化管理 - 根据权限显示子菜单 -->
          <a-sub-menu key="1" v-if="filteredMenuItems.some(item => item.startsWith('1_'))">
            <template #title>
              <span><IconApps />本地化管理 / L10n Management</span>
            </template>
            
            <!-- 请求管理 - 所有登录用户可见 -->
            <a-menu-item key="1_1" @click="onClickMenuItem('1_1')" v-if="filteredMenuItems.includes('1_1')">
              请求管理 / Request Management
            </a-menu-item>
            
            <!-- 项目管理 - LM和BO可见 -->
            <a-menu-item key="1_2" @click="onClickMenuItem('1_2')" v-if="filteredMenuItems.includes('1_2')">
              项目管理 / Project Management
            </a-menu-item>
            
            <!-- 财务管理 - 仅LM和FT可见 -->
            <a-menu-item key="1_3" @click="onClickMenuItem('1_3')" v-if="filteredMenuItems.includes('1_3')">
              财务管理 / Financial Management
            </a-menu-item>
          </a-sub-menu>
          
          <!-- 系统设置 - 仅LM可见 -->
          <a-menu-item key="2" @click="onClickMenuItem('2')" v-if="filteredMenuItems.includes('2')">
            <IconSettings />
            系统设置 / Settings
          </a-menu-item>
        </a-menu>
        <div class="user-avatar">
          <a-avatar @click="toggleLogin" v-if="!isLoggedIn">
            登录 / Login
          </a-avatar>
          <a-dropdown v-else trigger="click">
            <a-avatar @click="toggleLogin">
              {{ userName.charAt(0).toUpperCase() }}
            </a-avatar>
            <template #content>
              <a-doption>
                <div class="user-dropdown-item">
                  <span>{{ userName }}</span>
                  <span class="user-role">{{ userRole === 'LM' ? '本地化经理 / LM' : userRole === 'FT' ? '财务团队 / FT' : '业务负责人 / BO' }}</span>
                </div>
              </a-doption>
              <a-doption @click="toggleLogin">
                <IconExport />
                退出登录 / Logout
              </a-doption>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      <a-layout style="padding: 0 24px">
        <a-breadcrumb :style="{ margin: '16px 0' }">
          <a-breadcrumb-item>首页 / Home</a-breadcrumb-item>
          <a-breadcrumb-item>{{ getBreadcrumbText() }}</a-breadcrumb-item>
        </a-breadcrumb>
        <a-layout-content style="color: black;">
          <!-- AI助手页面 -->
          <div v-if="currentPage === 'menu1'">
            <h1>Arno's AI</h1>
            <div class="chat-container">
              <div class="chat-history" ref="chatHistory">
                <div v-for="(message, index) in messages" :key="index" class="chat-message" :class="{'user-message': message.sender === 'User', 'assistant-message': message.sender === 'Assistant'}">
                  <strong>{{ message.sender }}:</strong> <span v-html="message.text"></span>
                </div>
              </div>
              <a-input
                v-model="userInput"
                placeholder="Type your message..."
                @keyup.enter="sendMessage"
                style="margin-top: 16px;"
              />
              <a-button type="primary" @click="sendMessage" style="margin-top: 8px;">发送 / Send</a-button>
            </div>
          </div>
          
          <!-- 翻译工具页面 -->
          <div v-if="currentPage === 'translator'">
            <h1>Arno's Translator</h1>
            <TranslationForm />
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
} from '@arco-design/web-vue/es/icon';
import { Avatar } from '@arco-design/web-vue';
import TranslationForm from './components/TranslationForm.vue'; 
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
    Avatar,
    TranslationForm,
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
    const currentPage = ref('menu1'); // 将初始值设置为'menu1'
    const selectedMenuKey = ref('0_1'); // 将初始选中菜单项设置为'0_1'
    const messages = ref([]); // 存储聊天记录
    const userInput = ref(''); // 存储用户输入
    const chatHistory = ref(null); // 用于滚动到底部
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
      if (!isLoggedIn.value) return false;
      
      // 所有用户都可以访问的页面
      const commonPages = ['menu1', 'translator', 'request_management'];
      if (commonPages.includes(page)) return true;
      
      // LM可以访问所有页面
      if (userRole.value === 'LM') return true;
      
      // BO只能访问特定页面
      if (userRole.value === 'BO') {
        const boPages = ['menu1', 'translator', 'request_management', 'project_management'];
        return boPages.includes(page);
      }
      
      // FT可以访问财务管理页面
      if (userRole.value === 'FT') {
        const ftPages = ['menu1', 'translator', 'financial_management'];
        return ftPages.includes(page);
      }
      
      return false;
    };

    // 根据用户角色过滤菜单项
    const filteredMenuItems = computed(() => {
      if (!isLoggedIn.value) {
        // 未登录用户只能看到AI助手和翻译工具
        return ['0_1', '0_2'];
      }
      
      if (userRole.value === 'LM') {
        // LM可以看到所有菜单项
        return ['0_1', '0_2', '1_1', '1_2', '1_3', '2'];
      }
      
      if (userRole.value === 'BO') {
        // BO只能看到AI助手、翻译工具、请求管理和项目管理
        return ['0_1', '0_2', '1_1', '1_2'];
      }
      
      if (userRole.value === 'FT') {
        // FT只能看到AI助手、翻译工具和财务管理
        return ['0_1', '0_2', '1_3'];
      }
      
      return [];
    });

    const onCollapse = (val) => {
      collapsed.value = val;
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
          }
        } catch (error) {
          console.error('自动登录失败:', error);
          // 清除无效令牌
          localStorage.removeItem('token');
          axios.defaults.headers.common['Authorization'] = '';
        }
      }
    };

    // 页面加载时检查认证状态
    checkAuth();

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
        
        // 重定向到首页
        currentPage.value = 'menu1';
        selectedMenuKey.value = '0_1';
        
        Message.info({
          content: '已退出登录 / Logged out',
          duration: 2000,
        });
      }
    };

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
        case '0_1':
          targetPage = 'menu1';
          break;
        case '0_2':
          targetPage = 'translator'; 
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
          targetPage = 'menu1';
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
        case 'menu1':
          return 'AI助手 / AI Assistant';
        case 'translator':
          return '翻译工具 / Translator';
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

    const scrollToBottom = () => {
      if (chatHistory.value) {
        chatHistory.value.scrollTop = chatHistory.value.scrollHeight;
      }
    };

    const sendMessage = async () => {
      if (userInput.value.trim() === '') return; // 防止发送空消息
      messages.value.push({ sender: 'User', text: userInput.value }); // 添加用户消息
      scrollToBottom(); // 滚动到底部

      // 调用 API 获取助手的回复
      try {
        const apiResponse = await getChatResponse(userInput.value);
        await displayAssistantResponse(apiResponse); // 逐字显示助手回复
        scrollToBottom(); // 滚动到底部
      } catch (error) {
        console.error('Error fetching response:', error);
        messages.value.push({ sender: 'Assistant', text: 'Error occurred while fetching response.' });
        scrollToBottom(); // 滚动到底部
      }

      userInput.value = ''; // 清空
    };

    const displayAssistantResponse = (response) => {
      return new Promise((resolve) => {
        const assistantMessage = { sender: 'Assistant', text: '' }; // 初始化助手消息
        messages.value.push(assistantMessage); // 添加空的助手消息

        let index = 0;
        const interval = setInterval(() => {
          if (index < response.length) {
            assistantMessage.text += response[index]; // 逐字添加
            index++;
          } else {
            clearInterval(interval); // 停止定时器
            resolve(); // 完成 Promise
          }
        }, 50); // 每 50ms 显示一个字
      });
    };

    const getChatResponse = async (userMessage) => {
      try {
        const response = await axios.post('http://localhost:5000/api/chat', {
          message: userMessage
        });
        return response.data.response; // 返回助手的回复
      } catch (error) {
        console.error('Error fetching response:', error);
        return 'Error occurred while fetching response.';
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
      messages,
      userInput,
      sendMessage,
      chatHistory,
      columns,
      projectData,
      fetchProjectData,
      getBreadcrumbText,
      filteredMenuItems,
      hasPermission,
      loginLoading,
      userId,
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
.layout-demo :deep(.arco-layout-header)  {
  height: 64px;
  line-height: 64px;
  background: var(--color-bg-3);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.user-avatar {
  margin-right: 16px;
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
  /* 修改这里，禁用内容区域的滚动条 */
  overflow-y: hidden;
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
.chat-container {
  display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
  padding: 16px;
  border-radius: 8px;
  background-color: #f9f9f9;
  max-height: 400px;
  overflow-y: auto;
}

.chat-history {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.chat-message {
  margin-bottom: 8px;
  border-radius: 10px;
  padding: 10px;
  max-width: 70%;
  word-wrap: break-word;
  display: inline-block; 
}

.user-message {
  background-color: #d1e7dd; 
  align-self: flex-end; 
  margin-left: auto; 
  max-width: 80%; 
}

.assistant-message {
  background-color: #f8d7da;
  align-self: flex-start;
  margin-right: auto; 
  max-width: 80%; 
}
</style>