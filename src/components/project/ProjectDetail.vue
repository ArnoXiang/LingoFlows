<template>
  <div class="project-detail-container">
    <a-drawer
      v-model:visible="visible"
      :width="drawerWidth"
      :title="drawerTitle"
      unmountOnClose
      @close="closeDrawer"
      ok-text="Confirm"
      cancel-text="Cancel"
      @ok="saveProject"
      :ok-button-props="{ disabled: !isEditing }"
    >
      <!-- 自定义拖拽条 -->
      <div 
        class="drawer-resize-handle" 
        v-if="visible"
        @mousedown="startResize"
        title="Drag to resize"
      >
        <div class="resize-indicator"></div>
      </div>
      <div v-if="project">
        <a-tabs v-model:activeKey="activeTabKey">
          <a-tab-pane key="info" title="Project Info">
            <a-descriptions :column="1" bordered size="large" title="Basic Information" class="info-section">
              <a-descriptions-item label="Project Name">
                <a-input v-model="project.projectName" placeholder="Enter project name" :disabled="!isEditing" />
              </a-descriptions-item>
              
              <a-descriptions-item label="Project Status">
                <a-select v-model="project.status" :disabled="!isEditing">
                  <a-option value="pending">Pending</a-option>
                  <a-option value="in_progress">In Progress</a-option>
                  <a-option value="completed">Completed</a-option>
                  <a-option value="cancelled">Cancelled</a-option>
                </a-select>
              </a-descriptions-item>
              
              <!-- 源自请求的信息 -->
              <a-descriptions-item label="Request Name">
                <span>{{ project.requestName || 'N/A' }}</span>
              </a-descriptions-item>
              
              <a-descriptions-item label="Project Manager">
                <a-input v-model="project.projectManager" placeholder="Enter project manager name" :disabled="!isEditing" />
              </a-descriptions-item>
              
              <a-descriptions-item label="Create Time">
                <span>{{ formatDate(project.createdAt) }}</span>
              </a-descriptions-item>
              
              <a-descriptions-item label="Source Language">
                <a-select v-model="project.sourceLanguage" placeholder="Select source language" :disabled="!isEditing">
                  <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">
                    {{ lang.name }}
                  </a-option>
                </a-select>
              </a-descriptions-item>
              
              <a-descriptions-item label="Target Languages">
                <a-select v-model="project.targetLanguages" placeholder="Select target languages" multiple :disabled="!isEditing">
                  <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">
                    {{ lang.name }}
                  </a-option>
                </a-select>
                <div class="description-hint">
                  Selected: {{ formatSelectedLanguages(project.targetLanguages) }}
                </div>
              </a-descriptions-item>
              
              <a-descriptions-item label="Word Count">
                <a-input-number v-model="project.wordCount" :min="1" :step="100" :disabled="!isEditing" />
              </a-descriptions-item>
              
              <a-descriptions-item label="Expected Delivery Date">
                <a-date-picker 
                  v-model="project.expectedDeliveryDate" 
                  style="width: 100%;" 
                  placeholder="Please select date" 
                  :disabled="!isEditing"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD" 
                />
              </a-descriptions-item>
              
              <a-descriptions-item label="Additional Requirements">
                <div class="additional-requirements-checkboxes">
                  <a-space direction="vertical">
                    <a-checkbox value="lqa" :disabled="!isEditing">Linguistic Quality Assurance</a-checkbox>
                    <a-checkbox value="imageTranslation" :disabled="!isEditing">Image Text Translation</a-checkbox>
                    <a-checkbox value="custom" :disabled="!isEditing">Custom Requirements</a-checkbox>
                  </a-space>
                  <a-textarea v-model="project.additionalRequirements" style="margin-top: 10px;" :disabled="!isEditing" />
                </div>
              </a-descriptions-item>
            </a-descriptions>
            
            <!-- 项目任务管理 -->
            <div class="task-section">
              <h3>Task Details</h3>
              
              <a-collapse default-active-key="1">
                <a-collapse-item header="Translation Task" key="1">
                  <div v-if="targetLanguagesList.length > 0">
                    <!-- 添加语言选择标签页 -->
                    <a-tabs v-model:activeKey="activeLanguageKeys.translation" class="language-tabs">
                      <a-tab-pane v-for="lang in targetLanguagesList" :key="lang" :title="getLanguageName(lang)">
                        <a-form-item label="Assignee">
                          <a-input
                            v-model="languageAssignments.translation[lang].assignee" 
                            placeholder="Translator name"
                            :disabled="!isEditing"
                          />
                        </a-form-item>
                        <a-form-item label="Deadline">
                          <a-date-picker 
                            v-model="languageAssignments.translation[lang].deadline" 
                            style="width: 100%;"
                            placeholder="Please select date"
                            :disabled="!isEditing"
                            value-format="YYYY-MM-DD"
                          />
                        </a-form-item>
                        <a-form-item label="Notes">
                          <a-textarea 
                            v-model="languageAssignments.translation[lang].notes" 
                            placeholder="Task notes"
                            :disabled="!isEditing"
                          />
                        </a-form-item>
                      </a-tab-pane>
                    </a-tabs>
                    
                    <a-form-item label="Status">
                      <a-select v-model="project.tasks.translation.status" :disabled="!isEditing">
                        <a-option value="not_started">Not Started</a-option>
                        <a-option value="in_progress">In Progress</a-option>
                        <a-option value="completed">Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="Assignee" v-if="!targetLanguagesList.length">
                      <a-input v-model="project.tasks.translation.assignee" placeholder="Translator" :disabled="!isEditing" />
                    </a-form-item>
                    <a-form-item label="Deadline" v-if="!targetLanguagesList.length">
                      <a-date-picker v-model="project.tasks.translation.deadline" style="width: 100%;" placeholder="Please select date" :disabled="!isEditing" />
                    </a-form-item>
                    <a-form-item label="Notes" v-if="!targetLanguagesList.length">
                      <a-textarea v-model="project.tasks.translation.notes" placeholder="Task notes" :disabled="!isEditing" />
                    </a-form-item>
                  </div>
                </a-collapse-item>
                
                <a-collapse-item header="LQA Task" key="2">
                  <div v-if="targetLanguagesList.length > 0">
                    <!-- 添加语言选择标签页 -->
                    <a-tabs v-model:activeKey="activeLanguageKeys.lqa" class="language-tabs">
                      <a-tab-pane v-for="lang in targetLanguagesList" :key="lang" :title="getLanguageName(lang)">
                        <a-form-item label="Assignee">
                          <a-input
                            v-model="languageAssignments.lqa[lang].assignee" 
                            placeholder="LQA Specialist name"
                            :disabled="!isEditing"
                          />
                        </a-form-item>
                        <a-form-item label="Deadline">
                          <a-date-picker 
                            v-model="languageAssignments.lqa[lang].deadline" 
                            style="width: 100%;"
                            placeholder="Please select date"
                            :disabled="!isEditing"
                            value-format="YYYY-MM-DD"
                          />
                        </a-form-item>
                        <a-form-item label="Notes">
                          <a-textarea 
                            v-model="languageAssignments.lqa[lang].notes" 
                            placeholder="Task notes"
                            :disabled="!isEditing"
                          />
                        </a-form-item>
                      </a-tab-pane>
                    </a-tabs>
                    
                    <a-form-item label="Status">
                      <a-select v-model="project.tasks.lqa.status" :disabled="!isEditing">
                        <a-option value="not_started">Not Started</a-option>
                        <a-option value="in_progress">In Progress</a-option>
                        <a-option value="completed">Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="Assignee" v-if="!targetLanguagesList.length">
                      <a-input v-model="project.tasks.lqa.assignee" placeholder="LQA Specialist" :disabled="!isEditing" />
                    </a-form-item>
                    <a-form-item label="Deadline" v-if="!targetLanguagesList.length">
                      <a-date-picker v-model="project.tasks.lqa.deadline" style="width: 100%;" placeholder="Please select date" :disabled="!isEditing" />
                    </a-form-item>
                    <a-form-item label="Notes" v-if="!targetLanguagesList.length">
                      <a-textarea v-model="project.tasks.lqa.notes" placeholder="Task notes" :disabled="!isEditing" />
                    </a-form-item>
                  </div>
                </a-collapse-item>
                
                <a-collapse-item header="Translation Update" key="3">
                  <div v-if="targetLanguagesList.length > 0">
                    <!-- 添加语言选择标签页 -->
                    <a-tabs v-model:activeKey="activeLanguageKeys.translationUpdate" class="language-tabs">
                      <a-tab-pane v-for="lang in targetLanguagesList" :key="lang" :title="getLanguageName(lang)">
                        <a-form-item label="Assignee">
                          <a-input
                            v-model="languageAssignments.translationUpdate[lang].assignee" 
                            placeholder="Update Specialist name"
                            :disabled="!isEditing"
                          />
                        </a-form-item>
                        <a-form-item label="Deadline">
                          <a-date-picker 
                            v-model="languageAssignments.translationUpdate[lang].deadline" 
                            style="width: 100%;"
                            placeholder="Please select date"
                            :disabled="!isEditing"
                            value-format="YYYY-MM-DD"
                          />
                        </a-form-item>
                        <a-form-item label="Notes">
                          <a-textarea 
                            v-model="languageAssignments.translationUpdate[lang].notes" 
                            placeholder="Task notes"
                            :disabled="!isEditing"
                          />
                        </a-form-item>
                      </a-tab-pane>
                    </a-tabs>
                    
                    <a-form-item label="Status">
                      <a-select v-model="project.tasks.translationUpdate.status" :disabled="!isEditing">
                        <a-option value="not_started">Not Started</a-option>
                        <a-option value="in_progress">In Progress</a-option>
                        <a-option value="completed">Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="Assignee" v-if="!targetLanguagesList.length">
                      <a-input v-model="project.tasks.translationUpdate.assignee" placeholder="Update Specialist" :disabled="!isEditing" />
                    </a-form-item>
                    <a-form-item label="Deadline" v-if="!targetLanguagesList.length">
                      <a-date-picker v-model="project.tasks.translationUpdate.deadline" style="width: 100%;" placeholder="Please select date" :disabled="!isEditing" />
                    </a-form-item>
                    <a-form-item label="Notes" v-if="!targetLanguagesList.length">
                      <a-textarea v-model="project.tasks.translationUpdate.notes" placeholder="Task notes" :disabled="!isEditing" />
                    </a-form-item>
                  </div>
                </a-collapse-item>
                
                <a-collapse-item header="LQA Report Finalization" key="4">
                  <div v-if="targetLanguagesList.length > 0">
                    <!-- 添加语言选择标签页 -->
                    <a-tabs v-model:activeKey="activeLanguageKeys.lqaReportFinalization" class="language-tabs">
                      <a-tab-pane v-for="lang in targetLanguagesList" :key="lang" :title="getLanguageName(lang)">
                        <a-form-item label="Assignee">
                          <a-input
                            v-model="languageAssignments.lqaReportFinalization[lang].assignee" 
                            placeholder="Report Specialist name"
                            :disabled="!isEditing"
                          />
                        </a-form-item>
                        <a-form-item label="Deadline">
                          <a-date-picker 
                            v-model="languageAssignments.lqaReportFinalization[lang].deadline" 
                            style="width: 100%;"
                            placeholder="Please select date"
                            :disabled="!isEditing"
                            value-format="YYYY-MM-DD"
                          />
                        </a-form-item>
                        <a-form-item label="Notes">
                          <a-textarea 
                            v-model="languageAssignments.lqaReportFinalization[lang].notes" 
                            placeholder="Task notes"
                            :disabled="!isEditing"
                          />
                        </a-form-item>
                      </a-tab-pane>
                    </a-tabs>
                    
                    <a-form-item label="Status">
                      <a-select v-model="project.tasks.lqaReportFinalization.status" :disabled="!isEditing">
                        <a-option value="not_started">Not Started</a-option>
                        <a-option value="in_progress">In Progress</a-option>
                        <a-option value="completed">Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="Assignee" v-if="!targetLanguagesList.length">
                      <a-input v-model="project.tasks.lqaReportFinalization.assignee" placeholder="Report Specialist" :disabled="!isEditing" />
                    </a-form-item>
                    <a-form-item label="Deadline" v-if="!targetLanguagesList.length">
                      <a-date-picker v-model="project.tasks.lqaReportFinalization.deadline" style="width: 100%;" placeholder="Please select date" :disabled="!isEditing" />
                    </a-form-item>
                    <a-form-item label="Notes" v-if="!targetLanguagesList.length">
                      <a-textarea v-model="project.tasks.lqaReportFinalization.notes" placeholder="Task notes" :disabled="!isEditing" />
                    </a-form-item>
                  </div>
                </a-collapse-item>
              </a-collapse>
            </div>
          </a-tab-pane>
          
          <!-- 新增文件管理标签页 -->
          <a-tab-pane key="files" title="Project Files">
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
              
              <!-- 上传/下载文件按钮 -->
              <div class="file-operation-buttons">
                <a-button type="primary" @click="openUploadModal" :disabled="!isEditing">
                  <template #icon><icon-upload /></template>
                  Upload Files
                </a-button>
              </div>
            </div>
          </a-tab-pane>
        </a-tabs>
        
        <div class="drawer-footer" style="margin-top: 24px; text-align: right;">
          <a-space>
            <!-- Save按钮已移除 -->
            <a-button 
              v-if="props.userRole === 'LM'" 
              type="primary" 
              status="danger" 
              @click="confirmDeleteProject"
            >
              <template #icon><icon-delete /></template>
              Delete Project
            </a-button>
          </a-space>
        </div>
      </div>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, computed, watch, nextTick } from 'vue';
