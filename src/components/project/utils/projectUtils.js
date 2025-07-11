/**
 * 项目管理通用工具函数
 */
import { languages } from '../../../utils/languages';

/**
 * 获取项目状态对应的颜色
 * @param {string} status 项目状态
 * @returns {string} 颜色代码
 */
export const getStatusColor = (status) => {
  const statusMap = {
    pending: 'orange',
    in_progress: 'blue',
    completed: 'green',
    cancelled: 'red',
  };
  return statusMap[status] || 'gray';
};

/**
 * 获取项目状态文本表示
 * @param {string} status 项目状态
 * @returns {string} 状态文本
 */
export const getStatusText = (status) => {
  const statusMap = {
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed',
    cancelled: 'Cancelled',
  };
  return statusMap[status] || 'Unknown';
};

/**
 * 获取任务进度百分比
 * @param {string} taskStatus 任务状态
 * @returns {number} 进度百分比
 */
export const getTaskProgress = (taskStatus) => {
  const progressMap = {
    not_started: 0,
    in_progress: 50,
    completed: 100,
  };
  return progressMap[taskStatus] || 0;
};

/**
 * 获取任务状态对应的UI状态
 * @param {string} taskStatus 任务状态
 * @returns {string} UI状态
 */
export const getTaskStatus = (taskStatus) => {
  const statusMap = {
    not_started: 'normal',
    in_progress: 'warning',
    completed: 'success',
  };
  return statusMap[taskStatus] || 'normal';
};

/**
 * 获取任务状态文本表示
 * @param {string} taskStatus 任务状态
 * @returns {string} 状态文本
 */
export const getTaskText = (taskStatus) => {
  const textMap = {
    not_started: 'Not Started',
    in_progress: 'In Progress',
    completed: 'Completed',
  };
  return textMap[taskStatus] || 'Unknown';
};

/**
 * 获取需求文本描述
 * @param {string} requirement 需求代码
 * @returns {string} 需求文本
 */
export const getRequirementText = (requirement) => {
  const requirementMap = {
    lqa: 'Linguistic Quality Assurance',
    imageTranslation: 'Image Text Translation',
  };
  return requirementMap[requirement] || requirement;
};

/**
 * 根据语言代码获取语言名称
 * @param {string} code 语言代码
 * @returns {string} 语言名称
 */
export const getLanguageName = (code) => {
  if (!code) return 'Not specified';
  const language = languages.find(lang => lang.code === code);
  return language ? language.name.replace(/^.*? \/ /, '') : code;
};

/**
 * 格式化日期显示，使用北京时间（东八区，UTC+8）
 * @param {string|Date} dateString 日期字符串或日期对象
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'Not set';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString; // 如果无法解析，则返回原始字符串
    
    // 格式化为北京时间（东八区，UTC+8）
    const options = { 
      timeZone: 'Asia/Shanghai',
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit' 
    };
    
    return date.toLocaleDateString('zh-CN', options);
  } catch (error) {
    console.error('日期格式化错误:', error);
    return dateString;
  }
};

/**
 * 处理项目数据，确保所有字段格式正确
 * @param {Object} project 原始项目数据
 * @returns {Object} 处理后的项目数据
 */
