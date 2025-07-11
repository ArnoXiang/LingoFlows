<template>
  <div class="request-form-container">
    <h2>Submit Localization Request</h2>
    <a-form :model="form" :style="{ width: '600px' }" @submit="handleSubmit">
      <a-form-item field="requestName" label="Request Name" required>
        <a-input v-model="form.requestName" placeholder="Provide a clear and distinguishable title" />
      </a-form-item>
      
      <a-form-item field="requestBackground" label="Request Background" required>
        <a-textarea 
          v-model="form.requestBackground" 
          :auto-size="{ minRows: 3, maxRows: 6 }"
          placeholder="Briefly outline the project scope and objectives"
        />
      </a-form-item>
      
      <a-form-item field="sourceLanguage" label="Source Language" required>
        <a-select v-model="form.sourceLanguage" placeholder="Select source language">
          <a-option v-for="language in languages" :key="language.code" :value="language.code">
            {{ language.name.replace(/^.*? \/ /, '') }}
          </a-option>
        </a-select>
      </a-form-item>
      
      <a-form-item field="targetLanguages" label="Target Languages" required>
        <a-select 
          v-model="form.targetLanguages" 
          placeholder="Select target languages"
          multiple
          allow-clear
        >
          <a-option v-for="language in targetLanguageOptions" :key="language.code" :value="language.code">
            {{ language.name.replace(/^.*? \/ /, '') }}
          </a-option>
        </a-select>
      </a-form-item>
      
      <a-form-item field="wordCount" label="Estimated Word Count" required>
        <a-input-number v-model="form.wordCount" placeholder="Estimated word count" :min="1" />
      </a-form-item>
      
      <a-form-item field="additionalRequirements" label="Additional Requirements">
        <a-space direction="vertical" style="width: 100%;">
          <a-checkbox v-model="lqaChecked">Linguistic Quality Assurance</a-checkbox>
          <a-checkbox v-model="imageTranslationChecked">Image Text Translation</a-checkbox>
          <a-checkbox v-model="customChecked">Custom Requirements</a-checkbox>
          <a-textarea 
            v-model="form.customRequirements" 
            placeholder="Please specify your custom requirements here"
            :disabled="!customChecked"
            :auto-size="{ minRows: 2, maxRows: 4 }"
            style="margin-top: 8px;"
          />
        </a-space>
      </a-form-item>
      
      <a-form-item field="expectedDeliveryDate" label="Expected Delivery Date" required>
        <a-date-picker v-model="form.expectedDeliveryDate" style="width: 100%;" placeholder="Please select date" />
      </a-form-item>
      
      <a-form-item field="files" label="Upload Files">
        <a-upload
          action="http://localhost:5000/api/upload"
          :file-list="fileList"
          @change="handleFileChange"
          :headers="uploadHeaders"
          multiple
        >
          <template #upload-button>
            <a-button type="primary">
              Upload Files
            </a-button>
          </template>
          <template #description>
            <div>Click to upload</div>
          </template>
        </a-upload>
      </a-form-item>
      
      <a-form-item>
        <a-space>
          <a-button type="primary" html-type="submit" :loading="submitting">Submit Request</a-button>
          <a-button style="margin-left: 16px" @click="resetForm">Reset</a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { Message } from '@arco-design/web-vue';
import { languages } from '../utils/languages';
import axios from 'axios';

// 设置targetLanguageOptions为导入的languages数组
const targetLanguageOptions = languages;

// 附加需求勾选框状态
const lqaChecked = ref(false);
const imageTranslationChecked = ref(false);
const customChecked = ref(false);

// 表单响应式状态 - 使用reactive而不是ref，确保字段名一致
const form = reactive({
  requestName: '',
  requestBackground: '',
  sourceLanguage: '',
  targetLanguages: [],
  wordCount: 0,
  additionalRequirements: [],
  expectedDeliveryDate: null,
  customRequirements: '',
});

// 文件上传相关状态
const fileList = ref([]);  // 上传文件列表UI状态
const uploadedFiles = ref([]); // 成功上传的文件
const uploading = ref(false); // 上传状态

// 提交状态
const submitting = ref(false);

// 获取上传请求的headers
const uploadHeaders = computed(() => {
  // 从localStorage获取token
  const token = localStorage.getItem('token');
  return {
    Authorization: token ? `Bearer ${token}` : ''
  };
});

// 禁用今天之前的日期
const disabledDate = (date) => {
  return date.getTime() < Date.now() - 86400000; // 86400000 = 24 * 60 * 60 * 1000
};