import { Message, Modal } from '@arco-design/web-vue';
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
import { IconDelete } from '@arco-design/web-vue/es/icon';

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

// 添加格式化选中语言的函数
const formatSelectedLanguages = (langCodes) => {
  if (!langCodes || langCodes.length === 0) {
    return 'None';
  }
  
  // 将语言代码转换为语言名称
  return langCodes
    .map(code => {
      const lang = languages.find(l => l.code === code);
      return lang ? lang.name : code;
    })
    .join(', ');
};

const emit = defineEmits(['close', 'update', 'files-refreshed']);

// 状态
const visible = ref(false);
const drawerTitle = ref('Project Details');
const project = ref(null);
const isEditing = ref(false);
const activeTabKey = ref('info'); // 当前激活的标签页
const fileManagerRef = ref(null); // 文件管理器引用
const drawerWidth = ref(800); // 添加drawerWidth状态

// 添加每种任务类型当前选中的语言标签
const activeLanguageKeys = ref({
  translation: '',
  lqa: '',
  translationUpdate: '',
  lqaReportFinalization: ''
});

// 用于拖拽调整抽屉宽度
const isResizing = ref(false);
const minDrawerWidth = 600; // 最小宽度
const maxDrawerWidth = 1200; // 最大宽度

// 目标语言列表计算属性
const targetLanguagesList = computed(() => {
  if (!project.value || !project.value.targetLanguages) {
    return [];
  }

  try {
    // 如果目标语言是数组，直接返回有效的语言代码
    if (Array.isArray(project.value.targetLanguages)) {
      return project.value.targetLanguages.filter(Boolean);
    }

    // 如果目标语言是字符串，按逗号分割并过滤掉空值
    if (typeof project.value.targetLanguages === 'string') {
      return project.value.targetLanguages
        .split(',')
        .map(lang => lang.trim())
        .filter(Boolean);
    }

    console.warn('目标语言不是数组也不是字符串:', typeof project.value.targetLanguages);
    return [];
  } catch (error) {
    console.error('处理目标语言列表时出错:', error);
    return [];
  }
});

