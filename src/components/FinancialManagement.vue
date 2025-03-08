<template>
  <div class="financial-management-container">
    <h2>财务管理 / Financial Management</h2>
    
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
      <a-button type="primary" style="margin-left: 16px;" @click="showExtractModal">
        提取报价 / Extract Quote
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
      
      <!-- 金额列 -->
      <template #quoteAmount="{ record }">
        {{ formatCurrency(record.quoteAmount, record.currency) }}
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
            v-if="record.status === 'pending'" 
            type="text" 
            status="success" 
            size="small" 
            @click="approveQuote(record)"
          >
            批准 / Approve
          </a-button>
          <a-button 
            v-if="record.status === 'pending'" 
            type="text" 
            status="danger" 
            size="small" 
            @click="rejectQuote(record)"
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
    
    <!-- 报价详情抽屉 -->
    <a-drawer
      v-model:visible="drawerVisible"
      :width="600"
      :title="drawerTitle"
      unmountOnClose
    >
      <div v-if="currentQuote">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="项目名称 / Project Name">
            {{ currentQuote.projectName }}
          </a-descriptions-item>
          <a-descriptions-item label="LSP名称 / LSP Name">
            {{ currentQuote.lspName }}
          </a-descriptions-item>
          <a-descriptions-item label="报价金额 / Quote Amount">
            {{ formatCurrency(currentQuote.quoteAmount, currentQuote.currency) }}
          </a-descriptions-item>
          <a-descriptions-item label="字数 / Word Count">
            {{ currentQuote.wordCount }}
          </a-descriptions-item>
          <a-descriptions-item label="单价 / Unit Price">
            {{ calculateUnitPrice(currentQuote.quoteAmount, currentQuote.wordCount, currentQuote.currency) }}
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
            {{ currentQuote.notes || '无 / None' }}
          </a-descriptions-item>
        </a-descriptions>
        
        <div class="drawer-footer" style="margin-top: 24px; text-align: right;">
          <a-space>
            <a-button @click="drawerVisible = false">
              关闭 / Close
            </a-button>
            <a-button v-if="currentQuote.status === 'pending'" type="primary" status="success" @click="approveQuote(currentQuote)">
              批准 / Approve
            </a-button>
            <a-button v-if="currentQuote.status === 'pending'" type="primary" status="danger" @click="rejectQuote(currentQuote)">
              拒绝 / Reject
            </a-button>
          </a-space>
        </div>
      </div>
    </a-drawer>
    
    <!-- 编辑报价对话框 -->
    <a-modal
      v-model:visible="editModalVisible"
      title="编辑报价 / Edit Quote"
      @ok="saveQuote"
      @cancel="editModalVisible = false"
      :ok-loading="saving"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item field="lspName" label="LSP名称 / LSP Name" required>
          <a-input v-model="editForm.lspName" placeholder="LSP名称 / LSP Name" />
        </a-form-item>
        <a-form-item field="quoteAmount" label="报价金额 / Quote Amount" required>
          <a-input-number v-model="editForm.quoteAmount" placeholder="报价金额 / Quote Amount" :min="0" :precision="2" />
        </a-form-item>
        <a-form-item field="currency" label="货币 / Currency" required>
          <a-select v-model="editForm.currency">
            <a-option value="USD">美元 / USD</a-option>
            <a-option value="EUR">欧元 / EUR</a-option>
            <a-option value="CNY">人民币 / CNY</a-option>
            <a-option value="JPY">日元 / JPY</a-option>
            <a-option value="GBP">英镑 / GBP</a-option>
          </a-select>
        </a-form-item>
        <a-form-item field="wordCount" label="字数 / Word Count" required>
          <a-input-number v-model="editForm.wordCount" placeholder="字数 / Word Count" :min="1" />
        </a-form-item>
        <a-form-item field="quoteDate" label="报价日期 / Quote Date" required>
          <a-date-picker v-model="editForm.quoteDate" />
        </a-form-item>
        <a-form-item field="notes" label="备注 / Notes">
          <a-textarea v-model="editForm.notes" placeholder="备注 / Notes" :auto-size="{ minRows: 3, maxRows: 5 }" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 提取报价对话框 -->
    <a-modal
      v-model:visible="extractModalVisible"
      title="从邮件提取报价 / Extract Quote from Email"
      @ok="extractQuote"
      @cancel="extractModalVisible = false"
      :ok-loading="extracting"
    >
      <a-form :model="extractForm" layout="vertical">
        <a-form-item field="projectId" label="项目 / Project" required>
          <a-select v-model="extractForm.projectId" placeholder="选择项目 / Select Project">
            <a-option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.projectName }}
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item field="lspName" label="LSP名称 / LSP Name" required>
          <a-input v-model="extractForm.lspName" placeholder="LSP名称 / LSP Name" />
        </a-form-item>
        <a-form-item field="emailContent" label="邮件内容 / Email Content" required>
          <a-textarea 
            v-model="extractForm.emailContent" 
            placeholder="粘贴邮件内容以提取报价信息 / Paste email content to extract quote information" 
            :auto-size="{ minRows: 5, maxRows: 10 }" 
          />
        </a-form-item>
      </a-form>
      
      <div v-if="extractedData" class="extracted-data">
        <h3>提取的数据 / Extracted Data</h3>
        <a-descriptions :column="1" bordered size="small">
          <a-descriptions-item v-if="extractedData.projectId" label="项目ID / Project ID">
            {{ extractedData.projectId }}
          </a-descriptions-item>
          <a-descriptions-item v-if="extractedData.quoteAmount" label="报价金额 / Quote Amount">
            {{ extractedData.quoteAmount }}
          </a-descriptions-item>
          <a-descriptions-item v-if="extractedData.currency" label="货币 / Currency">
            {{ extractedData.currency }}
          </a-descriptions-item>
          <a-descriptions-item v-if="extractedData.wordCount" label="字数 / Word Count">
            {{ extractedData.wordCount }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>
    
    <!-- 财务报表部分 -->
    <div class="financial-reports" style="margin-top: 32px;">
      <h3>财务报表 / Financial Reports</h3>
      
      <div class="report-filters" style="margin-bottom: 16px;">
        <a-space>
          <a-select
            v-model="reportType"
            placeholder="报表类型 / Report Type"
            style="width: 200px;"
          >
            <a-option value="project">按项目 / By Project</a-option>
            <a-option value="lsp">按LSP / By LSP</a-option>
            <a-option value="month">按月份 / By Month</a-option>
          </a-select>
          
          <a-range-picker
            v-model="dateRange"
            style="width: 300px;"
            :disabled-date="disabledDate"
          />
          
          <a-button type="primary" @click="generateReport">
            生成报表 / Generate Report
          </a-button>
          
          <a-button @click="exportReport">
            导出 / Export
          </a-button>
        </a-space>
      </div>
      
      <div class="report-chart" style="height: 400px; margin-bottom: 24px;">
        <!-- 这里可以使用图表库如ECharts或Chart.js来展示数据 -->
        <div class="chart-placeholder" style="height: 100%; display: flex; justify-content: center; align-items: center; background-color: #f5f5f5; border-radius: 4px;">
          <p>图表将在这里显示 / Chart will be displayed here</p>
        </div>
      </div>
      
      <a-table
        :columns="reportColumns"
        :data="reportData"
        :loading="reportLoading"
        :pagination="false"
        style="margin-top: 16px;"
      >
        <!-- 金额列 -->
        <template #amount="{ record }">
          {{ formatCurrency(record.amount, 'USD') }}
        </template>
      </a-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';

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
    filterable: true,
  },
  {
    title: '报价金额 / Quote Amount',
    dataIndex: 'quoteAmount',
    key: 'quoteAmount',
    slotName: 'quoteAmount',
    sortable: true,
  },
  {
    title: '货币 / Currency',
    dataIndex: 'currency',
    key: 'currency',
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
    fixed: 'right',
    width: 200,
  },
];