export const processProject = (project) => {
  // 确保id字段存在且为数字类型
  const id = project.id ? Number(project.id) : null;
  
  // 确保created_by字段存在且为数字类型
  const created_by = project.created_by ? Number(project.created_by) : null;
  
  // 处理requesterName字段，如果不存在则设置默认值
  const requesterName = project.requesterName || 'Unknown';
  
  // 处理targetLanguages字段，如果是字符串则转换为数组
  let targetLanguages = project.targetLanguages;
  if (typeof targetLanguages === 'string' && targetLanguages) {
    targetLanguages = targetLanguages.split(',');
  } else if (!targetLanguages) {
    targetLanguages = [];
  }
  
  // 处理additionalRequirements字段，如果是字符串则转换为数组
  let additionalRequirements = project.additionalRequirements;
  if (typeof additionalRequirements === 'string' && additionalRequirements) {
    additionalRequirements = additionalRequirements.split(',');
  } else if (!additionalRequirements) {
    additionalRequirements = [];
  }
  
  // 处理预期交付日期，确保格式一致，使用北京时间
  let expectedDeliveryDate = project.expectedDeliveryDate;
  if (expectedDeliveryDate) {
    try {
      // 转换日期为北京时间（东八区，UTC+8）
      const date = new Date(expectedDeliveryDate);
      if (!isNaN(date.getTime())) {
        const options = { 
          timeZone: 'Asia/Shanghai',
          year: 'numeric', 
          month: '2-digit', 
          day: '2-digit' 
        };
        expectedDeliveryDate = date.toLocaleDateString('zh-CN', options);
      }
    } catch (error) {
      console.error('处理预期交付日期时出错:', error);
    }
  } else {
    expectedDeliveryDate = '未设置 / Not set';
  }
  
  // 处理创建时间，确保使用北京时间
  let createTime = project.createTime;
  if (createTime) {
    try {
      const date = new Date(createTime);
      if (!isNaN(date.getTime())) {
        const options = { 
          timeZone: 'Asia/Shanghai',
          year: 'numeric', 
          month: '2-digit', 
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        };
        createTime = date.toLocaleString('zh-CN', options);
      }
    } catch (error) {
      console.error('处理创建时间时出错:', error);
    }
  }
  
  // 确保status和projectStatus同步
  const projectStatus = project.projectStatus || project.status || 'pending';
  const status = project.status || project.projectStatus || 'pending';
  
  // 返回处理后的项目对象
  return {
    ...project,
    id,
    created_by,
    requesterName,
    targetLanguages,
    additionalRequirements,
    expectedDeliveryDate,
    createTime,
    // 同时提供status和projectStatus
    status,
    projectStatus,
    // 确保任务状态字段存在
    taskTranslation: project.taskTranslation || 'not_started',
    taskLQA: project.taskLQA || 'not_started',
    taskTranslationUpdate: project.taskTranslationUpdate || 'not_started',
    taskLQAReportFinalization: project.taskLQAReportFinalization || 'not_started',
    // 确保任务详细信息字段存在
    translationAssignee: project.translationAssignee || '',
    translationDeadline: project.translationDeadline || null,
    translationNotes: project.translationNotes || '',
    lqaAssignee: project.lqaAssignee || '',
    lqaDeadline: project.lqaDeadline || null,
    lqaNotes: project.lqaNotes || '',
  };
};

/**
 * 检查用户是否有权限查看项目
 * @param {Object} project 项目数据 
 * @param {number} userId 用户ID
 * @param {string} userRole 用户角色
 * @returns {boolean} 是否有权限
 */
export const canViewProject = (project, userId, userRole) => {
  if (!project) {
    console.log('canViewProject - 项目为空');
    return false;
  }
  
  // 如果用户ID为null，则无权限
  if (userId === null || userId === undefined) {
    console.log('canViewProject - 用户ID为null或undefined，无权限');
    return false;
  }
  
  if (userRole === 'LM') {
    console.log('canViewProject - 用户是LM，有权限');
    return true; // LM可以查看所有项目
  }
  
  // BO只能查看自己的项目
  // 确保类型匹配，将两者都转换为数字进行比较
  const projectCreatedBy = project.created_by !== null && project.created_by !== undefined ? Number(project.created_by) : null;
  const userIdNumber = Number(userId);
  
  // 如果项目的created_by为null，则无法确定所有者，BO无权限
  if (projectCreatedBy === null) {
    console.log('canViewProject - 项目created_by为null，BO无权限');
    return false;
  }
  
  const hasPermission = projectCreatedBy === userIdNumber;
  console.log('canViewProject - 权限检查结果:', hasPermission);
  return hasPermission;
};

/**
 * 检查用户是否有权限执行项目操作
 * @param {Object} project 项目数据
 * @param {number} userId 用户ID
 * @param {string} userRole 用户角色
 * @returns {boolean} 是否有权限
 */
export const canPerformAction = (project, userId, userRole) => {
  if (!project) {
    console.log('canPerformAction - 项目为空');
    return false;
  }
  
  // 如果用户ID为null，则无权限
  if (userId === null || userId === undefined) {
    console.log('canPerformAction - 用户ID为null或undefined，无权限');
    return false;
  }
  
  if (userRole === 'LM') {
    console.log('canPerformAction - 用户是LM，有权限');
    return true; // LM可以执行所有操作
  }
  
  // BO只能操作自己的项目
  // 确保类型匹配，将两者都转换为数字进行比较
  const projectCreatedBy = project.created_by !== null && project.created_by !== undefined ? Number(project.created_by) : null;
  const userIdNumber = Number(userId);
  
  // 如果项目的created_by为null，则无法确定所有者，BO无权限
  if (projectCreatedBy === null) {
    console.log('canPerformAction - 项目created_by为null，BO无权限');
    return false;
  }
  
  const hasPermission = projectCreatedBy === userIdNumber;
  console.log('canPerformAction - 权限检查结果:', hasPermission);
  return hasPermission;
};

