import { createApp } from 'vue';
import ArcoVue from '@arco-design/web-vue';
import App from './App.vue';
import '@arco-design/web-vue/dist/arco.css';
import './style.css';

// 导入自定义的国际化配置
import i18n from './utils/i18n';

const app = createApp(App);

// 使用自定义的国际化配置
app.use(ArcoVue, {
  locale: i18n
});

app.mount('#app');