const handleFileChange = async (file, fileList) => {
  console.log('File changed:', file, fileList);
  
  if (!file.raw) {
    console.error('Invalid file object');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', file.raw);
  
  // 获取token
  const token = localStorage.getItem('token');
  if (!token) {
    Message.error('Please login first');
    return;
  }
  
  uploading.value = true;
  
  try {
    const response = await axios.post('http://localhost:5000/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('Upload response:', response);
    
    if (response.data && response.data.file_id) {
      // 确保文件ID是数字类型
      const fileId = parseInt(response.data.file_id, 10);
      const fileName = response.data.originalName || file.name;
      
      if (isNaN(fileId)) {
        console.error('服务器返回了无效的文件ID:', response.data.file_id);
        Message.error('Server returned invalid file ID');
        return;
      }
      
      console.log('解析的文件ID:', fileId, '类型:', typeof fileId);
      
      // 保存到上传文件列表
      uploadedFiles.value.push({
        id: fileId,  // 使用解析后的数字ID
        name: fileName,
        url: response.data.url || null
      });
      
      console.log('文件ID:', fileId, '文件名:', fileName);
      console.log('当前上传文件列表:', uploadedFiles.value);
      
      Message.success('File uploaded successfully');
    } else {
      console.error('Upload failed:', response.data);
      Message.error(response.data.error || 'Upload failed');
      
      // 移除失败的文件
      fileList.splice(fileList.indexOf(file), 1);
    }
  } catch (error) {
    console.error('Upload error:', error);
    
    // 检查是否有详细的错误信息
    let errorMessage = 'Upload failed';
    
    if (error.response) {
      console.error('Error response:', error.response.data);
      
      // 处理401未授权错误
      if (error.response.status === 401) {
        errorMessage = 'Unauthorized, please login again';
      } else if (error.response.data && error.response.data.error) {
        errorMessage = error.response.data.error;
      }
    }
    
    Message.error(errorMessage);
    
    // 移除失败的文件
    fileList.splice(fileList.indexOf(file), 1);
  } finally {
    uploading.value = false;
  }
};

// 添加修复文件映射的函数
const fixFileMappings = async () => {
  try {
    console.log('自动修复文件映射关系...');
    // 删除加载消息
    // Message.loading({
    //   content: 'Fixing file mappings, please wait...',
    //   duration: 0
    // });
    
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('未找到认证令牌，无法修复文件映射');
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
      
      // 删除成功消息，只保留控制台日志
      if (newMappings > 0) {
        // Message.success({
        //   content: `File mappings fixed! Added ${newMappings} mappings`,
        //   duration: 5000
        // });
        console.log(`文件映射已自动修复! 新增 ${newMappings} 个映射`);
      } else {
        console.log('没有需要修复的文件映射');
      }
    } else {
      console.warn('修复结果未成功:', response.data);
    }
  } catch (error) {
    console.error('修复文件映射失败:', error);
  } finally {
    // 删除消息清理
    // Message.destroy();
  }
};

const handleSubmit = async () => {
  if (uploading.value) {
    Message.warning('Files are still uploading, please wait');
    return;
  }
  
  // 验证表单 - 现在直接访问form对象的字段，不再需要 .value
  if (!form.requestName.trim()) {
    Message.error('Please enter request name');
    return;
  }
  if (!form.sourceLanguage) {
    Message.error('Please select source language');
    return;
  }
  if (!form.targetLanguages || form.targetLanguages.length === 0) {
    Message.error('Please select at least one target language');
    return;
  }
  if (!form.wordCount || form.wordCount <= 0) {
    Message.error('Please enter a valid word count');
    return;
  }
  if (!form.expectedDeliveryDate) {
    Message.error('Please select expected delivery date');
    return;
  }
  
  // 收集附加需求
  form.additionalRequirements = [];
  if (lqaChecked.value) form.additionalRequirements.push('lqa');
  if (imageTranslationChecked.value) form.additionalRequirements.push('imageTranslation');
  if (customChecked.value) form.additionalRequirements.push('custom');
  
  submitting.value = true;
  console.log('Submitting form with data:', form);
  
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('Please login first');
      submitting.value = false;
      return;
    }
    
    // 详细记录上传的文件信息
    console.log('上传文件列表详情 (uploadedFiles):', JSON.stringify(uploadedFiles.value, null, 2));
    
    // 遍历并处理每个文件对象，确保ID为数字类型
    const processedFiles = uploadedFiles.value.map((file, index) => {
      // 如果ID不是数字类型，尝试转换
      if (file.id !== undefined && file.id !== null) {
        const numId = parseInt(file.id, 10);
        if (!isNaN(numId)) {
          console.log(`文件[${index}] ID转换: ${file.id} (${typeof file.id}) -> ${numId} (number)`);
          return { ...file, id: numId };
        } else {
          console.error(`文件[${index}] ID无效无法转换为数字: ${file.id}`);
          return file;
        }
      } else {
        console.error(`文件[${index}] 缺少ID`);
        return file;
      }
    });
    
    // 提取所有有效的文件ID (必须是数字类型)
    const validFileIds = processedFiles
      .filter(file => file.id !== undefined && file.id !== null && !isNaN(file.id))
      .map(file => file.id);
    
    console.log('有效的文件ID列表:', validFileIds, '数量:', validFileIds.length);
    
    if (uploadedFiles.value.length > 0 && validFileIds.length === 0) {
      console.error('存在上传文件但没有有效的文件ID，检查文件上传状态');
      Message.warning('File upload is incomplete or has issues, please check');
    }
    
    // 准备提交数据
    const requestData = {
      requestName: form.requestName,
      requestBackground: form.requestBackground,
      sourceLanguage: form.sourceLanguage,
      targetLanguages: form.targetLanguages,
      wordCount: form.wordCount,
      additionalRequirements: form.additionalRequirements,
      customRequirements: form.customRequirements,
      expectedDeliveryDate: formatDate(form.expectedDeliveryDate),
      fileIds: validFileIds // 使用处理后的有效文件ID列表
    };
    
    console.log('提交请求数据:', JSON.stringify(requestData, null, 2));
    
    // 发送请求
    const response = await axios.post('http://localhost:5000/api/requests', requestData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('请求提交响应:', response.data);
    
    if (response.data && response.data.id) {
      Message.success(`Request submitted successfully`);
      
      // 检查是否有上传文件，如果有则自动修复文件映射
      if (validFileIds.length > 0) {
        console.log(`检测到 ${validFileIds.length} 个文件，执行自动文件映射修复...`);
        // 等待服务器处理完请求后再运行修复
        setTimeout(async () => {
          await fixFileMappings();
        }, 1000);
      }
      
      // 重置表单
      resetForm();
      
      // 如果需要，可以跳转到需求列表页面
      // router.push('/requests');
    } else {
      console.error('Request submission failed:', response.data);
      Message.error(response.data.error || 'Submission failed');
    }
  } catch (error) {
    console.error('Request submission error:', error);
    
    let errorMessage = 'Submission failed';
    
    if (error.response) {
      console.error('Error response:', error.response.data);
      
      if (error.response.status === 401) {
        errorMessage = 'Unauthorized, please login again';
      } else if (error.response.data && error.response.data.error) {
        errorMessage = error.response.data.error;
      }
    }
    
    Message.error(errorMessage);
  } finally {
    submitting.value = false;
  }
};