// 报表列定义
const reportColumns = [
  {
    title: '名称 / Name',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '项目数 / Project Count',
    dataIndex: 'projectCount',
    key: 'projectCount',
  },
  {
    title: '总字数 / Total Word Count',
    dataIndex: 'wordCount',
    key: 'wordCount',
  },
  {
    title: '总金额 / Total Amount',
    dataIndex: 'amount',
    key: 'amount',
    slotName: 'amount',
  },
];

// 状态和数据
const quotes = ref([]);
const projects = ref([]);
const loading = ref(false);
const searchKeyword = ref('');
const statusFilter = ref('all');
const drawerVisible = ref(false);
const drawerTitle = ref('报价详情 / Quote Details');
const currentQuote = ref(null);
const editModalVisible = ref(false);
const saving = ref(false);
const extractModalVisible = ref(false);
const extracting = ref(false);
const extractedData = ref(null);
const reportType = ref('project');
const dateRange = ref([]);
const reportData = ref([]);
const reportLoading = ref(false);

// 表单数据
const editForm = reactive({
  id: null,
  projectId: null,
  lspName: '',
  quoteAmount: 0,
  currency: 'USD',
  wordCount: 0,
  quoteDate: null,
  notes: '',
});

const extractForm = reactive({
  projectId: null,
  lspName: '',
  emailContent: '',
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
  fetchQuotes();
  fetchProjects();
});

