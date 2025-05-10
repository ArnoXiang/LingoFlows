// 支持的语言列表
export const languages = [
  { code: 'en', name: 'English' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'es', name: 'Spanish' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'ru', name: 'Russian' },
  { code: 'ar', name: 'Arabic' },
  { code: 'hi', name: 'Hindi' },
  { code: 'bn', name: 'Bengali' },
  { code: 'th', name: 'Thai' },
  { code: 'vi', name: 'Vietnamese' },
  { code: 'id', name: 'Indonesian' },
  { code: 'ms', name: 'Malay' },
  { code: 'nl', name: 'Dutch' },
  { code: 'sv', name: 'Swedish' },
  { code: 'no', name: 'Norwegian' },
  { code: 'da', name: 'Danish' },
  { code: 'fi', name: 'Finnish' },
  { code: 'pl', name: 'Polish' },
  { code: 'tr', name: 'Turkish' },
  { code: 'cs', name: 'Czech' },
  { code: 'hu', name: 'Hungarian' },
  { code: 'ro', name: 'Romanian' },
  { code: 'el', name: 'Greek' },
  { code: 'he', name: 'Hebrew' },
  { code: 'uk', name: 'Ukrainian' },
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