<template>
  <div class="project-list-container">
    <!-- 操作按钮区域 -->
    <div style="margin-bottom: 16px; display: flex; justify-content: flex-end;">
      <a-space>
        <a-dropdown trigger="click" v-if="userRole === 'LM' || userRole === 'BO'" :disabled="exportLoading">
          <a-button type="primary" :loading="exportLoading">
            Export CSV
            <icon-down v-if="!exportLoading" />
          </a-button>
          <template #content>
            <a-doption @click="exportToCSV(true)" :disabled="filteredProjects.length === 0">
              Export Filtered Data ({{ filteredProjects.length }})
            </a-doption>
            <a-doption @click="exportToCSV(false)" :disabled="projects.length === 0">
              Export All Data ({{ projects.length }})
            </a-doption>
          </template>
        </a-dropdown>
        <a-button type="primary" @click="refreshProjects" :loading="loading">
          Refresh List
        </a-button>
      </a-space>
    </div>
    
    <div class="action-bar">
      <a-input-search
        v-model="searchKeyword"
        placeholder="Search projects"
        style="width: 300px; margin-right: 16px;"
        @search="handleSearch"
      />
      <a-select
        v-model="statusFilter"
        placeholder="Project Status"
        style="width: 200px; margin-right: 16px;"
        allow-clear
        @change="handleStatusChange"
      >
        <a-option value="all">All</a-option>
        <a-option value="pending">Pending</a-option>
        <a-option value="in_progress">In Progress</a-option>
        <a-option value="completed">Completed</a-option>
        <a-option value="cancelled">Cancelled</a-option>
      </a-select>
      <a-select
        v-model="projectManagerFilter"
        placeholder="Project Manager"
        style="width: 200px; margin-right: 16px;"
        allow-clear
        @change="handleManagerChange"
      >
        <a-option value="all">All</a-option>
        <a-option v-for="manager in uniqueProjectManagers" :key="manager" :value="manager">
          {{ manager }}
        </a-option>
      </a-select>
      <a-date-picker
        v-model="deliveryDateFilter"
        placeholder="Delivery Date Filter"
        style="width: 220px; margin-right: 16px;"
        allow-clear
        @change="handleDeliveryDateChange"
      >
        <template #extra>
          <div style="padding: 0 10px; text-align: right;">
            <a-space>
              <a-radio-group v-model="dateFilterMode" type="button" size="small">
                <a-radio value="before">Before</a-radio>
                <a-radio value="after">After</a-radio>
              </a-radio-group>
              <a-button type="text" @click="handleDateFilterReset">Reset</a-button>
            </a-space>
          </div>
        </template>
      </a-date-picker>
    </div>
    
    <a-table
      :columns="columns"
      :data="filteredProjects"
      :loading="loading"
      :pagination="{
        showTotal: true,
        showPageSize: true,
        pageSize: pageSize,
        total: filteredProjects.length,
        sizeCanChange: true,
        pageSizeOptions: [10, 20, 50, 100],
        onPageSizeChange: (size) => pageSize = size,
        formatTotal: (total) => `Total ${total} items`,
        formatPageSize: (pageSize) => `${pageSize} items/page`
      }"
      row-key="id"
      style="margin-top: 16px;"
      :column-resizable="true"
    >
      <!-- 空状态提示 -->
      <template #empty>
        <div style="text-align: center; padding: 20px;">
          <a-empty description="No project data available">
            <template #image>
              <icon-file style="font-size: 48px; color: #c2c7d0;" />
            </template>
            <a-button type="primary" @click="refreshProjects">
              Refresh
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
            View
          </a-button>
          <a-button type="text" size="small" @click="onEditProject(record)" v-if="userRole === 'LM'">
            Edit
          </a-button>
          <a-button type="text" size="small" @click="onSendEmail(record)" v-if="userRole === 'LM'">
            Send Email
          </a-button>
          <a-button type="text" size="small" @click="onUploadFiles(record)" v-if="userRole === 'LM' || (userRole === 'BO' && canPerformAction(record, userId, userRole))">
            Upload Files
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
import { IconFile, IconDownload, IconDown } from '@arco-design/web-vue/es/icon';
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
    title: 'Project ID',
    dataIndex: 'id',
    key: 'id',
    sortable: true,
    resizable: true,
    width: 120,
  },
  {
    title: 'Project Name',
    dataIndex: 'projectName',
    key: 'projectName',
    sortable: true,
    resizable: true,
  },
  {
    title: 'Project Status',
    dataIndex: 'projectStatus',
    key: 'projectStatus',
    slotName: 'projectStatus',
    sortable: true,
    resizable: true,
  },
  {
    title: 'Request Name',
    dataIndex: 'requestName',
    key: 'requestName',
    resizable: true,
  },
  {
    title: 'Project Manager',
    dataIndex: 'projectManager',
    key: 'projectManager',
    sortable: true,
    resizable: true,
  },
  {
    title: 'Create Time',
    dataIndex: 'createTime',
    key: 'createTime',
    sortable: true,
    resizable: true,
  },
  {
    title: 'Expected Delivery Date',
    dataIndex: 'expectedDeliveryDate',
    key: 'expectedDeliveryDate',
    sortable: true,
    resizable: true,
  },
  {
    title: 'Translation Task',
    dataIndex: 'taskTranslation',
    key: 'taskTranslation',
    slotName: 'taskTranslation',
    resizable: true,
  },
  {
    title: 'LQA Task',
    dataIndex: 'taskLQA',
    key: 'taskLQA',
    slotName: 'taskLQA',
    resizable: true,
  },
  {
    title: 'Translation Update',
    dataIndex: 'taskTranslationUpdate',
    key: 'taskTranslationUpdate',
    slotName: 'taskTranslationUpdate',
    resizable: true,
  },
  {
    title: 'LQA Report Finalization',
    dataIndex: 'taskLQAReportFinalization',
    key: 'taskLQAReportFinalization',
    slotName: 'taskLQAReportFinalization',
    resizable: true,
  },
  {
    title: 'Operations',
    slotName: 'operations',
    width: 250,
    resizable: true,
  },
];