// 方法
const fetchQuotes = async () => {
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

const formatCurrency = (amount, currency) => {
  if (amount === undefined || amount === null) return '';
  
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
  });
  
  return formatter.format(amount);
};

const calculateUnitPrice = (amount, wordCount, currency) => {
  if (!amount || !wordCount) return formatCurrency(0, currency);
  
  const unitPrice = amount / wordCount;
  return formatCurrency(unitPrice, currency) + ' per word';
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const viewQuote = (quote) => {
  currentQuote.value = quote;
  drawerTitle.value = `报价详情 / Quote Details: ${quote.lspName}`;
  drawerVisible.value = true;
};

const editQuote = (quote) => {
  editForm.id = quote.id;
  editForm.projectId = quote.projectId;
  editForm.lspName = quote.lspName;
  editForm.quoteAmount = quote.quoteAmount;
  editForm.currency = quote.currency;
  editForm.wordCount = quote.wordCount;
  editForm.quoteDate = new Date(quote.quoteDate);
  editForm.notes = quote.notes || '';
  
  editModalVisible.value = true;
};

const saveQuote = async () => {
  // 表单验证
  if (!editForm.lspName || !editForm.quoteAmount || !editForm.wordCount || !editForm.quoteDate) {
    Message.error('请填写所有必填字段 / Please fill in all required fields');
    return;
  }
  
  try {
    saving.value = true;
    
    // 准备更新的报价数据
    const updatedQuote = {
      id: editForm.id,
      projectId: editForm.projectId,
      lspName: editForm.lspName,
      quoteAmount: editForm.quoteAmount,
      currency: editForm.currency,
      wordCount: editForm.wordCount,
      quoteDate: editForm.quoteDate.toISOString().split('T')[0], // 格式化日期为 YYYY-MM-DD
      notes: editForm.notes,
    };
    
    // 发送更新请求
    const response = await axios.put(`http://localhost:5000/api/quotes/${editForm.id}`, updatedQuote);
    
    if (response.status === 200) {
      Message.success('报价更新成功 / Quote updated successfully');
      fetchQuotes(); // 刷新报价列表
      editModalVisible.value = false;
    } else {
      throw new Error('更新失败 / Update failed');
    }
  } catch (error) {
    console.error('Error updating quote:', error);
    Message.error(`更新失败: ${error.message} / Update failed: ${error.message}`);
  } finally {
    saving.value = false;
  }
};

const approveQuote = async (quote) => {
  try {
    const response = await axios.put(`http://localhost:5000/api/quotes/${quote.id}`, {
      status: 'approved'
    });
    
    if (response.status === 200) {
      Message.success('报价已批准 / Quote approved');
      fetchQuotes(); // 刷新报价列表
      drawerVisible.value = false;
    } else {
      throw new Error('操作失败 / Operation failed');
    }
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
    
    if (response.status === 200) {
      Message.success('报价已拒绝 / Quote rejected');
      fetchQuotes(); // 刷新报价列表
      drawerVisible.value = false;
    } else {
      throw new Error('操作失败 / Operation failed');
    }
  } catch (error) {
    console.error('Error rejecting quote:', error);
    Message.error(`操作失败: ${error.message} / Operation failed: ${error.message}`);
  }
};

const showExtractModal = () => {
  extractForm.projectId = null;
  extractForm.lspName = '';
  extractForm.emailContent = '';
  extractedData.value = null;
  extractModalVisible.value = true;
};

const extractQuote = async () => {
  // 表单验证
  if (!extractForm.projectId || !extractForm.lspName || !extractForm.emailContent) {
    Message.error('请填写所有必填字段 / Please fill in all required fields');
    return;
  }
  
  try {
    extracting.value = true;
    
    // 发送提取请求
    const response = await axios.post('http://localhost:5000/api/quotes/extract', {
      emailContent: extractForm.emailContent
    });
    
    if (response.status === 200) {
      extractedData.value = response.data;
      
      // 如果提取成功，创建新的报价
      if (Object.keys(extractedData.value).length > 0) {
        const quoteData = {
          projectId: extractForm.projectId,
          lspName: extractForm.lspName,
          quoteAmount: extractedData.value.quoteAmount || 0,
          currency: extractedData.value.currency || 'USD',
          wordCount: extractedData.value.wordCount || 0,
          quoteDate: new Date().toISOString().split('T')[0],
          status: 'pending',
          notes: `从邮件提取的报价 / Quote extracted from email on ${new Date().toLocaleString()}`,
        };
        
        const createResponse = await axios.post('http://localhost:5000/api/quotes', quoteData);
        
        if (createResponse.status === 201) {
          Message.success('报价提取并创建成功 / Quote extracted and created successfully');
          fetchQuotes(); // 刷新报价列表
          extractModalVisible.value = false;
        } else {
          throw new Error('创建报价失败 / Failed to create quote');
        }
      } else {
        Message.warning('未能从邮件中提取有效的报价信息 / Could not extract valid quote information from email');
      }
    } else {
      throw new Error('提取失败 / Extraction failed');
    }
  } catch (error) {
    console.error('Error extracting quote:', error);
    Message.error(`提取失败: ${error.message} / Extraction failed: ${error.message}`);
  } finally {
    extracting.value = false;
  }
};

// 禁用今天之后的日期
const disabledDate = (date) => {
  return date.getTime() > Date.now();
};

const generateReport = async () => {
  reportLoading.value = true;
  
  try {
    // 这里应该调用后端API获取报表数据
    // 这里使用模拟数据作为示例
    setTimeout(() => {
      if (reportType.value === 'project') {
        reportData.value = [
          { name: '产品手册翻译项目', projectCount: 1, wordCount: 5000, amount: 1000 },
          { name: '营销材料本地化', projectCount: 1, wordCount: 3000, amount: 600 },
          { name: '软件界面翻译', projectCount: 1, wordCount: 2000, amount: 400 },
        ];
      } else if (reportType.value === 'lsp') {
        reportData.value = [
          { name: 'LSP A', projectCount: 2, wordCount: 8000, amount: 1600 },
          { name: 'LSP B', projectCount: 1, wordCount: 2000, amount: 400 },
        ];
      } else if (reportType.value === 'month') {
        reportData.value = [
          { name: '2023-01', projectCount: 1, wordCount: 5000, amount: 1000 },
          { name: '2023-02', projectCount: 1, wordCount: 3000, amount: 600 },
          { name: '2023-03', projectCount: 1, wordCount: 2000, amount: 400 },
        ];
      }
      
      reportLoading.value = false;
      Message.success('报表生成成功 / Report generated successfully');
    }, 1000);
  } catch (error) {
    console.error('Error generating report:', error);
    Message.error('生成报表失败 / Failed to generate report');
    reportLoading.value = false;
  }
};

const exportReport = () => {
  Message.info('导出功能正在开发中 / Export feature is under development');
};
</script>

<style scoped>
.financial-management-container {
  padding: 20px;
}

h2, h3 {
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

.extracted-data {
  margin-top: 16px;
  padding: 16px;
  background-color: var(--color-fill-2);
  border-radius: 4px;
}

:deep(.arco-table-th) {
  background-color: var(--color-fill-2);
}

:deep(.arco-descriptions-item-label) {
  width: 200px;
}
</style>
