<template>
  <div class="quote-uploader-container">
    <a-modal
      v-model:visible="visible"
      :title="`报价录入: ${currentProject ? currentProject.projectName : ''}`"
      :ok-text="'提交 / Submit'"
      :cancel-text="'取消 / Cancel'"
      @ok="submitQuote"
      @cancel="closeModal"
      :ok-loading="submitting"
      unmount-on-close
      style="width: 700px;"
    >
      <a-form :model="quoteForm" layout="vertical">
        <!-- 项目任务选择 -->
        <a-form-item field="task" label="项目任务 / Project Task" required>
          <a-select v-model="quoteForm.task" placeholder="选择任务 / Select task">
            <a-option value="translation">翻译任务 / Translation Task</a-option>
            <a-option value="lqa">LQA任务 / LQA Task</a-option>
            <a-option value="translationUpdate">翻译更新 / Translation Update</a-option>
            <a-option value="lqaReportFinalization">LQA报告定稿 / LQA Report Finalization</a-option>
          </a-select>
        </a-form-item>
        
        <!-- 任务负责人 -->
        <a-form-item field="assignee" label="任务负责人 / Task Assignee" required>
          <a-input v-model="quoteForm.assignee" placeholder="输入负责人 / Enter assignee name" />
        </a-form-item>
        
        <!-- 语言选择 -->
        <a-form-item field="language" label="语言 / Language" required>
          <a-select v-model="quoteForm.language" placeholder="选择语言 / Select language">
            <a-option v-for="lang in availableLanguages" :key="lang.code" :value="lang.code">
              {{ lang.name }}
            </a-option>
          </a-select>
        </a-form-item>
        
        <!-- 报价金额和货币 -->
        <div class="quote-amount-row">
          <a-form-item field="quoteAmount" label="报价金额 / Quote Amount" required style="flex: 1; margin-right: 12px;">
            <a-input-number v-model="quoteForm.quoteAmount" placeholder="报价金额 / Quote amount" :min="0" :precision="2" />
          </a-form-item>
          
          <a-form-item field="currency" label="货币 / Currency" style="flex: 0.5;">
            <a-select v-model="quoteForm.currency" placeholder="选择货币 / Select currency">
              <a-option value="USD">美元 / USD</a-option>
              <a-option value="EUR">欧元 / EUR</a-option>
              <a-option value="CNY">人民币 / CNY</a-option>
              <a-option value="JPY">日元 / JPY</a-option>
              <a-option value="GBP">英镑 / GBP</a-option>
            </a-select>
          </a-form-item>
        </div>
        
        <!-- 字数和单价 -->
        <div class="quote-amount-row">
          <a-form-item field="wordCount" label="字数 / Word Count" style="flex: 1; margin-right: 12px;">
            <a-input-number v-model="quoteForm.wordCount" placeholder="字数 / Word count" :min="0" />
          </a-form-item>
          
          <a-form-item field="unitPrice" label="单价 / Unit Price" style="flex: 1;">
            <a-input-number v-model="quoteForm.unitPrice" placeholder="单价 / Unit price" :min="0" :precision="4" />
          </a-form-item>
        </div>
        
        <!-- 截止日期 -->
        <a-form-item field="deadline" label="截止日期 / Deadline">
          <a-date-picker v-model="quoteForm.deadline" style="width: 100%;" />
        </a-form-item>
        
        <!-- 上传报价文件 -->
        <a-form-item field="quoteFile" label="报价文件 / Quote File">
          <a-upload
            action="http://localhost:5000/api/upload"
            :file-list="fileList"
            @change="handleFileChange"
            :headers="uploadHeaders"
            :limit="1"
            accept=".xls,.xlsx,.csv,.pdf,.doc,.docx"
          >
            <template #upload-button>
              <a-button>
                上传报价文件 / Upload Quote File
              </a-button>
            </template>
          </a-upload>
        </a-form-item>
        
        <!-- 自动提取报价信息按钮 -->
        <a-form-item>
          <a-button type="primary" @click="extractQuoteInfo" :disabled="!hasUploadedFile" :loading="extracting">
            <template #icon><icon-robot /></template>
            自动提取报价信息 / Extract Quote Info
          </a-button>
          <a-tooltip content="从上传的报价文件中自动提取报价信息 / Automatically extract quote information from the uploaded file">
            <icon-info-circle style="margin-left: 8px; color: var(--color-text-3);" />
          </a-tooltip>
        </a-form-item>
        
        <!-- 备注 -->
        <a-form-item field="notes" label="备注 / Notes">
          <a-textarea v-model="quoteForm.notes" placeholder="备注 / Notes" :auto-size="{ minRows: 3, maxRows: 5 }" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, defineProps, defineEmits } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';
