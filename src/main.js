import { createApp } from 'vue';
import ArcoVue from '@arco-design/web-vue';
import App from './App.vue';
import '@arco-design/web-vue/dist/arco.css';
import './style.css';
// 导入英文语言包
import enUS from '@arco-design/web-vue/es/locale/lang/en-us';

const app = createApp(App);
// 使用英文作为默认语言
app.use(ArcoVue, {
  locale: enUS
});
app.mount('#app');