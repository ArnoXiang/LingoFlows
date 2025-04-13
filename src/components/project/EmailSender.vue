<template>
  <div class="email-sender-container">
    <a-modal
      v-model:visible="visible"
      title="发送项目邮件 / Send Project Email"
      @ok="sendProjectEmail"
      @cancel="closeModal"
      :ok-loading="sendingEmail"
    >
      <a-form :model="emailForm">
        <a-form-item field="to" label="收件人 / To" required>
          <a-input v-model="emailForm.to" placeholder="收件人邮箱 / Recipient email" />
        </a-form-item>
        <a-form-item field="cc" label="抄送 / CC">
          <a-input v-model="emailForm.cc" placeholder="抄送邮箱 / CC email" />
        </a-form-item>
        <a-form-item field="subject" label="主题 / Subject" required>
          <a-input v-model="emailForm.subject" placeholder="邮件主题 / Email subject" />
        </a-form-item>
        
        <!-- Project Schedule 表格 -->
        <a-form-item field="projectSchedule" label="项目计划 / Project Schedule">
          <div class="project-schedule-table">
            <a-table :columns="scheduleColumns" :data="detailedScheduleData" :bordered="true" :pagination="false" size="small">
              <template #empty>
                <div>项目数据不可用 / Project data unavailable</div>
              </template>
            </a-table>
          </div>
        </a-form-item>
        
        <a-form-item field="content" label="内容 / Content" required>
          <a-textarea
            v-model="emailForm.content"
            placeholder="邮件内容 / Email content"
            :auto-size="{ minRows: 5, maxRows: 10 }"
          />
        </a-form-item>
        <a-form-item field="attachments" label="附件 / Attachments">
          <a-upload
            action="http://localhost:5000/api/upload"
            :file-list="emailAttachments"
            @change="handleEmailAttachmentChange"
            :headers="uploadHeaders"
            multiple
          >
            <a-button>上传附件 / Upload Attachments</a-button>
          </a-upload>
        </a-form-item>
      </a-form>
      <template #footer>
        <a-space>
          <a-button @click="closeModal">取消 / Cancel</a-button>
          <a-button type="primary" @click="previewEmail">
            <template #icon><icon-eye /></template>
            预览邮件 / Preview Email
          </a-button>
          <a-button type="primary" @click="sendProjectEmail" :loading="sendingEmail">发送 / Send</a-button>
        </a-space>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits, onMounted } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';
import { IconEye } from '@arco-design/web-vue/es/icon';
import { getScheduleData } from './utils/projectUtils';