// 格式化日期为 YYYY-MM-DD 字符串
const formatDate = (date) => {
  if (!date) return '';
  
  // 处理 Date 对象
  if (date instanceof Date) {
    return date.toISOString().split('T')[0];
  }
  
  // 处理字符串日期
  if (typeof date === 'string') {
    // 如果已经是 YYYY-MM-DD 格式，直接返回
    if (/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      return date;
    }
    // 尝试转换为日期对象
    const dateObj = new Date(date);
    if (!isNaN(dateObj.getTime())) {
      return dateObj.toISOString().split('T')[0];
    }
  }
  
  // 处理 Arco Design 日期对象
  if (date && typeof date === 'object' && date.toString) {
    return date.toString();
  }
  
  // 如果无法处理，返回当前日期
  console.warn('Unable to format date, using current date instead:', date);
  return new Date().toISOString().split('T')[0];
};

// 重置表单
const resetForm = () => {
  // 重置所有表单字段
  form.requestName = '';
  form.requestBackground = '';
  form.sourceLanguage = '';
  form.targetLanguages = [];
  form.wordCount = 0;
  form.additionalRequirements = [];
  form.expectedDeliveryDate = null;
  form.customRequirements = '';
  
  // 重置勾选框状态
  lqaChecked.value = false;
  imageTranslationChecked.value = false;
  customChecked.value = false;
  
  // 清空文件列表
  fileList.value = [];
  uploadedFiles.value = [];
};
</script>

<style scoped>
.request-form-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  margin-bottom: 24px;
  color: var(--color-text-1);
}
</style> 