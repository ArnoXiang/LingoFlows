<template>
  <div class="financial-management-container">
    <h2>财务管理 / Financial Management</h2>
    
    <!-- 只有FT用户可以访问财务管理 -->
    <div v-if="userRole === 'FT'">
      <!-- 项目列表 -->
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
        <a-button type="primary" @click="refreshProjects">
          刷新列表 / Refresh List
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
        
        <!-- 操作列 -->
        <template #operations="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="onViewProject(record)">
              查看 / View
            </a-button>
            <a-button type="text" size="small" @click="onUploadQuote(record)">
              报价录入 / Quote
            </a-button>
          </a-space>
        </template>
      </a-table>
      
      <!-- 项目详情抽屉 -->
      <a-drawer
        v-model:visible="projectDetailVisible"
        :title="currentProject ? `项目详情: ${currentProject.projectName}` : '项目详情 / Project Details'"
        :width="drawerWidth"
        unmount-on-close
      >
        <!-- 自定义拖拽条 -->
        <div 
          class="drawer-resize-handle" 
          v-if="projectDetailVisible"
          @mousedown="startResize"
          title="拖拽调整宽度 / Drag to resize"
        >
          <div class="resize-indicator"></div>
        </div>
        <div v-if="currentProject" class="project-detail">
          <a-descriptions :column="1" bordered size="small" title="基本信息 / Basic Information">
            <a-descriptions-item label="项目名称 / Project Name">{{ currentProject.projectName }}</a-descriptions-item>
            <a-descriptions-item label="项目状态 / Project Status">
              <a-tag :color="getStatusColor(currentProject.projectStatus)">
                {{ getStatusText(currentProject.projectStatus) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="请求名称 / Request Name">{{ currentProject.requestName }}</a-descriptions-item>
            <a-descriptions-item label="项目经理 / Project Manager">{{ currentProject.projectManager }}</a-descriptions-item>
            <a-descriptions-item label="创建时间 / Create Time">{{ formatDate(currentProject.createTime) }}</a-descriptions-item>
            <a-descriptions-item label="源语言 / Source Language">{{ getLanguageName(currentProject.sourceLanguage) }}</a-descriptions-item>
            <a-descriptions-item label="目标语言 / Target Languages">
              <template v-if="Array.isArray(currentProject.targetLanguages) && currentProject.targetLanguages.length > 0">
                <a-space>
                  <a-tag v-for="lang in currentProject.targetLanguages" :key="lang">
                    {{ getLanguageName(lang) }}
                  </a-tag>
                </a-space>
              </template>
              <span v-else>无 / None</span>
            </a-descriptions-item>
            <a-descriptions-item label="字数 / Word Count">{{ currentProject.wordCount }}</a-descriptions-item>
            <a-descriptions-item label="预期交付日期 / Expected Delivery Date">{{ formatDate(currentProject.expectedDeliveryDate) }}</a-descriptions-item>
          </a-descriptions>
          
          <a-divider />
          
          <a-descriptions :column="1" bordered size="small" title="任务信息 / Task Information">
            <!-- 翻译任务 -->
            <a-descriptions-item label="翻译任务 / Translation Task">
              <div class="task-info">
                <div class="task-progress">
                  <a-progress
                    :percent="getTaskProgress(currentProject.taskTranslation)"
                    :status="getTaskStatus(currentProject.taskTranslation)"
                    :show-text="true"
                    size="small"
                  />
                </div>
                <div class="task-detail">
                  <div><strong>任务状态 / Status:</strong> {{ getTaskText(currentProject.taskTranslation) }}</div>
                  <div><strong>负责人 / Assignee:</strong> {{ currentProject.translationAssignee || '未分配 / Not assigned' }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(currentProject.translationDeadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ currentProject.translationNotes || '无 / None' }}</div>
                </div>
                <!-- 报价信息 -->
                <div v-if="taskQuotes.translation" class="quote-info">
                  <div class="quote-header">报价信息 / Quote Information</div>
                  <div><strong>语言 / Language:</strong> {{ getLanguageName(taskQuotes.translation.language) }}</div>
                  <div><strong>负责人 / Vendor:</strong> {{ taskQuotes.translation.assignee }}</div>
                  <div><strong>金额 / Amount:</strong> {{ taskQuotes.translation.quoteAmount }} {{ taskQuotes.translation.currency }}</div>
                  <div><strong>字数 / Word Count:</strong> {{ taskQuotes.translation.wordCount }}</div>
                  <div><strong>单价 / Unit Price:</strong> {{ taskQuotes.translation.unitPrice }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(taskQuotes.translation.deadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ taskQuotes.translation.notes || '无 / None' }}</div>
                </div>
              </div>
            </a-descriptions-item>
            
            <!-- LQA任务 -->
            <a-descriptions-item label="LQA任务 / LQA Task">
              <div class="task-info">
                <div class="task-progress">
                  <a-progress
                    :percent="getTaskProgress(currentProject.taskLQA)"
                    :status="getTaskStatus(currentProject.taskLQA)"
                    :show-text="true"
                    size="small"
                  />
                </div>
                <div class="task-detail">
                  <div><strong>任务状态 / Status:</strong> {{ getTaskText(currentProject.taskLQA) }}</div>
                  <div><strong>负责人 / Assignee:</strong> {{ currentProject.lqaAssignee || '未分配 / Not assigned' }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(currentProject.lqaDeadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ currentProject.lqaNotes || '无 / None' }}</div>
                </div>
                <!-- 报价信息 -->
                <div v-if="taskQuotes.lqa" class="quote-info">
                  <div class="quote-header">报价信息 / Quote Information</div>
                  <div><strong>语言 / Language:</strong> {{ getLanguageName(taskQuotes.lqa.language) }}</div>
                  <div><strong>负责人 / Vendor:</strong> {{ taskQuotes.lqa.assignee }}</div>
                  <div><strong>金额 / Amount:</strong> {{ taskQuotes.lqa.quoteAmount }} {{ taskQuotes.lqa.currency }}</div>
                  <div><strong>字数 / Word Count:</strong> {{ taskQuotes.lqa.wordCount }}</div>
                  <div><strong>单价 / Unit Price:</strong> {{ taskQuotes.lqa.unitPrice }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(taskQuotes.lqa.deadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ taskQuotes.lqa.notes || '无 / None' }}</div>
                </div>
              </div>
            </a-descriptions-item>
            
            <!-- 翻译更新 -->
            <a-descriptions-item label="翻译更新 / Translation Update">
              <div class="task-info">
                <div class="task-progress">
                  <a-progress
                    :percent="getTaskProgress(currentProject.taskTranslationUpdate)"
                    :status="getTaskStatus(currentProject.taskTranslationUpdate)"
                    :show-text="true"
                    size="small"
                  />
                </div>
                <div class="task-detail">
                  <div><strong>任务状态 / Status:</strong> {{ getTaskText(currentProject.taskTranslationUpdate) }}</div>
                  <div><strong>负责人 / Assignee:</strong> {{ currentProject.translationUpdateAssignee || '未分配 / Not assigned' }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(currentProject.translationUpdateDeadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ currentProject.translationUpdateNotes || '无 / None' }}</div>
                </div>
                <!-- 报价信息 -->
                <div v-if="taskQuotes.translationUpdate" class="quote-info">
                  <div class="quote-header">报价信息 / Quote Information</div>
                  <div><strong>语言 / Language:</strong> {{ getLanguageName(taskQuotes.translationUpdate.language) }}</div>
                  <div><strong>负责人 / Vendor:</strong> {{ taskQuotes.translationUpdate.assignee }}</div>
                  <div><strong>金额 / Amount:</strong> {{ taskQuotes.translationUpdate.quoteAmount }} {{ taskQuotes.translationUpdate.currency }}</div>
                  <div><strong>字数 / Word Count:</strong> {{ taskQuotes.translationUpdate.wordCount }}</div>
                  <div><strong>单价 / Unit Price:</strong> {{ taskQuotes.translationUpdate.unitPrice }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(taskQuotes.translationUpdate.deadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ taskQuotes.translationUpdate.notes || '无 / None' }}</div>
                </div>
              </div>
            </a-descriptions-item>
            
            <!-- LQA报告定稿 -->
            <a-descriptions-item label="LQA报告定稿 / LQA Report Finalization">
              <div class="task-info">
                <div class="task-progress">
                  <a-progress
                    :percent="getTaskProgress(currentProject.taskLQAReportFinalization)"
                    :status="getTaskStatus(currentProject.taskLQAReportFinalization)"
                    :show-text="true"
                    size="small"
                  />
                </div>
                <div class="task-detail">
                  <div><strong>任务状态 / Status:</strong> {{ getTaskText(currentProject.taskLQAReportFinalization) }}</div>
                  <div><strong>负责人 / Assignee:</strong> {{ currentProject.lqaReportFinalizationAssignee || '未分配 / Not assigned' }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(currentProject.lqaReportFinalizationDeadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ currentProject.lqaReportFinalizationNotes || '无 / None' }}</div>
                </div>
                <!-- 报价信息 -->
                <div v-if="taskQuotes.lqaReportFinalization" class="quote-info">
                  <div class="quote-header">报价信息 / Quote Information</div>
                  <div><strong>语言 / Language:</strong> {{ getLanguageName(taskQuotes.lqaReportFinalization.language) }}</div>
                  <div><strong>负责人 / Vendor:</strong> {{ taskQuotes.lqaReportFinalization.assignee }}</div>
                  <div><strong>金额 / Amount:</strong> {{ taskQuotes.lqaReportFinalization.quoteAmount }} {{ taskQuotes.lqaReportFinalization.currency }}</div>
                  <div><strong>字数 / Word Count:</strong> {{ taskQuotes.lqaReportFinalization.wordCount }}</div>
                  <div><strong>单价 / Unit Price:</strong> {{ taskQuotes.lqaReportFinalization.unitPrice }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(taskQuotes.lqaReportFinalization.deadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ taskQuotes.lqaReportFinalization.notes || '无 / None' }}</div>
                </div>
              </div>
            </a-descriptions-item>
          </a-descriptions>
          
          <div class="drawer-footer">
            <a-button @click="projectDetailVisible = false">关闭 / Close</a-button>
          </div>
        </div>
      </a-drawer>
      
      <!-- 报价录入对话框 -->
      <QuoteUploader
        ref="quoteUploaderRef"
        :userRole="userRole"
        :userId="userId"
        @uploaded="handleQuoteUploaded"
      />
    </div>
    
    <!-- 非FT用户无权访问 -->
    <div v-else class="no-permission">
      <a-result
        status="403"
        title="无权访问 / Access Denied"
        subtitle="只有财务团队成员可以访问此页面 / Only Financial Team members can access this page"
      >
        <template #extra>
          <a-button type="primary">返回首页 / Back to Home</a-button>
        </template>
      </a-result>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';
import { IconFile } from '@arco-design/web-vue/es/icon';
import QuoteUploader from './finance/QuoteUploader.vue';
import { 
  getStatusColor, 
  getStatusText, 
  getTaskProgress, 
  getTaskStatus, 
  getTaskText,
  getLanguageName,
  formatDate,
  processProject
} from './project/utils/projectUtils';

// 接收用户角色和ID作为props
const props = defineProps({
  userRole: {
    type: String,
    default: ''
  },
  userId: {
    type: Number,
    default: null
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
    title: '操作 / Operations',
    slotName: 'operations',
    width: 200,
    resizable: true,
  },
];

// 状态
const projects = ref([]);
const loading = ref(false);
const searchKeyword = ref('');
const statusFilter = ref('all');
const projectDetailVisible = ref(false);
const currentProject = ref(null);
const quoteUploaderRef = ref(null);
const drawerWidth = ref(800); // 添加抽屉宽度状态
const taskQuotes = ref({
  translation: null,
  lqa: null,
  translationUpdate: null,
  lqaReportFinalization: null
});

// 拖拽相关状态
const isResizing = ref(false);
const minDrawerWidth = 600; // 最小宽度
const maxDrawerWidth = 1200; // 最大宽度

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
  if (props.userRole === 'FT') {
    console.log('FinancialManagement组件挂载，FT角色，立即获取项目数据');
    
    // 清空项目列表，避免可能的缓存问题
    projects.value = [];
    
    // 设置短暂延迟确保DOM更新
    setTimeout(() => {
      fetchProjects();
      
      // 如果第一次获取为空，尝试再次获取
      setTimeout(() => {
        if (projects.value.length === 0) {
          console.log('项目列表为空，尝试再次获取');
          fetchProjects();
        }
      }, 1000);
    }, 100);
  } else {
    console.log(`FinancialManagement组件挂载，非FT角色 (${props.userRole})，不获取项目数据`);
  }
});

// 当用户ID或角色变化时重新获取项目
watch([() => props.userId, () => props.userRole], () => {
  if (props.userRole === 'FT') {
    fetchProjects();
  }
});

// 获取项目列表
const fetchProjects = async () => {
  if (!props.userId) {
    console.log('未获取项目数据：用户ID为空');
    return;
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
    
    // 直接使用项目API接口，后端已经处理FT角色的权限
    console.log('发送请求到: http://localhost:5000/api/projects');
    
    const response = await axios.get('http://localhost:5000/api/projects', { headers });
    console.log(`获取项目数据成功，项目数量: ${response.data.length}`);
    
    if (Array.isArray(response.data)) {
      // 处理项目数据
      const processedProjects = response.data.map(project => processProject(project));
      
      console.log(`FinancialManagement - 处理后的项目数据: ${processedProjects.length} 条记录`);
      
      if (processedProjects.length === 0 && props.userRole === 'FT') {
        console.log('项目列表为空但角色是FT，尝试使用备用参数');
        
        // 尝试使用备用参数
        try {
          const allProjectsResponse = await axios.get('http://localhost:5000/api/projects?all=true', { headers });
          console.log(`备用请求成功，项目数量: ${allProjectsResponse.data.length}`);
          
          if (Array.isArray(allProjectsResponse.data) && allProjectsResponse.data.length > 0) {
            const allProjects = allProjectsResponse.data.map(project => processProject(project));
            projects.value = allProjects;
          } else {
            projects.value = [];
          }
        } catch (innerError) {
          console.error('备用请求失败:', innerError);
          projects.value = processedProjects; // 退回到原始结果
        }
      } else {
        projects.value = processedProjects;
      }
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
    
    // 尝试其他备用方法获取项目
    console.log('尝试备用方法获取项目...');
    try {
      const fallbackResponse = await axios.get('http://localhost:5000/api/projects?fallback=true', { 
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (Array.isArray(fallbackResponse.data) && fallbackResponse.data.length > 0) {
        const fallbackProjects = fallbackResponse.data.map(project => processProject(project));
        projects.value = fallbackProjects;
        console.log(`备用方法获取项目成功: ${fallbackProjects.length} 条记录`);
      } else {
        Message.error('获取项目列表失败 / Failed to fetch projects');
        projects.value = [];
      }
    } catch (fallbackError) {
      console.error('备用方法也失败:', fallbackError);
      Message.error('获取项目列表失败 / Failed to fetch projects');
      projects.value = [];
    }
  } finally {
    loading.value = false;
  }
};

// 刷新项目列表
const refreshProjects = () => {
  fetchProjects();
};

// 搜索处理
const handleSearch = () => {
  console.log('Searching for:', searchKeyword.value);
};

// 状态筛选变化处理
const handleStatusChange = () => {
  console.log('状态筛选变更为:', statusFilter.value);
};

// 查看项目详情
const onViewProject = async (project) => {
  currentProject.value = project;
  projectDetailVisible.value = true;
  
  // 清空之前的报价数据
  taskQuotes.value = {
    translation: null,
    lqa: null,
    translationUpdate: null,
    lqaReportFinalization: null
  };
  
  // 异步加载项目报价数据
  await fetchProjectQuotes(project.id);
  
  // 在抽屉打开后设置拖拽把手位置
  nextTick(() => {
    updateResizeHandlePosition();
  });
};

// 获取项目报价数据
const fetchProjectQuotes = async (projectId) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('未登录或会话已过期 / Not logged in or session expired');
      return;
    }
    
    const headers = {
      'Authorization': `Bearer ${token}`
    };
    
    // 获取项目的报价信息
    const response = await axios.get(`http://localhost:5000/api/quotes?projectId=${projectId}`, { headers });
    
    if (Array.isArray(response.data) && response.data.length > 0) {
      // 按任务类型组织报价数据
      const quotes = response.data;
      
      // 清空现有数据
      taskQuotes.value = {
        translation: null,
        lqa: null,
        translationUpdate: null,
        lqaReportFinalization: null
      };
      
      // 填充报价数据
      quotes.forEach(quote => {
        if (quote.task && taskQuotes.value.hasOwnProperty(quote.task)) {
          taskQuotes.value[quote.task] = quote;
        }
      });
      
      console.log('获取到项目报价数据:', taskQuotes.value);
    } else {
      console.log('未找到项目报价数据');
    }
  } catch (error) {
    console.error('获取项目报价数据失败:', error);
    Message.error('获取项目报价数据失败 / Failed to fetch project quotes');
  }
};

// 开始拖拽
const startResize = (e) => {
  // 阻止默认事件
  e.preventDefault();
  
  isResizing.value = true;
  
  // 计算抽屉左侧边缘的位置(从右侧打开，所以是窗口宽度减去抽屉宽度)
  const drawerLeftEdge = window.innerWidth - drawerWidth.value;
  
  // 设置拖拽把手位置
  const resizeHandle = e.currentTarget;
  resizeHandle.style.left = `${drawerLeftEdge}px`;
  
  // 设置指示器位置
  const indicator = resizeHandle.querySelector('.resize-indicator');
  if (indicator) {
    indicator.style.left = `${drawerLeftEdge + 3}px`;
  }
  
  // 添加鼠标移动和松开事件监听
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
  
  // 添加遮罩避免文本选择等问题
  const resizeMask = document.createElement('div');
  resizeMask.id = 'resize-mask';
  resizeMask.style.position = 'fixed';
  resizeMask.style.top = '0';
  resizeMask.style.left = '0';
  resizeMask.style.right = '0';
  resizeMask.style.bottom = '0';
  resizeMask.style.zIndex = '10000';
  resizeMask.style.cursor = 'col-resize';
  document.body.appendChild(resizeMask);
  
  // 更改鼠标样式
  document.body.style.cursor = 'col-resize';
};

// 处理拖拽过程
const handleResize = (e) => {
  if (!isResizing.value) return;
  
  // 计算新宽度 - 抽屉从右侧打开，所以鼠标越靠左，抽屉越宽
  const newWidth = window.innerWidth - e.clientX;
  
  // 限制在最小和最大宽度范围内
  if (newWidth >= minDrawerWidth && newWidth <= maxDrawerWidth) {
    drawerWidth.value = newWidth;
    
    // 更新拖拽把手和指示器的位置
    const drawerLeftEdge = e.clientX;
    const resizeHandle = document.querySelector('.drawer-resize-handle');
    if (resizeHandle) {
      resizeHandle.style.left = `${drawerLeftEdge}px`;
      
      // 更新指示器位置
      const indicator = resizeHandle.querySelector('.resize-indicator');
      if (indicator) {
        indicator.style.left = `${drawerLeftEdge + 3}px`;
      }
    }
  }
};

// 停止拖拽
const stopResize = () => {
  isResizing.value = false;
  
  // 移除事件监听
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  
  // 移除遮罩
  const resizeMask = document.getElementById('resize-mask');
  if (resizeMask) {
    document.body.removeChild(resizeMask);
  }
  
  // 恢复鼠标样式
  document.body.style.cursor = 'default';
};

// 更新拖拽把手位置
const updateResizeHandlePosition = () => {
  // 计算抽屉左侧边缘的位置
  const drawerLeftEdge = window.innerWidth - drawerWidth.value;
  
  // 获取拖拽把手元素
  const resizeHandle = document.querySelector('.drawer-resize-handle');
  if (resizeHandle) {
    resizeHandle.style.left = `${drawerLeftEdge}px`;
    
    // 获取指示器元素并设置其位置
    const indicator = resizeHandle.querySelector('.resize-indicator');
    if (indicator) {
      indicator.style.left = `${drawerLeftEdge + 3}px`;
    }
  }
};

// 监听抽屉可见性和宽度变化，更新拖拽把手位置
watch([projectDetailVisible, drawerWidth], ([newVisible, newWidth]) => {
  if (newVisible) {
    // 延迟执行以确保抽屉已渲染
    nextTick(() => {
      updateResizeHandlePosition();
    });
  }
});

// 上传报价
const onUploadQuote = (project) => {
  if (quoteUploaderRef.value) {
    quoteUploaderRef.value.openQuoteModal(project);
  }
};

// 处理报价上传完成
const handleQuoteUploaded = async () => {
  Message.success('报价已上传 / Quote has been uploaded');
  await fetchProjects(); // 刷新项目列表
  
  // 如果当前正在查看项目，也刷新项目报价数据
  if (currentProject.value && projectDetailVisible.value) {
    await fetchProjectQuotes(currentProject.value.id);
  }
};
</script>

<style scoped>
.financial-management-container {
  width: 100%;
  height: 100%;
  padding: 20px;
  background-color: var(--color-bg-2);
}

h2 {
  margin-bottom: 24px;
  color: var(--color-text-1);
}

.action-bar {
  display: flex;
  margin-bottom: 16px;
}

.project-detail {
  padding-bottom: 60px;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-progress {
  margin-bottom: 8px;
}

.task-detail > div {
  margin-bottom: 4px;
}

.drawer-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 24px;
  background-color: var(--color-bg-2);
  border-top: 1px solid var(--color-border);
  text-align: right;
}

.no-permission {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.drawer-resize-handle {
  position: fixed;
  top: 0;
  width: 15px;
  height: 100vh;
  background-color: transparent;
  cursor: col-resize;
  z-index: 2001;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-resize-handle:hover,
.drawer-resize-handle:active {
  background-color: rgba(64, 158, 255, 0.3);
}

.resize-indicator {
  width: 6px;
  height: 100vh;
  background-color: rgba(64, 158, 255, 0.5);
  border-radius: 3px;
  position: fixed;
  left: 3px;
  top: 0;
  bottom: 0;
  visibility: visible;
  opacity: 0.3;
  transition: opacity 0.2s;
}

.drawer-resize-handle:hover .resize-indicator {
  opacity: 1;
  background-color: rgba(64, 158, 255, 0.8);
}

:deep(.arco-drawer) {
  overflow: visible !important;
}

.quote-info {
  margin-top: 12px;
  padding: 12px;
  background-color: rgba(64, 158, 255, 0.05);
  border-radius: 4px;
  border-left: 4px solid var(--color-primary-light-4);
}

.quote-header {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 8px;
  color: var(--color-text-1);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 4px;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-progress {
  margin-bottom: 8px;
}

.task-detail, .quote-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drawer-footer {
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 24px;
  background-color: var(--color-bg-2);
  border-top: 1px solid var(--color-border);
  text-align: right;
  margin-top: 16px;
  z-index: 100;
}

:deep(.arco-drawer-content) .arco-tag {
  color: #000000 !important;
}

:deep(.arco-drawer-content) .arco-tag * {
  color: #000000 !important;
}
</style>
