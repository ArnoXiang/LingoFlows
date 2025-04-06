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
        width="700px"
        unmount-on-close
      >
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
                  <div><strong>负责人 / Assignee:</strong> {{ currentProject.translationAssignee || '未分配 / Not assigned' }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(currentProject.translationDeadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ currentProject.translationNotes || '无 / None' }}</div>
                </div>
              </div>
            </a-descriptions-item>
            
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
                  <div><strong>负责人 / Assignee:</strong> {{ currentProject.lqaAssignee || '未分配 / Not assigned' }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(currentProject.lqaDeadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ currentProject.lqaNotes || '无 / None' }}</div>
                </div>
              </div>
            </a-descriptions-item>
            
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
                  <div><strong>负责人 / Assignee:</strong> {{ currentProject.translationUpdateAssignee || '未分配 / Not assigned' }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(currentProject.translationUpdateDeadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ currentProject.translationUpdateNotes || '无 / None' }}</div>
                </div>
              </div>
            </a-descriptions-item>
            
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
                  <div><strong>负责人 / Assignee:</strong> {{ currentProject.lqaReportFinalizationAssignee || '未分配 / Not assigned' }}</div>
                  <div><strong>截止日期 / Deadline:</strong> {{ formatDate(currentProject.lqaReportFinalizationDeadline) }}</div>
                  <div><strong>备注 / Notes:</strong> {{ currentProject.lqaReportFinalizationNotes || '无 / None' }}</div>
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
import { ref, computed, watch, onMounted } from 'vue';
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
const onViewProject = (project) => {
  currentProject.value = project;
  projectDetailVisible.value = true;
};

// 上传报价
const onUploadQuote = (project) => {
  if (quoteUploaderRef.value) {
    quoteUploaderRef.value.openQuoteModal(project);
  }
};

// 处理报价上传完成
const handleQuoteUploaded = () => {
  Message.success('报价已上传 / Quote has been uploaded');
  fetchProjects(); // 刷新项目列表
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
</style>
