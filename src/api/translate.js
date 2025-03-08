import axios from 'axios';

const RAPIDAPI_KEY = '2818a09a0cmsh1273edb1e2a65efp120488jsnf5072d8d3962';
const API_URL = 'https://google-translate113.p.rapidapi.com/api/v1/translator/text';

export const translateText = async (text, targetLang = 'en', sourceLang = 'auto') => {
  const options = {
    method: 'POST',
    url: API_URL,
    headers: {
      'x-rapidapi-key': RAPIDAPI_KEY,
      'x-rapidapi-host': 'google-translate113.p.rapidapi.com',
      'Content-Type': 'application/json',
    },
    data: {
      from: sourceLang, // 源语言
      to: targetLang,   // 目标语言
      text: text,       // 需要翻译的文本
    },
  };

  try {
    const response = await axios.request(options);
    console.log('API 响应数据：', response.data); // 打印完整响应数据

    // 检查响应中是否包含翻译结果
    if (!response.data.trans) {
      throw new Error('翻译结果未返回');
    }

    return response.data.trans; // 返回翻译后的文本
  } catch (error) {
    console.error('翻译失败：', error);

    // 抛出更详细的错误信息
    if (error.response) {
      throw new Error(error.response.data?.message || error.response.statusText);
    } else if (error.request) {
      throw new Error('无法连接到翻译服务，请检查网络连接');
    } else {
      throw new Error(error.message || '未知错误');
    }
  }
};