// 按语言分配任务的数据结构
const languageAssignments = ref({
  translation: {},
  lqa: {},
  translationUpdate: {},
  lqaReportFinalization: {}
});

// 初始化语言分配数据
const initLanguageAssignments = (languages, existingAssignments = {}) => {
  const taskTypes = ['translation', 'lqa', 'translationUpdate', 'lqaReportFinalization'];
  
  // 先确保languageAssignments各字段都初始化为对象
  taskTypes.forEach(taskType => {
    if (!languageAssignments.value[taskType]) {
      languageAssignments.value[taskType] = {};
    }
  });
  
  // 仅在有语言时才进行初始化
  if (!languages || languages.length === 0) {
    return;
  }
  
  // 为每种任务类型初始化
  taskTypes.forEach(taskType => {
    // 为每种语言初始化
    languages.forEach(lang => {
      // 如果语言代码为空，跳过
      if (!lang) return;
      
      // 如果不存在该语言的对象，创建它
      if (!languageAssignments.value[taskType][lang]) {
        languageAssignments.value[taskType][lang] = {
          assignee: '',
          deadline: null,
          notes: ''
        };
      }
      
      // 修复：检查existingAssignments[taskType]是否存在，以及language是否存在
      const existing = existingAssignments && 
                       existingAssignments[taskType] && 
                       existingAssignments[taskType][lang];
      
      if (existing) {
        languageAssignments.value[taskType][lang].assignee = existing.assignee || '';
        languageAssignments.value[taskType][lang].deadline = existing.deadline || null;
        languageAssignments.value[taskType][lang].notes = existing.notes || '';
      }
    });

    // 初始化每个任务类型的当前选中语言
    if (languages.length > 0) {
      activeLanguageKeys.value[taskType] = languages[0];
    }
  });
  
  console.log("初始化后的语言分配数据:", JSON.stringify(languageAssignments.value));
};

// 格式化语言分配数据用于提交
const formatLanguageAssignmentsForSubmit = () => {
  const result = [];
  const taskTypes = ['translation', 'lqa', 'translationUpdate', 'lqaReportFinalization'];
  
  if (!project.value || !project.value.id) return result;
  
  // 获取所有目标语言
  const allLanguages = targetLanguagesList.value;
  if (!allLanguages || allLanguages.length === 0) return result;
  
  // 确保所有目标语言和任务类型的组合都有分配记录
  ensureAllLanguageTasksInitialized(allLanguages);
  
  // 日期格式化辅助函数
  const formatDateForSubmit = (dateValue) => {
    if (!dateValue) return null;
    
    // 如果已经是标准日期字符串格式(YYYY-MM-DD)，则直接返回
    if (typeof dateValue === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateValue)) {
      return dateValue;
    }
    
    try {
      // 如果是日期对象，或其他格式的日期字符串，转换为YYYY-MM-DD格式
      const date = new Date(dateValue);
      if (isNaN(date.getTime())) {
        console.warn('无效日期值:', dateValue);
        return null;
      }
      
      // 格式化为YYYY-MM-DD
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    } catch (error) {
      console.error('格式化日期时出错:', error);
      return null;
    }
  };
  
  taskTypes.forEach(taskType => {
    if (languageAssignments.value[taskType]) {
      allLanguages.forEach(lang => {
        // 总是包含所有语言的分配，即使assignee为空
        const assignment = getLanguageAssignment(taskType, lang);
        
        // 获取deadline并格式化为YYYY-MM-DD
        let deadline = formatDateForSubmit(assignment.deadline);
        
        // 记录日期处理过程
        console.log(`处理任务分配日期: ${taskType}-${lang}, 原始值:`, assignment.deadline, '格式化后:', deadline);
        
        result.push({
          project_id: project.value.id,
          task_type: taskType,
          language: lang,
          assignee: assignment.assignee || '', // 即使为空也提交
          deadline: deadline,
          notes: assignment.notes || ''
        });
      });
    }
  });
  
  console.log('准备提交的任务分配数据:', result);
  return result;
};

// 确保所有语言的所有任务类型都被初始化
const ensureAllLanguageTasksInitialized = (languages) => {
  if (!languages || languages.length === 0) return;
  
  const taskTypes = ['translation', 'lqa', 'translationUpdate', 'lqaReportFinalization'];
  
  taskTypes.forEach(taskType => {
    if (!languageAssignments.value[taskType]) {
      languageAssignments.value[taskType] = {};
    }
    
    languages.forEach(lang => {
      if (!lang) return;
      
      if (!languageAssignments.value[taskType][lang]) {
        languageAssignments.value[taskType][lang] = {
          assignee: '',
          deadline: null,
          notes: ''
        };
      }
    });
  });
  
  console.log('已确保所有语言任务初始化:', Object.keys(languageAssignments.value.translation));
};