const props = defineProps({
  userRole: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['close', 'sent']);

// 状态
const visible = ref(false);
const sendingEmail = ref(false);
const emailAttachments = ref([]);
const currentProject = ref(null);
const taskAssignments = ref([]);

// 表单数据
const emailForm = ref({
  to: '',
  cc: '',
  subject: '',
  content: '',
  htmlContent: '', // 用于存储HTML格式内容
});

// Project Schedule 表格列定义
const scheduleColumns = [
  {
    title: '任务 / Task',
    dataIndex: 'task',
    key: 'task',
  },
  {
    title: '语言 / Language',
    dataIndex: 'language',
    key: 'language',
  },
  {
    title: '截止日期 / Deadline',
    dataIndex: 'deadline',
    key: 'deadline',
  },
  {
    title: '负责人 / Owner(s)',
    dataIndex: 'owner',
    key: 'owner',
  },
  {
    title: '备注 / Notes',
    dataIndex: 'notes',
    key: 'notes',
  }
];

// 基本表格数据
const scheduleData = computed(() => {
  if (!currentProject.value) return [];
  return getScheduleData(currentProject.value);
});

// 详细表格数据（包含每个任务的语言和负责人）
const detailedScheduleData = computed(() => {
  if (!currentProject.value || !taskAssignments.value.length) return scheduleData.value;
  
  // 按任务类型和语言组织任务分配数据
  const assignmentsByTaskType = {};
  taskAssignments.value.forEach(assignment => {
    if (!assignmentsByTaskType[assignment.task_type]) {
      assignmentsByTaskType[assignment.task_type] = {};
    }
    assignmentsByTaskType[assignment.task_type][assignment.language] = assignment;
  });
  
  // 基于任务分配数据生成详细表格数据
  const result = [];
  
  // 将任务类型映射到显示名称
  const taskTypeDisplayNames = {
    'translation': 'Translation',
    'lqa': 'LQA',
    'translationUpdate': 'Translation Update',
    'lqaReportFinalization': 'LQA Report Finalization'
  };
  
  // 获取项目的目标语言列表
  const targetLanguages = Array.isArray(currentProject.value.targetLanguages) 
    ? currentProject.value.targetLanguages 
    : (currentProject.value.targetLanguages || '').split(',').filter(lang => lang.trim());
  
  // 获取语言的本地化名称
  const getLanguageDisplayName = (code) => {
    try {
      return new Intl.DisplayNames(['en'], { type: 'language' }).of(code);
    } catch (e) {
      // fallback
      return code.toUpperCase();
    }
  };
  
  // 处理每个任务类型
  Object.keys(assignmentsByTaskType).forEach(taskType => {
    const taskDisplayName = taskTypeDisplayNames[taskType] || taskType;
    
    // 对于每种语言，添加一行数据
    targetLanguages.forEach(language => {
      const assignment = assignmentsByTaskType[taskType][language];
      
      if (assignment) {
        result.push({
          task: taskDisplayName,
          language: getLanguageDisplayName(language),
          deadline: assignment.deadline ? new Date(assignment.deadline).toLocaleDateString() : 'TBD',
          owner: assignment.assignee || 'Not Assigned',
          notes: assignment.notes || ''
        });
      }
    });
  });
  
  // 如果没有任务分配数据，则使用默认数据
  if (result.length === 0) {
    return scheduleData.value;
  }
  
  return result;
});

// 计算属性
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`
  };
});

// 加载项目任务分配数据
const loadProjectTaskAssignments = async (projectId) => {
  if (!projectId) return;
  
  try {
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('未找到认证令牌，无法获取任务分配数据');
      return;
    }
    
    // 发送请求获取任务分配数据
    const response = await axios.get(`http://localhost:5000/api/project-task-assignments/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.data && Array.isArray(response.data)) {
      taskAssignments.value = response.data;
      console.log('已加载项目任务分配数据:', response.data);
    }
  } catch (error) {
    console.error('获取项目任务分配数据失败:', error);
    taskAssignments.value = [];
  }
};

// 打开邮件发送对话框
const openEmailModal = async (project) => {
  if (props.userRole !== 'LM') {
    Message.error('只有本地化经理可以发送项目邮件 / Only Localization Managers can send project emails');
    return;
  }

  // 保存当前项目信息
  currentProject.value = project;

  // 加载项目任务分配数据
  await loadProjectTaskAssignments(project.id);

  // 设置邮件主题
  emailForm.value.subject = `项目更新: ${project.projectName} / Project Update: ${project.projectName}`;
  
  // 构建邮件正文
  generateEmailContent();
  
  // 清空其他字段
  emailForm.value.to = '';
  emailForm.value.cc = '';
  emailAttachments.value = [];
  
  // 显示对话框
  visible.value = true;
};

