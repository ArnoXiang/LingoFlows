<template>
  <div class="project-detail-container">
    <a-drawer
      v-model:visible="visible"
      :width="600"
      :title="drawerTitle"
      unmountOnClose
    >
      <div v-if="project">
        <a-tabs v-model:activeKey="activeTabKey">
          <a-tab-pane key="info" title="项目信息 / Project Info">
            <a-descriptions :column="1" bordered>
              <a-descriptions-item label="项目名称 / Project Name">
                <a-input v-model="project.projectName" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ project.projectName }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="项目状态 / Project Status">
                <a-select v-model="project.projectStatus" v-if="isEditing && userRole === 'LM'">
                  <a-option value="pending">待处理 / Pending</a-option>
                  <a-option value="in_progress">进行中 / In Progress</a-option>
                  <a-option value="completed">已完成 / Completed</a-option>
                  <a-option value="cancelled">已取消 / Cancelled</a-option>
                </a-select>
                <a-tag v-else :color="getStatusColor(project.projectStatus)">
                  {{ getStatusText(project.projectStatus) }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="请求名称 / Request Name">
                <a-input v-model="project.requestName" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ project.requestName }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="项目经理 / Project Manager">
                <a-input v-model="project.projectManager" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ project.projectManager }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="创建时间 / Create Time">
                {{ formatDate(project.createTime) }}
              </a-descriptions-item>
              <a-descriptions-item label="源语言 / Source Language">
                <a-select v-model="project.sourceLanguage" v-if="isEditing && userRole === 'LM'">
                  <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">{{ lang.name }}</a-option>
                </a-select>
                <span v-else>{{ getLanguageName(project.sourceLanguage) }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="目标语言 / Target Languages">
                <a-select v-model="project.targetLanguages" multiple v-if="isEditing && userRole === 'LM'">
                  <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">{{ lang.name }}</a-option>
                </a-select>
                <div v-else>
                  <a-tag v-for="lang in project.targetLanguages" :key="lang" style="margin: 2px;">
                    {{ getLanguageName(lang) }}
                  </a-tag>
                </div>
              </a-descriptions-item>
              <a-descriptions-item label="字数 / Word Count">
                <a-input-number v-model="project.wordCount" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ project.wordCount }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="预期交付日期 / Expected Delivery Date">
                <a-date-picker v-model="project.expectedDeliveryDate" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ formatDate(project.expectedDeliveryDate) }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="附加要求 / Additional Requirements">
                <a-checkbox-group 
                  v-model="project.additionalRequirements" 
                  v-if="isEditing && userRole === 'LM'"
                >
                  <a-checkbox value="lqa">语言质量保证 (LQA) / Linguistic Quality Assurance</a-checkbox>
                  <a-checkbox value="imageTranslation">图像文本翻译 / Image Text Translation</a-checkbox>
                </a-checkbox-group>
                <div v-else>
                  <a-tag v-for="req in project.additionalRequirements" :key="req" style="margin: 2px;">
                    {{ getRequirementText(req) }}
                  </a-tag>
                </div>
              </a-descriptions-item>
            </a-descriptions>
            
            <!-- 任务状态和详细信息 -->
            <div v-if="userRole === 'LM' && isEditing" style="margin-top: 24px;">
              <h3>任务详情 / Task Details</h3>
              <a-form :model="project.tasks">
                <a-collapse>
                  <a-collapse-item header="翻译任务 / Translation Task" key="1">
                    <a-form-item label="状态 / Status">
                      <a-select v-model="project.tasks.translation.status">
                        <a-option value="not_started">未开始 / Not Started</a-option>
                        <a-option value="in_progress">进行中 / In Progress</a-option>
                        <a-option value="completed">已完成 / Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="负责人 / Assignee">
                      <a-input v-model="project.tasks.translation.assignee" placeholder="翻译人员 / Translator" />
                    </a-form-item>
                    <a-form-item label="截止日期 / Deadline">
                      <a-date-picker v-model="project.tasks.translation.deadline" />
                    </a-form-item>
                    <a-form-item label="备注 / Notes">
                      <a-textarea v-model="project.tasks.translation.notes" placeholder="任务备注 / Task notes" />
                    </a-form-item>
                  </a-collapse-item>
                  <a-collapse-item header="LQA任务 / LQA Task" key="2">
                    <a-form-item label="状态 / Status">
                      <a-select v-model="project.tasks.lqa.status">
                        <a-option value="not_started">未开始 / Not Started</a-option>
                        <a-option value="in_progress">进行中 / In Progress</a-option>
                        <a-option value="completed">已完成 / Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="负责人 / Assignee">
                      <a-input v-model="project.tasks.lqa.assignee" placeholder="LQA人员 / LQA Specialist" />
                    </a-form-item>
                    <a-form-item label="截止日期 / Deadline">
                      <a-date-picker v-model="project.tasks.lqa.deadline" />
                    </a-form-item>
                    <a-form-item label="备注 / Notes">
                      <a-textarea v-model="project.tasks.lqa.notes" placeholder="任务备注 / Task notes" />
                    </a-form-item>
                  </a-collapse-item>
                </a-collapse>
              </a-form>
            </div>
            
            <div class="task-status" style="margin-top: 24px;" v-if="userRole === 'BO'">
              <h3>任务状态 / Task Status</h3>
              <a-descriptions :column="1" bordered>
                <a-descriptions-item label="翻译任务 / Translation Task">
                  <a-tag :color="getTaskStatus(project.taskTranslation)">
                    {{ getTaskText(project.taskTranslation) }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="LQA任务 / LQA Task">
                  <a-tag :color="getTaskStatus(project.taskLQA)">
                    {{ getTaskText(project.taskLQA) }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="翻译更新 / Translation Update">
                  <a-tag :color="getTaskStatus(project.taskTranslationUpdate)">
                    {{ getTaskText(project.taskTranslationUpdate) }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="LQA报告定稿 / LQA Report Finalization">
                  <a-tag :color="getTaskStatus(project.taskLQAReportFinalization)">
                    {{ getTaskText(project.taskLQAReportFinalization) }}
                  </a-tag>
                </a-descriptions-item>
              </a-descriptions>
            </div>
          </a-tab-pane>
          
          <!-- 新增文件管理标签页 -->
          <a-tab-pane key="files" title="项目文件 / Project Files">
            <div class="project-files-container">
              <!-- 内嵌FileManager组件，明确设置visible为true -->
              <FileManager
                ref="fileManagerRef"
                :projectId="project.id"
                :userRole="userRole"
                :userId="userId"
                :visible="true"
                @refresh-files="handleFilesRefreshed"
              />
              
              <!-- 如果需要额外的上传按钮，可以放在这里 -->
              <div class="upload-button-container" style="margin-top: 16px; text-align: right;">
                <a-button type="primary" @click="openFileUploadModal">
                  上传文件 / Upload Files
                </a-button>
              </div>
            </div>
          </a-tab-pane>
        </a-tabs>
        
        <div class="drawer-footer" style="margin-top: 24px; text-align: right;">
          <a-space>
            <a-button @click="closeDrawer">
              关闭 / Close
            </a-button>
            <a-button type="primary" @click="saveProject" v-if="userRole === 'LM' && isEditing">
              保存 / Save
            </a-button>
          </a-space>
        </div>
      </div>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, computed, watch, nextTick } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';
import { languages } from '../../utils/languages';
import { 
  getStatusColor, 
  getStatusText, 
  getTaskStatus, 
  getTaskText,
  getRequirementText,
  getLanguageName,
  formatDate 
} from './utils/projectUtils';
import FileManager from './FileManager.vue'; // 导入FileManager组件

const props = defineProps({
  userRole: {
    type: String,
    default: ''
  },
  userId: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(['close', 'save', 'files-refreshed']);

// 状态
const visible = ref(false);
const drawerTitle = ref('项目详情 / Project Details');
const project = ref(null);
const isEditing = ref(false);
const activeTabKey = ref('info'); // 当前激活的标签页
const fileManagerRef = ref(null); // 文件管理器引用

// 监听标签页变化
watch(() => activeTabKey.value, async (newVal) => {
  if (newVal === 'files' && project.value && project.value.id) {
    console.log('切换到文件标签页，执行自动加载文件');
    
    // 加载文件和修复映射关系
    if (fileManagerRef.value) {
      try {
        // 加载项目文件前先进行自动修复
        console.log('开始修复文件映射并加载文件...');
        
        // 先显示加载状态
        fileManagerRef.value.loadingFiles = true;
        
        // 修复映射关系（静默模式）
        try {
          await fileManagerRef.value.fixFileMappings(true);
        } catch (error) {
          console.error('自动修复文件映射失败:', error);
          // 继续加载文件，不中断流程
        }
        
        // 加载项目文件
        await fileManagerRef.value.loadProjectFiles(project.value.id);
        
        // 通知父组件文件已刷新
        emit('files-refreshed');
      } catch (error) {
        console.error('自动加载文件失败:', error);
        Message.error('加载项目文件失败，请稍后重试');
      }
    }
  }
});

// 方法
const openDrawer = (currentProject, mode = 'view') => {
  // 处理任务详细信息
  let translationDeadline = null;
  if (currentProject.translationDeadline) {
    try {
      translationDeadline = new Date(currentProject.translationDeadline);
    } catch (error) {
      console.error('处理翻译截止日期时出错:', error);
    }
  }
  
  let lqaDeadline = null;
  if (currentProject.lqaDeadline) {
    try {
      lqaDeadline = new Date(currentProject.lqaDeadline);
    } catch (error) {
      console.error('处理LQA截止日期时出错:', error);
    }
  }
  
  // 处理预期交付日期
  let expectedDeliveryDate = currentProject.expectedDeliveryDate;
  if (expectedDeliveryDate) {
    try {
      // 尝试将日期字符串转换为日期对象
      const dateObj = new Date(expectedDeliveryDate);
      if (!isNaN(dateObj.getTime())) {
        expectedDeliveryDate = dateObj;
      }
    } catch (error) {
      console.error('处理日期字段时出错:', error);
    }
  }
  
  // 克隆项目数据，避免直接修改原始数据
  project.value = {
    ...currentProject,
    expectedDeliveryDate,
    tasks: {
      translation: {
        status: currentProject.taskTranslation || 'not_started',
        assignee: currentProject.translationAssignee || '',
        deadline: translationDeadline,
        notes: currentProject.translationNotes || '',
      },
      lqa: {
        status: currentProject.taskLQA || 'not_started',
        assignee: currentProject.lqaAssignee || '',
        deadline: lqaDeadline,
        notes: currentProject.lqaNotes || '',
      },
    },
  };
  
  isEditing.value = mode === 'edit';
  drawerTitle.value = isEditing.value 
    ? `编辑项目 / Edit Project: ${currentProject.projectName}`
    : `项目详情 / Project Details: ${currentProject.projectName}`;
  
  visible.value = true;
  activeTabKey.value = 'info'; // 默认显示信息标签页
  
  // 如果文件管理器引用存在，加载项目文件
  if (project.value && project.value.id && fileManagerRef.value) {
    // 在nextTick中执行，确保DOM已经更新
    nextTick(() => {
      fileManagerRef.value.loadProjectFiles(project.value.id);
    });
  }
};

const closeDrawer = () => {
  visible.value = false;
  emit('close');
};

// 打开文件上传模态框
const openFileUploadModal = () => {
  if (!project.value || !project.value.id) {
    Message.error('项目ID不存在，无法上传文件 / Project ID does not exist, cannot upload files');
    return;
  }
  
  if (fileManagerRef.value) {
    fileManagerRef.value.openUploadModal(project.value.id);
  }
};

// 处理文件刷新事件
const handleFilesRefreshed = () => {
  console.log('项目文件已刷新');
  emit('files-refreshed');
};

const saveProject = async () => {
  if (!project.value) return;
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('只有本地化经理可以更新项目 / Only Localization Managers can update projects');
    return;
  }
  
  try {
    // 格式化日期为字符串
    let formattedExpectedDeliveryDate = project.value.expectedDeliveryDate;
    if (formattedExpectedDeliveryDate instanceof Date) {
      formattedExpectedDeliveryDate = formattedExpectedDeliveryDate.toISOString().split('T')[0]; // 格式化为 YYYY-MM-DD
    }
    
    // 格式化任务截止日期
    let formattedTranslationDeadline = project.value.tasks.translation.deadline;
    if (formattedTranslationDeadline instanceof Date) {
      formattedTranslationDeadline = formattedTranslationDeadline.toISOString().split('T')[0];
    }
    
    let formattedLQADeadline = project.value.tasks.lqa.deadline;
    if (formattedLQADeadline instanceof Date) {
      formattedLQADeadline = formattedLQADeadline.toISOString().split('T')[0];
    }
    
    // 准备更新的项目数据
    const updatedProject = {
      id: project.value.id,
      projectName: project.value.projectName,
      projectStatus: project.value.projectStatus,
      requestName: project.value.requestName,
      projectManager: project.value.projectManager,
      
      // 任务状态
      taskTranslation: project.value.tasks.translation.status,
      taskLQA: project.value.tasks.lqa.status,
      taskTranslationUpdate: project.value.taskTranslationUpdate || 'not_started',
      taskLQAReportFinalization: project.value.taskLQAReportFinalization || 'not_started',
      
      // 任务详细信息
      translationAssignee: project.value.tasks.translation.assignee || '',
      translationDeadline: formattedTranslationDeadline || null,
      translationNotes: project.value.tasks.translation.notes || '',
      
      lqaAssignee: project.value.tasks.lqa.assignee || '',
      lqaDeadline: formattedLQADeadline || null,
      lqaNotes: project.value.tasks.lqa.notes || '',
      
      // 其他信息
      sourceLanguage: project.value.sourceLanguage,
      targetLanguages: Array.isArray(project.value.targetLanguages) 
        ? project.value.targetLanguages.join(',') 
        : project.value.targetLanguages,
      wordCount: project.value.wordCount,
      expectedDeliveryDate: formattedExpectedDeliveryDate,
      additionalRequirements: Array.isArray(project.value.additionalRequirements) 
        ? project.value.additionalRequirements.join(',') 
        : project.value.additionalRequirements,
    };
    
    console.log('准备更新项目数据:', updatedProject);
    
    // 发送更新请求
    const response = await axios.put(`http://localhost:5000/api/projects/${updatedProject.id}`, updatedProject);
    
    if (response.status === 200) {
      Message.success('项目更新成功 / Project updated successfully');
      visible.value = false;
      emit('save', response.data); // 通知父组件更新成功
    } else {
      throw new Error('更新失败 / Update failed');
    }
  } catch (error) {
    console.error('Error updating project:', error);
    
    let errorMessage = '更新失败 / Update failed';
    
    if (error.response) {
      // 服务器返回了错误响应
      console.error('错误响应:', error.response.data);
      console.error('状态码:', error.response.status);
      errorMessage = `更新失败: ${error.response.data?.error || error.response.statusText}`;
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('请求已发送但没有收到响应:', error.request);
      errorMessage = '无法连接到服务器，请检查网络连接 / Cannot connect to server, please check your network';
    } else {
      // 设置请求时发生错误
      errorMessage = `更新失败: ${error.message}`;
    }
    
    Message.error(errorMessage);
  }
};

// 切换到文件标签页
const switchToFilesTab = async () => {
  if (!project.value || !project.value.id) {
    console.warn('无法切换到文件标签页：项目不存在或没有ID');
    return;
  }
  
  console.log('手动切换到文件标签页，项目ID:', project.value.id);
  
  // 先切换标签页
  activeTabKey.value = 'files';
  
  // 确保DOM更新
  await nextTick();
  
  // 等待一些时间，确保DOM完全更新
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // 然后手动加载文件
  if (fileManagerRef.value) {
    try {
      console.log('手动加载项目文件...');
      
      // 设置加载状态
      fileManagerRef.value.loadingFiles = true;
      
      // 尝试修复文件映射
      try {
        await fileManagerRef.value.fixFileMappings(true);
      } catch (error) {
        console.error('文件映射修复失败，但继续加载文件:', error);
      }
      
      // 加载项目文件
      await fileManagerRef.value.loadProjectFiles(project.value.id);
      
      console.log('文件加载成功');
    } catch (error) {
      console.error('手动加载文件失败:', error);
      Message.error('加载项目文件失败，请稍后重试');
    }
  } else {
    console.error('fileManagerRef不存在，无法加载文件');
  }
};

// 暴露方法给父组件
defineExpose({
  openDrawer,
  // 添加便捷方法
  viewProject: (project) => openDrawer(project, 'view'),
  editProject: (project) => openDrawer(project, 'edit'),
  switchToFilesTab
});
</script>

<style scoped>
.project-detail-container {
  width: 100%;
}

.project-files-container {
  margin-top: 16px;
}

.upload-button-container {
  margin-top: 16px;
  text-align: right;
}
</style> 