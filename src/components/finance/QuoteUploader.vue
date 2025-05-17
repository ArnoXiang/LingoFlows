<template>
  <div class="quote-uploader-container">
    <a-modal
      v-model:visible="visible"
      :title="`Quote Entry: ${currentProject ? currentProject.projectName : ''}`"
      :ok-text="'Submit'"
      :cancel-text="'Cancel'"
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
        <a-form-item field="task" label="Project Task" required>
          <a-select 
            v-model="quoteForm.task" 
            placeholder="Select task"
            allow-clear
          >
            <a-option value="translation">Translation Task</a-option>
            <a-option value="lqa">LQA Task</a-option>
            <a-option value="translationUpdate">Translation Update</a-option>
            <a-option value="lqaReportFinalization">LQA Report Finalization</a-option>
          </a-select>
        </a-form-item>
        
        <!-- 任务负责人 -->
        <a-form-item field="assignee" label="Task Assignee" required>
          <a-input v-model="quoteForm.assignee" placeholder="Enter assignee name" />
        </a-form-item>
        
        <!-- 语言选择 -->
        <a-form-item field="language" label="Language" required>
          <a-radio-group v-model="quoteForm.language" type="button" size="medium">
            <a-radio v-for="lang in availableLanguages" :key="lang.code" :value="lang.code">
              {{ lang.name }}
            </a-radio>
          </a-radio-group>
          <div class="language-hint" v-if="availableLanguages.length === 0">
            (No project languages set)
          </div>
        </a-form-item>
        
        <!-- 报价金额和货币 -->
        <div class="quote-amount-row">
          <a-form-item field="quoteAmount" label="Quote Amount" required style="flex: 1; margin-right: 12px;">
            <a-input-number v-model="quoteForm.quoteAmount" placeholder="Quote amount" :min="0" :precision="2" />
          </a-form-item>
          
          <a-form-item field="currency" label="Currency" style="flex: 0.5;">
            <a-select v-model="quoteForm.currency" placeholder="Select currency">
              <a-option value="USD">USD</a-option>
              <a-option value="EUR">EUR</a-option>
              <a-option value="CNY">CNY</a-option>
              <a-option value="JPY">JPY</a-option>
              <a-option value="GBP">GBP</a-option>
            </a-select>
          </a-form-item>
        </div>
        
        <!-- 字数和单价 -->
        <div class="quote-amount-row">
          <a-form-item field="wordCount" label="Word Count" style="flex: 1; margin-right: 12px;">
            <a-input-number v-model="quoteForm.wordCount" placeholder="Word count" :min="0" />
          </a-form-item>
          
          <a-form-item field="unitPrice" label="Unit Price" style="flex: 1;">
            <a-input-number v-model="quoteForm.unitPrice" placeholder="Unit price" :min="0" :precision="4" />
          </a-form-item>
        </div>
        
        <!-- 加权字数 -->
        <a-form-item field="weightedCount" label="Weighted Count">
          <a-input-number v-model="quoteForm.weightedCount" placeholder="Weighted count" :min="0" />
        </a-form-item>
        
        <!-- 截止日期 -->
        <a-form-item field="deadline" label="Deadline">
          <a-date-picker 
            v-model="quoteForm.deadline" 
            style="width: 100%;"
            format="YYYY-MM-DD"
          />
        </a-form-item>
        
        <!-- 上传报价文件 -->
        <a-form-item field="quoteFile" label="Quote File">
          <a-upload
            action="http://localhost:5000/api/upload"
            :file-list="fileList"
            @change="handleFileChange"
            :headers="uploadHeaders"
            :limit="1"
            accept=".xls,.xlsx,.csv,.pdf,.doc,.docx"
            :show-upload-button="true"
            @before-upload="handleBeforeUpload"
          >
            <template #upload-button>
              <a-button type="primary">
                Upload Quote File
              </a-button>
            </template>
          </a-upload>
        </a-form-item>
        
        <!-- 自动提取报价信息按钮 -->
        <a-form-item>
          <a-button type="primary" @click="extractQuoteInfo" :loading="extracting">
            <template #icon><icon-robot /></template>
            Extract Quote Info
          </a-button>
          <a-tooltip content="Automatically extract quote information from the uploaded file">
            <icon-info-circle style="margin-left: 8px; color: var(--color-text-3);" />
          </a-tooltip>
        </a-form-item>
        
        <!-- 提取的数据表格 -->
        <div v-if="extractedTableData.length > 0" class="extracted-data-table">
          <h3>Extracted Quote Information</h3>
          <a-table :columns="extractedColumns" :data="extractedTableData" :bordered="true" :pagination="false">
            <template #footer>
              <div v-if="grandTotal > 0" class="grand-total-row">
                <div class="grand-total-label">Grand Total in USD</div>
                <div class="grand-total-value">${{ grandTotal.toFixed(2) }}</div>
              </div>
            </template>
          </a-table>
        </div>
        
        <!-- 备注 -->
        <a-form-item field="notes" label="Notes">
          <a-textarea v-model="quoteForm.notes" placeholder="Notes" :auto-size="{ minRows: 3, maxRows: 5 }" />
        </a-form-item>
        
        <!-- 提取的特定列数据 -->
        <div v-if="extractedQuoteInfo.length > 0" class="extracted-quote-info">
          <h3>Extracted Quote Information</h3>
          <a-table 
            :columns="extractedInfoColumns" 
            :data="extractedQuoteInfo" 
            :bordered="true" 
            :pagination="false"
          >
            <template #footer>
              <div v-if="grandTotal > 0" class="grand-total-row">
                <div class="grand-total-label">Grand Total in USD</div>
                <div class="grand-total-value">${{ grandTotal.toFixed(2) }}</div>
              </div>
            </template>
          </a-table>
        </div>
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
import * as XLSX from 'xlsx';

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
const extractedTableData = ref([]);
const grandTotal = ref(0);
const extractedQuoteInfo = ref([]);