// 为表格获取任务分配数据
const getTaskAssignmentTableData = (taskType) => {
  if (!targetLanguagesList.value.length) {
    return [];
  }
  
  // 确保有语言分配数据
  if (!languageAssignments.value || !languageAssignments.value[taskType]) {
    return targetLanguagesList.value.map(lang => ({
      language: getLanguageName(lang),
      assignee: '未分配 / Not Assigned',
      deadline: '未设置 / Not Set',
      notes: '无 / None'
    }));
  }
  
  return targetLanguagesList.value.map(lang => {
    let assignment = { assignee: '', deadline: null, notes: '' };
    
    // 尝试获取语言分配
    if (languageAssignments.value[taskType][lang]) {
      assignment = languageAssignments.value[taskType][lang];
    }
    
    return {
      language: getLanguageName(lang),
      assignee: assignment.assignee || '未分配 / Not Assigned',
      deadline: assignment.deadline ? formatDate(assignment.deadline) : '未设置 / Not Set',
      notes: assignment.notes || '无 / None'
    };
  });
};

// 从API响应加载语言分配数据
const loadLanguageAssignmentsFromResponse = (assignments) => {
  // 初始化数据结构
  const result = {
    translation: {},
    lqa: {},
    translationUpdate: {},
    lqaReportFinalization: {}
  };
  
  // 确保assignments是数组
  if (!Array.isArray(assignments)) {
    console.warn('loadLanguageAssignmentsFromResponse: assignments不是数组', assignments);
    return result;
  }
  
  // 处理每个分配
  assignments.forEach(assignment => {
    // 确保assignment是有效对象
    if (!assignment) return;
    
    const { task_type, language, assignee, deadline, notes } = assignment;
    
    // 确保task_type和language都有效
    if (!task_type || !language) {
      console.warn('忽略无效的任务分配:', assignment);
      return;
    }
    
    if (!result[task_type]) {
      result[task_type] = {};
    }
    
    result[task_type][language] = {
      assignee: assignee || '',
      deadline: deadline ? new Date(deadline) : null,
      notes: notes || ''
    };
  });
  
  return result;
};

// 获取特定任务类型和语言的分配对象
const getLanguageAssignment = (taskType, language) => {
  // 确保参数有效
  if (!taskType || !language) {
    console.warn('getLanguageAssignment: 无效的参数', { taskType, language });
    return { assignee: '', deadline: null, notes: '' };
  }
  
  // 确保taskType有效
  if (!languageAssignments.value[taskType]) {
    languageAssignments.value[taskType] = {};
  }
  
  // 确保语言对象有效
  if (!languageAssignments.value[taskType][language]) {
    languageAssignments.value[taskType][language] = {
      assignee: '',
      deadline: null,
      notes: ''
    };
  }
  
  return languageAssignments.value[taskType][language];
};