// 状态
const projects = ref([]);
const loading = ref(false);
const exportLoading = ref(false);
const searchKeyword = ref('');
const statusFilter = ref('all');
const projectManagerFilter = ref('all');
const deliveryDateFilter = ref(null);
const dateFilterMode = ref('before');
const pageSize = ref(10);

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
  
  // 交付日期过滤
  if (deliveryDateFilter.value) {
    const filterDateObj = new Date(deliveryDateFilter.value);
    // 设置时间为当天的23:59:59，确保包含当天
    filterDateObj.setHours(23, 59, 59, 999);
    
    result = result.filter(project => {
      // 处理项目日期可能是字符串的情况
      if (!project.expectedDeliveryDate || project.expectedDeliveryDate === 'Not set') {
        return false; // 没有设置交付日期的项目不显示
      }
      
      let projectDateObj;
      if (typeof project.expectedDeliveryDate === 'string') {
        // 尝试解析日期字符串
        const dateParts = project.expectedDeliveryDate.split(/[\/\-\.]/);
        if (dateParts.length >= 3) {
          // 假设格式为 MM/DD/YYYY 或 YYYY-MM-DD
          const isYearFirst = dateParts[0].length === 4;
          const year = isYearFirst ? parseInt(dateParts[0]) : parseInt(dateParts[2]);
          const month = parseInt(isYearFirst ? dateParts[1] : dateParts[0]) - 1; // 月份从0开始
          const day = parseInt(isYearFirst ? dateParts[2] : dateParts[1]);
          projectDateObj = new Date(year, month, day);
        } else {
          // 直接尝试解析
          projectDateObj = new Date(project.expectedDeliveryDate);
        }
      } else if (project.expectedDeliveryDate instanceof Date) {
        projectDateObj = project.expectedDeliveryDate;
      } else {
        return false; // 无效的日期格式
      }
      
      // 确保是有效的日期对象
      if (isNaN(projectDateObj.getTime())) {
        return false;
      }
      
      if (dateFilterMode.value === 'before') {
        return projectDateObj <= filterDateObj;
      } else {
        return projectDateObj >= filterDateObj;
      }
    });
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
      Message.error('Not logged in or session expired');
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
    Message.error('Failed to fetch projects');
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

const handleDeliveryDateChange = () => {
  console.log('交付日期筛选变更为:', deliveryDateFilter.value);
  console.log('日期筛选模式:', dateFilterMode.value === 'before' ? '早于所选日期' : '晚于所选日期');
};

const handleDateFilterReset = () => {
  deliveryDateFilter.value = null;
  dateFilterMode.value = 'before'; // 重置为默认的"早于"模式
  console.log('已重置日期筛选');
};

// 导出CSV功能
const exportToCSV = async (filteredOnly = true) => {
  try {
    exportLoading.value = true;
    // 确定要导出的数据
    const dataToExport = filteredOnly ? filteredProjects.value : projects.value;
    
    // 检查是否有数据可导出
    if (dataToExport.length === 0) {
      Message.warning('No data to export');
      return;
    }
    
    // 显示导出开始提示
    Message.loading({
      content: `Preparing to export ${dataToExport.length} projects`,
      duration: 1000,
    });
    
    // CSV标题行
    const headers = [
      'Project ID',
      'Project Name',
      'Project Status',
      'Request Name',
      'Project Manager',
      'Create Time',
      'Expected Delivery Date',
      'Translation Task',
      'LQA Task',
      'Translation Update',
      'LQA Report Finalization'
    ];
    
    // 将项目数据转换为CSV行
    const csvData = dataToExport.map(project => {
      return [
        project.id,
        project.projectName,
        getStatusText(project.projectStatus), // 转换状态代码为可读文本
        project.requestName,
        project.projectManager,
        project.createTime,
        project.expectedDeliveryDate || 'Not set',
        getTaskText(project.taskTranslation), // 转换任务状态为可读文本
        getTaskText(project.taskLQA),
        getTaskText(project.taskTranslationUpdate),
        getTaskText(project.taskLQAReportFinalization)
      ];
    });
    
    // 将CSV标题和数据合并
    csvData.unshift(headers);
    
    // 将数组转换为CSV字符串 (支持UTF-8编码的BOM头，确保Excel正确识别中文)
    const BOM = "\uFEFF"; // UTF-8 BOM
    const csvContent = BOM + csvData.map(row => 
      row.map(cell => 
        // 处理包含逗号、引号或换行符的单元格
        typeof cell === 'string' && (cell.includes(',') || cell.includes('"') || cell.includes('\n'))
          ? `"${cell.replace(/"/g, '""')}"` // 将双引号替换为两个双引号
          : cell
      ).join(',')
    ).join('\n');
    
    // 使用setTimeout给UI一点时间显示加载状态
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 创建Blob对象
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    
    // 创建下载链接
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    // 设置下载属性
    const dateStr = new Date().toISOString().slice(0, 10); // 格式: YYYY-MM-DD
    const fileType = filteredOnly ? 'filtered_projects' : 'all_projects';
    link.setAttribute('href', url);
    link.setAttribute('download', `${fileType}_${dateStr}.csv`);
    link.style.visibility = 'hidden';
    
    // 添加到文档并触发下载
    document.body.appendChild(link);
    link.click();
    
    // 清理
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    Message.success({
      content: `Successfully exported ${dataToExport.length} projects`,
      duration: 3000
    });
  } catch (error) {
    console.error('导出CSV时发生错误:', error);
    Message.error({
      content: 'Export failed, please try again',
      duration: 3000
    });
  } finally {
    exportLoading.value = false;
  }
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
  /* 移除可能导致滚动条的固定高度 */
  /* 确保内容适应父容器 */
}

.action-bar {
  display: flex;
  margin-bottom: 16px;
}
</style> 