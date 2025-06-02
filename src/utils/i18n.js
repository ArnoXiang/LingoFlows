import enUS from '@arco-design/web-vue/es/locale/lang/en-us';

// 抓bug时添加的额外的翻译
const extraTranslations = {
  pagination: {
    goto: 'Go to',
    page: 'Page',
    itemsPerPage: 'Items per page',
    total: 'Total {} items',
    prev: 'Previous',
    next: 'Next',
    countPerPage: 'rows/page'
  },
  table: {
    filterConfirm: 'Confirm',
    filterReset: 'Reset',
    sortAscend: 'Ascending order',
    sortDescend: 'Descending order'
  }
};

function deepMerge(target, source) {
  for (const key in source) {
    if (source.hasOwnProperty(key)) {
      if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
        target[key] = target[key] || {};
        deepMerge(target[key], source[key]);
      } else {
        target[key] = source[key];
      }
    }
  }
  return target;
}

const mergedLocale = deepMerge(JSON.parse(JSON.stringify(enUS)), extraTranslations);

export default mergedLocale; 