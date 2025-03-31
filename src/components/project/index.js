import ProjectList from './ProjectList.vue';
import ProjectDetail from './ProjectDetail.vue';
import FileManager from './FileManager.vue';
import EmailSender from './EmailSender.vue';

// 导出工具函数
import * as utils from './utils/projectUtils';

export {
  ProjectList,
  ProjectDetail,
  FileManager,
  EmailSender,
  utils
};

// 默认导出所有组件对象
export default {
  ProjectList,
  ProjectDetail,
  FileManager,
  EmailSender
}; 