/**
 * 获取文件类型文本
 * @param {string} fileType 文件类型代码
 * @returns {string} 文件类型文本
 */
export const getFileTypeText = (fileType) => {
  const typeMap = {
    source: 'Source Files',
    translation: 'Translation Files',
    lqa: 'LQA Reports',
    other: 'Other Files'
  };
  return typeMap[fileType] || 'Unknown Type';
};

/**
 * 获取Project Schedule表格数据
 * @param {Object} project 项目数据
 * @returns {Array} 表格数据
 */
export const getScheduleData = (project) => {
  if (!project) return [];
  
  // 安全地获取项目字段值
  const getProjectValue = (field, defaultValue = '') => {
    return project[field] !== undefined && project[field] !== null 
      ? project[field] 
      : defaultValue;
  };

  // 安全地格式化日期
  const safeDateFormat = (date) => {
    if (!date) return 'TBD';
    try {
      // 如果是日期对象，格式化它
      if (date instanceof Date) {
        // 使用北京时间格式化
        const options = { 
          timeZone: 'Asia/Shanghai',
          year: 'numeric', 
          month: '2-digit', 
          day: '2-digit' 
        };
        return new Date(date).toLocaleDateString('zh-CN', options);
      }
      // 如果是字符串，尝试解析
      const dateObj = new Date(date);
      // 使用北京时间格式化
      const options = { 
        timeZone: 'Asia/Shanghai',
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit' 
      };
      return dateObj.toLocaleDateString('zh-CN', options);
    } catch (e) {
      return 'TBD';
    }
  };

  // 检查项目是否需要LQA
  const additionalRequirements = getProjectValue('additionalRequirements', '');
  let hasLQA = false;
  
  // 处理additionalRequirements可能是字符串或数组的情况
  if (additionalRequirements) {
    if (Array.isArray(additionalRequirements)) {
      hasLQA = additionalRequirements.includes('lqa');
    } else if (typeof additionalRequirements === 'string') {
      hasLQA = additionalRequirements.split(',').map(req => req.trim()).includes('lqa');
    }
  }
  
  // 获取项目的交付日期（作为备用）
  const deliveryDate = safeDateFormat(getProjectValue('expectedDeliveryDate'));
  
  // 获取各任务的截止日期
  const translationDeadline = safeDateFormat(getProjectValue('translationDeadline')) || deliveryDate;
  const lqaDeadline = safeDateFormat(getProjectValue('lqaDeadline')) || deliveryDate;
  const translationUpdateDeadline = safeDateFormat(getProjectValue('translationUpdateDeadline')) || deliveryDate;
  const lqaReportFinalizationDeadline = safeDateFormat(getProjectValue('lqaReportFinalizationDeadline')) || deliveryDate;
  
  // 根据是否有LQA返回不同的数据结构
  if (hasLQA) {
    // 包含LQA的4行表格
    return [
      { task: 'Translation', deadline: translationDeadline, owner: getProjectValue('translationAssignee', 'Translation Vendor') },
      { task: 'LQA', deadline: lqaDeadline, owner: getProjectValue('lqaAssignee', 'LQA Vendor') },
      { task: 'Translation Update', deadline: translationUpdateDeadline, owner: getProjectValue('translationUpdateAssignee', 'Translation Vendor') },
      { task: 'LQA Report Finalization', deadline: lqaReportFinalizationDeadline, owner: getProjectValue('lqaReportFinalizationAssignee', 'LQA Vendor') }
    ];
  } else {
    // 不包含LQA的3行表格
    return [
      { task: 'Translation', deadline: translationDeadline, owner: getProjectValue('translationAssignee', 'Translation Vendor') },
      { task: 'Review', deadline: deliveryDate, owner: 'Internal Reviewer' },
      { task: 'Final Delivery', deadline: deliveryDate, owner: getProjectValue('translationAssignee', 'Translation Vendor') }
    ];
  }
}; 