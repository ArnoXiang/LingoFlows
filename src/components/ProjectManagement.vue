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
            <a-select v-model="currentProject.sourceLanguage" v-if="isEditing && props.userRole === 'LM'">
              <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">
                {{ lang.name }}
              </a-option>
            </a-select>
            <span v-else>{{ getLanguageName(currentProject.sourceLanguage) }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="目标语言 / Target Languages">
            <div v-if="isEditing && props.userRole === 'LM'">
              <a-select
                v-model="currentProject.targetLanguages"
                placeholder="选择目标语言 / Select target languages"
                multiple
              >
                <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">
                  {{ lang.name }}
                </a-option>
              </a-select>
            </div>
            <a-space v-else>
              <a-tag v-for="lang in currentProject.targetLanguages" :key="lang">
                {{ getLanguageName(lang) }}
              </a-tag>
            </a-space>
          </a-descriptions-item>
          <a-descriptions-item label="字数 / Word Count">
            <a-input-number v-model="currentProject.wordCount" v-if="isEditing && props.userRole === 'LM'" :min="0" />
            <span v-else>{{ currentProject.wordCount }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="预期交付日期 / Expected Delivery Date">
            <a-date-picker v-model="currentProject.expectedDeliveryDate" v-if="isEditing && props.userRole === 'LM'" />
            <span v-else>{{ formatDate(currentProject.expectedDeliveryDate) }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="附加要求 / Additional Requirements">
            <div v-if="isEditing && props.userRole === 'LM'">
              <a-checkbox-group v-model="currentProject.additionalRequirements">
                <a-checkbox value="lqa">语言质量保证 (LQA) / Linguistic Quality Assurance</a-checkbox>
                <a-checkbox value="imageTranslation">图像文本翻译 / Image Text Translation</a-checkbox>
              </a-checkbox-group>
            </div>
            <a-space v-else>
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
    
    const response = await axios.get('http://localhost:5000/api/projects', { headers });
    console.log('获取项目数据成功:', response.data);
    
    if (Array.isArray(response.data)) {
      console.log('ProjectManagement - 原始项目数据:', response.data);
      
      if (response.data.length > 0) {
        console.log('ProjectManagement - 第一个项目数据示例:', JSON.stringify(response.data[0]));
        console.log('ProjectManagement - 项目数据中是否有id字段:', response.data[0].hasOwnProperty('id'));
      }
      
      // 处理项目数据
      const processedProjects = response.data.map(project => processProject(project));
      
      console.log('ProjectManagement - 处理后的项目数据:', processedProjects);
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

const getRequirementText = (requirement) => {
  const requirementMap = {
    lqa: '语言质量保证 (LQA) / Linguistic Quality Assurance',
    imageTranslation: '图像文本翻译 / Image Text Translation',
  };
  return requirementMap[requirement] || requirement;
};

const getLanguageName = (code) => {
  const language = languages.find(lang => lang.code === code);
  return language ? language.name : code;
};

const formatDate = (dateString) => {
  if (!dateString) return '未设置 / Not Set';
  
  try {
    // 处理日期对象
    if (dateString instanceof Date) {
      return dateString.toLocaleDateString();
    }
    
    // 处理字符串日期
    const date = new Date(dateString);
    if (!isNaN(date.getTime())) {
      return date.toLocaleDateString();
    }
    
    // 如果无法解析，则返回原始字符串
    return dateString;
  } catch (error) {
    console.error('格式化日期时出错:', error);
    return dateString;
  }
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
  
  // 处理任务详细信息
  let translationDeadline = null;
  if (project.translationDeadline) {
    try {
      translationDeadline = new Date(project.translationDeadline);
    } catch (error) {
      console.error('处理翻译截止日期时出错:', error);
    }
  }
  
  let lqaDeadline = null;
  if (project.lqaDeadline) {
    try {
      lqaDeadline = new Date(project.lqaDeadline);
    } catch (error) {
      console.error('处理LQA截止日期时出错:', error);
    }
  }
  
  currentProject.value = {
    ...project,
    tasks: {
      translation: {
        status: project.taskTranslation || 'not_started',
        assignee: project.translationAssignee || '',
        deadline: translationDeadline,
        notes: project.translationNotes || '',
      },
      lqa: {
        status: project.taskLQA || 'not_started',
        assignee: project.lqaAssignee || '',
        deadline: lqaDeadline,
        notes: project.lqaNotes || '',
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
  
  // 处理项目数据，确保日期字段正确
  const processedProject = { ...project };
  
  // 处理预期交付日期
  if (processedProject.expectedDeliveryDate) {
    try {
      // 尝试将日期字符串转换为日期对象
      const dateObj = new Date(processedProject.expectedDeliveryDate);
      if (!isNaN(dateObj.getTime())) {
        processedProject.expectedDeliveryDate = dateObj;
      }
    } catch (error) {
      console.error('处理日期字段时出错:', error);
    }
  }
  
  // 处理任务详细信息
  let translationDeadline = null;
  if (processedProject.translationDeadline) {
    try {
      translationDeadline = new Date(processedProject.translationDeadline);
    } catch (error) {
      console.error('处理翻译截止日期时出错:', error);
    }
  }
  
  let lqaDeadline = null;
  if (processedProject.lqaDeadline) {
    try {
      lqaDeadline = new Date(processedProject.lqaDeadline);
    } catch (error) {
      console.error('处理LQA截止日期时出错:', error);
    }
  }
  
  // 处理任务状态
  currentProject.value = {
    ...processedProject,
    tasks: {
      translation: {
        status: processedProject.taskTranslation || 'not_started',
        assignee: processedProject.translationAssignee || '',
        deadline: translationDeadline,
        notes: processedProject.translationNotes || '',
      },
      lqa: {
        status: processedProject.taskLQA || 'not_started',
        assignee: processedProject.lqaAssignee || '',
        deadline: lqaDeadline,
        notes: processedProject.lqaNotes || '',
      },
    },
  };
  
  drawerTitle.value = `编辑项目 / Edit Project: ${processedProject.projectName}`;
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
    // 格式化日期为字符串
    let formattedExpectedDeliveryDate = currentProject.value.expectedDeliveryDate;
    if (formattedExpectedDeliveryDate instanceof Date) {
      formattedExpectedDeliveryDate = formattedExpectedDeliveryDate.toISOString().split('T')[0]; // 格式化为 YYYY-MM-DD
    }
    console.log('格式化后的日期:', formattedExpectedDeliveryDate);
    
    // 格式化任务截止日期
    let formattedTranslationDeadline = currentProject.value.tasks.translation.deadline;
    if (formattedTranslationDeadline instanceof Date) {
      formattedTranslationDeadline = formattedTranslationDeadline.toISOString().split('T')[0];
    }
    
    let formattedLQADeadline = currentProject.value.tasks.lqa.deadline;
    if (formattedLQADeadline instanceof Date) {
      formattedLQADeadline = formattedLQADeadline.toISOString().split('T')[0];
    }
    
    // 准备更新的项目数据
    const updatedProject = {
      id: currentProject.value.id,
      projectName: currentProject.value.projectName,
      projectStatus: currentProject.value.projectStatus,
      requestName: currentProject.value.requestName,
      projectManager: currentProject.value.projectManager,
      
      // 任务状态
      taskTranslation: currentProject.value.tasks.translation.status,
      taskLQA: currentProject.value.tasks.lqa.status,
      taskTranslationUpdate: currentProject.value.taskTranslationUpdate || 'not_started',
      taskLQAReportFinalization: currentProject.value.taskLQAReportFinalization || 'not_started',
      
      // 任务详细信息
      translationAssignee: currentProject.value.tasks.translation.assignee || '',
      translationDeadline: formattedTranslationDeadline || null,
      translationNotes: currentProject.value.tasks.translation.notes || '',
      
      lqaAssignee: currentProject.value.tasks.lqa.assignee || '',
      lqaDeadline: formattedLQADeadline || null,
      lqaNotes: currentProject.value.tasks.lqa.notes || '',
      
      // 其他信息
      sourceLanguage: currentProject.value.sourceLanguage,
      targetLanguages: Array.isArray(currentProject.value.targetLanguages) 
        ? currentProject.value.targetLanguages.join(',') 
        : currentProject.value.targetLanguages,
      wordCount: currentProject.value.wordCount,
      expectedDeliveryDate: formattedExpectedDeliveryDate,
      additionalRequirements: Array.isArray(currentProject.value.additionalRequirements) 
        ? currentProject.value.additionalRequirements.join(',') 
        : currentProject.value.additionalRequirements,
    };
    
    console.log('准备更新项目数据:', updatedProject);
    
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
    
    let errorMessage = '更新失败 / Update failed';
    
    if (error.response) {
      // 服务器返回了错误响应
      console.error('错误响应:', error.response.data);
      console.error('状态码:', error.response.status);
      errorMessage = `更新失败: ${error.response.data?.error || error.response.statusText}`;
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('请求已发送但没有收到响应:', error.request);
      errorMessage = '无法连接到服务器，请检查网络连接 / Cannot connect to server, please check your network';
    } else {
      // 设置请求时发生错误
      errorMessage = `更新失败: ${error.message}`;
    }
    
    Message.error(errorMessage);
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
      Message.success(`附件 ${options.file.name} 上传成功 / Attachment ${options.file.name} uploaded successfully`);
    }
  }
  
  // 处理上传失败的情况
  if (options.file.status === 'error') {
    console.error('Attachment upload error:', options.file.response);
    Message.error(`附件 ${options.file.name} 上传失败 / Attachment ${options.file.name} upload failed`);
  }
  
  // 更新附件列表
  projectFiles.value = options.fileList;
};

const processProject = (project) => {
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
    taskLQAReportFinalization: project.taskLQAReportFinalization || 'not_started',
    // 确保任务详细信息字段存在
    translationAssignee: project.translationAssignee || '',
    translationDeadline: project.translationDeadline || null,
    translationNotes: project.translationNotes || '',
    lqaAssignee: project.lqaAssignee || '',
    lqaDeadline: project.lqaDeadline || null,
    lqaNotes: project.lqaNotes || '',
  };
};
</script>

<style scoped>

</style>