// 表单数据
const quoteForm = reactive({
  task: '',
  assignee: '',
  language: '',
  quoteAmount: 0,
  currency: 'USD',
  wordCount: 0,
  unitPrice: 0,
  weightedCount: 0,
  deadline: null,
  notes: '',
});

// 表格列定义
const extractedColumns = {
  columnA: [],
  columnB: [],
  columnL: [],
  columnM: []
};

// 特定列数据表格列定义
const extractedInfoColumns = [
  { title: 'Source Language', dataIndex: 'sourceLanguage' },
  { title: 'Target Language', dataIndex: 'targetLanguage' },
  { title: 'Total Word Count', dataIndex: 'totalWordCount' },
  { title: 'Weighted Word Count', dataIndex: 'weightedWordCount' }
];

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

// 修复按钮无法点击的问题 - 调整检查逻辑
const canExtract = computed(() => {
  // 只要有文件就允许点击，不再检查状态
  return true;
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
    Message.error('Only Financial Team or LM can enter quotes');
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
  extractedTableData.value = [];
  grandTotal.value = 0;
  extractedQuoteInfo.value = [];
};

// 处理文件上传
const handleFileChange = (file) => {
  // 检查file参数是否是事件对象或文件数组
  if (file && file.fileList) {
    console.log('Received fileList event:', file.fileList);
    // 处理Arco Design的事件对象
    fileList.value = file.fileList;
    // 检查是否有已完成上传的文件
    const completedFile = file.fileList.find(f => f.status === 'done');
    if (completedFile && completedFile.response && completedFile.response.file_id) {
      uploadedFileId.value = completedFile.response.file_id;
      console.log('Set uploadedFileId from fileList:', uploadedFileId.value);
      
      // 同时保存原始文件对象以便本地处理
      if (completedFile.originFile) {
        window._originalQuoteFile = completedFile.originFile;
        console.log('Saved original file from fileList for local processing');
      } else if (file.fileList.length > 0 && file.fileList[0].originFile) {
        // 如果completedFile没有originFile，尝试从第一个文件获取
        window._originalQuoteFile = file.fileList[0].originFile;
        console.log('Saved first file from fileList for local processing');
      } else if (file.fileList.length > 0 && file.fileList[0].raw) {
        // 尝试获取raw属性（有些UI库使用raw而不是originFile）
        window._originalQuoteFile = file.fileList[0].raw;
        console.log('Saved raw file from fileList for local processing');
      }
    }
    return;
  }
  
  // 正常处理单个文件状态变化
  console.log('File upload status changed:', file);
  console.log('Current file status:', file.status);
  console.log('File object:', file);
  
  if (file.status === 'done') {
    // 上传成功处理
    console.log('File upload response:', file.response);
    if (file.response && file.response.file_id) {
      // 保存文件ID
      uploadedFileId.value = file.response.file_id;
      console.log('File uploaded successfully, saved file_id:', uploadedFileId.value);
      Message.success('File uploaded successfully. Click "Extract Quote Info" to process the file.');
      
      // 保存原始文件对象以便本地处理
      if (file.originFile) {
        console.log('Saving original file for local processing');
        window._originalQuoteFile = file.originFile;
      } else if (file.raw) {
        // 尝试使用raw属性（有些UI库使用raw而不是originFile）
        window._originalQuoteFile = file.raw;
        console.log('Saving raw file for local processing');
      }
    } else {
      console.error('Missing file_id in response:', file.response);
      Message.error('Missing file_id in server response. Will try local processing.');
      
      // 即使没有file_id，也保存文件对象以便本地处理
      if (file.originFile) {
        window._originalQuoteFile = file.originFile;
        console.log('Saved file for local processing anyway');
      } else if (file.raw) {
        window._originalQuoteFile = file.raw;
        console.log('Saved raw file for local processing anyway');
      }
    }
  } else if (file.status === 'error') {
    // 上传错误处理
    console.error('File upload error:', file.response);
    Message.error(`Upload failed: ${file.response?.error || 'Unknown error'}. Will try local processing.`);
    
    // 保存文件对象以便本地处理
    if (file.originFile) {
      window._originalQuoteFile = file.originFile;
      console.log('Saved file for local processing despite upload error');
    } else if (file.raw) {
      window._originalQuoteFile = file.raw;
      console.log('Saved raw file for local processing despite upload error');
    }
  } else if (file.status === 'uploading') {
    console.log('File uploading...');
    // 保存文件对象
    if (file.originFile) {
      window._originalQuoteFile = file.originFile;
      console.log('Saving file reference during upload');
    } else if (file.raw) {
      window._originalQuoteFile = file.raw;
      console.log('Saving raw file reference during upload');
    }
  } else if (file.status === 'removed') {
    console.log('File removed');
    // 文件被删除，清除文件ID和引用
    uploadedFileId.value = null;
    window._originalQuoteFile = null;
  }
};

// 文件上传前处理
const handleBeforeUpload = (file) => {
  console.log('Before upload file:', file);
  // 在上传前保存文件引用
  window._originalQuoteFile = file;
  console.log('Saved file reference before upload');
  return true; // 允许上传继续
};

// 提取报价信息 - 添加本地处理作为备份
const extractQuoteInfo = async () => {
  console.log("===== Extract Quote Info Debugging =====");
  console.log("File List:", fileList.value);
  console.log("Uploaded File ID:", uploadedFileId.value);
  console.log("Original Quote File exists:", !!window._originalQuoteFile);
  if (window._originalQuoteFile) {
    console.log("Original Quote File type:", typeof window._originalQuoteFile);
    console.log("Original Quote File name:", window._originalQuoteFile.name);
    console.log("Original Quote File size:", window._originalQuoteFile.size);
  }
  console.log("======================================");

  extracting.value = true;
  extractedTableData.value = [];
  grandTotal.value = 0;
  extractedQuoteInfo.value = [];
  
  try {
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('Session expired, please login again');
      extracting.value = false;
      return;
    }
    
    // 检查是否有服务器端文件ID
    if (uploadedFileId.value) {
      console.log('Attempting to use server-side file processing');
      try {
        // 调用后端API解析已上传的文件
        console.log('Calling backend API to extract data from file ID:', uploadedFileId.value);
        
        const response = await axios.post(
          'http://localhost:5000/api/quotes/extract',
          { fileId: uploadedFileId.value },
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            timeout: 30000 // 增加超时时间，因为Excel解析可能需要更长时间
          }
        );
        
        console.log('Backend extraction response:', response.data);
        
        // 处理后端返回的数据
        processExtractedData(response.data);
        return; // 成功处理后退出函数
      } catch (apiError) {
        console.error('Backend API error, falling back to local processing:', apiError);
      }
    }
    
    // 本地处理 - 如果没有fileId或API调用失败
    if (!window._originalQuoteFile) {
      console.log('No _originalQuoteFile, trying to get file from fileList');
      // 尝试从fileList中获取文件
      if (fileList.value && fileList.value.length > 0) {
        const firstFile = fileList.value[0];
        if (firstFile.originFile) {
          window._originalQuoteFile = firstFile.originFile;
          console.log('Retrieved file from fileList.originFile');
        } else if (firstFile.raw) {
          window._originalQuoteFile = firstFile.raw;
          console.log('Retrieved file from fileList.raw');
        } else {
          Message.error('No file available for extraction');
          extracting.value = false;
          return;
        }
      } else {
        Message.error('No file available for extraction');
        extracting.value = false;
        return;
      }
    }
    
    // 使用保存的文件引用进行本地解析
    const file = window._originalQuoteFile;
    console.log('Local file processing:', file);
    
    // 读取文件内容
    const data = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(new Uint8Array(e.target.result));
      reader.onerror = (e) => reject(new Error('Failed to read file'));
      reader.readAsArrayBuffer(file);
    });
    
    // 使用xlsx库解析Excel文件
    const workbook = XLSX.read(data, { type: 'array' });
    
    // 检查是否存在名为"Log"的表格
    if (!workbook.SheetNames.includes('Log')) {
      console.warn('No "Log" sheet found in the Excel file');
      // 尝试使用第一个sheet
      if (workbook.SheetNames.length > 0) {
        console.log('Using the first sheet instead:', workbook.SheetNames[0]);
      } else {
        throw new Error('Excel file does not contain any sheets');
      }
    }
    
    // 获取"Log"表格内容，如果不存在则使用第一个表格
    const sheetName = workbook.SheetNames.includes('Log') ? 'Log' : workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    
    // 将表格转换为JSON对象数组
    const jsonData = XLSX.utils.sheet_to_json(sheet, { 
      header: 1,  // 使用1-indexed数组作为header
      defval: '',  // 默认值为空字符串
      blankrows: true,  // 不忽略空行，我们需要检测空行
      raw: false  // 不使用raw值，转换为字符串以便统一处理
    });
    
    console.log('Extracted sheet data:', jsonData);
    
    // 提取A、B、L、M列数据
    extractedColumns.columnA = [];
    extractedColumns.columnB = [];
    extractedColumns.columnL = [];
    extractedColumns.columnM = [];
    
    let mColumnValueAfterEmptyRow = '';
    let foundEmptyRow = false;
    
    // 遍历行数据，提取A、B、L、M列直到遇到空行
    for (let i = 0; i < jsonData.length; i++) {
      const row = jsonData[i];
      
      // 检查是否为空行（所有单元格为空或只有空白字符）
      const isEmptyRow = !row.some(cell => (cell && String(cell).trim() !== ''));
      
      if (!foundEmptyRow) {
        // 尚未找到空行，继续收集数据
        if (!isEmptyRow) {
          // 提取A列（索引0）、B列（索引1）、L列（索引11）、M列（索引12）的数据
          if (row[0] !== undefined && row[0] !== '') {
            extractedColumns.columnA.push(row[0]);
          }
          
          if (row[1] !== undefined && row[1] !== '') {
            extractedColumns.columnB.push(row[1]);
          }
          
          if (row.length > 11 && row[11] !== undefined && row[11] !== '') {
            extractedColumns.columnL.push(row[11]);
          }
          
          if (row.length > 12 && row[12] !== undefined && row[12] !== '') {
            extractedColumns.columnM.push(row[12]);
          }
        } else {
          // 找到空行
          foundEmptyRow = true;
          
          // 检查空行之后M列（索引12）的下一个单元格
          for (let j = i + 1; j < jsonData.length; j++) {
            const nextRow = jsonData[j];
            if (nextRow && nextRow.length > 12 && nextRow[12] !== undefined && nextRow[12] !== '') {
              mColumnValueAfterEmptyRow = nextRow[12];
              break;
            }
          }
        }
      }
    }
    
    console.log('Extracted column data:', extractedColumns);
    console.log('M column value after empty row:', mColumnValueAfterEmptyRow);
    
    // 创建表格数据以显示提取的信息 - 垂直展示
    const extractedInfo = [];
    
    // 去掉可能存在的标题行
    let columnAData = [...extractedColumns.columnA];
    let columnBData = [...extractedColumns.columnB];
    let columnLData = [...extractedColumns.columnL];
    let columnMData = [...extractedColumns.columnM];
    
    // 如果第一行是标题行（包含Source/Target/Total/Weighted等）则跳过
    if (columnAData[0] && (columnAData[0].toLowerCase().includes('source'))) {
      columnAData.shift();
      columnBData.shift();
      columnLData.shift();
      columnMData.shift();
    }
    
    // 将每列数据垂直排列
    const maxLength = Math.max(
      columnAData.length,
      columnBData.length,
      columnLData.length,
      columnMData.length
    );
    
    for (let i = 0; i < maxLength; i++) {
      extractedInfo.push({
        sourceLanguage: columnAData[i] || '',
        targetLanguage: columnBData[i] || '',
        totalWordCount: columnLData[i] || '',
        weightedWordCount: columnMData[i] || ''
      });
    }
    
    // 添加Grand Total行到常规提取数据
    let grandTotalValue = 0;
    if (mColumnValueAfterEmptyRow) {
      // 提取数字部分
      const numericValue = parseFloat(mColumnValueAfterEmptyRow.replace(/[^0-9.]/g, '')) || 0;
      grandTotalValue = numericValue;
    }
    
    // 修正变量名称并设置总价格
    extractedQuoteInfo.value = extractedInfo;
    grandTotal.value = grandTotalValue;
    
    // 处理常规提取数据
    // 如果值很多，可能还需要将部分数据放入常规提取
    const extractedData = {
      sourceLanguage: columnAData[0] || '',
      targetLanguages: columnBData,
      wordCount: parseFloat(columnLData[0] || '0') || 0,
      weightedCount: parseFloat(columnMData[0] || '0') || 0,
      quoteAmount: grandTotalValue,
      currency: 'USD'
    };
    
    // 处理常规提取数据并显示
    processExtractedData(extractedData);
    
  } catch (error) {
    console.error('Error extracting quote info:', error);
    Message.error('Failed to extract quote information');
  } finally {
    extracting.value = false;
  }
};

