<template>
  <div class="project-management-container">
    <h2>项目管理 / Project Management</h2>
    
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
      >
        <a-option value="all">全部 / All</a-option>
        <a-option value="pending">待处理 / Pending</a-option>
        <a-option value="in_progress">进行中 / In Progress</a-option>
        <a-option value="completed">已完成 / Completed</a-option>
        <a-option value="cancelled">已取消 / Cancelled</a-option>
      </a-select>
      <a-button type="primary" @click="refreshProjects">
        刷新 / Refresh
      </a-button>
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
          <a-button type="text" size="small" @click="viewProject(record)">
            查看 / View
          </a-button>
          <a-button type="text" size="small" @click="editProject(record)" v-if="props.userRole === 'LM'">
            编辑 / Edit
          </a-button>
          <a-button type="text" size="small" @click="sendEmail(record)" v-if="props.userRole === 'LM'">
            发送邮件 / Send Email
          </a-button>
          <a-button type="text" size="small" @click="uploadFiles(record)" v-if="props.userRole === 'LM'">
            上传文件 / Upload Files
          </a-button>
        </a-space>
      </template>
    </a-table>
    
    <!-- 项目详情抽屉 -->
    <a-drawer
      v-model:visible="drawerVisible"
      :width="600"
      :title="drawerTitle"
      unmountOnClose
    >
      <div v-if="currentProject">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="项目名称 / Project Name">
            <a-input v-model="currentProject.projectName" v-if="isEditing && props.userRole === 'LM'" />
            <span v-else>{{ currentProject.projectName }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="项目状态 / Project Status">
            <a-select v-model="currentProject.projectStatus" v-if="isEditing && props.userRole === 'LM'">
              <a-option value="pending">待处理 / Pending</a-option>
              <a-option value="in_progress">进行中 / In Progress</a-option>
              <a-option value="completed">已完成 / Completed</a-option>
              <a-option value="cancelled">已取消 / Cancelled</a-option>
            </a-select>
            <a-tag v-else :color="getStatusColor(currentProject.projectStatus)">
              {{ getStatusText(currentProject.projectStatus) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="请求名称 / Request Name">
            <a-input v-model="currentProject.requestName" v-if="isEditing && props.userRole === 'LM'" />
            <span v-else>{{ currentProject.requestName }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="项目经理 / Project Manager">
            <a-input v-model="currentProject.projectManager" v-if="isEditing && props.userRole === 'LM'" />
            <span v-else>{{ currentProject.projectManager }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间 / Create Time">
            {{ formatDate(currentProject.createTime) }}
          </a-descriptions-item>
          <a-descriptions-item label="源语言 / Source Language">
            {{ getLanguageName(currentProject.sourceLanguage) }}
          </a-descriptions-item>
          <a-descriptions-item label="目标语言 / Target Languages">
            <a-space>
              <a-tag v-for="lang in currentProject.targetLanguages" :key="lang">
                {{ getLanguageName(lang) }}
              </a-tag>
            </a-space>
          </a-descriptions-item>
          <a-descriptions-item label="字数 / Word Count">
            {{ currentProject.wordCount }}
          </a-descriptions-item>
          <a-descriptions-item label="预期交付日期 / Expected Delivery Date">
            {{ formatDate(currentProject.expectedDeliveryDate) }}
          </a-descriptions-item>
          <a-descriptions-item label="附加要求 / Additional Requirements">
            <a-space>
              <a-tag v-for="req in currentProject.additionalRequirements" :key="req">
                {{ getRequirementText(req) }}
              </a-tag>
            </a-space>
          </a-descriptions-item>
        </a-descriptions>
        
        <div class="task-management" style="margin-top: 24px;" v-if="props.userRole === 'LM'">
          <h3>任务管理 / Task Management</h3>
          <a-collapse>
            <a-collapse-item header="翻译任务 / Translation Task" key="1">
              <a-form :model="currentProject.tasks.translation">
                <a-form-item field="status" label="状态 / Status">
                  <a-select v-model="currentProject.tasks.translation.status">
                    <a-option value="not_started">未开始 / Not Started</a-option>
                    <a-option value="in_progress">进行中 / In Progress</a-option>
                    <a-option value="completed">已完成 / Completed</a-option>
                  </a-select>
                </a-form-item>
                <a-form-item field="assignee" label="负责人 / Assignee">
                  <a-input v-model="currentProject.tasks.translation.assignee" />
                </a-form-item>
                <a-form-item field="deadline" label="截止日期 / Deadline">
                  <a-date-picker v-model="currentProject.tasks.translation.deadline" />
                </a-form-item>
                <a-form-item field="notes" label="备注 / Notes">
                  <a-textarea v-model="currentProject.tasks.translation.notes" />
                </a-form-item>
              </a-form>
            </a-collapse-item>
            
            <a-collapse-item header="LQA任务 / LQA Task" key="2">
              <a-form :model="currentProject.tasks.lqa">
                <a-form-item field="status" label="状态 / Status">
                  <a-select v-model="currentProject.tasks.lqa.status">
                    <a-option value="not_started">未开始 / Not Started</a-option>
                    <a-option value="in_progress">进行中 / In Progress</a-option>
                    <a-option value="completed">已完成 / Completed</a-option>
                  </a-select>
                </a-form-item>
                <a-form-item field="assignee" label="负责人 / Assignee">
                  <a-input v-model="currentProject.tasks.lqa.assignee" />
                </a-form-item>
                <a-form-item field="deadline" label="截止日期 / Deadline">
                  <a-date-picker v-model="currentProject.tasks.lqa.deadline" />
                </a-form-item>
                <a-form-item field="notes" label="备注 / Notes">
                  <a-textarea v-model="currentProject.tasks.lqa.notes" />
                </a-form-item>
              </a-form>
            </a-collapse-item>
          </a-collapse>
        </div>
        
        <!-- 只读任务状态显示，当用户只能查看但不能编辑时显示 -->
        <div class="task-status" style="margin-top: 24px;" v-if="props.userRole === 'BO'">
          <h3>任务状态 / Task Status</h3>
          <a-descriptions :column="1" bordered>
            <a-descriptions-item label="翻译任务 / Translation Task">
              <a-tag :color="getTaskStatus(currentProject.taskTranslation)">
                {{ getTaskText(currentProject.taskTranslation) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="LQA任务 / LQA Task">
              <a-tag :color="getTaskStatus(currentProject.taskLQA)">
                {{ getTaskText(currentProject.taskLQA) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="翻译更新 / Translation Update">
              <a-tag :color="getTaskStatus(currentProject.taskTranslationUpdate)">
                {{ getTaskText(currentProject.taskTranslationUpdate) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="LQA报告定稿 / LQA Report Finalization">
              <a-tag :color="getTaskStatus(currentProject.taskLQAReportFinalization)">
                {{ getTaskText(currentProject.taskLQAReportFinalization) }}
              </a-tag>
            </a-descriptions-item>
          </a-descriptions>
        </div>
        
        <div class="drawer-footer" style="margin-top: 24px; text-align: right;">
          <a-space>
            <a-button @click="drawerVisible = false">
              关闭 / Close
            </a-button>
            <a-button type="primary" @click="saveProject" v-if="props.userRole === 'LM' && isEditing">
              保存 / Save
            </a-button>
          </a-space>
        </div>
      </div>
    </a-drawer>
    
    <!-- 发送邮件对话框 -->
    <a-modal
      v-model:visible="emailModalVisible"
      title="发送项目邮件 / Send Project Email"
      @ok="sendProjectEmail"
      @cancel="emailModalVisible = false"
      :ok-loading="sendingEmail"
    >
      <a-form :model="emailForm">
        <a-form-item field="to" label="收件人 / To" required>
          <a-input v-model="emailForm.to" placeholder="收件人邮箱 / Recipient email" />
        </a-form-item>
        <a-form-item field="cc" label="抄送 / CC">
          <a-input v-model="emailForm.cc" placeholder="抄送邮箱 / CC email" />
        </a-form-item>
        <a-form-item field="subject" label="主题 / Subject" required>
          <a-input v-model="emailForm.subject" placeholder="邮件主题 / Email subject" />
        </a-form-item>
        <a-form-item field="content" label="内容 / Content" required>
          <a-textarea
            v-model="emailForm.content"
            placeholder="邮件内容 / Email content"
            :auto-size="{ minRows: 5, maxRows: 10 }"
          />
        </a-form-item>
        <a-form-item field="attachments" label="附件 / Attachments">
          <a-upload
            action="http://localhost:5000/api/upload"
            :file-list="emailAttachments"
            @change="handleEmailAttachmentChange"
            :headers="uploadHeaders"
            multiple
          >
            <a-button>上传附件 / Upload Attachments</a-button>
          </a-upload>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 上传文件对话框 -->
    <a-modal
      v-model:visible="uploadModalVisible"
      title="上传项目文件 / Upload Project Files"
      @ok="submitUploadFiles"
      @cancel="uploadModalVisible = false"
      :ok-loading="uploading"
    >
      <a-form :model="uploadForm">
        <a-form-item field="fileType" label="文件类型 / File Type" required>
          <a-select v-model="uploadForm.fileType">
            <a-option value="source">源文件 / Source Files</a-option>
            <a-option value="translation">翻译文件 / Translation Files</a-option>
            <a-option value="lqa">LQA报告 / LQA Reports</a-option>
            <a-option value="other">其他 / Other</a-option>
          </a-select>
        </a-form-item>
        <a-form-item field="files" label="文件 / Files" required>
          <a-upload
            action="http://localhost:5000/api/upload"
            :file-list="projectFiles"
            @change="handleProjectFileChange"
            :headers="uploadHeaders"
            multiple
          >
            <a-button>上传文件 / Upload Files</a-button>
          </a-upload>
        </a-form-item>
        <a-form-item field="notes" label="备注 / Notes">
          <a-textarea
            v-model="uploadForm.notes"
            placeholder="文件备注 / File notes"
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { Message } from '@arco-design/web-vue';
import { IconFile } from '@arco-design/web-vue/es/icon';
import axios from 'axios';
import { languages } from '../utils/languages';

// 接收用户角色和ID作为props
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
    filterable: true,
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
    filterable: true,
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

// 状态和数据
const projects = ref([]);
const loading = ref(false);
const searchKeyword = ref('');
const statusFilter = ref('all');
const drawerVisible = ref(false);
const drawerTitle = ref('项目详情 / Project Details');
const currentProject = ref(null);
const emailModalVisible = ref(false);
const uploadModalVisible = ref(false);
const sendingEmail = ref(false);
const uploading = ref(false);
const emailAttachments = ref([]);
const projectFiles = ref([]);
const isEditing = ref(false);

// 表单数据
const emailForm = reactive({
  to: '',
  cc: '',
  subject: '',
  content: '',
});

const uploadForm = reactive({
  fileType: 'source',
  notes: '',
});

// 获取上传请求的headers
const uploadHeaders = computed(() => {
  // 从localStorage获取token
  const token = localStorage.getItem('token');
  return {
    Authorization: token ? `Bearer ${token}` : ''
  };
});

// 过滤后的项目列表
const filteredProjects = computed(() => {
  console.log('ProjectManagement - 原始项目数据:', projects.value);
  
  // 检查数据格式
  if (projects.value && projects.value.length > 0) {
    console.log('ProjectManagement - 第一个项目数据示例:', JSON.stringify(projects.value[0]));
    console.log('ProjectManagement - 项目数据中是否有id字段:', projects.value[0].hasOwnProperty('id'));
  }
  
  let result = [...projects.value];
  
  // 状态过滤
  if (statusFilter.value !== 'all') {
    result = result.filter(project => project.projectStatus === statusFilter.value);
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
  
  console.log('ProjectManagement - 过滤后的项目数据:', result);
  return result;
});

// 检查用户是否有权限查看项目
// 与canPerformAction不同，这个函数允许BO查看自己的项目
const canViewProject = (project) => {
  if (!project) {
    console.log('canViewProject - 项目为空');
    return false;
  }
  
  console.log('canViewProject - 项目:', project);
  console.log('canViewProject - 用户ID:', props.userId, '类型:', typeof props.userId);
  console.log('canViewProject - 项目created_by:', project.created_by, '类型:', typeof project.created_by);
  
  // 如果用户ID为null，则无权限
  if (props.userId === null || props.userId === undefined) {
    console.log('canViewProject - 用户ID为null或undefined，无权限');
    return false;
  }
  
  if (props.userRole === 'LM') {
    console.log('canViewProject - 用户是LM，有权限');
    return true; // LM可以查看所有项目
  }
  
  // BO只能查看自己的项目
  // 确保类型匹配，将两者都转换为数字进行比较
  const projectCreatedBy = project.created_by !== null && project.created_by !== undefined ? Number(project.created_by) : null;
  const userId = Number(props.userId);
  
  console.log('canViewProject - 转换后的项目created_by:', projectCreatedBy);
  console.log('canViewProject - 转换后的用户ID:', userId);
  
  // 如果项目的created_by为null，则无法确定所有者，BO无权限
  if (projectCreatedBy === null) {
    console.log('canViewProject - 项目created_by为null，BO无权限');
    return false;
  }
  
  const hasPermission = projectCreatedBy === userId;
  console.log('canViewProject - 权限检查结果:', hasPermission);
  return hasPermission;
};

// 检查用户是否有权限执行操作
const canPerformAction = (project) => {
  if (!project) {
    console.log('canPerformAction - 项目为空');
    return false;
  }
  
  console.log('canPerformAction - 项目:', project);
  console.log('canPerformAction - 用户ID:', props.userId, '类型:', typeof props.userId);
  console.log('canPerformAction - 项目created_by:', project.created_by, '类型:', typeof project.created_by);
  
  // 如果用户ID为null，则无权限
  if (props.userId === null || props.userId === undefined) {
    console.log('canPerformAction - 用户ID为null或undefined，无权限');
    return false;
  }
  
  if (props.userRole === 'LM') {
    console.log('canPerformAction - 用户是LM，有权限');
    return true; // LM可以执行所有操作
  }
  
  // BO只能操作自己的项目
  // 确保类型匹配，将两者都转换为数字进行比较
  const projectCreatedBy = project.created_by !== null && project.created_by !== undefined ? Number(project.created_by) : null;
  const userId = Number(props.userId);
  
  console.log('canPerformAction - 转换后的项目created_by:', projectCreatedBy);
  console.log('canPerformAction - 转换后的用户ID:', userId);
  
  // 如果项目的created_by为null，则无法确定所有者，BO无权限
  if (projectCreatedBy === null) {
    console.log('canPerformAction - 项目created_by为null，BO无权限');
    return false;
  }
  
  const hasPermission = projectCreatedBy === userId;
  console.log('canPerformAction - 权限检查结果:', hasPermission);
  return hasPermission;
};

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
    console.log('ProjectManagement - 接收到App.vue传递的项目数据:', newData);
    
    // 处理接收到的项目数据
    const processedProjects = newData.map(project => {
      // 确保id字段存在且为数字类型
      const id = project.id ? Number(project.id) : null;
      
      // 确保created_by字段存在且为数字类型
      const created_by = project.created_by ? Number(project.created_by) : null;
      
      // 处理targetLanguages字段，如果是字符串则转换为数组
      let targetLanguages = project.targetLanguages;
      if (typeof targetLanguages === 'string' && targetLanguages) {
        targetLanguages = targetLanguages.split(',');
      } else if (!targetLanguages) {
        targetLanguages = [];
      }
      
      // 处理additionalRequirements字段，如果是字符串则转换为数组
      let additionalRequirements = project.additionalRequirements;
      if (typeof additionalRequirements === 'string' && additionalRequirements) {
        additionalRequirements = additionalRequirements.split(',');
      } else if (!additionalRequirements) {
        additionalRequirements = [];
      }
      
      // 返回处理后的项目对象
      return {
        ...project,
        id,
        created_by,
        targetLanguages,
        additionalRequirements,
        // 确保任务状态字段存在
        taskTranslation: project.taskTranslation || 'not_started',
        taskLQA: project.taskLQA || 'not_started',
        taskTranslationUpdate: project.taskTranslationUpdate || 'not_started',
        taskLQAReportFinalization: project.taskLQAReportFinalization || 'not_started'
      };
    });
    
    console.log('ProjectManagement - 处理后的App.vue项目数据:', processedProjects);
    projects.value = processedProjects;
  }
}, { immediate: true });

// 方法
const fetchProjects = async () => {
  if (!props.userId) {
    console.log('未获取项目数据：用户ID为空');
    return; // 如果没有用户ID，不获取数据
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
    console.log('Authorization头:', headers.Authorization);
    
    const response = await axios.get('http://localhost:5000/api/projects', { headers });
    console.log('获取项目数据成功，原始数据:', response.data);
    
    if (Array.isArray(response.data) && response.data.length === 0) {
      console.log('服务器返回了空数组，可能是因为没有项目或权限问题');
      if (props.userRole === 'LM') {
        console.log('当前用户是LM，应该能看到所有项目，可能是数据库中没有项目或created_by字段未设置');
      } else {
        console.log('当前用户不是LM，只能看到自己创建的项目，可能是没有项目与当前用户关联');
      }
      projects.value = [];
    } else if (Array.isArray(response.data)) {
      // 确保每个项目对象都有必要的字段
      const processedProjects = response.data.map(project => {
        // 确保id字段存在且为数字类型
        const id = project.id ? Number(project.id) : null;
        
        // 确保created_by字段存在且为数字类型
        const created_by = project.created_by ? Number(project.created_by) : null;
        
        // 处理targetLanguages字段，如果是字符串则转换为数组
        let targetLanguages = project.targetLanguages;
        if (typeof targetLanguages === 'string' && targetLanguages) {
          targetLanguages = targetLanguages.split(',');
        } else if (!targetLanguages) {
          targetLanguages = [];
        }
        
        // 处理additionalRequirements字段，如果是字符串则转换为数组
        let additionalRequirements = project.additionalRequirements;
        if (typeof additionalRequirements === 'string' && additionalRequirements) {
          additionalRequirements = additionalRequirements.split(',');
        } else if (!additionalRequirements) {
          additionalRequirements = [];
        }
        
        // 返回处理后的项目对象
        return {
          ...project,
          id,
          created_by,
          targetLanguages,
          additionalRequirements,
          // 确保任务状态字段存在
          taskTranslation: project.taskTranslation || 'not_started',
          taskLQA: project.taskLQA || 'not_started',
          taskTranslationUpdate: project.taskTranslationUpdate || 'not_started',
          taskLQAReportFinalization: project.taskLQAReportFinalization || 'not_started'
        };
      });
      
      console.log('处理后的项目数据:', processedProjects);
      projects.value = processedProjects;
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
  Message.success('项目列表已刷新 / Project list refreshed');
};

const handleSearch = () => {
  console.log('Searching for:', searchKeyword.value);
};

const getStatusColor = (status) => {
  const statusMap = {
    pending: 'orange',
    in_progress: 'blue',
    completed: 'green',
    cancelled: 'red',
  };
  return statusMap[status] || 'gray';
};

const getStatusText = (status) => {
  const statusMap = {
    pending: '待处理 / Pending',
    in_progress: '进行中 / In Progress',
    completed: '已完成 / Completed',
    cancelled: '已取消 / Cancelled',
  };
  return statusMap[status] || '未知 / Unknown';
};

const getTaskProgress = (taskStatus) => {
  const progressMap = {
    not_started: 0,
    in_progress: 50,
    completed: 100,
  };
  return progressMap[taskStatus] || 0;
};

const getTaskStatus = (taskStatus) => {
  const statusMap = {
    not_started: 'normal',
    in_progress: 'warning',
    completed: 'success',
  };
  return statusMap[taskStatus] || 'normal';
};

const getTaskText = (taskStatus) => {
  const textMap = {
    not_started: '未开始 / Not Started',
    in_progress: '进行中 / In Progress',
    completed: '已完成 / Completed',
  };
  return textMap[taskStatus] || '未知 / Unknown';
};

const getLanguageName = (code) => {
  const language = languages.find(lang => lang.code === code);
  return language ? language.name : code;
};

const getRequirementText = (req) => {
  const reqMap = {
    lqa: '语言质量保证 / LQA',
    imageTranslation: '图像文本翻译 / Image Translation',
  };
  return reqMap[req] || req;
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const viewProject = (project) => {
  console.log('查看项目:', project);
  console.log('当前用户ID:', props.userId, '类型:', typeof props.userId);
  console.log('项目created_by:', project.created_by, '类型:', typeof project.created_by);
  
  // 检查用户是否已登录
  if (props.userId === null || props.userId === undefined) {
    console.log('viewProject - 用户未登录或ID为null');
    Message.error('您需要登录才能查看项目 / You need to login to view projects');
    return;
  }
  
  const canView = canViewProject(project);
  console.log('canViewProject结果:', canView);
  
  if (!canView) {
    Message.error('您没有权限查看此项目 / You do not have permission to view this project');
    return;
  }
  
  currentProject.value = {
    ...project,
    tasks: {
      translation: {
        status: project.taskTranslation || 'not_started',
        assignee: '',
        deadline: null,
        notes: '',
      },
      lqa: {
        status: project.taskLQA || 'not_started',
        assignee: '',
        deadline: null,
        notes: '',
      },
    },
  };
  drawerTitle.value = `项目详情 / Project Details: ${project.projectName}`;
  drawerVisible.value = true;
  isEditing.value = false;
};

const editProject = (project) => {
  console.log('编辑项目:', project);
  console.log('当前用户ID:', props.userId, '类型:', typeof props.userId);
  console.log('项目created_by:', project.created_by, '类型:', typeof project.created_by);
  
  // 检查用户是否已登录
  if (props.userId === null || props.userId === undefined) {
    console.log('editProject - 用户未登录或ID为null');
    Message.error('您需要登录才能编辑项目 / You need to login to edit projects');
    return;
  }
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    console.log('editProject - 用户不是LM，无权编辑');
    Message.error('只有本地化经理可以编辑项目 / Only Localization Managers can edit projects');
    return;
  }
  
  currentProject.value = {
    ...project,
    tasks: {
      translation: {
        status: project.taskTranslation || 'not_started',
        assignee: '',
        deadline: null,
        notes: '',
      },
      lqa: {
        status: project.taskLQA || 'not_started',
        assignee: '',
        deadline: null,
        notes: '',
      },
    },
  };
  drawerTitle.value = `编辑项目 / Edit Project: ${project.projectName}`;
  drawerVisible.value = true;
  isEditing.value = true;
};

const saveProject = async () => {
  if (!currentProject.value) return;
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('只有本地化经理可以更新项目 / Only Localization Managers can update projects');
    return;
  }
  
  try {
    // 准备更新的项目数据
    const updatedProject = {
      ...currentProject.value,
      taskTranslation: currentProject.value.tasks.translation.status,
      taskLQA: currentProject.value.tasks.lqa.status,
    };
    
    // 发送更新请求
    const response = await axios.put(`http://localhost:5000/api/projects/${updatedProject.id}`, updatedProject);
    
    if (response.status === 200) {
      Message.success('项目更新成功 / Project updated successfully');
      fetchProjects(); // 刷新项目列表
      drawerVisible.value = false;
    } else {
      throw new Error('更新失败 / Update failed');
    }
  } catch (error) {
    console.error('Error updating project:', error);
    Message.error(`更新失败: ${error.message} / Update failed: ${error.message}`);
  }
};

const sendEmail = (project) => {
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('只有本地化经理可以发送项目邮件 / Only Localization Managers can send project emails');
    return;
  }
  
  currentProject.value = project;
  emailForm.to = '';
  emailForm.cc = '';
  emailForm.subject = `[LingoFlows] ${project.projectName} - 项目更新 / Project Update`;
  emailForm.content = `尊敬的合作伙伴，\n\n这是关于项目 ${project.projectName} 的更新。\n\n祝好，\n${project.projectManager}`;
  emailAttachments.value = [];
  emailModalVisible.value = true;
};

const handleEmailAttachmentChange = (options) => {
  console.log('Email attachment change event:', options);
  
  // 处理上传成功的情况
  if (options.file.status === 'done') {
    const response = options.file.response;
    if (response && response.filename) {
      Message.success(`附件 ${options.file.name} 上传成功 / Attachment ${options.file.name} uploaded successfully`);
    }
  }
  
  // 处理上传失败的情况
  if (options.file.status === 'error') {
    console.error('Attachment upload error:', options.file.response);
    Message.error(`附件 ${options.file.name} 上传失败 / Attachment ${options.file.name} upload failed`);
  }
  
  // 更新附件列表
  emailAttachments.value = options.fileList;
};

const sendProjectEmail = async () => {
  if (!currentProject.value) return;
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('只有本地化经理可以发送项目邮件 / Only Localization Managers can send project emails');
    return;
  }
  
  // 表单验证
  if (!emailForm.to || !emailForm.subject || !emailForm.content) {
    Message.error('请填写所有必填字段 / Please fill in all required fields');
    return;
  }
  
  try {
    sendingEmail.value = true;
    
    // 获取已上传附件的文件名
    const attachments = emailAttachments.value
      .filter(file => file.status === 'done' && file.response)
      .map(file => file.response.filename);
    
    // 准备邮件数据
    const emailData = {
      projectId: currentProject.value.id,
      to: emailForm.to,
      cc: emailForm.cc,
      subject: emailForm.subject,
      content: emailForm.content,
      attachments: attachments
    };
    
    // 发送邮件请求
    const response = await axios.post('http://localhost:5000/api/emails', emailData);
    
    if (response.status === 200) {
      Message.success('邮件发送成功 / Email sent successfully');
      emailModalVisible.value = false;
    } else {
      throw new Error('发送失败 / Sending failed');
    }
  } catch (error) {
    console.error('Error sending email:', error);
    Message.error(`发送失败: ${error.message} / Sending failed: ${error.message}`);
  } finally {
    sendingEmail.value = false;
  }
};

const uploadFiles = (project) => {
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('只有本地化经理可以上传项目文件 / Only Localization Managers can upload project files');
    return;
  }
  
  currentProject.value = project;
  uploadForm.fileType = 'source';
  uploadForm.notes = '';
  projectFiles.value = [];
  uploadModalVisible.value = true;
};

const handleProjectFileChange = (options) => {
  console.log('Project file change event:', options);
  
  // 处理上传成功的情况
  if (options.file.status === 'done') {
    const response = options.file.response;
    if (response && response.filename) {
      Message.success(`文件 ${options.file.name} 上传成功 / File ${options.file.name} uploaded successfully`);
    }
  }
  
  // 处理上传失败的情况
  if (options.file.status === 'error') {
    console.error('File upload error:', options.file.response);
    Message.error(`文件 ${options.file.name} 上传失败 / File ${options.file.name} upload failed`);
  }
  
  // 更新文件列表
  projectFiles.value = options.fileList;
};

const submitUploadFiles = async () => {
  if (!currentProject.value) return;
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('只有本地化经理可以上传项目文件 / Only Localization Managers can upload project files');
    return;
  }
  
  // 表单验证
  if (!uploadForm.fileType) {
    Message.error('请选择文件类型 / Please select file type');
    return;
  }
  
  if (projectFiles.value.length === 0) {
    Message.error('请上传至少一个文件 / Please upload at least one file');
    return;
  }
  
  try {
    uploading.value = true;
    
    // 获取已上传文件的文件名
    const uploadedFiles = projectFiles.value
      .filter(file => file.status === 'done' && file.response)
      .map(file => file.response.filename);
    
    if (uploadedFiles.length === 0) {
      throw new Error('没有成功上传的文件 / No successfully uploaded files');
    }
    
    // 准备项目文件数据
    const projectFileData = {
      projectId: currentProject.value.id,
      fileType: uploadForm.fileType,
      notes: uploadForm.notes,
      files: uploadedFiles
    };
    
    // 发送上传请求
    const response = await axios.post('http://localhost:5000/api/project-files', projectFileData);
    
    if (response.status === 201) {
      Message.success('文件上传成功 / Files uploaded successfully');
      uploadModalVisible.value = false;
      projectFiles.value = [];
      uploadForm.fileType = 'source';
      uploadForm.notes = '';
    } else {
      throw new Error('上传失败 / Upload failed');
    }
  } catch (error) {
    console.error('Error uploading project files:', error);
    Message.error(`上传失败: ${error.message} / Upload failed: ${error.message}`);
  } finally {
    uploading.value = false;
  }
};
</script>

<style scoped>
.project-management-container {
  padding: 20px;
}

h2 {
  margin-bottom: 24px;
  color: var(--color-text-1);
}

.action-bar {
  display: flex;
  margin-bottom: 16px;
}

.empty-state {
  padding: 40px 0;
}

:deep(.arco-table-th) {
  background-color: var(--color-fill-2);
}

:deep(.arco-descriptions-item-label) {
  width: 200px;
}
</style> 