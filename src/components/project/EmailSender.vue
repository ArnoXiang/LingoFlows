<template>
  <div class="email-sender-container">
    <a-modal
      v-model:visible="visible"
      title="Send Project Email"
      @ok="sendProjectEmail"
      @cancel="closeModal"
      :ok-loading="sendingEmail"
    >
      <a-form :model="emailForm">
        <a-form-item field="to" label="To" required>
          <a-input v-model="emailForm.to" placeholder="Recipient email" />
        </a-form-item>
        <a-form-item field="cc" label="CC">
          <a-input v-model="emailForm.cc" placeholder="CC email" />
        </a-form-item>
        <a-form-item field="subject" label="Subject" required>
          <a-input v-model="emailForm.subject" placeholder="Email subject" />
        </a-form-item>
        
        <!-- Project Schedule 表 -->
        <a-form-item field="projectSchedule" label="Project Schedule">
          <div class="project-schedule-table">
            <a-table :columns="scheduleColumns" :data="detailedScheduleData" :bordered="true" :pagination="false" size="small">
              <template #empty>
                <div>Project data unavailable</div>
              </template>
            </a-table>
          </div>
        </a-form-item>
        
        <a-form-item field="content" label="Content" required>
          <a-textarea
            v-model="emailForm.content"
            placeholder="Email content"
            :auto-size="{ minRows: 5, maxRows: 10 }"
          />
        </a-form-item>
        <a-form-item field="attachments" label="Attachments">
          <a-upload
            action="http://localhost:5000/api/upload"
            :file-list="emailAttachments"
            @change="handleEmailAttachmentChange"
            :headers="uploadHeaders"
            multiple
            upload-text="Upload"
          >
            <a-button>Upload Attachments</a-button>
          </a-upload>
        </a-form-item>
      </a-form>
      <template #footer>
        <a-space>
          <a-button @click="closeModal">Cancel</a-button>
          <a-button type="primary" @click="previewEmail">
            <template #icon><icon-eye /></template>
            Preview Email
          </a-button>
          <a-button type="primary" status="success" @click="openInEmailClient">
            <template #icon><icon-email /></template>
            Open in Email Client
          </a-button>
        </a-space>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits, onMounted } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';
import { IconEye, IconEmail } from '@arco-design/web-vue/es/icon';
import { getScheduleData } from './utils/projectUtils';

// 添加日期格式化
const safeDateFormat = (date) => {
  if (!date) return 'TBD';
  try {

    if (date instanceof Date) {
      return date.toLocaleDateString();
    }

    const dateObj = new Date(date);
    if (!isNaN(dateObj.getTime())) {
      return dateObj.toLocaleDateString();
    }
    return date;
  } catch (e) {
    console.error('日期格式化错误:', e);
    return date || 'TBD';
  }
};

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
  htmlContent: '', 
});


const scheduleColumns = [
  {
    title: 'Task',
    dataIndex: 'task',
    key: 'task',
  },
  {
    title: 'Language',
    dataIndex: 'language',
    key: 'language',
  },
  {
    title: 'Deadline',
    dataIndex: 'deadline',
    key: 'deadline',
  },
  {
    title: 'Owner(s)',
    dataIndex: 'owner',
    key: 'owner',
  },
  {
    title: 'Notes',
    dataIndex: 'notes',
    key: 'notes',
  }
];

// 表格数据
const scheduleData = computed(() => {
  if (!currentProject.value) return [];
  return getScheduleData(currentProject.value);
});

