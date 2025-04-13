<template>
  <div class="project-list-container">
    <!-- 操作按钮区域 -->
    <div style="margin-bottom: 16px; display: flex; justify-content: flex-end;">
      <a-space>
        <a-button type="primary" @click="refreshProjects">
          刷新列表 / Refresh List
        </a-button>
      </a-space>
    </div>
    
    <div class="action-bar">
      <a-input-search
        v-model="searchKeyword"
        placeholder="搜索项目 / Search projects"
        style="width: 300px; margin-right: 16px;"
        @search="handleSearch"
      />
      <a-select
        v-model="statusFilter"
        placeholder="项目状态 / Project Status"
        style="width: 200px; margin-right: 16px;"
        allow-clear
        @change="handleStatusChange"
      >
        <a-option value="all">全部 / All</a-option>
        <a-option value="pending">待处理 / Pending</a-option>
        <a-option value="in_progress">进行中 / In Progress</a-option>
        <a-option value="completed">已完成 / Completed</a-option>
        <a-option value="cancelled">已取消 / Cancelled</a-option>
      </a-select>
      <a-select
        v-model="projectManagerFilter"
        placeholder="项目经理 / Project Manager"
        style="width: 200px; margin-right: 16px;"
        allow-clear
        @change="handleManagerChange"
      >
        <a-option value="all">全部 / All</a-option>
        <a-option v-for="manager in uniqueProjectManagers" :key="manager" :value="manager">
          {{ manager }}
        </a-option>
      </a-select>
    </div>
    
    <a-table
      :columns="columns"
      :data="filteredProjects"
      :loading="loading"
      :pagination="{
        showTotal: true,
        showPageSize: true,
        pageSize: 10,
      }"
      row-key="id"
      style="margin-top: 16px;"
      :column-resizable="true"
    >
      <!-- 空状态提示 -->
      <template #empty>
        <div style="text-align: center; padding: 20px;">
          <a-empty description="暂无项目数据 / No project data available">
            <template #image>
              <icon-file style="font-size: 48px; color: #c2c7d0;" />
            </template>
            <a-button type="primary" @click="refreshProjects">
              刷新 / Refresh
            </a-button>
          </a-empty>
        </div>
      </template>
      
      <!-- 项目状态列 -->
      <template #projectStatus="{ record }">
        <a-tag :color="getStatusColor(record.projectStatus)">
          {{ getStatusText(record.projectStatus) }}
        </a-tag>
      </template>
      
      <!-- 任务状态列 -->
      <template #taskTranslation="{ record }">
        <a-progress
          :percent="getTaskProgress(record.taskTranslation)"
          :status="getTaskStatus(record.taskTranslation)"
          :show-text="false"
          size="small"
        />
        <span>{{ getTaskText(record.taskTranslation) }}</span>
      </template>
      
      <template #taskLQA="{ record }">
        <a-progress
          :percent="getTaskProgress(record.taskLQA)"
          :status="getTaskStatus(record.taskLQA)"
          :show-text="false"
          size="small"
        />
        <span>{{ getTaskText(record.taskLQA) }}</span>
      </template>
      
      <template #taskTranslationUpdate="{ record }">
        <a-progress
          :percent="getTaskProgress(record.taskTranslationUpdate)"
          :status="getTaskStatus(record.taskTranslationUpdate)"
          :show-text="false"
          size="small"
        />
        <span>{{ getTaskText(record.taskTranslationUpdate) }}</span>
      </template>
      
      <template #taskLQAReportFinalization="{ record }">
        <a-progress
          :percent="getTaskProgress(record.taskLQAReportFinalization)"
          :status="getTaskStatus(record.taskLQAReportFinalization)"
          :show-text="false"
          size="small"
        />
        <span>{{ getTaskText(record.taskLQAReportFinalization) }}</span>
      </template>
      
      <!-- 操作列 -->
      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="onViewProject(record)">
            查看 / View
          </a-button>
          <a-button type="text" size="small" @click="onEditProject(record)" v-if="userRole === 'LM'">
            编辑 / Edit
          </a-button>
          <a-button type="text" size="small" @click="onSendEmail(record)" v-if="userRole === 'LM'">
            发送邮件 / Send Email
          </a-button>
          <a-button type="text" size="small" @click="onUploadFiles(record)" v-if="userRole === 'LM' || (userRole === 'BO' && canPerformAction(record, userId, userRole))">
            上传文件 / Upload Files
          </a-button>
        </a-space>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';
import { IconFile } from '@arco-design/web-vue/es/icon';
import { 
  getStatusColor, 
  getStatusText, 
  getTaskProgress, 
  getTaskStatus, 
  getTaskText,
  processProject,
  canPerformAction
} from './utils/projectUtils';