// 处理提取的数据
const processExtractedData = (extractedData) => {
  if (!extractedData) {
    Message.warning('No valid data could be extracted');
    return;
  }
  
  console.log('Processing extracted data:', extractedData);
  
  // 验证提取的数据是否包含必要的字段
  if (extractedData.sourceLanguage && extractedData.targetLanguages && extractedData.targetLanguages.length > 0) {
    const source = extractedData.sourceLanguage;
    
    // 计算每种语言的字数平均值
    const totalWordCount = Math.round(extractedData.wordCount / extractedData.targetLanguages.length);
    const weightedWordCount = Math.round(extractedData.weightedCount / extractedData.targetLanguages.length);
    
    // 为每个目标语言创建一行数据
    extractedTableData.value = extractedData.targetLanguages.map(target => ({
      sourceLanguage: source,
      targetLanguage: target,
      totalWordCount: totalWordCount,
      weightedWordCount: weightedWordCount
    }));
    
    // 设置总价格
    grandTotal.value = extractedData.quoteAmount;
    
    // 将总金额设置到表单中便于提交
    quoteForm.quoteAmount = extractedData.quoteAmount;
    
    Message.success('Successfully extracted quote information');
  } else {
    Message.warning('No valid language data found in the file');
  }
};

// 提交报价
const submitQuote = async () => {
  // 表单验证
  if (!quoteForm.task) {
    Message.error('Please select a project task');
    return;
  }
  
  if (!quoteForm.assignee) {
    Message.error('Please enter task assignee');
    return;
  }
  
  if (!quoteForm.language) {
    Message.error('Please select a language');
    return;
  }
  
  if (quoteForm.quoteAmount <= 0) {
    Message.error('Please enter a valid quote amount');
    return;
  }
  
  submitting.value = true;
  
  try {
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('Session expired, please login again');
      submitting.value = false;
      return;
    }
    
    // 检查当前项目是否有效
    if (!currentProject.value || !currentProject.value.id) {
      Message.error('Invalid project information, please try again');
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
      weightedCount: quoteForm.weightedCount || 0,
      deadline: formattedDeadline,
      notes: quoteForm.notes,
      fileId: uploadedFileId.value,
      extractedInfo: extractedQuoteInfo.value.length > 0 ? JSON.stringify(extractedQuoteInfo.value) : null
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
        Message.success('Quote submitted successfully');
        console.log('报价创建成功，ID:', response.data.id);
        emit('uploaded');
        closeModal();
      } else {
        console.error('报价提交返回了非成功状态码:', response.status);
        console.error('响应数据:', response.data);
        throw new Error(`Submission returned a non-success status code: ${response.status}`);
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
          throw new Error(`Database error: ${errorMsg}`);
        } else {
          throw new Error(`Server internal error: ${errorMsg}`);
        }
      }
      
      throw axiosError; // 重新抛出，让下面的错误处理逻辑处理
    }
  } catch (error) {
    console.error('Error submitting quote:', error);
    
    let errorMessage = 'Unknown error';
    
    if (error.response) {
      // 服务器响应了，但返回错误状态码
      console.error('服务器错误响应:', error.response.data);
      console.error('状态码:', error.response.status);
      
      // 针对不同状态码显示不同错误信息
      if (error.response.status === 401) {
        errorMessage = 'Authentication failed, please login again';
      } else if (error.response.status === 403) {
        errorMessage = 'Insufficient permissions to submit quote';
      } else if (error.response.status === 500) {
        errorMessage = 'Server internal error';
      } else {
        errorMessage = `Server error: ${error.response.status} - ${error.response.data.error || error.message}`;
      }
    } else if (error.request) {
      // 请求已发送，但没有收到响应
      console.error('没有收到服务器响应:', error.request);
      errorMessage = 'No response from server, please check network connection and backend service status';
    } else {
      // 请求配置错误
      console.error('请求错误:', error.message);
      errorMessage = `Request error: ${error.message}`;
    }
    
    Message.error(`Submission failed: ${errorMessage}`);
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
      console.error('Invalid date:', date);
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

.extracted-data-table {
  margin-top: 20px;
}

.grand-total-row {
  display: flex;
  justify-content: flex-end;
  padding: 10px 16px;
  border-top: 1px solid var(--color-border);
  font-weight: bold;
}

.grand-total-label {
  margin-right: 20px;
  min-width: 150px;
  text-align: right;
}

.grand-total-value {
  min-width: 100px;
  text-align: right;
}

.extracted-quote-info {
  margin-top: 20px;
  border-top: 1px solid var(--color-border-2);
  padding-top: 16px;
}

.extracted-quote-info h3 {
  margin-bottom: 16px;
  color: var(--color-text-1);
}
</style> 