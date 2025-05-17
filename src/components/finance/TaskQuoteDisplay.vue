<template>
  <div class="task-quote-display">
    <!-- 按语言显示报价信息 -->
    <div v-if="quotes && quotes.length > 0" class="quotes-by-language">
      <!-- 语言选择标签 -->
      <a-radio-group v-model="activeLanguage" type="button" size="small" style="margin-bottom: 12px;">
        <a-radio 
          v-for="quote in quotes" 
          :key="quote.language" 
          :value="quote.language"
        >
          {{ getLanguageName(quote.language) }}
        </a-radio>
      </a-radio-group>
      
      <!-- 当前选中语言的报价详情 -->
      <div v-if="currentQuote" class="quote-info">
        <div><strong>Language:</strong> {{ getLanguageName(currentQuote.language) }}</div>
        <div><strong>Vendor:</strong> {{ currentQuote.assignee }}</div>
        <div><strong>Amount:</strong> {{ currentQuote.quoteAmount }} {{ currentQuote.currency }}</div>
        <div><strong>Word Count:</strong> {{ currentQuote.wordCount }}</div>
        <div><strong>Unit Price:</strong> {{ currentQuote.unitPrice }}</div>
        <div><strong>Deadline:</strong> {{ formatDate(currentQuote.deadline) }}</div>
        <div><strong>Notes:</strong> {{ currentQuote.notes || 'None' }}</div>
        
        <!-- 查看提取的特定列数据的按钮 -->
        <div class="extracted-info-actions">
          <a-button 
            type="outline" 
            size="small"
            @click="showExtractedInfo" 
            :disabled="!hasExtractedInfo"
          >
            View Extracted Quote Info
          </a-button>
        </div>
        
        <!-- 提取的特定列数据弹窗 -->
        <a-modal
          v-model:visible="extractedInfoVisible"
          title="Extracted Quote Information"
          :footer="false"
          :mask-closable="true"
          width="700px"
        >
          <div v-if="extractedInfoData && extractedInfoData.length > 0" class="extracted-info-content">
            <a-table
              :columns="extractedInfoColumns"
              :data="extractedInfoData"
              :bordered="true"
              :pagination="false"
            ></a-table>
          </div>
          <div v-else class="no-data">
            No extracted information available
          </div>
        </a-modal>
      </div>
    </div>
    <div v-else class="no-quotes">
      <span>No quote information available</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, watch } from 'vue';
import { getLanguageName, formatDate } from '../project/utils/projectUtils';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';

const props = defineProps({
  quotes: {
    type: Array,
    default: () => []
  }
});

// 活跃选中的语言
const activeLanguage = ref('');

// 提取的特定列数据相关状态
const extractedInfoVisible = ref(false);
const extractedInfoData = ref([]);
const extractedInfoLoading = ref(false);

// 表格列定义
const extractedInfoColumns = [
  { title: 'Data Type', dataIndex: 'dataType' },
  { title: 'Values', dataIndex: 'values' }
];

// 当前显示的报价详情
const currentQuote = computed(() => {
  if (!activeLanguage.value || !props.quotes || props.quotes.length === 0) {
    return null;
  }
  
  return props.quotes.find(quote => quote.language === activeLanguage.value) || null;
});

// 判断当前报价是否有提取的特定列数据
const hasExtractedInfo = computed(() => {
  return currentQuote.value && currentQuote.value.id;
});

// 当报价数据变化时，自动选择第一个语言
watch(() => props.quotes, (newQuotes) => {
  if (newQuotes && newQuotes.length > 0) {
    activeLanguage.value = newQuotes[0].language;
  } else {
    activeLanguage.value = '';
  }
}, { immediate: true });

// 显示提取的特定列数据
const showExtractedInfo = async () => {
  if (!currentQuote.value || !currentQuote.value.id) {
    Message.error('No quote information available');
    return;
  }
  
  extractedInfoLoading.value = true;
  extractedInfoData.value = [];
  
  try {
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('Session expired, please login again');
      return;
    }
    
    // 调用API获取提取的特定列数据
    const response = await axios.get(
      `http://localhost:5000/api/quotes/${currentQuote.value.id}/extracted-info`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    if (response.data && response.data.extractedInfo) {
      extractedInfoData.value = response.data.extractedInfo;
      extractedInfoVisible.value = true;
    } else {
      Message.warning('No extracted information available for this quote');
    }
  } catch (error) {
    console.error('Error fetching extracted info:', error);
    Message.error('Failed to fetch extracted information');
  } finally {
    extractedInfoLoading.value = false;
  }
};
</script>

<style scoped>
.task-quote-display {
  width: 100%;
}

.quotes-by-language {
  background-color: rgba(255, 255, 255, 0.5);
  padding: 12px;
  border-radius: 4px;
}

.quote-info {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  border-left: 4px solid var(--color-primary-light-4);
}

.extracted-info-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-start;
}

.extracted-info-content {
  max-height: 400px;
  overflow-y: auto;
}

.no-quotes, .no-data {
  color: var(--color-text-3);
  padding: 12px;
  text-align: center;
  font-style: italic;
}
</style> 