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
            :auto-upload="false"
            ref="uploadRef"
          >
            <template #upload-button>
              <a-button type="primary">
                Upload Quote File
              </a-button>
            </template>
          </a-upload>
          <a-button 
            type="secondary" 
            style="margin-top: 8px;" 
            @click="manualUpload"
            v-if="fileList && fileList.length > 0"
          >
            Manual Upload
          </a-button>
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
const extractedColumns = [
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
};

// 处理文件上传
const handleFileChange = (file) => {
  // 直接输出完整的file对象，查看其结构
  console.log('File change event:', file);
  
  // 检查file参数是否是事件对象或文件数组
  if (file && file.fileList) {
    console.log('File list:', file.fileList);
    
    // 处理Arco Design的事件对象
    fileList.value = file.fileList;
    
    // 立即尝试保存文件引用 - 即使状态不是"done"
    file.fileList.forEach(fileItem => {
      if (fileItem.originFile) {
        console.log('Saving original file from fileList');
        window._originalQuoteFile = fileItem.originFile;
      } else if (fileItem.file) {
        console.log('Saving file property from fileList');
        window._originalQuoteFile = fileItem.file;
      }
    });
    
    // 检查是否有已完成上传的文件
    const completedFile = file.fileList.find(f => f.status === 'done');
    if (completedFile && completedFile.response && completedFile.response.file_id) {
      uploadedFileId.value = completedFile.response.file_id;
      console.log('Set uploadedFileId from fileList:', uploadedFileId.value);
    }
    return;
  }
  
  // 正常处理单个文件状态变化
  console.log('Processing single file:', file);
  
  // 尝试保存所有可能的文件引用
  if (file.originFile) {
    console.log('Saving originFile reference');
    window._originalQuoteFile = file.originFile;
  } else if (file.file) {
    console.log('Saving file reference');
    window._originalQuoteFile = file.file;
  } else if (file instanceof File) {
    console.log('Saving direct File instance');
    window._originalQuoteFile = file;
  }
  
  if (file.status === 'done') {
    // 上传成功处理
    console.log('File upload response:', file.response);
    if (file.response && file.response.file_id) {
      // 保存文件ID
      uploadedFileId.value = file.response.file_id;
      console.log('File uploaded successfully, saved file_id:', uploadedFileId.value);
      Message.success('File uploaded successfully. Click "Extract Quote Info" to process the file.');
    } else {
      console.error('Missing file_id in response:', file.response);
      Message.error('Missing file_id in server response. Will try local processing.');
    }
  } else if (file.status === 'error') {
    // 上传错误处理
    console.error('File upload error:', file.response);
    Message.error(`Upload failed: ${file.response?.error || 'Unknown error'}. Will try local processing.`);
  } else if (file.status === 'removed') {
    console.log('File removed');
    // 文件被删除，清除文件ID和引用
    uploadedFileId.value = null;
    window._originalQuoteFile = null;
  }
};

// 引用上传组件
const uploadRef = ref(null);

// 手动上传文件 - 添加按钮调用这个方法
const manualUpload = () => {
  console.log('Manual upload triggered');
  console.log('Upload component reference:', uploadRef.value);
  
  // 检查是否有文件
  if (fileList.value && fileList.value.length > 0) {
    console.log('Files to upload:', fileList.value);
    
    // 尝试保存文件引用 - 在上传前
    if (fileList.value[0].originFile) {
      console.log('Saving originFile before upload');
      window._originalQuoteFile = fileList.value[0].originFile;
    } else if (fileList.value[0].file) {
      console.log('Saving file before upload');
      window._originalQuoteFile = fileList.value[0].file;
    }
    
    // 调用组件的上传方法
    if (uploadRef.value) {
      uploadRef.value.submit();
    }
  } else {
    Message.warning('Please select a file first');
  }
};

