<template>
  <div class="request-form-container">
    <h2>提交本地化请求 / Submit Localization Request</h2>
    <a-form :model="form" :style="{ width: '600px' }" @submit="handleSubmit">
      <a-form-item field="requestName" label="请求名称 / Request Name" required>
        <a-input v-model="form.requestName" placeholder="请提供一个清晰且可区分的标题 / Provide a clear and distinguishable title" />
      </a-form-item>
      
      <a-form-item field="requestBackground" label="请求背景 / Request Background" required>
        <a-textarea 
          v-model="form.requestBackground" 
          placeholder="简要概述项目范围和目标 / Briefly outline the project scope and objectives"
          :auto-size="{ minRows: 3, maxRows: 5 }"
        />
      </a-form-item>
      
      <a-form-item field="sourceLanguage" label="源语言 / Source Language" required>
        <a-select v-model="form.sourceLanguage" placeholder="选择源语言 / Select source language">
          <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">
            {{ lang.name }}
          </a-option>
        </a-select>
      </a-form-item>
      
      <a-form-item field="targetLanguages" label="目标语言 / Target Languages" required>
        <a-select
          v-model="form.targetLanguages"
          placeholder="选择目标语言 / Select target languages"
          multiple
        >
          <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">
            {{ lang.name }}
          </a-option>
        </a-select>
      </a-form-item>
      
      <a-form-item field="wordCount" label="估计字数 / Estimated Word Count" required>
        <a-input-number v-model="form.wordCount" placeholder="估计字数 / Estimated word count" :min="1" />
      </a-form-item>
      
      <a-form-item field="additionalRequirements" label="附加要求 / Additional Requirements">
        <a-checkbox-group v-model="form.additionalRequirements">
          <a-checkbox value="lqa">语言质量保证 (LQA) / Linguistic Quality Assurance</a-checkbox>
          <a-checkbox value="imageTranslation">图像文本翻译 / Image Text Translation</a-checkbox>
        </a-checkbox-group>
      </a-form-item>
      
      <a-form-item field="expectedDeliveryDate" label="预期交付日期 / Expected Delivery Date" required>
        <a-date-picker v-model="form.expectedDeliveryDate" :disabled-date="disabledDate" />
      </a-form-item>
      
      <a-form-item field="files" label="上传文件 / Upload Files">
        <a-upload
          action="http://localhost:5000/api/upload"
          :file-list="fileList"
          @change="handleFileChange"
          multiple
        >
          <a-button>上传文件 / Upload Files</a-button>
        </a-upload>
      </a-form-item>
      
      <a-form-item>
        <a-button type="primary" html-type="submit" :loading="submitting">
          提交请求 / Submit Request
        </a-button>
        <a-button style="margin-left: 16px" @click="resetForm">
          重置 / Reset
        </a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { Message } from '@arco-design/web-vue';
import { languages } from '../utils/languages';
import axios from 'axios';

const form = reactive({
  requestName: '',
  requestBackground: '',
  sourceLanguage: '',
  targetLanguages: [],
  wordCount: 0,
  additionalRequirements: [],
  expectedDeliveryDate: null,
});

const fileList = ref([]);
const submitting = ref(false);

// 禁用今天之前的日期
const disabledDate = (date) => {
  return date.getTime() < Date.now() - 86400000; // 86400000 = 24 * 60 * 60 * 1000
};

const handleFileChange = (fileList) => {
  console.log('File list changed:', fileList);
};

const handleSubmit = async () => {
  // 表单验证
  if (!form.requestName || !form.requestBackground || !form.sourceLanguage || 
      form.targetLanguages.length === 0 || !form.wordCount || !form.expectedDeliveryDate) {
    Message.error('请填写所有必填字段 / Please fill in all required fields');
    return;
  }

  try {
    submitting.value = true;
    
    // 准备请求数据
    const requestData = {
      ...form,
      // 处理日期格式，确保兼容不同类型的日期对象
      expectedDeliveryDate: formatDate(form.expectedDeliveryDate),
      files: fileList.value.map(file => file.name),
    };
    
    // 发送请求到后端
    const response = await axios.post('http://localhost:5000/api/requests', requestData);
    
    if (response.status === 200 || response.status === 201) {
      Message.success('请求提交成功 / Request submitted successfully');
      resetForm();
    } else {
      throw new Error('提交失败 / Submission failed');
    }
  } catch (error) {
    console.error('Error submitting request:', error);
    Message.error(`提交失败: ${error.message} / Submission failed: ${error.message}`);
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

const resetForm = () => {
  // 重置表单
  Object.keys(form).forEach(key => {
    if (Array.isArray(form[key])) {
      form[key] = [];
    } else if (typeof form[key] === 'number') {
      form[key] = 0;
    } else {
      form[key] = '';
    }
  });
  form.expectedDeliveryDate = null;
  fileList.value = [];
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