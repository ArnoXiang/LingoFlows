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
        <a-menu-item key="0_1">
          <IconHome />
          AI助手 / AI Assistant
        </a-menu-item>
        <a-menu-item key="0_2">
          <IconEdit />
          翻译工具 / Translator
        </a-menu-item>
        <a-sub-menu key="1">
          <template #title>
            <span><IconApps />本地化管理 / L10n Management</span>
          </template>
          <a-menu-item key="1_1">请求管理 / Request Management</a-menu-item>
          <a-menu-item key="1_2">项目管理 / Project Management</a-menu-item>
          <a-menu-item key="1_3">财务管理 / Financial Management</a-menu-item>
        </a-sub-menu>
        <a-menu-item key="2">
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
          <a-menu-item key="0_1" @click="onClickMenuItem('0_1')">
            <IconHome />
            AI助手 / AI Assistant
          </a-menu-item>
          <a-menu-item key="0_2" @click="onClickMenuItem('0_2')">
            <IconEdit />
            翻译工具 / Translator
          </a-menu-item>
          <a-sub-menu key="1">
            <template #title>
              <span><IconApps />本地化管理 / L10n Management</span>
            </template>
            <a-menu-item key="1_1" @click="onClickMenuItem('1_1')">请求管理 / Request Management</a-menu-item>
            <a-menu-item key="1_2" @click="onClickMenuItem('1_2')">项目管理 / Project Management</a-menu-item>
            <a-menu-item key="1_3" @click="onClickMenuItem('1_3')">财务管理 / Financial Management</a-menu-item>
          </a-sub-menu>
          <a-menu-item key="2" @click="onClickMenuItem('2')">
            <IconSettings />
            系统设置 / Settings
          </a-menu-item>
        </a-menu>
        <div class="user-avatar">
          <a-avatar @click="toggleLogin" v-if="!isLoggedIn">
            登录 / Login
          </a-avatar>
          <a-avatar v-else @click="toggleLogin">
            {{ userName.charAt(0).toUpperCase() }}
          </a-avatar>
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
            <ProjectManagement />
          </div>
          
          <!-- 财务管理页面 -->
          <div v-if="currentPage === 'financial_management'">
            <FinancialManagement />
          </div>
          
          <!-- 系统设置页面 -->
          <div v-if="currentPage === 'settings'">
            <h1>系统设置 / System Settings</h1>
            <p>系统设置页面正在开发中... / System settings page is under development...</p>
          </div>
        </a-layout-content>
        <a-layout-footer>
          <div class="footer-content">
            <p>© 2023 LingoFlows - Collaborative Localization Management System</p>
            <p>Developed by Yizhuo Xiang</p>
          </div>
        </a-layout-footer>
      </a-layout>
    </a-layout>

    <!-- 登录弹窗 -->
    <a-modal v-model:visible="visible" title="登录 / Login" @cancel="handleCancel" @before-ok="handleBeforeOk">
      <a-form :model="form">
        <a-form-item field="username" label="用户名 / Username">
          <a-input v-model="form.username" />
        </a-form-item>
        <a-form-item field="password" label="密码 / Password">
          <a-input type="password" v-model="form.password" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 返回顶部按钮 -->
    <a-back-top :style="{ position: 'absolute', right: '20px', bottom: '20px' }" />
  </a-layout>
</template>

<script>
import { defineComponent, ref, reactive } from 'vue';
import { Message } from '@arco-design/web-vue';
import {
  IconHome,
  IconCalendar,
  IconSettings,
  IconApps,
  IconEdit,
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
    Avatar,
    TranslationForm,
    RequestForm,
    ProjectManagement,
    FinancialManagement,
  },
  setup() {
    const collapsed = ref(false);
    const isLoggedIn = ref(false);
    const userName = ref('Yizhuo Xiang');
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

    const onCollapse = (val, type) => {
      const content = type === 'responsive' ? '触发响应式收缩' : '点击触发收缩';
      Message.info({
        content,
        duration: 2000,
      });
      collapsed.value = val;
    };

    const toggleLogin = () => {
      if (!isLoggedIn.value) {
        visible.value = true;
      } else {
        isLoggedIn.value = false; 
        Message.info({
          content: '已退出登录 / Logged out',
          duration: 2000,
        });
      }
    };

    const handleBeforeOk = (done) => {
      console.log(form);
      isLoggedIn.value = true;
      visible.value = false;
      Message.success({
        content: '登录成功 / Login successful',
        duration: 2000,
      });
      done();
    };

    const handleCancel = () => {
      visible.value = false;
    };

    const onClickMenuItem = (key) => {
      selectedMenuKey.value = key; // 更新选中的菜单项
      
      // 根据菜单项切换页面
      switch (key) {
        case '0_1':
          currentPage.value = 'menu1'; // AI助手
          break;
        case '0_2':
          currentPage.value = 'translator'; // 翻译工具
          break;
        case '1_1':
          currentPage.value = 'request_management'; // 请求管理
          break;
        case '1_2':
          currentPage.value = 'project_management'; // 项目管理
          break;
        case '1_3':
          currentPage.value = 'financial_management'; // 财务管理
          break;
        case '2':
          currentPage.value = 'settings'; // 系统设置
          break;
        default:
          currentPage.value = 'menu1';
      }
      
      Message.info({ content: `You select ${key}`, showIcon: true });
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

      userInput.value = ''; // 清空输入框
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
        const response = await axios.get('http://localhost:5000/api/projects');
        projectData.value = response.data;
      } catch (error) {
        console.error('Error fetching project data:', error);
      }
    };

    fetchProjectData(); // 在组件加载时获取数据

    return {
      collapsed,
      onCollapse,
      toggleLogin,
      isLoggedIn,
      userName,
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
    };
  }
});
</script>

<style scoped>
.layout-demo {
  height: 100vh;
  background: var(--color-fill-2);
  border: 1px solid var(--color-border);
}
.layout-demo :deep(.arco-layout-sider) {
  height: 100%;
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
  display: inline-block; /* 使气泡根据内容自适应宽度 */
}

.user-message {
  background-color: #d1e7dd; /* 用户消息气泡颜色 */
  align-self: flex-end; /* 用户消息右对齐 */
  margin-left: auto; /* 将用户气泡推到右侧 */
  max-width: 80%; /* 设置最大宽度 */
}

.assistant-message {
  background-color: #f8d7da; /* 助手消息气泡颜色 */
  align-self: flex-start; /* 助手消息左对齐 */
  margin-right: auto; /* 将助手气泡推到左侧 */
  max-width: 80%; /* 设置最大宽度 */
}
</style>