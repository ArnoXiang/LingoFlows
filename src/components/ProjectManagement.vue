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
          <a-button type="text" size="small" @click="editProject(record)">
            编辑 / Edit
          </a-button>
          <a-button type="text" size="small" @click="sendEmail(record)">
            发送邮件 / Send Email
          </a-button>
          <a-button type="text" size="small" @click="uploadFiles(record)">
            上传文件 / Upload Files
          </a-button>
        </a-space>
      </template>
      
      <!-- 空状态 -->
      <template #empty>
        <div class="empty-state">
          <a-empty description="暂无项目数据 / No project data available" />
        </div>
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
            {{ currentProject.projectName }}
          </a-descriptions-item>
          <a-descriptions-item label="项目状态 / Project Status">
            <a-tag :color="getStatusColor(currentProject.projectStatus)">
              {{ getStatusText(currentProject.projectStatus) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="请求名称 / Request Name">
            {{ currentProject.requestName }}
          </a-descriptions-item>
          <a-descriptions-item label="项目经理 / Project Manager">
            {{ currentProject.projectManager }}
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
        
        <div class="task-management" style="margin-top: 24px;">
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
        
        <div class="drawer-footer" style="margin-top: 24px; text-align: right;">
          <a-space>
            <a-button @click="drawerVisible = false">
              取消 / Cancel
            </a-button>
            <a-button type="primary" @click="saveProject">
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
            @change="handleUploadFilesChange"
            multiple
            directory
          >
            <a-button>选择文件 / Select Files</a-button>
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
import { ref, reactive, computed, onMounted } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';
import { languages } from '../utils/languages';

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

// 过滤后的项目列表
const filteredProjects = computed(() => {
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
  
  return result;
});

// 生命周期钩子
onMounted(() => {
  fetchProjects();
});

// 方法
const fetchProjects = async () => {
  loading.value = true;
  try {
    const response = await axios.get('http://localhost:5000/api/projects');
    projects.value = response.data;
  } catch (error) {
    console.error('Error fetching projects:', error);
    Message.error('获取项目列表失败 / Failed to fetch projects');
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
};

const editProject = (project) => {
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
};

const saveProject = async () => {
  if (!currentProject.value) return;
  
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
  currentProject.value = project;
  emailForm.to = '';
  emailForm.cc = '';
  emailForm.subject = `[LingoFlows] ${project.projectName} - 项目更新 / Project Update`;
  emailForm.content = `尊敬的合作伙伴，\n\n这是关于项目 ${project.projectName} 的更新。\n\n祝好，\n${project.projectManager}`;
  emailAttachments.value = [];
  emailModalVisible.value = true;
};

const handleEmailAttachmentChange = (fileList) => {
  console.log('Email attachment list changed:', fileList);
  emailAttachments.value = fileList;
};

const sendProjectEmail = async () => {
  if (!emailForm.to || !emailForm.subject || !emailForm.content) {
    Message.error('请填写必填字段 / Please fill in all required fields');
    return;
  }
  
  try {
    sendingEmail.value = true;
    
    // 准备邮件数据
    const emailData = {
      projectId: currentProject.value.id,
      to: emailForm.to,
      cc: emailForm.cc,
      subject: emailForm.subject,
      content: emailForm.content,
      attachments: emailAttachments.value.map(file => file.name),
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
  currentProject.value = project;
  uploadForm.fileType = 'source';
  uploadForm.notes = '';
  projectFiles.value = [];
  uploadModalVisible.value = true;
};

const handleUploadFilesChange = (fileList) => {
  console.log('Upload file list changed:', fileList);
  projectFiles.value = fileList;
};

const submitUploadFiles = async () => {
  if (!uploadForm.fileType || projectFiles.value.length === 0) {
    Message.error('请选择文件类型和上传文件 / Please select file type and upload files');
    return;
  }
  
  try {
    uploading.value = true;
    
    // 准备上传数据
    const uploadData = {
      projectId: currentProject.value.id,
      fileType: uploadForm.fileType,
      notes: uploadForm.notes,
      files: projectFiles.value.map(file => file.name),
    };
    
    // 发送上传请求
    const response = await axios.post('http://localhost:5000/api/project-files', uploadData);
    
    if (response.status === 200) {
      Message.success('文件上传成功 / Files uploaded successfully');
      uploadModalVisible.value = false;
    } else {
      throw new Error('上传失败 / Upload failed');
    }
  } catch (error) {
    console.error('Error uploading files:', error);
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