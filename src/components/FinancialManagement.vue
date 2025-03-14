<template>
  <div class="financial-management-container">
    <h2>财务管理 / Financial Management</h2>
    
    <!-- 只有LM可以访问财务管理 -->
    <div v-if="userRole === 'LM'">
      <div class="action-bar">
        <a-input-search
          v-model="searchKeyword"
          placeholder="搜索项目或LSP / Search projects or LSPs"
          style="width: 300px; margin-right: 16px;"
          @search="handleSearch"
        />
        <a-select
          v-model="statusFilter"
          placeholder="报价状态 / Quote Status"
          style="width: 200px; margin-right: 16px;"
          allow-clear
        >
          <a-option value="all">全部 / All</a-option>
          <a-option value="pending">待审批 / Pending</a-option>
          <a-option value="approved">已批准 / Approved</a-option>
          <a-option value="rejected">已拒绝 / Rejected</a-option>
        </a-select>
        <a-button type="primary" @click="refreshQuotes">
          刷新 / Refresh
        </a-button>
        <a-button type="primary" style="margin-left: 16px;" @click="showCreateQuoteModal">
          创建报价 / Create Quote
        </a-button>
      </div>
      
      <a-table
        :columns="columns"
        :data="filteredQuotes"
        :loading="loading"
        :pagination="{
          showTotal: true,
          showPageSize: true,
          pageSize: 10,
        }"
        row-key="id"
        style="margin-top: 16px;"
      >
        <!-- 报价状态列 -->
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>
        
        <!-- 操作列 -->
        <template #operations="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="viewQuote(record)">
              查看 / View
            </a-button>
            <a-button type="text" size="small" @click="editQuote(record)">
              编辑 / Edit
            </a-button>
            <a-button 
              type="text" 
              size="small" 
              @click="approveQuote(record)"
              v-if="record.status === 'pending'"
            >
              批准 / Approve
            </a-button>
            <a-button 
              type="text" 
              status="danger" 
              size="small" 
              @click="rejectQuote(record)"
              v-if="record.status === 'pending'"
            >
              拒绝 / Reject
            </a-button>
          </a-space>
        </template>
        
        <!-- 空状态 -->
        <template #empty>
          <div class="empty-state">
            <a-empty description="暂无报价数据 / No quote data available" />
          </div>
        </template>
      </a-table>
      
      <!-- 创建/编辑报价对话框 -->
      <a-modal
        v-model:visible="quoteModalVisible"
        :title="isEditMode ? '编辑报价 / Edit Quote' : '创建报价 / Create Quote'"
        @ok="submitQuote"
        @cancel="quoteModalVisible = false"
        :ok-loading="submitting"
      >
        <a-form :model="quoteForm" layout="vertical">
          <a-form-item field="projectId" label="项目 / Project" required>
            <a-select v-model="quoteForm.projectId" placeholder="选择项目 / Select project">
              <a-option 
                v-for="project in projects" 
                :key="project.id" 
                :value="project.id"
              >
                {{ project.projectName }}
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="lspName" label="LSP名称 / LSP Name" required>
            <a-input v-model="quoteForm.lspName" placeholder="LSP名称 / LSP name" />
          </a-form-item>
          <a-form-item field="quoteAmount" label="报价金额 / Quote Amount" required>
            <a-input-number v-model="quoteForm.quoteAmount" placeholder="报价金额 / Quote amount" :min="0" :precision="2" />
          </a-form-item>
          <a-form-item field="currency" label="货币 / Currency">
            <a-select v-model="quoteForm.currency" placeholder="选择货币 / Select currency">
              <a-option value="USD">美元 / USD</a-option>
              <a-option value="EUR">欧元 / EUR</a-option>
              <a-option value="CNY">人民币 / CNY</a-option>
              <a-option value="JPY">日元 / JPY</a-option>
              <a-option value="GBP">英镑 / GBP</a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="wordCount" label="字数 / Word Count">
            <a-input-number v-model="quoteForm.wordCount" placeholder="字数 / Word count" :min="0" />
          </a-form-item>
          <a-form-item field="quoteDate" label="报价日期 / Quote Date">
            <a-date-picker v-model="quoteForm.quoteDate" />
          </a-form-item>
          <a-form-item field="notes" label="备注 / Notes">
            <a-textarea v-model="quoteForm.notes" placeholder="备注 / Notes" :auto-size="{ minRows: 3, maxRows: 5 }" />
          </a-form-item>
        </a-form>
      </a-modal>
      
      <!-- 查看报价详情对话框 -->
      <a-modal
        v-model:visible="viewModalVisible"
        title="报价详情 / Quote Details"
        @cancel="viewModalVisible = false"
        :footer="false"
      >
        <a-descriptions :column="1" bordered v-if="currentQuote">
          <a-descriptions-item label="项目名称 / Project Name">
            {{ getProjectName(currentQuote.projectId) }}
          </a-descriptions-item>
          <a-descriptions-item label="LSP名称 / LSP Name">
            {{ currentQuote.lspName }}
          </a-descriptions-item>
          <a-descriptions-item label="报价金额 / Quote Amount">
            {{ currentQuote.quoteAmount }} {{ currentQuote.currency }}
          </a-descriptions-item>
          <a-descriptions-item label="字数 / Word Count">
            {{ currentQuote.wordCount }}
          </a-descriptions-item>
          <a-descriptions-item label="报价日期 / Quote Date">
            {{ formatDate(currentQuote.quoteDate) }}
          </a-descriptions-item>
          <a-descriptions-item label="状态 / Status">
            <a-tag :color="getStatusColor(currentQuote.status)">
              {{ getStatusText(currentQuote.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="备注 / Notes">
            {{ currentQuote.notes }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间 / Create Time">
            {{ formatDate(currentQuote.createTime) }}
          </a-descriptions-item>
        </a-descriptions>
      </a-modal>
    </div>
    
    <!-- 非LM用户无权访问 -->
    <div v-else class="no-permission">
      <a-result
        status="403"
        title="无权访问 / Access Denied"
        subtitle="您没有权限访问财务管理页面 / You do not have permission to access the Financial Management page"
      >
        <template #extra>
          <a-button type="primary">返回首页 / Back to Home</a-button>
        </template>
      </a-result>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';

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
  },
  {
    title: 'LSP名称 / LSP Name',
    dataIndex: 'lspName',
    key: 'lspName',
    sortable: true,
  },
  {
    title: '报价金额 / Quote Amount',
    dataIndex: 'quoteAmount',
    key: 'quoteAmount',
    sortable: true,
    render: (col, record) => `${record.quoteAmount} ${record.currency}`,
  },
  {
    title: '字数 / Word Count',
    dataIndex: 'wordCount',
    key: 'wordCount',
    sortable: true,
  },
  {
    title: '报价日期 / Quote Date',
    dataIndex: 'quoteDate',
    key: 'quoteDate',
    sortable: true,
  },
  {
    title: '状态 / Status',
    dataIndex: 'status',
    key: 'status',
    slotName: 'status',
    sortable: true,
    filterable: true,
  },
  {
    title: '操作 / Operations',
    slotName: 'operations',
    width: 250,
  },
];

// 状态和数据
const quotes = ref([]);
const projects = ref([]);
const loading = ref(false);
const searchKeyword = ref('');
const statusFilter = ref('all');
const quoteModalVisible = ref(false);
const viewModalVisible = ref(false);
const submitting = ref(false);
const isEditMode = ref(false);
const currentQuote = ref(null);

// 表单数据
const quoteForm = reactive({
  id: null,
  projectId: null,
  lspName: '',
  quoteAmount: 0,
  currency: 'USD',
  wordCount: 0,
  quoteDate: new Date(),
  status: 'pending',
  notes: '',
});

// 过滤后的报价列表
const filteredQuotes = computed(() => {
  let result = [...quotes.value];
  
  // 状态过滤
  if (statusFilter.value !== 'all') {
    result = result.filter(quote => quote.status === statusFilter.value);
  }
  
  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(quote => 
      quote.projectName.toLowerCase().includes(keyword) ||
      quote.lspName.toLowerCase().includes(keyword)
    );
  }
  
  return result;
});

// 生命周期钩子
onMounted(() => {
  if (props.userRole === 'LM') {
    fetchQuotes();
    fetchProjects();
  }
});

// 当用户ID或角色变化时重新获取数据
watch([() => props.userId, () => props.userRole], () => {
  if (props.userRole === 'LM') {
    fetchQuotes();
    fetchProjects();
  }
});

// 方法
const fetchQuotes = async () => {
  if (props.userRole !== 'LM' || !props.userId) return;
  
  loading.value = true;
  try {
    const response = await axios.get('http://localhost:5000/api/quotes');
    quotes.value = response.data;
  } catch (error) {
    console.error('Error fetching quotes:', error);
    Message.error('获取报价列表失败 / Failed to fetch quotes');
  } finally {
    loading.value = false;
  }
};

const fetchProjects = async () => {
  if (props.userRole !== 'LM' || !props.userId) return;
  
  try {
    const response = await axios.get('http://localhost:5000/api/projects');
    projects.value = response.data;
  } catch (error) {
    console.error('Error fetching projects:', error);
    Message.error('获取项目列表失败 / Failed to fetch projects');
  }
};

const refreshQuotes = () => {
  fetchQuotes();
  Message.success('报价列表已刷新 / Quote list refreshed');
};

const handleSearch = () => {
  console.log('Searching for:', searchKeyword.value);
};

const getStatusColor = (status) => {
  const statusMap = {
    pending: 'orange',
    approved: 'green',
    rejected: 'red',
  };
  return statusMap[status] || 'gray';
};

const getStatusText = (status) => {
  const statusMap = {
    pending: '待审批 / Pending',
    approved: '已批准 / Approved',
    rejected: '已拒绝 / Rejected',
  };
  return statusMap[status] || '未知 / Unknown';
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const getProjectName = (projectId) => {
  const project = projects.value.find(p => p.id === projectId);
  return project ? project.projectName : '未知项目 / Unknown Project';
};

const resetQuoteForm = () => {
  quoteForm.id = null;
  quoteForm.projectId = null;
  quoteForm.lspName = '';
  quoteForm.quoteAmount = 0;
  quoteForm.currency = 'USD';
  quoteForm.wordCount = 0;
  quoteForm.quoteDate = new Date();
  quoteForm.status = 'pending';
  quoteForm.notes = '';
};

const showCreateQuoteModal = () => {
  isEditMode.value = false;
  resetQuoteForm();
  quoteModalVisible.value = true;
};

const viewQuote = (quote) => {
  currentQuote.value = quote;
  viewModalVisible.value = true;
};

const editQuote = (quote) => {
  isEditMode.value = true;
  
  // 复制报价数据到表单
  quoteForm.id = quote.id;
  quoteForm.projectId = quote.projectId;
  quoteForm.lspName = quote.lspName;
  quoteForm.quoteAmount = quote.quoteAmount;
  quoteForm.currency = quote.currency;
  quoteForm.wordCount = quote.wordCount;
  quoteForm.quoteDate = quote.quoteDate ? new Date(quote.quoteDate) : new Date();
  quoteForm.status = quote.status;
  quoteForm.notes = quote.notes || '';
  
  quoteModalVisible.value = true;
};

const submitQuote = async () => {
  if (!quoteForm.projectId || !quoteForm.lspName || quoteForm.quoteAmount <= 0) {
    Message.error('请填写必填字段 / Please fill in all required fields');
    return;
  }
  
  try {
    submitting.value = true;
    
    // 准备报价数据
    const quoteData = {
      ...quoteForm,
      quoteDate: quoteForm.quoteDate ? formatDate(quoteForm.quoteDate) : formatDate(new Date()),
    };
    
    let response;
    
    if (isEditMode.value) {
      // 更新报价
      response = await axios.put(`http://localhost:5000/api/quotes/${quoteForm.id}`, quoteData);
      Message.success('报价更新成功 / Quote updated successfully');
    } else {
      // 创建报价
      response = await axios.post('http://localhost:5000/api/quotes', quoteData);
      Message.success('报价创建成功 / Quote created successfully');
    }
    
    quoteModalVisible.value = false;
    fetchQuotes(); // 刷新报价列表
  } catch (error) {
    console.error('Error submitting quote:', error);
    Message.error(`提交失败: ${error.message} / Submission failed: ${error.message}`);
  } finally {
    submitting.value = false;
  }
};

const approveQuote = async (quote) => {
  try {
    const response = await axios.put(`http://localhost:5000/api/quotes/${quote.id}`, {
      status: 'approved'
    });
    
    Message.success('报价已批准 / Quote approved');
    fetchQuotes(); // 刷新报价列表
  } catch (error) {
    console.error('Error approving quote:', error);
    Message.error(`操作失败: ${error.message} / Operation failed: ${error.message}`);
  }
};

const rejectQuote = async (quote) => {
  try {
    const response = await axios.put(`http://localhost:5000/api/quotes/${quote.id}`, {
      status: 'rejected'
    });
    
    Message.success('报价已拒绝 / Quote rejected');
    fetchQuotes(); // 刷新报价列表
  } catch (error) {
    console.error('Error rejecting quote:', error);
    Message.error(`操作失败: ${error.message} / Operation failed: ${error.message}`);
  }
};
</script>

<style scoped>
.financial-management-container {
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

.no-permission {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>