// 加载项目任务分配
const loadProjectTaskAssignments = async (projectId) => {
  if (!projectId) return Promise.resolve([]);
  
  try {
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('未找到认证令牌，无法获取任务分配数据');
      return Promise.resolve([]);
    }
    
    // 发送请求获取任务分配数据
    const response = await axios.get(`http://localhost:5000/api/project-task-assignments/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.data && Array.isArray(response.data)) {
      // 处理响应数据
      const assignmentsData = loadLanguageAssignmentsFromResponse(response.data);
      
      // 更新语言分配数据
      languageAssignments.value = assignmentsData;
      
      console.log('已加载项目任务分配数据:', assignmentsData);
      return Promise.resolve(response.data);
    }
    
    return Promise.resolve([]);
  } catch (error) {
    console.error('获取项目任务分配数据失败:', error);
    // 确保即使API调用失败，也不会丢失本地的任务分配数据
    // 注意：这里我们返回空数组而不是拒绝Promise，避免错误传播
    return Promise.resolve([]);
  }
};

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

// 监听编辑模式和项目变化，确保所有语言的任务分配都被初始化
watch(
  [() => isEditing.value, () => project.value, () => targetLanguagesList.value], 
  ([editing, currentProject, languages]) => {
    if (editing && currentProject && languages && languages.length > 0) {
      console.log('编辑模式下检测到项目或语言变更，确保所有任务分配初始化:', languages);
      nextTick(() => {
        ensureAllLanguageTasksInitialized(languages);
      });
    }
  },
  { deep: true }
);

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
  
  let translationUpdateDeadline = null;
  if (currentProject.translationUpdateDeadline) {
    try {
      translationUpdateDeadline = new Date(currentProject.translationUpdateDeadline);
    } catch (error) {
      console.error('处理翻译更新截止日期时出错:', error);
    }
  }
  
  let lqaReportFinalizationDeadline = null;
  if (currentProject.lqaReportFinalizationDeadline) {
    try {
      lqaReportFinalizationDeadline = new Date(currentProject.lqaReportFinalizationDeadline);
    } catch (error) {
      console.error('处理LQA报告定稿截止日期时出错:', error);
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
  
  // 处理目标语言 - 确保它总是一个数组
  let targetLanguages = currentProject.targetLanguages;
  if (typeof targetLanguages === 'string') {
    targetLanguages = targetLanguages.split(',').map(lang => lang.trim()).filter(Boolean);
  } else if (!Array.isArray(targetLanguages)) {
    targetLanguages = [];
  }
  
  // 初始化任务字段
  const initTaskField = (status, assignee, deadline, notes) => {
    return {
      status: status || 'not_started',
      assignee: assignee || '',
      deadline: deadline || null,
      notes: notes || ''
    };
  };
  
  // 克隆项目数据，避免直接修改原始数据
  project.value = {
    ...currentProject,
    targetLanguages, // 使用处理后的目标语言数组
    expectedDeliveryDate,
    tasks: {
      translation: initTaskField(
        currentProject.taskTranslation,
        currentProject.translationAssignee,
        translationDeadline,
        currentProject.translationNotes
      ),
      lqa: initTaskField(
        currentProject.taskLQA,
        currentProject.lqaAssignee,
        lqaDeadline,
        currentProject.lqaNotes
      ),
      translationUpdate: initTaskField(
        currentProject.taskTranslationUpdate,
        currentProject.translationUpdateAssignee,
        translationUpdateDeadline,
        currentProject.translationUpdateNotes
      ),
      lqaReportFinalization: initTaskField(
        currentProject.taskLQAReportFinalization,
        currentProject.lqaReportFinalizationAssignee,
        lqaReportFinalizationDeadline,
        currentProject.lqaReportFinalizationNotes
      )
    },
    // 保存原始deadline值以便在其他组件中使用
    translationDeadline: currentProject.translationDeadline,
    lqaDeadline: currentProject.lqaDeadline,
    translationUpdateDeadline: currentProject.translationUpdateDeadline,
    lqaReportFinalizationDeadline: currentProject.lqaReportFinalizationDeadline
  };
  
  isEditing.value = mode === 'edit';
  drawerTitle.value = isEditing.value 
    ? `Edit Project: ${currentProject.projectName}`
    : `Project Details: ${currentProject.projectName}`;
  
  visible.value = true;
  
  // 初始化单个任务字段
  initLanguageAssignmentFields();
  
  // 在抽屉打开后延迟设置拖拽把手位置
  nextTick(() => {
    // 计算抽屉左侧边缘位置并设置把手
    const drawerLeftEdge = window.innerWidth - drawerWidth.value;
    const resizeHandle = document.querySelector('.drawer-resize-handle');
    if (resizeHandle) {
      resizeHandle.style.left = `${drawerLeftEdge}px`;
      
      // 设置指示器位置
      const indicator = resizeHandle.querySelector('.resize-indicator');
      if (indicator) {
        indicator.style.left = `${drawerLeftEdge + 3}px`;
      }
    }
  });
  
  // 根据不同场景选择初始标签页
  if (isEditing.value) {
    activeTabKey.value = 'info'; // 编辑模式下默认显示信息标签页
  } else {
    // 查看模式默认显示项目信息
    activeTabKey.value = 'info';
  }
  
  // 初始化语言分配
  console.log("目标语言处理前:", currentProject.targetLanguages);
  console.log("处理后的目标语言数组:", targetLanguages);
  
  const languages = targetLanguagesList.value;
  console.log("经过计算属性处理后的目标语言列表:", languages);
  
  // 先初始化空的分配数据，确保每种语言都有初始化的数据结构
  initLanguageAssignments(languages);
  
  // 不管是编辑模式还是查看模式，都加载项目的任务分配数据
  if (project.value && project.value.id) {
    loadProjectTaskAssignments(project.value.id)
      .then((assignments) => {
        // 确保在任务分配数据加载完成后更新UI
        if (!isEditing.value) {
          console.log('查看模式：任务分配数据已加载');
        } else {
          console.log('编辑模式：任务分配数据已加载:', assignments);
        }
        
        // 确保所有语言的所有任务类型都被正确初始化
        // 此处传入的第二个参数应该是languageAssignments.value，而不是直接使用它
        // 这里确保在API请求完成后，再次初始化所有语言
        initLanguageAssignments(languages, languageAssignments.value);
        
        // 重新初始化单个任务字段
        initLanguageAssignmentFields();
        
        // 强制更新组件以显示新的数据
        nextTick(() => {
          // 如果需要，可以在这里添加额外的UI更新逻辑
        });
      })
      .catch(error => {
        console.error('加载任务分配数据失败:', error);
        // 即使加载失败，也要确保所有语言都被初始化
        // 确保在错误情况下重新初始化语言分配
        initLanguageAssignments(languages);
        
        // 初始化单个任务字段
        initLanguageAssignmentFields();
      });
  }
  
  // 如果文件管理器引用存在，加载项目文件
  if (project.value && project.value.id && fileManagerRef.value) {
    // 在nextTick中执行，确保DOM已经更新
    nextTick(() => {
      fileManagerRef.value.loadProjectFiles(project.value.id);
    });
  }
};

// 初始化单个任务字段的方法
const initLanguageAssignmentFields = () => {
  if (!targetLanguagesList.value || targetLanguagesList.value.length === 0) {
    console.log('没有目标语言，不初始化单个任务字段');
    return;
  }
  
  // 获取第一个语言的任务分配信息作为默认值
  const firstLang = targetLanguagesList.value[0];
  
  // 翻译任务
  if (languageAssignments.value.translation && languageAssignments.value.translation[firstLang]) {
    const translationAssignment = languageAssignments.value.translation[firstLang];
    selectedTranslator.value = translationAssignment.assignee || '';
    selectedTranslationDeadline.value = translationAssignment.deadline || null;
    selectedTranslationNotes.value = translationAssignment.notes || '';
  }
  
  // LQA任务
  if (languageAssignments.value.lqa && languageAssignments.value.lqa[firstLang]) {
    const lqaAssignment = languageAssignments.value.lqa[firstLang];
    selectedLqaSpecialist.value = lqaAssignment.assignee || '';
    selectedLqaDeadline.value = lqaAssignment.deadline || null;
    selectedLqaNotes.value = lqaAssignment.notes || '';
  }
  
  // 翻译更新任务
  if (languageAssignments.value.translationUpdate && languageAssignments.value.translationUpdate[firstLang]) {
    const updateAssignment = languageAssignments.value.translationUpdate[firstLang];
    selectedUpdateSpecialist.value = updateAssignment.assignee || '';
    selectedUpdateDeadline.value = updateAssignment.deadline || null;
    selectedUpdateNotes.value = updateAssignment.notes || '';
  }
  
  // LQA报告定稿任务
  if (languageAssignments.value.lqaReportFinalization && languageAssignments.value.lqaReportFinalization[firstLang]) {
    const reportAssignment = languageAssignments.value.lqaReportFinalization[firstLang];
    selectedReportSpecialist.value = reportAssignment.assignee || '';
    selectedReportDeadline.value = reportAssignment.deadline || null;
    selectedReportNotes.value = reportAssignment.notes || '';
  }
  
  console.log('已初始化单个任务字段');
};

const closeDrawer = () => {
  visible.value = false;
  emit('close');
};

// 打开文件上传模态框
const openUploadModal = () => {
  if (!project.value || !project.value.id) {
    Message.error('Project ID does not exist, cannot upload files');
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

// 切换到文件标签页
const switchToFilesTab = () => {
  if (!project.value || !project.value.id) {
    console.warn('无法切换到文件标签页：项目不存在或没有ID');
    return;
  }
  
  console.log('切换到文件标签页');
  activeTabKey.value = 'files';
};

// 确认删除项目
const confirmDeleteProject = () => {
  if (!project.value || !project.value.id) {
    Message.error('Project does not exist or has no ID');
    return;
  }
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('Only Localization Managers can delete projects');
    return;
  }
  
  // 显示确认对话框
  Modal.warning({
    title: 'Delete Project',
    content: `Are you sure you want to delete project "${project.value.projectName}"? This action cannot be undone.`,
    okText: 'Delete',
    cancelText: 'Cancel',
    onOk: () => deleteProject()
  });
};

// 删除项目
const deleteProject = async () => {
  if (!project.value || !project.value.id) return;
  
  try {
    // 显示加载状态
    Message.loading({
      content: 'Deleting project...',
      duration: 500
    });
    
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('Authentication token not found');
      return;
    }
    
    // 发送删除请求
    const response = await axios.delete(`http://localhost:5000/api/projects/${project.value.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.status === 200) {
      Message.success('Project deleted successfully');
      visible.value = false;
      emit('update', { deleted: true, projectId: project.value.id }); // 通知父组件项目已删除
    } else {
      throw new Error('Deletion failed');
    }
  } catch (error) {
    console.error('Error deleting project:', error);
    let errorMessage = 'Failed to delete project';
    
    if (error.response) {
      if (error.response.status === 403) {
        errorMessage = 'You do not have permission to delete this project';
      } else if (error.response.status === 404) {
        errorMessage = 'Project not found';
      } else if (error.response.data && error.response.data.error) {
        errorMessage = error.response.data.error;
      }
    }
    
    Message.error(errorMessage);
  }
};