import { IconRobot, IconInfoCircle } from '@arco-design/web-vue/es/icon';
import { languages } from '../../utils/languages';
import { extractQuoteFromFile } from './QuoteExtractionService';

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

const emit = defineEmits(['uploaded']);

// 状态变量
const visible = ref(false);
const submitting = ref(false);
const extracting = ref(false);
const currentProject = ref(null);
const fileList = ref([]);
const uploadedFileId = ref(null);

// 表单数据
const quoteForm = reactive({
  task: '',
  assignee: '',
  language: '',
  quoteAmount: 0,
  currency: 'USD',
  wordCount: 0,
  unitPrice: 0,
  deadline: null,
  notes: ''
});

// 计算属性
const availableLanguages = computed(() => {
  if (!currentProject.value || !currentProject.value.targetLanguages) {
    return languages;
  }
  
  // 如果项目有目标语言，只显示这些语言
  const targetLangCodes = Array.isArray(currentProject.value.targetLanguages) 
    ? currentProject.value.targetLanguages
    : currentProject.value.targetLanguages.split(',');
  
  // 添加源语言
  const sourceLang = currentProject.value.sourceLanguage;
  const allCodes = [...targetLangCodes];
  if (sourceLang && !allCodes.includes(sourceLang)) {
    allCodes.push(sourceLang);
  }
  
  // 过滤语言列表
  return languages.filter(lang => allCodes.includes(lang.code));
});