// 详细数据（包含每个任务的语言和负责人）
const detailedScheduleData = computed(() => {
  if (!currentProject.value || !taskAssignments.value.length) return scheduleData.value;
  
  // 按任务类型和语言分配数据
  const assignmentsByTaskType = {};
  taskAssignments.value.forEach(assignment => {
    if (!assignmentsByTaskType[assignment.task_type]) {
      assignmentsByTaskType[assignment.task_type] = {};
    }
    assignmentsByTaskType[assignment.task_type][assignment.language] = assignment;
  });
  

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
  
  // 获取语言locale
  const getLanguageDisplayName = (code) => {
    try {
      return new Intl.DisplayNames(['en'], { type: 'language' }).of(code);
    } catch (e) {
      return code.toUpperCase();
    }
  };
  

  Object.keys(assignmentsByTaskType).forEach(taskType => {
    const taskDisplayName = taskTypeDisplayNames[taskType] || taskType;
    

    targetLanguages.forEach(language => {
      const assignment = assignmentsByTaskType[taskType][language];
      
      if (assignment) {

        let deadline = "TBD";
        if (assignment.deadline) {
          try {

            const deadlineDate = new Date(assignment.deadline);
            if (!isNaN(deadlineDate.getTime())) {
              deadline = deadlineDate.toLocaleDateString();
            }
          } catch (e) {
            console.error('Error formatting deadline:', e);
            deadline = assignment.deadline; 
          }
        }
        
        result.push({
          task: taskDisplayName,
          language: getLanguageDisplayName(language),
          deadline: deadline,
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
  
  console.log('Email preview schedule data:', result);
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
    
    // 发送请求
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

//  收集邮箱地址
const collectAssigneeEmails = () => {
  if (!taskAssignments.value || taskAssignments.value.length === 0) {
    return [];
  }
  
  // assignee
  const assignees = new Set();
  
  taskAssignments.value.forEach(assignment => {
    if (assignment.assignee && assignment.assignee.trim() !== '' && assignment.assignee !== 'Not Assigned') {
      assignees.add(assignment.assignee.trim());
    }
  });
  
  // 将assignee转换为email地址
  const emails = Array.from(assignees).map(assignee => {
    // 移除地址中的特殊字符
    const cleanName = assignee.replace(/[^\w\s]/gi, '').replace(/\s+/g, '.');
    return `${cleanName}@sample.com`;
  });
  
  return emails;
};

// 打开邮件对话框
const openEmailModal = async (project) => {
  if (props.userRole !== 'LM') {
    Message.error('Only Localization Managers can send project emails');
    return;
  }

  currentProject.value = project;

  await loadProjectTaskAssignments(project.id);

  emailForm.value.subject = `Project Update: ${project.projectName}`;
  generateEmailContent();
  
  // 自动填充收件人
  const emails = collectAssigneeEmails();
  emailForm.value.to = emails.join('; ');
  
  // 如果没有自动找到邮箱，可以使用pm名称
  if (emails.length === 0 && project.projectManager) {
    const managerEmail = `${project.projectManager.replace(/[^\w\s]/gi, '').replace(/\s+/g, '.')}@sample.com`;
    emailForm.value.to = managerEmail;
  }
  
  // 清空抄送字段和附件
  emailForm.value.cc = '';
  emailAttachments.value = [];
  
  visible.value = true;
};

// 生成邮件内容
const generateEmailContent = () => {
  if (!currentProject.value) return;
  
  // 纯文本格式（用于实际发送）
  let textSchedule = 'Project Schedule:\r\n';
  textSchedule += '--------------------------------\r\n';
  
  // 表头
  textSchedule += 'Task             Language        Deadline        Owner(s)         Notes\r\n';
  textSchedule += '--------------------------------\r\n';
  
  // 项目行
  detailedScheduleData.value.forEach(item => {
    const task = (item.task || '').padEnd(16);
    const language = (item.language || '').padEnd(15);
    const deadline = (item.deadline || '').padEnd(15);
    const owner = (item.owner || '').padEnd(16);
    const notes = item.notes || '';
    
    textSchedule += `${task}${language}${deadline}${owner}${notes}\r\n`;
  });
  textSchedule += '--------------------------------\r\n\r\n';
  
  // HTML预览，Task列相同值合并
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
  
  const taskGroups = {};
  detailedScheduleData.value.forEach(item => {
    const taskName = item.task || '';
    if (!taskGroups[taskName]) {
      taskGroups[taskName] = [];
    }
    taskGroups[taskName].push(item);
  });
  
  // 遍历每个任务组生成表格行
  Object.keys(taskGroups).forEach(taskName => {
    const taskItems = taskGroups[taskName];
    const rowCount = taskItems.length;
    
    // 生成该任务的所有行
    taskItems.forEach((item, index) => {
      htmlSchedule += '<tr>';
      

      if (index === 0) {
        htmlSchedule += `
          <td style="border:1px solid #ddd;padding:8px;text-align:left;vertical-align:top" rowspan="${rowCount}">${taskName}</td>
        `;
      }
      

      htmlSchedule += `
        <td style="border:1px solid #ddd;padding:8px;text-align:left">${item.language || ''}</td>
        <td style="border:1px solid #ddd;padding:8px;text-align:left">${item.deadline || ''}</td>
        <td style="border:1px solid #ddd;padding:8px;text-align:left">${item.owner || ''}</td>
        <td style="border:1px solid #ddd;padding:8px;text-align:left">${item.notes || ''}</td>
      `;
      
      htmlSchedule += '</tr>';
    });
  });
  
  htmlSchedule += `
        </tbody>
      </table>
    </div>
  `;
  
  // 邮件内容（
  let plainTextContent = `Dear supplier,\r\n\r\n`;
  plainTextContent += `I hope this email finds you well. I am providing you with the latest project schedule for the ${currentProject.value.projectName} project.\r\n\r\n`;
  plainTextContent += textSchedule;
  plainTextContent += `If you have any questions, please feel free to contact me.\r\n\r\n`;
  plainTextContent += `Regards,\r\n${currentProject.value.projectManager}\r\n`;
  
  // 保存简化版本用于mailto链接
  let mailtoContent = `Dear supplier,\r\n\r\n`;
  mailtoContent += `I hope this email finds you well. I am providing you with the latest project schedule for the ${currentProject.value.projectName} project.\r\n\r\n`;
  mailtoContent += `Project Schedule Summary:\r\n\r\n`;
  
  // 添加ddl信息
  mailtoContent += `Important Deadlines:\r\n`;
  if (currentProject.value.translationDeadline) {
    mailtoContent += `- Translation: ${safeDateFormat(currentProject.value.translationDeadline)}\r\n`;
  }
  if (currentProject.value.lqaDeadline) {
    mailtoContent += `- LQA: ${safeDateFormat(currentProject.value.lqaDeadline)}\r\n`;
  }
  if (currentProject.value.translationUpdateDeadline) {
    mailtoContent += `- Translation Update: ${safeDateFormat(currentProject.value.translationUpdateDeadline)}\r\n`;
  }
  if (currentProject.value.lqaReportFinalizationDeadline) {
    mailtoContent += `- LQA Report Finalization: ${safeDateFormat(currentProject.value.lqaReportFinalizationDeadline)}\r\n`;
  }
  mailtoContent += `- Project Final Delivery: ${safeDateFormat(currentProject.value.expectedDeliveryDate)}\r\n\r\n`;
  
  // 任务类型、语言和负责人
  const taskTypes = new Set();
  const languages = new Set();
  const assigneesByTask = {};
  
  detailedScheduleData.value.forEach(item => {
    if (item.task) {
      taskTypes.add(item.task);
      
      if (!assigneesByTask[item.task]) {
        assigneesByTask[item.task] = {};
      }
      
      if (item.language && item.owner) {
        assigneesByTask[item.task][item.language] = item.owner;
      }
    }
    
    if (item.language) languages.add(item.language);
  });
  
  const taskArray = Array.from(taskTypes);
  const languageArray = Array.from(languages);
  
  // ASCII表格
  let headerRow = '+-----------------+';
  languageArray.forEach(() => {
    headerRow += '----------------+';
  });
  
  mailtoContent += headerRow + '\r\n';
  
  // 任务/语言行
  let langHeaderRow = '| Task/Language    |';
  languageArray.forEach(lang => {
    langHeaderRow += ` ${lang.padEnd(14)} |`;
  });
  
  mailtoContent += langHeaderRow + '\r\n';
  mailtoContent += headerRow + '\r\n';
  
  // 数据行
  taskArray.forEach(task => {
    let dataRow = `| ${task.padEnd(15)} |`;
    
    languageArray.forEach(lang => {
      const assignee = assigneesByTask[task]?.[lang] || 'N/A';
      // 限制显示长度，以维持表格对齐
      const displayAssignee = assignee.length > 14 ? assignee.substring(0, 11) + '...' : assignee;
      dataRow += ` ${displayAssignee.padEnd(14)} |`;
    });
    
    mailtoContent += dataRow + '\r\n';
  });
  
  mailtoContent += headerRow + '\r\n\r\n';
  
  mailtoContent += `Deadline: ${currentProject.value.expectedDeliveryDate || 'TBD'}\r\n`;
  mailtoContent += `Project Manager: ${currentProject.value.projectManager || 'TBD'}\r\n\r\n`;
  
  mailtoContent += `For detailed schedule, please see the attached preview or contact me.\r\n\r\n`;
  mailtoContent += `If you have any questions, please feel free to contact me.\r\n\r\n`;
  mailtoContent += `Regards,\r\n${currentProject.value.projectManager}`;
  
  // HTML格式的邮件内容
  let htmlContent = `
    <p>Dear supplier,</p>
    <p>I hope this email finds you well. I am providing you with the latest project schedule for the ${currentProject.value.projectName} project.</p>
    
    <div style="background-color:#f5f7fa;padding:15px;border-left:4px solid #165dff;margin:15px 0;border-radius:4px;">
      <h3 style="margin-top:0;color:#165dff">Important Deadlines</h3>
      <ul style="list-style-type:none;padding-left:0;line-height:1.8">
        ${currentProject.value.translationDeadline ? 
          `<li><strong>Translation:</strong> ${safeDateFormat(currentProject.value.translationDeadline)}</li>` : ''}
        ${currentProject.value.lqaDeadline ? 
          `<li><strong>LQA:</strong> ${safeDateFormat(currentProject.value.lqaDeadline)}</li>` : ''}
        ${currentProject.value.translationUpdateDeadline ? 
          `<li><strong>Translation Update:</strong> ${safeDateFormat(currentProject.value.translationUpdateDeadline)}</li>` : ''}
        ${currentProject.value.lqaReportFinalizationDeadline ? 
          `<li><strong>LQA Report Finalization:</strong> ${safeDateFormat(currentProject.value.lqaReportFinalizationDeadline)}</li>` : ''}
        <li><strong>Project Final Delivery:</strong> ${safeDateFormat(currentProject.value.expectedDeliveryDate)}</li>
      </ul>
    </div>
    
    ${htmlSchedule}
    <p>If you have any questions, please feel free to contact me.</p>
    <p>Regards,<br>${currentProject.value.projectManager}</p>
  `;
  
 
  emailForm.value.content = plainTextContent;
  emailForm.value.mailtoContent = mailtoContent;
  emailForm.value.htmlContent = htmlContent;
};

const closeModal = () => {
  visible.value = false;
  emit('close');
};

// 预览
const previewEmail = () => {
  if (!emailForm.value.content) {
    Message.error('Email content cannot be empty');
    return;
  }
  
  // 使用htmlContent否则将纯文本转换为HTML
  let emailContent = emailForm.value.htmlContent || '';
  
  // 如果没有HTML内容，将纯文本转换为HTML
  if (!emailContent) {
    emailContent = emailForm.value.content
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');
    emailContent = '<p>' + emailContent + '</p>';
  }
  
  // 创建完整的HTML预览页面
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
  
  const previewWindow = window.open(url, '_blank');
  
  // 当预览窗口关闭时释放URL对象
  if (previewWindow) {
    previewWindow.addEventListener('beforeunload', () => {
      URL.revokeObjectURL(url);
    });
  } else {
    // 浏览器可能阻止了窗口打开
    Message.error('Browser blocked opening the window, please allow popups');
    // 释放URL对象
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
};

// 在默认邮件client中打开
const openInEmailClient = () => {
  if (!emailForm.value.to || !emailForm.value.subject || !emailForm.value.content) {
    Message.error('Please fill in all required fields');
    return;
  }
  
  try {
    const emailContent = emailForm.value.mailtoContent || emailForm.value.content;
    
    // 构建mailto链接，保持url参数长度在合理范围内
    let mailtoLink = 'mailto:' + encodeURIComponent(emailForm.value.to);
    
    // 添加抄送
    if (emailForm.value.cc) {
      mailtoLink += '?cc=' + encodeURIComponent(emailForm.value.cc);
    }
    
    // 添加主题
    mailtoLink += (mailtoLink.includes('?') ? '&' : '?') + 'subject=' + encodeURIComponent(emailForm.value.subject);
    
    // 添加正文
    const maxBodyLength = 9999;
    let bodyContent = emailContent;
    
    if (bodyContent.length > maxBodyLength) {
      console.warn(`Email body content truncated from ${bodyContent.length} to ${maxBodyLength} characters`);
      bodyContent = bodyContent.substring(0, maxBodyLength) + 
        "\r\n...\r\n[Content truncated due to length. Full content will be visible in your email client.]";
    }
    
    mailtoLink += '&body=' + encodeURIComponent(bodyContent);
    
    
    const link = document.createElement('a');
    link.href = mailtoLink;
    link.style.display = 'none';
    document.body.appendChild(link);
    

    link.click();
    
    setTimeout(() => {
      document.body.removeChild(link);
    }, 100);
    

    Message.success({
      content: 'Trying to open your default mail client. If the project schedule is incomplete, please use the Preview function to view the full content.',
      duration: 5000
    });
    
    
  } catch (error) {
    console.error('Error opening email client:', error);
    
    Message.error({
      content: `Unable to open mail client: ${error.message}. Please make sure your system has set up a default mail application, or copy the content and send it manually.`,
      duration: 5000
    });
    
    
    
  }
};

// 发送项目邮件
const sendProjectEmail = async () => {
  if (!currentProject.value) return;
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('Only Localization Managers can send project emails');
    return;
  }
  
  // 表单验证
  if (!emailForm.value.to || !emailForm.value.subject || !emailForm.value.content) {
    Message.error('Please fill in all required fields');
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
      Message.success('Email sent successfully');
      visible.value = false;
      emit('sent', response.data); // 通知父组件邮件已发送
    } else {
      throw new Error('Sending failed');
    }
  } catch (error) {
    console.error('Error sending email:', error);
    Message.error(`Sending failed: ${error.message}`);
  } finally {
    sendingEmail.value = false;
  }
};


const handleEmailAttachmentChange = (options) => {

  if (options.file.status === 'done') {
    const response = options.file.response;
    if (response && response.filename) {
      Message.success(`Attachment ${options.file.name} uploaded successfully`);
    }
  }
  
  if (options.file.status === 'error') {
    console.error('Attachment upload error:', options.file.response);
    Message.error(`Attachment ${options.file.name} upload failed`);
  }
  
  emailAttachments.value = options.fileList;
};


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