// 生成邮件内容
const generateEmailContent = () => {
  if (!currentProject.value) return;
  
  // 纯文本格式的项目进度表（用于实际发送）
  let textSchedule = 'Project Schedule:\n';
  textSchedule += '--------------------------------\n';
  
  // 添加表头
  textSchedule += 'Task             Language        Deadline        Owner(s)         Notes\n';
  textSchedule += '--------------------------------\n';
  
  // 添加任务行
  detailedScheduleData.value.forEach(item => {
    const task = (item.task || '').padEnd(16);
    const language = (item.language || '').padEnd(15);
    const deadline = (item.deadline || '').padEnd(15);
    const owner = (item.owner || '').padEnd(16);
    const notes = item.notes || '';
    
    textSchedule += `${task}${language}${deadline}${owner}${notes}\n`;
  });
  textSchedule += '--------------------------------\n\n';
  
  // HTML格式的项目进度表（用于预览）
  let htmlSchedule = `
    <div style="background-color:#f9f9f9;padding:10px;border-left:4px solid #4080ff;margin:15px 0;border-radius:4px;">
      <h3 style="margin-top:0;margin-bottom:10px;">Project Schedule</h3>
      <table style="border-collapse:collapse;width:100%;margin:10px 0;border:1px solid #ddd;">
        <thead>
          <tr>
            <th style="border:1px solid #ddd;padding:8px;text-align:left;background-color:#f2f3f5;font-weight:bold">Task</th>
            <th style="border:1px solid #ddd;padding:8px;text-align:left;background-color:#f2f3f5;font-weight:bold">Language</th>
            <th style="border:1px solid #ddd;padding:8px;text-align:left;background-color:#f2f3f5;font-weight:bold">Deadline</th>
            <th style="border:1px solid #ddd;padding:8px;text-align:left;background-color:#f2f3f5;font-weight:bold">Owner(s)</th>
            <th style="border:1px solid #ddd;padding:8px;text-align:left;background-color:#f2f3f5;font-weight:bold">Notes</th>
          </tr>
        </thead>
        <tbody>
  `;
  
  // 添加表格行
  detailedScheduleData.value.forEach(item => {
    htmlSchedule += `
      <tr>
        <td style="border:1px solid #ddd;padding:8px;text-align:left">${item.task || ''}</td>
        <td style="border:1px solid #ddd;padding:8px;text-align:left">${item.language || ''}</td>
        <td style="border:1px solid #ddd;padding:8px;text-align:left">${item.deadline || ''}</td>
        <td style="border:1px solid #ddd;padding:8px;text-align:left">${item.owner || ''}</td>
        <td style="border:1px solid #ddd;padding:8px;text-align:left">${item.notes || ''}</td>
      </tr>
    `;
  });
  
  htmlSchedule += `
        </tbody>
      </table>
    </div>
  `;
  
  // 设置邮件内容（纯文本）
  let plainTextContent = `亲爱的供应商，\n\n`;
  plainTextContent += `希望这封邮件能找到您一切安好。我在此向您提供${currentProject.value.projectName}项目的最新进度安排。\n\n`;
  plainTextContent += textSchedule;
  plainTextContent += `如有任何问题，请随时与我联系。\n\n`;
  plainTextContent += `此致，\n${currentProject.value.projectManager}\n`;
  
  // HTML格式的邮件内容
  let htmlContent = `
    <p>亲爱的供应商，</p>
    <p>希望这封邮件能找到您一切安好。我在此向您提供${currentProject.value.projectName}项目的最新进度安排。</p>
    ${htmlSchedule}
    <p>如有任何问题，请随时与我联系。</p>
    <p>此致，<br>${currentProject.value.projectManager}</p>
  `;
  
  // 保存两种格式
  emailForm.value.content = plainTextContent;
  emailForm.value.htmlContent = htmlContent;
};

// 关闭邮件发送对话框
const closeModal = () => {
  visible.value = false;
  emit('close');
};