const props = defineProps({
  userRole: {
    type: String,
    default: ''
  },
  userId: {
    type: Number,
    default: null
  },
  projectData: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits([
  'view-project', 
  'edit-project', 
  'send-email', 
  'upload-files',
  'refresh-projects'
]);

// 表格列定义
const columns = [
  {
    title: '项目名称 / Project Name',
    dataIndex: 'projectName',
    key: 'projectName',
    sortable: true,
    resizable: true,
  },
  {
    title: '项目状态 / Project Status',
    dataIndex: 'projectStatus',
    key: 'projectStatus',
    slotName: 'projectStatus',
    sortable: true,
    resizable: true,
  },
  {
    title: '请求名称 / Request Name',
    dataIndex: 'requestName',
    key: 'requestName',
    resizable: true,
  },
  {
    title: '项目经理 / Project Manager',
    dataIndex: 'projectManager',
    key: 'projectManager',
    sortable: true,
    resizable: true,
  },
  {
    title: '创建时间 / Create Time',
    dataIndex: 'createTime',
    key: 'createTime',
    sortable: true,
    resizable: true,
  },
  {
    title: '翻译任务 / Translation Task',
    dataIndex: 'taskTranslation',
    key: 'taskTranslation',
    slotName: 'taskTranslation',
    resizable: true,
  },
  {
    title: 'LQA任务 / LQA Task',
    dataIndex: 'taskLQA',
    key: 'taskLQA',
    slotName: 'taskLQA',
    resizable: true,
  },
  {
    title: '翻译更新 / Translation Update',
    dataIndex: 'taskTranslationUpdate',
    key: 'taskTranslationUpdate',
    slotName: 'taskTranslationUpdate',
    resizable: true,
  },
  {
    title: 'LQA报告定稿 / LQA Report Finalization',
    dataIndex: 'taskLQAReportFinalization',
    key: 'taskLQAReportFinalization',
    slotName: 'taskLQAReportFinalization',
    resizable: true,
  },
  {
    title: '操作 / Operations',
    slotName: 'operations',
    width: 250,
    resizable: true,
  },
];

// 状态
const projects = ref([]);
const loading = ref(false);
const searchKeyword = ref('');
const statusFilter = ref('all');
const projectManagerFilter = ref('all');

// 过滤后的项目列表
const filteredProjects = computed(() => {
  let result = [...projects.value];
  
  // 状态过滤
  if (statusFilter.value !== 'all') {
    result = result.filter(project => project.projectStatus === statusFilter.value);
  }
  
  // 项目经理过滤
  if (projectManagerFilter.value !== 'all') {
    result = result.filter(project => project.projectManager === projectManagerFilter.value);
  }
  
  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(project => 
      project.projectName.toLowerCase().includes(keyword) ||
      project.requestName.toLowerCase().includes(keyword) ||
      project.projectManager.toLowerCase().includes(keyword)
    );
  }
  
  return result;
});

// 获取唯一的项目经理列表
const uniqueProjectManagers = computed(() => {
  const managers = new Set();
  projects.value.forEach(project => {
    if (project.projectManager) {
      managers.add(project.projectManager);
    }
  });
  return Array.from(managers);
});

// 生命周期钩子
onMounted(() => {
  fetchProjects();
});

// 当用户ID或角色变化时重新获取项目
watch([() => props.userId, () => props.userRole], () => {
  fetchProjects();
});

// 监听projectData变化
watch(() => props.projectData, (newData) => {
  if (newData && newData.length > 0) {
    console.log('ProjectList - 接收到项目数据:', newData);
    
    // 处理接收到的项目数据
    const processedProjects = newData.map(project => processProject(project));
    
    console.log('ProjectList - 处理后的项目数据:', processedProjects);
    projects.value = processedProjects;
    
    // 强制UI更新 - 添加以下代码
    nextTick(() => {
      console.log('ProjectList - 强制UI刷新');
      // 如果存在进度条或状态标签，刷新它们
      if (document.querySelectorAll('.arco-progress').length > 0) {
        // 触发重新计算
        window.dispatchEvent(new Event('resize'));
      }
    });
  }
}, { immediate: true, deep: true });  // 添加deep: true以确保深度监听对象变化

const fetchProjects = async () => {
  if (!props.userId) {
    console.log('未获取项目数据：用户ID为空');
    return; // 没有用户ID，不获取
  }
  
  console.log(`开始获取项目数据，用户ID: ${props.userId}, 用户角色: ${props.userRole}`);
  loading.value = true;
  
  try {
    // 获取存储的令牌
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('未找到令牌，无法获取项目数据');
      Message.error('未登录或会话已过期 / Not logged in or session expired');
      return;
    }
    
    // 设置请求头
    const headers = {
      'Authorization': `Bearer ${token}`
    };
    console.log('发送请求到 /api/projects，带有Authorization头');
    
    const response = await axios.get('http://localhost:5000/api/projects', { headers });
    console.log('获取项目数据成功:', response.data);
    
    if (Array.isArray(response.data)) {
      // 处理项目数据
      const processedProjects = response.data.map(project => processProject(project));
      
      console.log('ProjectList - 处理后的项目数据:', processedProjects);
      projects.value = processedProjects;
      
      // 触发刷新事件，通知父组件
      emit('refresh-projects', processedProjects);
    } else {
      console.error('返回的数据不是数组:', response.data);
      projects.value = [];
    }
  } catch (error) {
    console.error('获取项目数据失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.data);
      console.error('状态码:', error.response.status);
    }
    Message.error('获取项目列表失败 / Failed to fetch projects');
    projects.value = [];
  } finally {
    loading.value = false;
  }
};

const refreshProjects = () => {
  fetchProjects();
};

const handleSearch = () => {
  console.log('Searching for:', searchKeyword.value);
};

const handleStatusChange = () => {
  console.log('状态筛选变更为:', statusFilter.value);
};

const handleManagerChange = () => {
  console.log('项目经理筛选变更为:', projectManagerFilter.value);
};

// 事件处理函数 - 触发自定义事件到父组件
const onViewProject = (project) => {
  emit('view-project', project);
};

const onEditProject = (project) => {
  emit('edit-project', project);
};

const onSendEmail = (project) => {
  emit('send-email', project);
};

const onUploadFiles = (project) => {
  emit('upload-files', project);
};
</script>

<style scoped>
.project-list-container {
  width: 100%;
}

.action-bar {
  display: flex;
  margin-bottom: 16px;
}
</style> 