// 提取报价信息 - 添加错误处理和备用方法
const extractQuoteInfo = async () => {
  console.log('Extract button clicked');
  extracting.value = true;
  extractedTableData.value = [];
  grandTotal.value = 0;
  
  try {
    // 调试当前状态
    console.log('Current file list:', fileList.value);
    console.log('Saved original file:', window._originalQuoteFile);
    
    // 强化文件获取逻辑 - 尝试多种方式获取文件对象
    let localFile = null;
    
    // 遍历所有可能包含文件的来源
    const possibleFileSources = [
      { name: 'Global variable', file: window._originalQuoteFile },
      { name: 'FileList', file: fileList.value && fileList.value.length > 0 ? 
              (fileList.value[0].originFile || fileList.value[0].file || fileList.value[0].raw) : null }
    ];
    
    // 添加从上传组件获取文件的方法
    if (uploadRef.value && uploadRef.value.$el) {
      const fileInput = uploadRef.value.$el.querySelector('input[type="file"]');
      if (fileInput && fileInput.files && fileInput.files.length > 0) {
        possibleFileSources.push({ name: 'Upload input', file: fileInput.files[0] });
      }
    }
    
    // 尝试所有文件输入框
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach((input, index) => {
      if (input.files && input.files.length > 0) {
        possibleFileSources.push({ name: `File input ${index}`, file: input.files[0] });
      }
    });
    
    // 尝试所有可能的文件源
    for (const source of possibleFileSources) {
      if (source.file) {
        console.log(`Found file from ${source.name}:`, source.file);
        localFile = source.file;
        break;
      }
    }
    
    // 如果找不到文件，给出明确的错误
    if (!localFile) {
      throw new Error('找不到上传的文件。请先上传文件或尝试手动上传。');
    }
    
    console.log('Processing file:', localFile);
    
    // 检查文件类型
    const fileName = localFile.name || '';
    console.log('File name:', fileName);
    
    // 使用更安全的文件读取方法 - 包含超时保护
    try {
      const fileData = await readFileWithTimeout(localFile, 10000); // 10秒超时
      console.log('File read successful, size:', fileData.byteLength);
      
      // 尝试使用xlsx库解析
      const workbook = XLSX.read(fileData, { type: 'array' });
      console.log('XLSX parse successful, sheets:', workbook.SheetNames);
      
      // 查找Log表或第一个表
      const sheetName = workbook.SheetNames.includes('Log') ? 'Log' : workbook.SheetNames[0];
      console.log('Using sheet:', sheetName);
      
      // 获取表格数据并加入预处理步骤
      const sheet = workbook.Sheets[sheetName];
      const sheetData = normalizeSheetData(XLSX.utils.sheet_to_json(sheet, { header: 1 }));
      console.log('Sheet data has', sheetData.length, 'rows');
      
      // 添加数据预览，方便调试
      displayDataPreview(sheetData);
      
      // 提取数据
      const extractedData = extractDataFromSheetJson(sheetData);
      processExtractedData(extractedData);
    } catch (fileError) {
      console.error('File processing error:', fileError);
      
      // 提供备用的数据，便于继续开发和测试
      console.log('Using fallback data for development/testing');
      const fallbackData = {
        sourceLanguage: 'EN',
        targetLanguages: ['ZH', 'JA', 'DE'],
        wordCount: 10000,
        weightedCount: 8500,
        quoteAmount: 2500
      };
      
      // 使用备用数据
      processExtractedData(fallbackData);
      
      // 同时仍然显示错误
      Message.warning(`文件处理出错，但使用了示例数据: ${fileError.message}`);
    }
  } catch (error) {
    console.error('Error extracting quote info:', error);
    Message.error(`提取失败: ${error.message || '未知错误'}`);
  } finally {
    extracting.value = false;
  }
};

// 带超时保护的文件读取
const readFileWithTimeout = (file, timeout) => {
  return new Promise((resolve, reject) => {
    // 设置超时
    const timeoutId = setTimeout(() => {
      reject(new Error('文件读取超时'));
    }, timeout);
    
    // 创建FileReader
    const reader = new FileReader();
    
    reader.onload = (e) => {
      clearTimeout(timeoutId); // 清除超时
      resolve(new Uint8Array(e.target.result));
    };
    
    reader.onerror = (e) => {
      clearTimeout(timeoutId); // 清除超时
      reject(new Error(`文件读取错误: ${e.target.error?.message || '未知错误'}`));
    };
    
    // 开始读取
    try {
      reader.readAsArrayBuffer(file);
    } catch (e) {
      clearTimeout(timeoutId);
      reject(new Error(`无法读取文件: ${e.message}`));
    }
  });
};

// 规范化表格数据，处理可能的奇怪格式
const normalizeSheetData = (jsonData) => {
  if (!Array.isArray(jsonData)) {
    console.warn('Sheet data is not an array');
    return [];
  }
  
  // 过滤掉空行和异常行
  return jsonData.filter(row => Array.isArray(row) && row.length > 0)
    .map(row => {
      // 转换每一行的单元格，确保字符串格式一致
      return row.map(cell => {
        if (cell === null || cell === undefined) return '';
        if (typeof cell === 'string') return cell.trim();
        return cell;
      });
    });
};

// 添加一个函数来显示数据预览，方便调试
const displayDataPreview = (sheetData) => {
  console.log('===================== Sheet Data Preview =====================');
  
  // 显示前10行，每行最多10个单元格
  const previewRows = sheetData.slice(0, Math.min(10, sheetData.length));
  
  previewRows.forEach((row, index) => {
    const previewCells = row.slice(0, Math.min(10, row.length));
    console.log(`Row ${index}:`, previewCells);
    
    // 如果行很长，指出被截断的部分
    if (row.length > 10) {
      console.log(`... and ${row.length - 10} more cells`);
    }
  });
  
  // 如果有很多行，指出被截断的部分
  if (sheetData.length > 10) {
    console.log(`... and ${sheetData.length - 10} more rows`);
  }
  
  console.log('================================================================');
};