const saveProject = async () => {
  if (!project.value) return;
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('Only Localization Managers can update projects');
    return;
  }
  
  try {
    // 显示保存中状态 - 设置为0.5秒后自动消失
    Message.loading({
      content: 'Saving project...',
      duration: 500
    });
    
    // 确保所有语言的任务分配都被初始化
    ensureAllLanguageTasksInitialized(targetLanguagesList.value);
    
    // 日期格式化辅助函数
    const formatDateForSubmit = (dateValue) => {
      if (!dateValue) return null;
      
      // 如果已经是标准日期字符串格式(YYYY-MM-DD)，则直接返回
      if (typeof dateValue === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateValue)) {
        return dateValue;
      }
      
      try {
        // 如果是日期对象，或其他格式的日期字符串，转换为YYYY-MM-DD格式
        const date = new Date(dateValue);
        if (isNaN(date.getTime())) {
          console.warn('无效日期值:', dateValue);
          return null;
        }
        
        // 格式化为YYYY-MM-DD
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      } catch (error) {
        console.error('格式化日期时出错:', error);
        return null;
      }
    };
    
    // 打印关键日期，帮助调试
    console.log('保存前日期检查:', {
      expectedDeliveryDate: project.value.expectedDeliveryDate,
      translationDeadline: project.value.translationDeadline,
      lqaDeadline: project.value.lqaDeadline,
      translationUpdateDeadline: project.value.translationUpdateDeadline,
      lqaReportFinalizationDeadline: project.value.lqaReportFinalizationDeadline,
      
      taskTranslationDeadline: project.value.tasks.translation.deadline,
      taskLqaDeadline: project.value.tasks.lqa.deadline,
      taskTranslationUpdateDeadline: project.value.tasks.translationUpdate.deadline,
      taskLqaReportFinalizationDeadline: project.value.tasks.lqaReportFinalization.deadline
    });
    
    // 格式化日期为字符串 - 确保所有日期都是YYYY-MM-DD格式
    let formattedExpectedDeliveryDate = formatDateForSubmit(project.value.expectedDeliveryDate);
    
    // 格式化各个任务的截止日期
    let formattedTranslationDeadline = formatDateForSubmit(project.value.translationDeadline);
    let formattedLQADeadline = formatDateForSubmit(project.value.lqaDeadline);
    let formattedTranslationUpdateDeadline = formatDateForSubmit(project.value.translationUpdateDeadline);
    let formattedLQAReportFinalizationDeadline = formatDateForSubmit(project.value.lqaReportFinalizationDeadline);
    
    // 准备更新的项目数据
    const updatedProject = {
      id: project.value.id,
      projectName: project.value.projectName,
      status: project.value.status,
      projectStatus: project.value.status, // 保持与status同步
      requestName: project.value.requestName,
      projectManager: project.value.projectManager,
      
      // 保留创建时间字段，防止被覆盖
      createTime: project.value.createTime,
      
      // 任务状态
      taskTranslation: project.value.tasks.translation.status,
      taskLQA: project.value.tasks.lqa.status,
      taskTranslationUpdate: project.value.tasks.translationUpdate.status,
      taskLQAReportFinalization: project.value.tasks.lqaReportFinalization.status,
      
      // 任务详细信息 - 使用直接格式化的日期
      translationAssignee: project.value.tasks.translation.assignee || '',
      translationDeadline: formattedTranslationDeadline || null,
      translationNotes: project.value.tasks.translation.notes || '',
      
      lqaAssignee: project.value.tasks.lqa.assignee || '',
      lqaDeadline: formattedLQADeadline || null,
      lqaNotes: project.value.tasks.lqa.notes || '',
      
      translationUpdateAssignee: project.value.tasks.translationUpdate.assignee || '',
      translationUpdateDeadline: formattedTranslationUpdateDeadline || null,
      translationUpdateNotes: project.value.tasks.translationUpdate.notes || '',
      
      lqaReportFinalizationAssignee: project.value.tasks.lqaReportFinalization.assignee || '',
      lqaReportFinalizationDeadline: formattedLQAReportFinalizationDeadline || null,
      lqaReportFinalizationNotes: project.value.tasks.lqaReportFinalization.notes || '',
      
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
    
    // 添加按语言任务分配数据
    updatedProject.taskAssignments = formatLanguageAssignmentsForSubmit();
    
    console.log('准备更新项目数据:', updatedProject);
    
    // 发送更新请求
    const response = await axios.put(`http://localhost:5000/api/projects/${updatedProject.id}`, updatedProject);
    
    if (response.status === 200) {
      // 处理成功响应
      const successMsg = response.data.message || 'Project updated successfully';
      Message.success(successMsg);
      visible.value = false;
      emit('update', updatedProject); // 通知父组件更新成功
    } else {
      // 处理其他非错误但非200的响应
      const infoMsg = response.data.message || 'Operation completed';
      Message.info(infoMsg);
    }
  } catch (error) {
    console.error('Error updating project:', error);
    
    let errorMessage = 'Update failed';
    let errorType = 'error'; // 默认为错误
    
    if (error.response) {
      console.error('Error response:', error.response.data);
      console.error('Status code:', error.response.status);
      
      if (error.response.status === 404) {
        errorMessage = 'Project not found or no changes needed';
        errorType = 'info'; // 使用info类型而非error
        
        // 用户可能看到了过时的数据，建议刷新
        setTimeout(() => {
          Message.info('Consider refreshing to get latest data');
        }, 2000);
      } else if (error.response.status === 403) {
        errorMessage = 'You do not have permission to perform this action';
      } else if (error.response.status === 400) {
        if (error.response.data.error && error.response.data.error.includes('task assignments')) {
          errorMessage = 'Project updated but task assignments failed';
          errorType = 'warning'; // 使用警告类型
          
          // 在一段时间后仍然关闭抽屉，因为基本信息已更新成功
          setTimeout(() => {
            visible.value = false;
            emit('update', updatedProject); // 仍然通知父组件更新
          }, 3000);
        } else {
          errorMessage = error.response.data.error || errorMessage;
        }
      } else {
        errorMessage = error.response.data.error || `${errorMessage}: ${error.response.status}`;
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('No response received:', error.request);
      errorMessage = 'Cannot connect to server, please check your network';
    } else {
      // 发送请求前出错
      errorMessage = error.message || errorMessage;
    }
    
    // 根据错误类型显示不同的消息样式
    if (errorType === 'error') {
      Message.error(errorMessage);
    } else if (errorType === 'warning') {
      Message.warning(errorMessage);
    } else {
      Message.info(errorMessage);
    }
  }
};

