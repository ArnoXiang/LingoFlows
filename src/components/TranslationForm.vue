<template>
  <div class="translation-container">
    <div class="language-selectors">
      <a-select 
        v-model="sourceLang"
        placeholder="Source Language"
        :style="{ width: '200px' }"
        allow-clear
      >
        <a-option value="auto">Auto Detect</a-option>
        <a-option 
          v-for="lang in languages"
          :key="lang.code"
          :value="lang.code"
        >
          {{ lang.name }}
        </a-option>
      </a-select>

      <a-button @click="swapLanguages" type="text" shape="circle">
        <icon-refresh />
      </a-button>

      <a-select
        v-model="targetLang"
        placeholder="Target Language"
        :style="{ width: '200px' }"
        allow-clear
      >
        <a-option 
          v-for="lang in languageOptions"
          :key="lang.code"
          :value="lang.code"
        >
          {{ lang.name }}
        </a-option>
      </a-select>
    </div>

    <div class="translation-area">
      <a-textarea
        v-model="sourceText"
        placeholder="Enter text to translate"
        :auto-size="{ minRows: 5, maxRows: 10 }"
      />
      <a-button 
        type="primary" 
        @click="handleTranslate"
        :loading="loading"
      >
        Translate
      </a-button>
      <a-textarea
        v-model="translatedText"
        placeholder="Translation result"
        :auto-size="{ minRows: 5, maxRows: 10 }"
        readonly
      />
    </div>

    <!-- 翻译历史 -->
    <div v-if="history.length" class="translation-history">
      <h3>Translation History</h3>
      <div 
        v-for="(item, index) in history"
        :key="index"
        class="history-item"
      >
        <p>{{ item.source }} → {{ item.target }}</p>
        <p class="text-sm">{{ item.original }} → {{ item.translated }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Message } from '@arco-design/web-vue';
import { languages } from '../utils/languages';
import { translateText } from '../api/translate';

const sourceLang = ref('auto');
const targetLang = ref('zh');
const sourceText = ref('');
const translatedText = ref('');
const loading = ref(false);
const history = ref([]); // 直接初始化为空数组，不再使用 localStorage

const languageOptions = computed(() => [
  { code: 'auto', name: 'Auto Detect' },
  ...languages
]);

const swapLanguages = () => {
  [sourceLang.value, targetLang.value] = [targetLang.value, sourceLang.value];
  if (sourceLang.value === 'auto') {
    sourceLang.value = 'zh';
  }
};

const handleTranslate = async () => {
  if (!sourceText.value.trim()) {
    Message.warning('Please enter text to translate');
    return;
  }

  try {
    loading.value = true;

    // 调用翻译函数
    const translatedTextResult = await translateText(
      sourceText.value, // 需要翻译的文本
      targetLang.value, // 目标语言
      sourceLang.value === 'auto' ? 'auto' : sourceLang.value // 源语言
    );

    // 更新翻译结果
    translatedText.value = translatedTextResult;

    // 保存历史记录
    const newHistory = {
      source: sourceLang.value === 'auto' 
        ? 'Auto Detect' 
        : languages.find(l => l.code === sourceLang.value)?.name,
      target: languages.find(l => l.code === targetLang.value).name,
      original: sourceText.value,
      translated: translatedText.value,
      timestamp: new Date().getTime()
    };
    
    history.value = [newHistory, ...history.value.slice(0, 9)]; // 保留最近 10 条记录
  } catch (error) {
    console.error('API Error Details:', error);

    // 改进错误信息显示
    let errorMessage = 'Translation failed';
    if (error.response) {
      // 如果 API 返回了错误响应
      errorMessage = error.response.data?.message || error.response.statusText;
    } else if (error.request) {
      // 如果请求已发送但没有收到响应
      errorMessage = 'Cannot connect to translation service, please check your network';
    } else {
      // 其他错误
      errorMessage = error.message || 'Unknown error';
    }

    Message.error(`Translation failed: ${errorMessage}`);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.translation-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.language-selectors {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
}

.translation-area {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.translation-history {
  border-top: 1px solid var(--color-border);
  padding-top: 16px;
}

.history-item {
  padding: 8px;
  margin: 8px 0;
  background: var(--color-fill-2);
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: var(--color-fill-3);
  }
}
</style>