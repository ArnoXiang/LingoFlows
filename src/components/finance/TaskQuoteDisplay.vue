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
        <div><strong>语言 / Language:</strong> {{ getLanguageName(currentQuote.language) }}</div>
        <div><strong>负责人 / Vendor:</strong> {{ currentQuote.assignee }}</div>
        <div><strong>金额 / Amount:</strong> {{ currentQuote.quoteAmount }} {{ currentQuote.currency }}</div>
        <div><strong>字数 / Word Count:</strong> {{ currentQuote.wordCount }}</div>
        <div><strong>单价 / Unit Price:</strong> {{ currentQuote.unitPrice }}</div>
        <div><strong>截止日期 / Deadline:</strong> {{ formatDate(currentQuote.deadline) }}</div>
        <div><strong>备注 / Notes:</strong> {{ currentQuote.notes || '无 / None' }}</div>
      </div>
    </div>
    <div v-else class="no-quotes">
      <span>暂无报价信息 / No quote information available</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, watch } from 'vue';
import { getLanguageName, formatDate } from '../project/utils/projectUtils';

const props = defineProps({
  quotes: {
    type: Array,
    default: () => []
  }
});

// 活跃选中的语言
const activeLanguage = ref('');

// 当前显示的报价详情
const currentQuote = computed(() => {
  if (!activeLanguage.value || !props.quotes || props.quotes.length === 0) {
    return null;
  }
  
  return props.quotes.find(quote => quote.language === activeLanguage.value) || null;
});

// 当报价数据变化时，自动选择第一个语言
watch(() => props.quotes, (newQuotes) => {
  if (newQuotes && newQuotes.length > 0) {
    activeLanguage.value = newQuotes[0].language;
  } else {
    activeLanguage.value = '';
  }
}, { immediate: true });
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

.no-quotes {
  color: var(--color-text-3);
  padding: 12px;
  text-align: center;
  font-style: italic;
}
</style> 