const hasUploadedFile = computed(() => {
  return fileList.value.length > 0 && fileList.value[0].status === 'done' && uploadedFileId.value;
});

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`
  };
});

// 打开模态框
const openQuoteModal = (project) => {
  if (props.userRole !== 'FT') {
    Message.error('只有财务团队可以录入报价 / Only Financial Team can enter quotes');
    return;
  }
  
  // 保存当前项目信息
  currentProject.value = project;
  
  // 重置表单
  resetForm();
  
  // 显示对话框
  visible.value = true;
};

// 关闭模态框
const closeModal = () => {
  resetForm();
  visible.value = false;
};

// 重置表单
const resetForm = () => {
  Object.keys(quoteForm).forEach(key => {
    if (key === 'currency') {
      quoteForm[key] = 'USD';
    } else if (typeof quoteForm[key] === 'number') {
      quoteForm[key] = 0;
    } else {
      quoteForm[key] = '';
    }
  });
  quoteForm.deadline = null;
  fileList.value = [];
  uploadedFileId.value = null;
};

// 处理文件上传
const handleFileChange = (file) => {
  console.log('File upload status changed:', file);
  
  if (file.status === 'done') {
    // 上传成功处理
    if (file.response && file.response.file_id) {
      uploadedFileId.value = file.response.file_id;
      Message.success('文件上传成功 / File uploaded successfully');
    } else {
      Message.error('文件上传响应中缺少file_id / Missing file_id in response');
    }
  } else if (file.status === 'error') {
    // 上传错误处理
    Message.error(`文件上传失败: ${file.response?.error || '未知错误'} / Upload failed: ${file.response?.error || 'Unknown error'}`);
  }
};

// 提取报价信息
const extractQuoteInfo = async () => {
  if (!hasUploadedFile.value) {
    Message.warning('请先上传报价文件 / Please upload a quote file first');
    return;
  }
  
  extracting.value = true;
  
  try {
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('登录会话已过期，请重新登录 / Session expired, please login again');
      extracting.value = false;
      return;
    }
    
    // 如果文件已上传到服务器，使用API提取
    // 如果后端API未实现，使用前端模拟实现
    try {
      // 首先尝试调用后端API
      const response = await axios.post(
        'http://localhost:5000/api/quotes/extract',
        { fileId: uploadedFileId.value },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data) {
        // 更新表单数据
        updateFormWithExtractedData(response.data);
        Message.success('成功提取报价信息 / Successfully extracted quote information');
      }
    } catch (error) {
      console.log('后端API提取失败，使用前端实现:', error);
      
      // 后端API调用失败，使用前端模拟实现
      if (fileList.value.length > 0 && fileList.value[0].raw) {
        const file = fileList.value[0].raw;
        const fileType = file.type || '';
        
        // 使用前端提取服务
        const extractedData = await extractQuoteFromFile(file, fileType);
        updateFormWithExtractedData(extractedData);
        
        Message.success('成功提取报价信息（前端模拟） / Successfully extracted quote information (frontend simulation)');
      } else {
        throw new Error('无法访问文件内容 / Cannot access file content');
      }
    }
  } catch (error) {
    console.error('Error extracting quote info:', error);
    Message.error(`提取失败: ${error.message || '未知错误'} / Extraction failed: ${error.message || 'Unknown error'}`);
  } finally {
    extracting.value = false;
  }
};

// 更新表单数据
const updateFormWithExtractedData = (extractedData) => {
  if (extractedData.quoteAmount) quoteForm.quoteAmount = parseFloat(extractedData.quoteAmount);
  if (extractedData.currency) quoteForm.currency = extractedData.currency;
  if (extractedData.wordCount) quoteForm.wordCount = parseInt(extractedData.wordCount);
  if (extractedData.unitPrice) quoteForm.unitPrice = parseFloat(extractedData.unitPrice);
  
  // 如果已有金额和字数，但没有单价，计算单价
  if (quoteForm.quoteAmount > 0 && quoteForm.wordCount > 0 && quoteForm.unitPrice === 0) {
    quoteForm.unitPrice = quoteForm.quoteAmount / quoteForm.wordCount;
  }
};

// 提交报价
const submitQuote = async () => {
  // 表单验证
  if (!quoteForm.task) {
    Message.error('请选择项目任务 / Please select a project task');
    return;
  }
  
  if (!quoteForm.assignee) {
    Message.error('请输入任务负责人 / Please enter task assignee');
    return;
  }
  
  if (!quoteForm.language) {
    Message.error('请选择语言 / Please select a language');
    return;
  }
  
  if (quoteForm.quoteAmount <= 0) {
    Message.error('请输入有效的报价金额 / Please enter a valid quote amount');
    return;
  }
  
  submitting.value = true;
  
  try {
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('登录会话已过期，请重新登录 / Session expired, please login again');
      submitting.value = false;
      return;
    }
    
    // 准备要提交的数据
    const quoteData = {
      projectId: currentProject.value.id,
      task: quoteForm.task,
      assignee: quoteForm.assignee,
      language: quoteForm.language,
      quoteAmount: quoteForm.quoteAmount,
      currency: quoteForm.currency,
      wordCount: quoteForm.wordCount || 0,
      unitPrice: quoteForm.unitPrice || 0,
      deadline: quoteForm.deadline ? formatDate(quoteForm.deadline) : null,
      notes: quoteForm.notes,
      fileId: uploadedFileId.value
    };
    
    // 发送请求
    const response = await axios.post(
      'http://localhost:5000/api/quotes',
      quoteData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (response.status === 200) {
      Message.success('报价提交成功 / Quote submitted successfully');
      emit('uploaded');
      closeModal();
    } else {
      throw new Error('提交失败 / Submission failed');
    }
  } catch (error) {
    console.error('Error submitting quote:', error);
    Message.error(`提交失败: ${error.message || '未知错误'} / Submission failed: ${error.message || 'Unknown error'}`);
  } finally {
    submitting.value = false;
  }
};

// 格式化日期为YYYY-MM-DD格式
const formatDate = (date) => {
  if (!date) return null;
  
  if (date instanceof Date) {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  }
  
  // 如果是字符串，尝试转换
  try {
    const d = new Date(date);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  } catch (e) {
    console.error('Error formatting date:', e);
    return null;
  }
};

// 暴露方法给父组件
defineExpose({
  openQuoteModal
});
</script>

<style scoped>
.quote-uploader-container {
  width: 100%;
}

.quote-amount-row {
  display: flex;
  gap: 12px;
}

:deep(.arco-upload-list-item) {
  margin-top: 8px;
}
</style> 