// 开始拖拽
const startResize = (e) => {
  // 阻止默认事件
  e.preventDefault();
  
  isResizing.value = true;
  
  // 计算抽屉左侧边缘的位置(从右侧打开，所以是窗口宽度减去抽屉宽度)
  const drawerLeftEdge = window.innerWidth - drawerWidth.value;
  
  // 动态设置拖拽把手和指示器的位置
  const resizeHandle = e.currentTarget;
  resizeHandle.style.left = `${drawerLeftEdge}px`;
  
  // 获取指示器元素并设置其位置
  const indicator = resizeHandle.querySelector('.resize-indicator');
  if (indicator) {
    indicator.style.left = `${drawerLeftEdge + 3}px`;
  }
  
  // 添加鼠标移动和松开事件监听
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
  
  // 添加一个遮罩避免文本选择等问题
  const resizeMask = document.createElement('div');
  resizeMask.id = 'resize-mask';
  resizeMask.style.position = 'fixed';
  resizeMask.style.top = '0';
  resizeMask.style.left = '0';
  resizeMask.style.right = '0';
  resizeMask.style.bottom = '0';
  resizeMask.style.zIndex = '10000';
  resizeMask.style.cursor = 'col-resize';
  document.body.appendChild(resizeMask);
  
  // 更改鼠标样式
  document.body.style.cursor = 'col-resize';
};

// 处理拖拽过程
const handleResize = (e) => {
  if (!isResizing.value) return;
  
  // 计算新宽度 - 抽屉从右侧打开，所以鼠标越靠左，抽屉越宽
  const newWidth = window.innerWidth - e.clientX;
  
  // 限制在最小和最大宽度范围内
  if (newWidth >= minDrawerWidth && newWidth <= maxDrawerWidth) {
    drawerWidth.value = newWidth;
    
    // 更新拖拽把手和指示器的位置
    const drawerLeftEdge = e.clientX;
    const resizeHandle = document.querySelector('.drawer-resize-handle');
    if (resizeHandle) {
      resizeHandle.style.left = `${drawerLeftEdge}px`;
      
      // 更新指示器位置
      const indicator = resizeHandle.querySelector('.resize-indicator');
      if (indicator) {
        indicator.style.left = `${drawerLeftEdge + 3}px`;
      }
    }
  }
};

// 停止拖拽
const stopResize = () => {
  isResizing.value = false;
  
  // 移除事件监听
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  
  // 移除遮罩
  const resizeMask = document.getElementById('resize-mask');
  if (resizeMask) {
    document.body.removeChild(resizeMask);
  }
  
  // 恢复鼠标样式
  document.body.style.cursor = 'default';
};

// 监听抽屉可见性和宽度变化，更新拖拽把手位置
watch([visible, drawerWidth], ([newVisible, newWidth]) => {
  if (newVisible) {
    // 延迟执行以确保抽屉已渲染
    nextTick(() => {
      // 计算抽屉左侧边缘的位置
      const drawerLeftEdge = window.innerWidth - newWidth;
      
      // 获取拖拽把手元素
      const resizeHandle = document.querySelector('.drawer-resize-handle');
      if (resizeHandle) {
        resizeHandle.style.left = `${drawerLeftEdge}px`;
        
        // 获取指示器元素并设置其位置
        const indicator = resizeHandle.querySelector('.resize-indicator');
        if (indicator) {
          indicator.style.left = `${drawerLeftEdge + 3}px`;
        }
      }

      // 动态插入样式以确保状态标签文字为黑色
      ensureStatusTagsTextColor();
    });
  }
});

// 确保状态标签文字颜色为黑色的函数
const ensureStatusTagsTextColor = () => {
  // 查找所有抽屉内的标签
  const drawerContent = document.querySelector('.arco-drawer-content');
  if (!drawerContent) return;

  // 查找所有标签
  const tags = drawerContent.querySelectorAll('.arco-tag');
  
  // 直接修改每个标签的样式
  tags.forEach(tag => {
    tag.style.color = '#000000';
    
    // 修改所有子元素
    Array.from(tag.querySelectorAll('*')).forEach(el => {
      el.style.color = '#000000';
    });
  });

  console.log(`已将${tags.length}个标签设置为黑色文字`);
};

// 更新语言任务的处理函数
const selectedTranslator = ref('');
const selectedLqaSpecialist = ref('');
const selectedUpdateSpecialist = ref('');
const selectedReportSpecialist = ref('');

const selectedTranslationDeadline = ref(null);
const selectedLqaDeadline = ref(null);
const selectedUpdateDeadline = ref(null);
const selectedReportDeadline = ref(null);

const selectedTranslationNotes = ref('');
const selectedLqaNotes = ref('');
const selectedUpdateNotes = ref('');
const selectedReportNotes = ref('');

// 更新语言任务的截止日期
const updateLanguageDeadlines = (taskType, date) => {
  console.log(`更新${taskType}任务的截止日期:`, date);
  
  if (!date) return;
  
  // 确保有目标语言列表
  if (!targetLanguagesList.value || targetLanguagesList.value.length === 0) {
    console.warn('没有目标语言，无法更新截止日期');
    return;
  }
  
  // 同时更新项目主任务的deadline
  if (taskType === 'translation') {
    project.value.translationDeadline = date;
    // 同时更新tasks对象中的deadline，确保两处都有更新
    if (project.value.tasks && project.value.tasks.translation) {
      project.value.tasks.translation.deadline = date;
    }
  } else if (taskType === 'lqa') {
    project.value.lqaDeadline = date;
    // 同时更新tasks对象中的deadline
    if (project.value.tasks && project.value.tasks.lqa) {
      project.value.tasks.lqa.deadline = date;
    }
  } else if (taskType === 'translationUpdate') {
    project.value.translationUpdateDeadline = date;
    // 同时更新tasks对象中的deadline
    if (project.value.tasks && project.value.tasks.translationUpdate) {
      project.value.tasks.translationUpdate.deadline = date;
    }
  } else if (taskType === 'lqaReportFinalization') {
    project.value.lqaReportFinalizationDeadline = date;
    // 同时更新tasks对象中的deadline
    if (project.value.tasks && project.value.tasks.lqaReportFinalization) {
      project.value.tasks.lqaReportFinalization.deadline = date;
    }
  }
  
  // 更新每个语言的截止日期
  targetLanguagesList.value.forEach(lang => {
    // 获取语言分配对象
    const assignment = getLanguageAssignment(taskType, lang);
    if (assignment) {
      // 直接使用日期字符串，不需要再转换
      assignment.deadline = date;
    }
  });
  
  // 更新选中的日期变量
  switch (taskType) {
    case 'translation':
      selectedTranslationDeadline.value = date;
      break;
    case 'lqa':
      selectedLqaDeadline.value = date;
      break;
    case 'translationUpdate':
      selectedUpdateDeadline.value = date;
      break;
    case 'lqaReportFinalization':
      selectedReportDeadline.value = date;
      break;
  }
  
  console.log(`已更新${taskType}任务的截止日期,当前项目状态:`, project.value);
};

