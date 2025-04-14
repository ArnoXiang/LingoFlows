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
      :ok-button-props="{ type: 'primary' }"
      :cancel-button-props="{ type: 'default' }"
      :mask-closable="false"
      unmount-on-close
      style="width: 700px;"
    >
      <a-form :model="quoteForm" layout="vertical" @submit.prevent="submitQuote">
        <!-- 项目任务选择 -->
        <a-form-item field="task" label="项目任务 / Project Task" required>
          <a-select 
            v-model="quoteForm.task" 
            placeholder="选择任务 / Select task"
            allow-clear
          >
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
          <a-radio-group v-model="quoteForm.language" type="button" size="medium">
            <a-radio v-for="lang in availableLanguages" :key="lang.code" :value="lang.code">
              {{ lang.name }}
            </a-radio>
          </a-radio-group>
          <div class="language-hint" v-if="availableLanguages.length === 0">
            (未设置项目语言 / No project languages set)
          </div>
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
          <a-date-picker 
            v-model="quoteForm.deadline" 
            style="width: 100%;"
            format="YYYY-MM-DD"
          />
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
              <a-button type="primary">
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
  notes: '',
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
  if (props.userRole !== 'FT' && props.userRole !== 'LM') {
    Message.error('只有财务团队或本地化经理可以录入报价 / Only Financial Team or LM can enter quotes');
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
    
    // 检查当前项目是否有效
    if (!currentProject.value || !currentProject.value.id) {
      Message.error('项目信息无效，请重试 / Invalid project information, please try again');
      submitting.value = false;
      return;
    }
    
    // 处理日期格式
    const formattedDeadline = quoteForm.deadline ? formatDate(quoteForm.deadline) : null;
    
    // 准备要提交的数据
    const quoteData = {
      projectId: currentProject.value.id,
      task: quoteForm.task,
      assignee: quoteForm.assignee,
      language: quoteForm.language,
      quoteAmount: quoteForm.quoteAmount,
      currency: quoteForm.currency,
      wordCount: quoteForm.wordCount || 0,
      unitPrice: quoteForm.unitPrice !== undefined ? quoteForm.unitPrice : 0,
      deadline: formattedDeadline,
      notes: quoteForm.notes,
      fileId: uploadedFileId.value
    };
    
    // 完整的请求URL
    const apiUrl = 'http://localhost:5000/api/quotes';
    console.log(`准备向 ${apiUrl} 提交报价数据:`, quoteData);
    
    // 设置请求配置
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 15000 // 15秒超时，防止长时间等待
    };
    
    console.log('请求配置:', config);
    
    try {
      // 发送请求
      const response = await axios.post(apiUrl, quoteData, config);
      
      console.log('报价提交响应:', response);
      console.log('响应状态码:', response.status);
      console.log('响应数据:', response.data);
      
      // 检查状态码 - 后端返回201表示创建成功
      if (response.status === 201 || response.status === 200) {
        Message.success('报价提交成功 / Quote submitted successfully');
        console.log('报价创建成功，ID:', response.data.id);
        emit('uploaded');
        closeModal();
      } else {
        console.error('报价提交返回了非成功状态码:', response.status);
        console.error('响应数据:', response.data);
        throw new Error(`提交返回了非成功状态码: ${response.status} / Submission returned a non-success status code: ${response.status}`);
      }
    } catch (axiosError) {
      console.error('Axios错误:', axiosError);
      
      // 检查是否是服务器内部错误(500)
      if (axiosError.response && axiosError.response.status === 500) {
        console.error('服务器内部错误，可能是数据库问题');
        console.error('错误详情:', axiosError.response.data);
        
        // 检查是否是MySQL错误
        const errorMsg = axiosError.response.data.error || '';
        if (errorMsg.includes('MySQL') || errorMsg.includes('database') || errorMsg.includes('sql')) {
          throw new Error(`数据库错误: ${errorMsg} / Database error: ${errorMsg}`);
        } else {
          throw new Error(`服务器内部错误: ${errorMsg} / Server internal error: ${errorMsg}`);
        }
      }
      
      throw axiosError; // 重新抛出，让下面的错误处理逻辑处理
    }
  } catch (error) {
    console.error('Error submitting quote:', error);
    
    let errorMessage = '未知错误 / Unknown error';
    
    if (error.response) {
      // 服务器响应了，但返回错误状态码
      console.error('服务器错误响应:', error.response.data);
      console.error('状态码:', error.response.status);
      
      // 针对不同状态码显示不同错误信息
      if (error.response.status === 401) {
        errorMessage = '认证失败，请重新登录 / Authentication failed, please login again';
      } else if (error.response.status === 403) {
        errorMessage = '权限不足，无法提交报价 / Insufficient permissions to submit quote';
      } else if (error.response.status === 500) {
        errorMessage = '服务器内部错误 / Server internal error';
      } else {
        errorMessage = `服务器错误: ${error.response.status} - ${error.response.data.error || error.message}`;
      }
    } else if (error.request) {
      // 请求已发送，但没有收到响应
      console.error('没有收到服务器响应:', error.request);
      errorMessage = '服务器没有响应，请检查网络连接和后端服务状态 / No response from server, please check network connection and backend service status';
    } else {
      // 请求配置错误
      console.error('请求错误:', error.message);
      errorMessage = `请求错误: ${error.message} / Request error: ${error.message}`;
    }
    
    Message.error(`提交失败: ${errorMessage} / Submission failed: ${errorMessage}`);
  } finally {
    submitting.value = false;
  }
};

// 格式化日期为YYYY-MM-DD格式
const formatDate = (date) => {
  if (!date) return null;
  
  try {
    let dateObj;
    
    if (date instanceof Date) {
      dateObj = date;
    } else {
      // 如果是字符串，尝试转换
      dateObj = new Date(date);
    }
    
    // 检查日期是否有效
    if (isNaN(dateObj.getTime())) {
      console.error('无效的日期:', date);
      return null;
    }
    
    // 格式化为YYYY-MM-DD
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
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

.language-hint {
  margin-top: 8px;
  font-size: 0.8em;
  color: var(--color-text-3);
}
</style> 