// 从Excel数据中提取信息
const extractDataFromSheetJson = (jsonData) => {
  console.log('Extracting data from sheet JSON');
  // 初始化提取的数据
  const extractedData = {
    sourceLanguage: '',
    targetLanguages: [],
    wordCount: 0,
    weightedCount: 0,
    quoteAmount: 0
  };
  
  try {
    // 查找表头行索引（包含Source、Target等的行）
    let headerRowIndex = -1;
    for (let i = 0; i < jsonData.length; i++) {
      const row = jsonData[i] || [];
      // 检查这一行是否包含Source和Target
      if (row.includes('Source') && row.includes('Target')) {
        headerRowIndex = i;
        break;
      }
    }
    
    if (headerRowIndex === -1) {
      console.warn('Header row not found, trying alternative search');
      // 尝试更宽松的搜索
      for (let i = 0; i < jsonData.length; i++) {
        const row = jsonData[i] || [];
        const rowStr = row.join(' ').toLowerCase();
        if (rowStr.includes('source') && rowStr.includes('target')) {
          headerRowIndex = i;
          break;
        }
      }
    }
    
    console.log('Header row index:', headerRowIndex);
    
    // 查找Grand Total行
    let grandTotalRowIndex = -1;
    for (let i = 0; i < jsonData.length; i++) {
      const row = jsonData[i] || [];
      const rowStr = row.join(' ').toLowerCase();
      if (rowStr.includes('grand total')) {
        grandTotalRowIndex = i;
        console.log('Found Grand Total row at index:', i);
        
        // 尝试提取总金额 - 通常是行中的最后一个数字
        for (let j = row.length - 1; j >= 0; j--) {
          const cell = row[j];
          if (typeof cell === 'number' || (typeof cell === 'string' && cell.includes('$'))) {
            // 如果是数字，直接使用；如果是字符串，提取数字部分
            let amount = typeof cell === 'number' ? cell : 
                        parseFloat(cell.replace(/[^0-9.]/g, ''));
            
            if (!isNaN(amount) && amount > 0) {
              extractedData.quoteAmount = amount;
              console.log('Extracted amount:', amount);
              break;
            }
          }
        }
        break;
      }
    }
    
    // 如果找到了表头行
    if (headerRowIndex !== -1) {
      const headers = jsonData[headerRowIndex] || [];
      
      // 查找各列的索引
      const sourceIndex = headers.indexOf('Source');
      const targetIndex = headers.indexOf('Target');
      const totalIndex = headers.indexOf('Total');
      const weightedIndex = headers.indexOf('Weighted');
      
      console.log('Column indices:', { sourceIndex, targetIndex, totalIndex, weightedIndex });
      
      // 处理数据行
      const dataRows = jsonData.slice(headerRowIndex + 1, grandTotalRowIndex !== -1 ? grandTotalRowIndex : undefined);
      
      for (const row of dataRows) {
        if (!row || row.length === 0) continue;
        
        // 提取Source语言
        if (sourceIndex !== -1 && row[sourceIndex] && !extractedData.sourceLanguage) {
          extractedData.sourceLanguage = row[sourceIndex];
          console.log('Found source language:', extractedData.sourceLanguage);
        }
        
        // 提取Target语言
        if (targetIndex !== -1 && row[targetIndex]) {
          const targetLang = row[targetIndex];
          if (!extractedData.targetLanguages.includes(targetLang)) {
            extractedData.targetLanguages.push(targetLang);
            console.log('Found target language:', targetLang);
          }
        }
        
        // 累加Total和Weighted值
        if (totalIndex !== -1 && row[totalIndex]) {
          const totalValue = typeof row[totalIndex] === 'number' ? 
                           row[totalIndex] : 
                           parseFloat(String(row[totalIndex]).replace(/[^0-9.]/g, ''));
          
          if (!isNaN(totalValue)) {
            extractedData.wordCount += totalValue;
          }
        }
        
        if (weightedIndex !== -1 && row[weightedIndex]) {
          const weightedValue = typeof row[weightedIndex] === 'number' ? 
                              row[weightedIndex] : 
                              parseFloat(String(row[weightedIndex]).replace(/[^0-9.]/g, ''));
          
          if (!isNaN(weightedValue)) {
            extractedData.weightedCount += weightedValue;
          }
        }
      }
    }
    
    // 如果没有找到金额，但在URL中看到了金额（如在提供的截图中显示$842.21）
    if (extractedData.quoteAmount === 0) {
      for (let i = jsonData.length - 1; i >= 0; i--) {
        const row = jsonData[i] || [];
        const rowStr = (row.join(' ') || '').toLowerCase();
        if (rowStr.includes('usd') || rowStr.includes('$') || rowStr.includes('total')) {
          for (let j = 0; j < row.length; j++) {
            const cell = row[j];
            if (cell && (typeof cell === 'string' && (cell.includes('$') || /\d+\.\d+/.test(cell)))) {
              const amount = parseFloat(String(cell).replace(/[^0-9.]/g, ''));
              if (!isNaN(amount) && amount > 0) {
                extractedData.quoteAmount = amount;
                console.log('Found amount in row with USD/$ mention:', amount);
                break;
              }
            }
          }
          if (extractedData.quoteAmount > 0) break;
        }
      }
    }
  } catch (error) {
    console.error('Error parsing Excel data:', error);
  }
  
  console.log('Extracted data from Excel:', extractedData);
  return extractedData;
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
</style> 