// 预览邮件
const previewEmail = () => {
  if (!emailForm.value.content) {
    Message.error('邮件内容不能为空 / Email content cannot be empty');
    return;
  }
  
  // 使用htmlContent字段（如果可用），否则尝试将纯文本转换为HTML
  let emailContent = emailForm.value.htmlContent || '';
  
  // 如果没有HTML内容，将纯文本转换为HTML
  if (!emailContent) {
    emailContent = emailForm.value.content
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');
    emailContent = '<p>' + emailContent + '</p>';
  }
  
  // 创建完整的HTML邮件预览页面
  const html = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${emailForm.value.subject}</title>
      <style>
        body { 
          font-family: Arial, sans-serif; 
          margin: 0; 
          padding: 0; 
          line-height: 1.6; 
          color: #333; 
          background-color: #f5f5f5; 
        }
        .email-container { 
          max-width: 800px; 
          margin: 20px auto; 
          background: white; 
          padding: 20px; 
          border-radius: 5px; 
          box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        }
        .email-header { 
          margin-bottom: 20px; 
          padding-bottom: 10px; 
          border-bottom: 1px solid #eee; 
        }
        .email-header-item { 
          margin: 5px 0; 
        }
        .email-subject { 
          font-size: 20px; 
          font-weight: bold; 
          margin: 0 0 15px; 
        }
        .email-content { 
          margin-bottom: 20px; 
        }
        table { 
          border-collapse: collapse; 
          width: 100%; 
          margin: 15px 0; 
        }
        th, td { 
          border: 1px solid #ddd; 
          padding: 8px; 
          text-align: left; 
        }
        th { 
          background-color: #f2f3f5; 
          font-weight: bold; 
        }
      </style>
    </head>
    <body>
      <div class="email-container">
        <div class="email-header">
          <h1 class="email-subject">${emailForm.value.subject}</h1>
          <div class="email-header-item"><strong>From:</strong> ${currentProject.value ? currentProject.value.projectManager : 'Project Manager'}</div>
          <div class="email-header-item"><strong>To:</strong> ${emailForm.value.to || 'recipient@example.com'}</div>
          ${emailForm.value.cc ? `<div class="email-header-item"><strong>CC:</strong> ${emailForm.value.cc}</div>` : ''}
          <div class="email-header-item"><strong>Date:</strong> ${new Date().toLocaleString()}</div>
        </div>
        <div class="email-content">${emailContent}</div>
      </div>
    </body>
    </html>
  `;
  
  // 创建Blob对象
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  
  // 在新标签中打开预览
  const previewWindow = window.open(url, '_blank');
  
  // 当预览窗口关闭时释放URL对象
  if (previewWindow) {
    previewWindow.addEventListener('beforeunload', () => {
      URL.revokeObjectURL(url);
    });
  } else {
    // 浏览器可能阻止了窗口打开
    Message.error('浏览器阻止了窗口打开，请允许弹出窗口 / Browser blocked opening the window, please allow popups');
    // 释放URL对象
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
};

// 发送项目邮件
const sendProjectEmail = async () => {
  if (!currentProject.value) return;
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('只有本地化经理可以发送项目邮件 / Only Localization Managers can send project emails');
    return;
  }
  
  // 表单验证
  if (!emailForm.value.to || !emailForm.value.subject || !emailForm.value.content) {
    Message.error('请填写所有必填字段 / Please fill in all required fields');
    return;
  }
  
  try {
    sendingEmail.value = true;
    
    // 获取已上传附件的文件ID
    const attachmentIds = emailAttachments.value
      .filter(file => file.status === 'done' && file.response)
      .map(file => file.response.file_id);
    
    // 准备邮件数据
    const emailData = {
      projectId: currentProject.value.id,
      to: emailForm.value.to,
      cc: emailForm.value.cc,
      subject: emailForm.value.subject,
      content: emailForm.value.content,
      attachmentIds: attachmentIds // 使用文件ID数组
    };
    
    // 发送邮件请求
    const response = await axios.post('http://localhost:5000/api/emails', emailData);
    
    if (response.status === 200) {
      Message.success('邮件发送成功 / Email sent successfully');
      visible.value = false;
      emit('sent', response.data); // 通知父组件邮件已发送
    } else {
      throw new Error('发送失败 / Sending failed');
    }
  } catch (error) {
    console.error('Error sending email:', error);
    Message.error(`发送失败: ${error.message} / Sending failed: ${error.message}`);
  } finally {
    sendingEmail.value = false;
  }
};

// 处理附件变化
const handleEmailAttachmentChange = (options) => {
  console.log('Email attachment change event:', options);
  
  // 处理上传成功的情况
  if (options.file.status === 'done') {
    const response = options.file.response;
    if (response && response.filename) {
      Message.success(`附件 ${options.file.name} 上传成功 / Attachment ${options.file.name} uploaded successfully`);
    }
  }
  
  // 处理上传失败的情况
  if (options.file.status === 'error') {
    console.error('Attachment upload error:', options.file.response);
    Message.error(`附件 ${options.file.name} 上传失败 / Attachment ${options.file.name} upload failed`);
  }
  
  // 更新附件列表
  emailAttachments.value = options.fileList;
};

// 暴露方法给父组件
defineExpose({
  openEmailModal
});
</script>

<style scoped>
.email-sender-container {
  width: 100%;
}

.project-schedule-table {
  margin-bottom: 16px;
}

.project-schedule-table :deep(.arco-table-th) {
  background-color: #f2f3f5;
  font-weight: bold;
}

.project-schedule-table :deep(.arco-table-cell) {
  padding: 8px 12px;
}

.project-schedule-table :deep(.arco-table-border) {
  border: 1px solid #e5e6eb;
  border-collapse: collapse;
}

.project-schedule-table :deep(.arco-table-tr) {
  border-bottom: 1px solid #e5e6eb;
}
</style> 