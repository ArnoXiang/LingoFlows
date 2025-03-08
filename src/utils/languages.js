// 支持的语言列表
export const languages = [
  { code: 'en', name: '英语 / English' },
  { code: 'zh', name: '中文 / Chinese' },
  { code: 'ja', name: '日语 / Japanese' },
  { code: 'ko', name: '韩语 / Korean' },
  { code: 'fr', name: '法语 / French' },
  { code: 'de', name: '德语 / German' },
  { code: 'es', name: '西班牙语 / Spanish' },
  { code: 'it', name: '意大利语 / Italian' },
  { code: 'pt', name: '葡萄牙语 / Portuguese' },
  { code: 'ru', name: '俄语 / Russian' },
  { code: 'ar', name: '阿拉伯语 / Arabic' },
  { code: 'hi', name: '印地语 / Hindi' },
  { code: 'bn', name: '孟加拉语 / Bengali' },
  { code: 'th', name: '泰语 / Thai' },
  { code: 'vi', name: '越南语 / Vietnamese' },
  { code: 'id', name: '印尼语 / Indonesian' },
  { code: 'ms', name: '马来语 / Malay' },
  { code: 'nl', name: '荷兰语 / Dutch' },
  { code: 'sv', name: '瑞典语 / Swedish' },
  { code: 'no', name: '挪威语 / Norwegian' },
  { code: 'da', name: '丹麦语 / Danish' },
  { code: 'fi', name: '芬兰语 / Finnish' },
  { code: 'pl', name: '波兰语 / Polish' },
  { code: 'tr', name: '土耳其语 / Turkish' },
  { code: 'cs', name: '捷克语 / Czech' },
  { code: 'hu', name: '匈牙利语 / Hungarian' },
  { code: 'ro', name: '罗马尼亚语 / Romanian' },
  { code: 'el', name: '希腊语 / Greek' },
  { code: 'he', name: '希伯来语 / Hebrew' },
  { code: 'uk', name: '乌克兰语 / Ukrainian' },
];

// 获取语言名称
export const getLanguageName = (code) => {
  const language = languages.find(lang => lang.code === code);
  return language ? language.name : code;
};

// 获取语言代码
export const getLanguageCode = (name) => {
  const language = languages.find(lang => lang.name === name);
  return language ? language.code : null;
};

// 检查是否支持该语言
export const isLanguageSupported = (code) => {
  return languages.some(lang => lang.code === code);
};

// 获取常用语言
export const getCommonLanguages = () => {
  return languages.filter(lang => 
    ['en', 'zh', 'ja', 'ko', 'fr', 'de', 'es', 'ru'].includes(lang.code)
  );
};

// 将语言代码列表转换为语言名称列表
export const languageCodesToNames = (codes) => {
  if (!codes) return [];
  
  // 如果是逗号分隔的字符串，转换为数组
  const codeArray = typeof codes === 'string' ? codes.split(',') : codes;
  
  return codeArray.map(code => {
    const language = languages.find(lang => lang.code === code);
    return language ? language.name : code;
  });
};

// 将语言名称列表转换为语言代码列表
export const languageNamesToCodes = (names) => {
  if (!names) return [];
  
  // 如果是逗号分隔的字符串，转换为数组
  const nameArray = typeof names === 'string' ? names.split(',') : names;
  
  return nameArray.map(name => {
    const language = languages.find(lang => lang.name === name);
    return language ? language.code : name;
  });
};