<template>
  <div class="project-management-container">
    <h2>项目管理 / Project Management</h2>
    
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
      >
        <a-option value="all">全部 / All</a-option>
        <a-option value="pending">待处理 / Pending</a-option>
        <a-option value="in_progress">进行中 / In Progress</a-option>
        <a-option value="completed">已完成 / Completed</a-option>
        <a-option value="cancelled">已取消 / Cancelled</a-option>
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
          <a-button type="text" size="small" @click="viewProject(record)">
            查看 / View
          </a-button>
          <a-button type="text" size="small" @click="editProject(record)" v-if="props.userRole === 'LM'">
            编辑 / Edit
          </a-button>
          <a-button type="text" size="small" @click="sendEmail(record)" v-if="props.userRole === 'LM'">
            发送邮件 / Send Email
          </a-button>
          <a-button type="text" size="small" @click="uploadFiles(record)" v-if="props.userRole === 'LM' || (props.userRole === 'BO' && canPerformAction(record))">
            上传文件 / Upload Files
          </a-button>
          <a-button @click="() => {
              currentProject.value = record;
              refreshFilesWithMapping();
            }" 
            type="success" 
            :loading="refreshingFiles"
          >
            检查文件 / Check Files
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
        <a-tabs>
          <a-tab-pane key="info" title="项目信息 / Project Info">
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
                  <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">{{ lang.name }}</a-option>
                </a-select>
                <span v-else>{{ getLanguageName(currentProject.sourceLanguage) }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="目标语言 / Target Languages">
                <a-select v-model="currentProject.targetLanguages" multiple v-if="isEditing && props.userRole === 'LM'">
                  <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">{{ lang.name }}</a-option>
                </a-select>
                <div v-else>
                  <a-tag v-for="lang in currentProject.targetLanguages" :key="lang" style="margin: 2px;">
                    {{ getLanguageName(lang) }}
                  </a-tag>
                </div>
              </a-descriptions-item>
              <a-descriptions-item label="字数 / Word Count">
                <a-input-number v-model="currentProject.wordCount" v-if="isEditing && props.userRole === 'LM'" />
                <span v-else>{{ currentProject.wordCount }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="预期交付日期 / Expected Delivery Date">
                <a-date-picker v-model="currentProject.expectedDeliveryDate" v-if="isEditing && props.userRole === 'LM'" />
                <span v-else>{{ formatDate(currentProject.expectedDeliveryDate) }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="附加要求 / Additional Requirements">
                <a-checkbox-group 
                  v-model="currentProject.additionalRequirements" 
                  v-if="isEditing && props.userRole === 'LM'"
                >
                  <a-checkbox value="lqa">语言质量保证 (LQA) / Linguistic Quality Assurance</a-checkbox>
                  <a-checkbox value="imageTranslation">图像文本翻译 / Image Text Translation</a-checkbox>
                </a-checkbox-group>
                <div v-else>
                  <a-tag v-for="req in currentProject.additionalRequirements" :key="req" style="margin: 2px;">
                    {{ getRequirementText(req) }}
                  </a-tag>
                </div>
              </a-descriptions-item>
            </a-descriptions>
            
            <!-- 任务状态和详细信息 -->
            <div v-if="props.userRole === 'LM' && isEditing" style="margin-top: 24px;">
              <h3>任务详情 / Task Details</h3>
              <a-form :model="currentProject.tasks">
                <a-collapse>
                  <a-collapse-item header="翻译任务 / Translation Task" key="1">
                    <a-form-item label="状态 / Status">
                      <a-select v-model="currentProject.tasks.translation.status">
                        <a-option value="not_started">未开始 / Not Started</a-option>
                        <a-option value="in_progress">进行中 / In Progress</a-option>
                        <a-option value="completed">已完成 / Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="负责人 / Assignee">
                      <a-input v-model="currentProject.tasks.translation.assignee" placeholder="翻译人员 / Translator" />
                    </a-form-item>
                    <a-form-item label="截止日期 / Deadline">
                      <a-date-picker v-model="currentProject.tasks.translation.deadline" />
                    </a-form-item>
                    <a-form-item label="备注 / Notes">
                      <a-textarea v-model="currentProject.tasks.translation.notes" placeholder="任务备注 / Task notes" />
                    </a-form-item>
                  </a-collapse-item>
                  <a-collapse-item header="LQA任务 / LQA Task" key="2">
                    <a-form-item label="状态 / Status">
                      <a-select v-model="currentProject.tasks.lqa.status">
                        <a-option value="not_started">未开始 / Not Started</a-option>
                        <a-option value="in_progress">进行中 / In Progress</a-option>
                        <a-option value="completed">已完成 / Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="负责人 / Assignee">
                      <a-input v-model="currentProject.tasks.lqa.assignee" placeholder="LQA人员 / LQA Specialist" />
                    </a-form-item>
                    <a-form-item label="截止日期 / Deadline">
                      <a-date-picker v-model="currentProject.tasks.lqa.deadline" />
                    </a-form-item>
                    <a-form-item label="备注 / Notes">
                      <a-textarea v-model="currentProject.tasks.lqa.notes" placeholder="任务备注 / Task notes" />
                    </a-form-item>
                  </a-collapse-item>
                </a-collapse>
              </a-form>
            </div>
            
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
          </a-tab-pane>
          
          <a-tab-pane key="files" title="项目文件 / Project Files">
            <a-spin :loading="loadingFiles">
              <div v-if="projectFileList.length === 0" style="text-align: center; margin: 20px 0;">
                <p>暂无项目文件 / No project files</p>
              </div>
              <div v-else>
                <div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                  <a-button type="primary" @click="downloadAllProjectFiles" :loading="downloadingFiles">
                    下载所有文件 / Download All Files
                  </a-button>
                  <a-button type="primary" @click="refreshFilesWithMapping" :loading="refreshingFiles">
                    刷新文件列表 / Refresh Files
                  </a-button>
                </div>
                <a-timeline>
                  <a-timeline-item 
                    v-for="fileGroup in projectFileList" 
                    :key="fileGroup.id"
                    :label="fileGroup.created_at ? new Date(fileGroup.created_at).toLocaleString() : '未知时间 / Unknown Time'"
                  >
                    <template #dot>
                      <icon-file />
                    </template>
                    <h4>项目文件组 / Project File Group</h4>
                    <p v-if="fileGroup.description">{{ fileGroup.description }}</p>
                    <a-space direction="vertical" style="width: 100%;">
                      <template v-if="fileGroup.fileList && fileGroup.fileList.length > 0">
                        <a-card 
                          v-for="file in fileGroup.fileList" 
                          :key="file.id || 'unknown'"
                          hoverable
                          size="small"
                          style="margin-bottom: 8px;"
                        >
                          <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                              <span>{{ file.name || file.filename || '未知文件 / Unknown File' }}</span>
                              <div v-if="file.created_at" style="font-size: 12px; color: #999;">
                                {{ new Date(file.created_at).toLocaleString() }}
                              </div>
                            </div>
                            <a-button 
                              type="primary" 
                              size="mini"
                              @click="downloadFile(file.url, file.name || file.filename, file)"
                              :loading="file.downloading"
                            >
                              <template #icon><icon-download /></template>
                              下载 / Download
                            </a-button>
                          </div>
                        </a-card>
                      </template>
                      <template v-else>
                        <p style="color: #999;">
                          文件列表为空或格式不正确 / Empty or invalid file list
                          <pre style="font-size: 12px; color: #666;">{{ JSON.stringify(fileGroup, null, 2) }}</pre>
                        </p>
                      </template>
                    </a-space>
                  </a-timeline-item>
                </a-timeline>
              </div>
            </a-spin>
          </a-tab-pane>
        </a-tabs>
        
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
      @cancel="handleUploadCancel"
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
            v-model:file-list="projectFiles"
            @change="handleProjectFileChange"
            :headers="uploadHeaders"
            multiple
            :show-upload-button="true"
            list-type="text"
            :show-remove-button="true"
            :custom-request="customRequest"
            :limit="5"
            :tip="'支持单个文件最大10MB / Max 10MB per file'"
          >
            <template #upload-button>
              <a-button type="primary">
                选择文件 / Select Files
              </a-button>
            </template>
          </a-upload>
          <div style="margin-top: 8px; color: #999;">
            上传文件将会自动关联到当前项目 / Files will be automatically linked to the current project
          </div>
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
import { Message, Modal } from '@arco-design/web-vue';
import { IconFile, IconDownload } from '@arco-design/web-vue/es/icon';
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

// 状态
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
const projectFileList = ref([]);
const loadingFiles = ref(false);
const diagnosing = ref(false);
const diagnosticsResult = ref(null);
const fixing = ref(false);
const refreshingFiles = ref(false); // 添加新的加载状态
const downloadingFiles = ref(false); // 添加下载文件加载状态

// 上传请求头（用于认证）
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`
  };
});

// 邮件表单
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
    console.log('canViewProject - 用户是PM，有权限');
    return true; // PM可以查看所有项目
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
    console.log('canPerformAction - 用户是PM，有权限');
    return true; // PM可以执行所有操作
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

// 根据语言代码获取语言名称
const getLanguageName = (code) => {
  if (!code) return '未指定 / Not specified';
  const language = languages.find(lang => lang.code === code);
  return language ? language.name : code;
};

// 格式化日期显示
const formatDate = (dateString) => {
  if (!dateString) return '未设置 / Not set';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString; // 如果无法解析，则返回原始字符串
    return date.toLocaleDateString();
  } catch (error) {
    console.error('日期格式化错误:', error);
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
  
  // 获取项目文件
  console.log('准备获取项目文件:', project.id);
  // 清空旧的项目文件列表
  projectFileList.value = [];
  // 开启加载状态
  loadingFiles.value = true;
  // 设置一个短暂延迟，确保界面已更新
  setTimeout(() => {
    // 使用新的刷新函数，自动修复文件映射
    refreshFilesWithMapping();
  }, 300);
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
    
    // 获取已上传附件的文件ID
    const attachmentIds = emailAttachments.value
      .filter(file => file.status === 'done' && file.response)
      .map(file => file.response.file_id);
    
    // 准备邮件数据
    const emailData = {
      projectId: currentProject.value.id,
      to: emailForm.to,
      cc: emailForm.cc,
      subject: emailForm.subject,
      content: emailForm.content,
      attachmentIds: attachmentIds // 改为使用文件ID数组
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
  if (props.userRole !== 'LM' && !(props.userRole === 'BO' && canPerformAction(project))) {
    Message.error('您没有权限上传项目文件 / You do not have permission to upload project files');
    return;
  }
  
  currentProject.value = project;
  
  // 重置上传表单和状态
  uploadForm.fileType = 'source';
  uploadForm.notes = '';
  projectFiles.value = [];
  uploading.value = false;
  
  // 重置可能的错误状态
  setTimeout(() => {
    console.log('上传弹窗已重置，当前projectFiles:', projectFiles.value);
  }, 100);
  
  uploadModalVisible.value = true;
};

const handleProjectFileChange = (info) => {
  console.log('Project file change event:', info);
  
  // 在ArcoVue组件中，fileList可能在info.fileList中
  const fileList = info.fileList || info;
  
  // 确保我们有一个数组
  if (!Array.isArray(fileList)) {
    console.error('无效的文件列表结构:', info);
    projectFiles.value = [];
    return;
  }
  
  projectFiles.value = fileList;
  console.log('处理后的projectFiles.value:', projectFiles.value);
  
  // 检查是否有新上传完成的文件
  if (fileList.length > 0) {
    const lastFile = fileList[fileList.length - 1];
    
    // 检查是否是新上传完成的文件
    if (lastFile && lastFile.status === 'done' && lastFile.response) {
      console.log('文件上传成功:', lastFile.name, '响应:', lastFile.response);
      Message.success(`附件 ${lastFile.name} 上传成功 / Attachment ${lastFile.name} uploaded successfully`);
    }
    
    // 检查是否有失败的文件
    const failedFile = fileList.find(file => file.status === 'error');
    if (failedFile) {
      console.error('文件上传失败:', failedFile.name, '错误信息:', failedFile.error);
      
      // 如果fileList包含自动移除的机制，我们需要手动处理
      // 某些UI框架会自动处理错误文件，但我们可以提供更好的用户反馈
      let errorMessage = `附件 ${failedFile.name} 上传失败`;
      
      // 如果有详细的错误信息，添加到消息中
      if (failedFile.error && failedFile.error.message) {
        errorMessage += `: ${failedFile.error.message}`;
      } else if (failedFile.response && failedFile.response.error) {
        errorMessage += `: ${failedFile.response.error}`;
      }
      
      Message.error(errorMessage);
      
      // 检查认证问题
      if (errorMessage.includes('Authorization') || 
          errorMessage.includes('token') || 
          errorMessage.includes('认证') || 
          errorMessage.includes('authentication')) {
        // 认证问题，可能需要重新登录
        setTimeout(() => {
          Message.warning('认证失败，请尝试重新登录 / Authentication failed, please try logging in again');
        }, 1000);
      }
    }
  }
};

// 提交上传的文件
const submitUploadFiles = async () => {
  if (!currentProject.value) {
    Message.error('项目数据不存在 / Project data does not exist');
    return;
  }
  
  // 检查用户角色
  if (props.userRole !== 'LM' && !(props.userRole === 'BO' && canPerformAction(currentProject.value))) {
    Message.error('您没有权限上传项目文件 / You do not have permission to upload project files');
    return;
  }
  
  if (projectFiles.value.length === 0) {
    Message.error('请至少上传一个文件 / Please upload at least one file');
    return;
  }
  
  try {
    uploading.value = true;
    
    // 获取已上传文件的ID
    const uploadedFileIds = projectFiles.value
      .filter(file => file.status === 'done' && file.response)
      .map(file => {
        console.log('Processing uploaded file:', file);
        // 从响应中获取文件ID
        return file.response.file_id;
      });
    
    if (uploadedFileIds.length === 0) {
      Message.error('没有成功上传的文件 / No successfully uploaded files');
      return;
    }
    
    console.log('准备关联的文件IDs:', uploadedFileIds);
    
    // 准备项目文件数据
    const projectFileData = {
      projectId: currentProject.value.id,
      fileType: uploadForm.fileType,
      notes: uploadForm.notes,
      fileIds: uploadedFileIds // 改为使用文件IDs数组
    };
    
    console.log('Submitting project files:', projectFileData);
    
    // 发送项目文件请求
    const response = await axios.post('http://localhost:5000/api/project-files', projectFileData, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (response.status === 200 || response.status === 201) {
      Message.success('项目文件上传成功 / Project files uploaded successfully');
      uploadModalVisible.value = false;
      
      // 刷新项目文件列表
      await fetchProjectFiles(currentProject.value.id);
      
      // 自动执行文件映射修复，确保文件关联正确
      console.log('自动执行文件映射修复...');
      Message.loading({
        content: '正在修复文件映射，请稍候... / Fixing file mappings, please wait...',
        duration: 0
      });
      
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('未找到认证令牌，无法修复文件映射');
          return;
        }
        
        // 添加重试机制
        let retries = 0;
        const maxRetries = 2;
        let success = false;
        let fixResponse;
        
        while (!success && retries <= maxRetries) {
          try {
            if (retries > 0) {
              console.log(`尝试第 ${retries} 次重试修复...`);
            }
            
            fixResponse = await axios.post('http://localhost:5000/api/fix-file-mappings', {}, {
              headers: {
                'Authorization': `Bearer ${token}`
              },
              timeout: 30000 // 30秒超时
            });
            
            success = true;
          } catch (error) {
            retries++;
            console.error(`修复尝试 ${retries} 失败:`, error);
            
            if (retries > maxRetries) {
              throw error; // 重试次数用完，抛出错误
            }
            
            // 等待1秒后重试
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
        
        console.log('修复结果:', fixResponse.data);
        
        if (fixResponse.data.status === 'success') {
          const newMappings = fixResponse.data.after_count - fixResponse.data.before_count;
          
          if (newMappings > 0) {
            Message.success({
              content: `文件映射已自动修复! 新增 ${newMappings} 个映射 / File mappings fixed! Added ${newMappings} mappings`,
              duration: 5000
            });
          } else {
            console.log('没有需要修复的文件映射');
          }
          
          // 再次刷新项目文件列表，确保显示最新数据
          await fetchProjectFiles(currentProject.value.id);
        } else {
          console.warn('修复结果未成功:', fixResponse.data);
        }
      } catch (error) {
        console.error('自动修复文件映射失败:', error);
        // 不向用户显示错误，避免干扰正常流程
      } finally {
        Message.destroy(); // 清除加载消息
      }
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

// 添加获取项目文件的函数
const fetchProjectFiles = async (projectId) => {
  if (!projectId) {
    console.error('项目ID为空，无法获取文件');
    return;
  }
  
  loadingFiles.value = true;
  
  try {
    // 获取存储的令牌
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('获取项目文件失败: 未找到令牌');
      loadingFiles.value = false;
      return;
    }
    
    const headers = {
      'Authorization': `Bearer ${token}`
    };
    
    console.log(`获取项目 ${projectId} 的文件`);
    const response = await axios.get(`http://localhost:5000/api/project-files/${projectId}`, { headers });
    
    console.log('项目文件API返回:', response);
    
    if (Array.isArray(response.data)) {
      console.log('项目文件数据:', JSON.stringify(response.data, null, 2));
      
      // 检查项目文件是否为空数组
      if (response.data.length === 0) {
        console.log('项目没有关联文件');
        projectFileList.value = [];
        loadingFiles.value = false;
        return;
      }
      
      // 处理每个文件组的文件列表
      const processedData = response.data.map(fileGroup => {
        console.log('处理文件组:', JSON.stringify(fileGroup, null, 2));
        
        // 确保文件组有必要的字段
        const processedFileGroup = {
          id: fileGroup.id,
          created_at: fileGroup.created_at || new Date().toISOString(),
          fileType: fileGroup.fileType || 'source',
          description: fileGroup.description || '项目文件',
          fileList: []
        };
        
        // 确保fileList是数组且有效
        if (!fileGroup.fileList) {
          console.warn('文件组的fileList缺失:', fileGroup);
          return processedFileGroup;
        }
        
        if (!Array.isArray(fileGroup.fileList)) {
          console.warn('文件组的fileList不是数组:', fileGroup);
          return processedFileGroup;
        }
        
        // 为每个文件添加完整的URL，确保可以正确访问
        processedFileGroup.fileList = fileGroup.fileList.map(file => {
          console.log('处理文件:', JSON.stringify(file, null, 2));
          
          // 检查是否存在有效的文件对象
          if (!file || typeof file !== 'object') {
            console.warn('文件对象无效:', file);
            return null;
          }
          
          // 确保file对象的所有必要字段
          const processedFile = {
            id: file.id,
            name: file.name || file.filename || file.originalName || '未知文件名',
            url: file.url || '',
            type: file.type || file.fileType || file.file_type || 'unknown',
            created_at: file.created_at || file.uploadTime || new Date().toISOString(),
            downloading: false  // 添加下载状态属性
          };
          
          // 确保URL是完整的
          if (processedFile.url && !processedFile.url.startsWith('http')) {
            processedFile.url = `http://localhost:5000${processedFile.url}`;
          }
          
          console.log('处理后的文件:', JSON.stringify(processedFile, null, 2));
          return processedFile;
        }).filter(file => file !== null); // 过滤掉无效的文件
        
        return processedFileGroup;
      });
      
      // 过滤掉没有文件的文件组
      const filteredData = processedData.filter(fileGroup => 
        fileGroup.fileList && fileGroup.fileList.length > 0
      );
      
      projectFileList.value = filteredData;
      console.log('处理后的项目文件列表:', JSON.stringify(projectFileList.value, null, 2));
      
      // 如果没有文件，显示提示信息
      if (filteredData.length === 0) {
        console.log('项目没有关联文件或处理后无有效文件');
      }
    } else {
      console.error('返回的文件数据不是数组:', response.data);
      projectFileList.value = [];
    }
  } catch (error) {
    console.error('获取项目文件失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.data);
    }
    Message.error('获取项目文件失败 / Failed to fetch project files');
    projectFileList.value = [];
  } finally {
    loadingFiles.value = false;
  }
};

// 添加以下函数用于文件类型转换和下载
const getFileTypeText = (fileType) => {
  const typeMap = {
    source: '源文件 / Source Files',
    translation: '翻译文件 / Translation Files',
    lqa: 'LQA报告 / LQA Reports',
    other: '其他文件 / Other Files'
  };
  return typeMap[fileType] || '未知类型 / Unknown Type';
};

const downloadFile = (url, fileName, fileObj) => {
  if (!url) {
    console.error('下载URL为空');
    Message.error('下载链接不可用 / Download URL not available');
    return;
  }
  
  if (!fileName) {
    console.warn('文件名为空，使用默认文件名');
    fileName = '下载文件.txt';
  }
  
  // 如果提供了文件对象，设置下载状态
  if (fileObj) {
    fileObj.downloading = true;
  }
  
  // 创建一个下载链接
  let downloadUrl = url;
  if (!url.startsWith('http')) {
    downloadUrl = `http://localhost:5000${url}`;
  }
  const token = localStorage.getItem('token');
  
  console.log(`准备下载文件: ${fileName}, URL: ${downloadUrl}`);
  
  // 使用axios下载文件
  axios({
    url: downloadUrl,
    method: 'GET',
    responseType: 'blob',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }).then(response => {
    console.log('文件下载成功，准备创建下载链接');
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    Message.success(`文件 ${fileName} 下载成功 / File downloaded successfully`);
  }).catch(error => {
    console.error('Error downloading file:', error);
    
    let errorMessage = '下载文件失败 / Failed to download file';
    if (error.response) {
      errorMessage += `: ${error.response.status} ${error.response.statusText}`;
    }
    
    Message.error(errorMessage);
  }).finally(() => {
    // 如果提供了文件对象，重置下载状态
    if (fileObj) {
      fileObj.downloading = false;
    }
  });
};

// 批量下载文件
const downloadSelectedFiles = (fileIds, zipName = 'project-files.zip') => {
  if (!fileIds || fileIds.length === 0) {
    Message.error('没有选择要下载的文件 / No files selected for download');
    return;
  }
  
  const token = localStorage.getItem('token');
  
  console.log(`准备批量下载文件，文件ID: ${fileIds.join(', ')}`);
  
  // 使用axios下载ZIP文件
  axios({
    url: 'http://localhost:5000/api/files/download-batch',
    method: 'POST',
    responseType: 'blob',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    data: {
      fileIds: fileIds
    }
  }).then(response => {
    console.log('ZIP文件下载成功，准备创建下载链接');
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', zipName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    Message.success(`文件已下载成功 / Files downloaded successfully`);
  }).catch(error => {
    console.error('Error downloading files:', error);
    
    let errorMessage = '下载文件失败 / Failed to download files';
    if (error.response) {
      errorMessage += `: ${error.response.status} ${error.response.statusText}`;
    }
    
    Message.error(errorMessage);
  });
};

// 删除文件
const deleteFile = async (fileId, fileName) => {
  if (!fileId) {
    Message.error('文件ID不可用 / File ID not available');
    return;
  }
  
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('未找到认证令牌 / Authentication token not found');
      return;
    }
    
    // 确认删除
    const confirmed = await Modal.confirm({
      title: '确认删除 / Confirm Deletion',
      content: `确定要删除文件 "${fileName}" 吗？此操作不可撤销。/ Are you sure you want to delete "${fileName}"? This cannot be undone.`,
      okText: '删除 / Delete',
      okButtonProps: { status: 'danger' },
      cancelText: '取消 / Cancel'
    });
    
    if (!confirmed) return;
    
    // 发送删除请求
    const response = await axios.delete(`http://localhost:5000/api/files/${fileId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.status === 200) {
      Message.success(`文件 ${fileName} 已删除 / File deleted successfully`);
      
      // 如果当前正在查看项目，刷新文件列表
      if (currentProject.value && currentProject.value.id) {
        await fetchProjectFiles(currentProject.value.id);
      }
    } else {
      throw new Error('删除失败');
    }
  } catch (error) {
    console.error('Error deleting file:', error);
    
    let errorMessage = '删除文件失败 / Failed to delete file';
    if (error.response) {
      errorMessage += `: ${error.response.data?.error || error.response.statusText}`;
    }
    
    Message.error(errorMessage);
  }
};

// 批量删除文件
const deleteSelectedFiles = async (fileIds) => {
  if (!fileIds || fileIds.length === 0) {
    Message.error('没有选择要删除的文件 / No files selected for deletion');
    return;
  }
  
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('未找到认证令牌 / Authentication token not found');
      return;
    }
    
    // 确认删除
    const confirmed = await Modal.confirm({
      title: '确认批量删除 / Confirm Batch Deletion',
      content: `确定要删除选中的 ${fileIds.length} 个文件吗？此操作不可撤销。/ Are you sure you want to delete ${fileIds.length} selected files? This cannot be undone.`,
      okText: '删除 / Delete',
      okButtonProps: { status: 'danger' },
      cancelText: '取消 / Cancel'
    });
    
    if (!confirmed) return;
    
    // 发送批量删除请求
    const response = await axios.post('http://localhost:5000/api/files/delete-batch', {
      fileIds: fileIds
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.status === 200) {
      Message.success(`已成功删除 ${response.data.message} / Files deleted successfully`);
      
      // 如果当前正在查看项目，刷新文件列表
      if (currentProject.value && currentProject.value.id) {
        await fetchProjectFiles(currentProject.value.id);
      }
    } else {
      throw new Error('批量删除失败');
    }
  } catch (error) {
    console.error('Error deleting files:', error);
    
    let errorMessage = '删除文件失败 / Failed to delete files';
    if (error.response) {
      errorMessage += `: ${error.response.data?.error || error.response.statusText}`;
    }
    
    Message.error(errorMessage);
  }
};

// 自定义文件上传请求处理
const customRequest = (options) => {
  console.log('开始文件上传，options:', options);
  
  // 检查file对象是否存在
  if (!options || !options.file) {
    console.error('错误: options或file为undefined', options);
    if (options && options.onError) {
      options.onError(new Error('文件对象不存在 / File object is missing'));
    }
    return;
  }
  
  const { file, onProgress, onSuccess, onError } = options;
  
  // 检查file是否是File对象或原始文件
  let actualFile = file;
  if (file.file && typeof file.file === 'object') {
    // Arco Design可能将文件封装在file.file中
    console.log('文件被封装在file.file中，使用file.file');
    actualFile = file.file;
  }
  
  // 检查文件对象是否有name属性
  if (!actualFile.name) {
    console.error('错误: 文件对象没有name属性', actualFile);
    onError(new Error('文件对象不完整 / File object is incomplete'));
    return;
  }
  
  console.log('处理文件上传，文件名:', actualFile.name, '文件类型:', actualFile.type, '文件大小:', actualFile.size);
  
  // 检查文件大小
  const maxFileSize = 10 * 1024 * 1024; // 10 MB
  if (actualFile.size > maxFileSize) {
    console.error('文件太大:', actualFile.size, '最大允许:', maxFileSize);
    onError(new Error(`文件太大，最大允许10MB / File too large, max 10MB allowed`));
    return;
  }
  
  const formData = new FormData();
  formData.append('file', actualFile); // 这里的'file'必须与后端的request.files['file']对应
  
  // 获取token
  const token = localStorage.getItem('token');
  if (!token) {
    console.error('未找到认证令牌');
    onError(new Error('未找到认证令牌，请重新登录 / Authentication token not found, please login again'));
    Message.error({
      content: '未找到认证令牌，请重新登录 / Authentication token not found, please login again',
      duration: 5000
    });
    return;
  }
  console.log('验证令牌:', token.substring(0, 10) + '...');
  
  // 发送上传请求
  const xhr = new XMLHttpRequest();
  
  xhr.upload.addEventListener('progress', (event) => {
    const percent = event.loaded / event.total * 100;
    console.log(`上传进度: ${percent.toFixed(2)}%`);
    onProgress({ percent });
  });
  
  xhr.addEventListener('load', () => {
    console.log('上传请求完成，状态:', xhr.status, xhr.statusText);
    
    if (xhr.status >= 200 && xhr.status < 300) {
      try {
        const response = JSON.parse(xhr.responseText);
        console.log('上传成功，响应:', response);
        onSuccess(response);
      } catch (error) {
        console.error('解析上传响应失败:', error, '原始响应:', xhr.responseText);
        onError(new Error('解析响应失败 / Failed to parse response'));
      }
    } else {
      console.error('上传失败，状态码:', xhr.status, '响应:', xhr.responseText);
      
      // 处理认证错误
      if (xhr.status === 401) {
        console.error('认证失败，需要重新登录');
        Message.error({
          content: '认证已过期，请重新登录 / Authentication expired, please login again',
          duration: 5000
        });
        onError(new Error('认证已过期，请重新登录 / Authentication expired, please login again'));
        
        // 可以选择重定向到登录页
        // setTimeout(() => { window.location.href = '/login'; }, 2000);
        return;
      }
      
      // 处理其他错误
      try {
        const errorResponse = JSON.parse(xhr.responseText);
        const errorMessage = errorResponse.error || xhr.statusText;
        console.error('服务器返回错误:', errorMessage);
        onError(new Error(`上传失败 (${xhr.status}): ${errorMessage}`));
        Message.error({
          content: `上传失败: ${errorMessage}`,
          duration: 5000
        });
      } catch (e) {
        onError(new Error(`上传失败 (${xhr.status}): ${xhr.statusText}`));
        Message.error({
          content: `上传失败 (${xhr.status}): ${xhr.statusText}`,
          duration: 5000
        });
      }
    }
  });
  
  xhr.addEventListener('error', (event) => {
    console.error('上传发生网络错误:', event);
    onError(new Error('网络错误，请检查网络连接 / Network error, please check your connection'));
    Message.error({
      content: '网络错误，请检查网络连接 / Network error, please check your connection',
      duration: 5000
    });
  });
  
  xhr.addEventListener('abort', () => {
    console.log('上传被取消');
    onError(new Error('上传被取消 / Upload aborted'));
  });
  
  const url = 'http://localhost:5000/api/upload';
  console.log('准备发送POST请求到:', url);
  xhr.open('POST', url);
  xhr.setRequestHeader('Authorization', `Bearer ${token}`);
  console.log('已设置Authorization头');
  
  // 添加一个超时处理
  xhr.timeout = 30000; // 30秒超时
  xhr.ontimeout = () => {
    console.error('上传请求超时');
    onError(new Error('请求超时，请稍后重试 / Request timeout, please try again later'));
    Message.error({
      content: '请求超时，请稍后重试 / Request timeout, please try again later',
      duration: 5000
    });
  };
  
  // 发送请求
  try {
    console.log('发送FormData，包含文件:', actualFile.name);
    xhr.send(formData);
    console.log('请求已发送');
  } catch (error) {
    console.error('发送请求时出错:', error);
    onError(new Error(`发送请求失败: ${error.message}`));
    Message.error({
      content: `发送请求失败: ${error.message}`,
      duration: 5000
    });
  }
};

const handleUploadCancel = () => {
  // A. 重置上传相关状态
  projectFiles.value = [];
  uploadForm.fileType = 'source';
  uploadForm.notes = '';
  uploading.value = false;
  
  // B. 关闭弹窗
  uploadModalVisible.value = false;
  
  console.log('上传已取消，状态已重置');
};

const runDiagnostics = async () => {
  diagnosing.value = true;
  
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('请先登录 / Please login first');
      return;
    }
    
    const headers = {
      'Authorization': `Bearer ${token}`
    };
    
    console.log('正在运行文件关联诊断...');
    const response = await axios.get('http://localhost:5000/api/diagnostics/file-relations', { headers });
    
    console.log('诊断结果:', response.data);
    diagnosticsResult.value = response.data;
    
    // 显示诊断结果
    Message.info({
      content: `诊断完成: 找到 ${response.data.file_count} 个文件, ${response.data.mapping_count} 个文件映射`,
      duration: 5000
    });
    
    // 如果文件映射数量小于文件数量，说明有未映射的文件，建议修复
    if (response.data.mapping_count < response.data.file_count) {
      const unmappedCount = response.data.file_count - response.data.mapping_count;
      const confirmFix = await Message.confirm({
        title: '发现问题 / Problem Found',
        content: `发现 ${unmappedCount} 个未映射的文件，是否进行自动修复？/ Found ${unmappedCount} unmapped files, run automatic fix?`,
        okText: '修复 / Fix',
        cancelText: '取消 / Cancel'
      });
      
      if (confirmFix) {
        await fixFileMappings();
      }
    }
    
    // 尝试刷新数据
    console.log('尝试刷新项目文件数据...');
    if (currentProject.value) {
      await fetchProjectFiles(currentProject.value.id);
    }
    
  } catch (error) {
    console.error('运行诊断失败:', error);
    Message.error('运行诊断失败 / Failed to run diagnostics');
  } finally {
    diagnosing.value = false;
  }
};

const fixFileMappings = async () => {
  fixing.value = true;
  
  try {
    console.log('正在修复文件映射关系...');
    Message.loading({
      content: '正在修复文件映射，请稍候... / Fixing file mappings, please wait...',
      duration: 0
    });
    
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('请先登录 / Please login first');
      return;
    }
    
    // 添加重试机制
    let retries = 0;
    const maxRetries = 2;
    let success = false;
    let response;
    
    while (!success && retries <= maxRetries) {
      try {
        if (retries > 0) {
          console.log(`尝试第 ${retries} 次重试修复...`);
          Message.info({
            content: `第 ${retries} 次重试修复... / Retry ${retries}...`,
            duration: 2000
          });
        }
        
        response = await axios.post('http://localhost:5000/api/fix-file-mappings', {}, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          timeout: 30000 // 30秒超时
        });
        
        success = true;
      } catch (error) {
        retries++;
        console.error(`修复尝试 ${retries} 失败:`, error);
        
        if (retries > maxRetries) {
          throw error; // 重试次数用完，抛出错误
        }
        
        // 等待1秒后重试
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    console.log('修复结果:', response.data);
    
    if (response.data.status === 'success') {
      const newMappings = response.data.after_count - response.data.before_count;
      
      Message.success({
        content: `修复完成! 修复前: ${response.data.before_count} 映射, 修复后: ${response.data.after_count} 映射, 新增: ${newMappings} 映射`,
        duration: 5000
      });
      
      // 尝试刷新项目数据
      await refreshProjects();
      
      // 如果有选中的项目，刷新项目文件
      if (currentProject.value) {
        await fetchProjectFiles(currentProject.value.id);
      }
      
      // 执行另一次诊断以验证结果
      setTimeout(async () => {
        await runDiagnostics();
      }, 1000);
      
    } else {
      Message.error('修复失败 / Fix failed');
    }
  } catch (error) {
    console.error('修复文件映射失败:', error);
    
    let errorMessage = '修复文件映射失败 / Failed to fix file mappings';
    if (error.response) {
      errorMessage += `: ${error.response.data?.error || error.response.statusText}`;
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    
    Message.error({
      content: errorMessage,
      duration: 5000
    });
  } finally {
    fixing.value = false;
    Message.destroy();
  }
};

// 刷新文件列表并自动修复文件映射
const refreshFilesWithMapping = async () => {
  if (!currentProject.value || !currentProject.value.id) {
    Message.error('项目数据不存在 / Project data does not exist');
    return;
  }
  
  refreshingFiles.value = true;
  
  try {
    console.log('刷新文件列表并修复文件映射...');
    
    // 先刷新文件列表
    await fetchProjectFiles(currentProject.value.id);
    
    // 然后执行文件映射修复
    console.log('自动修复文件映射关系...');
    
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('请先登录 / Please login first');
      return;
    }
    
    // 执行修复
    try {
      const response = await axios.post('http://localhost:5000/api/fix-file-mappings', {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        timeout: 30000 // 30秒超时
      });
      
      console.log('修复结果:', response.data);
      
      if (response.data.status === 'success') {
        const newMappings = response.data.after_count - response.data.before_count;
        console.log(`文件映射已修复: ${newMappings} 个新映射`);
        
        // 再次刷新文件列表，确保显示最新数据
        await fetchProjectFiles(currentProject.value.id);
      } else {
        console.log('文件列表刷新成功，但服务器返回非成功状态');
      }
    } catch (error) {
      console.error('修复文件映射失败:', error);
    }
  } catch (error) {
    console.error('刷新文件列表失败:', error);
  } finally {
    refreshingFiles.value = false;
    Message.destroy(); // 清除所有消息
  }
};

// 批量下载当前项目的所有文件
const downloadAllProjectFiles = async () => {
  if (!currentProject.value || !currentProject.value.id) {
    Message.error('项目数据不存在 / Project data does not exist');
    return;
  }
  
  if (projectFileList.value.length === 0) {
    Message.info('项目没有可下载的文件 / No files available for download');
    return;
  }
  
  downloadingFiles.value = true;
  
  try {
    // 收集当前项目所有文件的ID
    const allFileIds = [];
    
    projectFileList.value.forEach(fileGroup => {
      if (fileGroup.fileList && fileGroup.fileList.length > 0) {
        fileGroup.fileList.forEach(file => {
          if (file.id) {
            allFileIds.push(file.id);
          }
        });
      }
    });
    
    if (allFileIds.length === 0) {
      Message.info('没有找到有效的文件ID / No valid file IDs found');
      return;
    }
    
    console.log(`准备下载 ${allFileIds.length} 个项目文件`);
    
    // 使用已有的批量下载函数
    const projectName = currentProject.value.projectName || 'project';
    const safeProjectName = projectName.replace(/[^a-zA-Z0-9]/g, '_');
    const zipName = `${safeProjectName}_files.zip`;
    
    await downloadSelectedFiles(allFileIds, zipName);
    
    Message.success(`项目文件下载完成 / Project files downloaded successfully`);
  } catch (error) {
    console.error('批量下载文件失败:', error);
    Message.error('批量下载文件失败 / Failed to download files');
  } finally {
    downloadingFiles.value = false;
  }
};
</script>

<style scoped>
/* Add your styles here */
</style>