// 更新语言任务的分配人
const updateLanguageAssignees = (taskType, assignee) => {
  console.log(`更新${taskType}任务的分配人:`, assignee);
  
  if (assignee === undefined) return;
  
  // 确保有目标语言列表
  if (!targetLanguagesList.value || targetLanguagesList.value.length === 0) {
    console.warn('没有目标语言，无法更新分配人');
    return;
  }
  
  // 更新每个语言的分配人
  targetLanguagesList.value.forEach(lang => {
    // 获取语言分配对象
    const assignment = getLanguageAssignment(taskType, lang);
    if (assignment) {
      // 更新分配人
      assignment.assignee = assignee;
    }
  });
  
  console.log(`已更新${taskType}任务的分配人`);
};

// 更新语言任务的备注
const updateLanguageNotes = (taskType, notes) => {
  console.log(`更新${taskType}任务的备注:`, notes);
  
  if (notes === undefined) return;
  
  // 确保有目标语言列表
  if (!targetLanguagesList.value || targetLanguagesList.value.length === 0) {
    console.warn('没有目标语言，无法更新备注');
    return;
  }
  
  // 更新每个语言的备注
  targetLanguagesList.value.forEach(lang => {
    // 获取语言分配对象
    const assignment = getLanguageAssignment(taskType, lang);
    if (assignment) {
      // 更新备注
      assignment.notes = notes;
    }
  });
  
  console.log(`已更新${taskType}任务的备注`);
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

.task-details-container {
  margin-top: 16px;
}

.task-details-container h3 {
  margin-bottom: 16px;
  font-size: 18px;
  color: var(--color-text-1);
}

.task-details-container h4 {
  margin: 10px 0;
  font-size: 16px;
  color: var(--color-text-2);
}

.task-details-container .arco-collapse-item {
  margin-bottom: 16px;
}

.task-details-container .arco-table-th {
  background-color: var(--color-fill-2);
  font-weight: 600;
}

.task-details-container .arco-table-container {
  width: 100%;
  overflow-x: auto;
}

.task-details-container .arco-table-td {
  word-break: normal;
  white-space: normal;
  max-width: 200px;
}

.task-details-container .arco-descriptions-item-content {
  width: 100%;
}

/* 抽屉可调整大小样式 */
:deep(.arco-drawer-resize-trigger) {
  width: 5px;
  background-color: var(--color-fill-3);
  transition: background-color 0.2s;
}

:deep(.arco-drawer-resize-trigger:hover) {
  background-color: var(--color-primary-light-4);
  cursor: col-resize;
}

:deep(.arco-drawer-body) {
  overflow-x: hidden;
  padding: 16px;
}

/* 自定义拖拽把手 */
.drawer-resize-handle {
  position: fixed; /* 改为fixed定位，使其不随内容滚动 */
  top: 0;
  /* 把手的位置会在JavaScript中动态计算和设置 */
  width: 15px; /* 增加点击区域宽度，便于操作 */
  height: 100vh; /* 设置为视口高度，确保覆盖整个屏幕高度 */
  background-color: transparent;
  cursor: col-resize;
  z-index: 2001;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-resize-handle:hover,
.drawer-resize-handle:active {
  background-color: rgba(64, 158, 255, 0.3); /* 保持原有的悬停效果 */
}

/* 拖拽指示器 */
.resize-indicator {
  width: 6px; /* 增加宽度，使其更加明显 */
  height: 100vh; /* 设置为视口高度，确保指示器始终覆盖整个屏幕高度 */
  background-color: rgba(64, 158, 255, 0.5);
  border-radius: 3px;
  position: fixed; /* 改为fixed定位，使其不随内容滚动 */
  left: 3px;
  top: 0;
  bottom: 0;
  visibility: visible; /* 保持始终可见 */
  opacity: 0.3;
  transition: opacity 0.2s;
}

.drawer-resize-handle:hover .resize-indicator {
  opacity: 1; /* 悬停时完全不透明 */
  background-color: rgba(64, 158, 255, 0.8); /* 悬停时加深颜色 */
}

/* 调整抽屉层级确保边缘可拖拽 */
:deep(.arco-drawer) {
  overflow: visible !important;
}

/* 抽屉中状态标签文本 - 更精确的选择器 */
:deep(.arco-drawer-content) .arco-tag {
  color: #000000 !important;
}

/* 确保标签内部的所有文本元素都是黑色 */
:deep(.arco-drawer-content) .arco-tag * {
  color: #000000 !important;
}

/* 直接针对标签内部的span元素 */
:deep(.arco-drawer-content) .arco-tag span {
  color: #000000 !important;
}

/* 针对特定类型的标签 - 进行中状态 */
:deep(.arco-drawer-content) .arco-tag-blue {
  color: #000000 !important;
}

:deep(.arco-drawer-content) .arco-tag-green {
  color: #000000 !important;
}

:deep(.arco-drawer-content) .arco-tag-orange {
  color: #000000 !important;
}

:deep(.arco-drawer-content) .arco-tag-red {
  color: #000000 !important;
}

:deep(.arco-drawer-content) .arco-tag-gray {
  color: #000000 !important;
}

/* 任务状态标签文本 */
.task-details-container .arco-tag,
.task-details-container .arco-tag * {
  color: #000000 !important;
}

/* 覆盖任何可能的内联样式 */
:deep(.arco-drawer-content) [style*="color"] {
  color: #000000 !important;
}

/* 移除之前不兼容的选择器 */

/* 语言标签页样式 */
.language-tabs {
  margin-bottom: 16px;
  width: 100%;
}

:deep(.language-tabs .arco-tabs-nav-tab) {
  background-color: var(--color-fill-2);
  border-radius: 4px 4px 0 0;
  padding: 0 4px;
}

:deep(.language-tabs .arco-tabs-nav-tab .arco-tabs-tab) {
  padding: 8px 16px;
  font-size: 14px;
}

:deep(.language-tabs .arco-tabs-content) {
  padding: 16px;
  border: 1px solid var(--color-border);
  border-top: none;
  border-radius: 0 0 4px 4px;
  background-color: var(--color-bg-2);
}
</style> 