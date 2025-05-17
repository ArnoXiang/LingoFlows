<template>
  <div class="file-manager-container" v-if="visible">
    <a-spin :loading="loadingFiles">
      <div v-if="projectFiles.length === 0" style="text-align: center; margin: 20px 0;">
        <p>No project files</p>
      </div>
      <div v-else>
        <div class="file-manager-toolbar">
          <a-button type="primary" @click="downloadAllFiles" :loading="downloadingFiles">
            <template #icon><icon-download /></template>
            Download All Files
          </a-button>
          <a-button type="outline" @click="refreshFiles" :loading="refreshingFiles">
            <template #icon><icon-refresh /></template>
            Refresh Files
          </a-button>
        </div>
        <a-timeline class="file-timeline">
          <a-timeline-item 
            v-for="fileGroup in projectFiles" 
            :key="fileGroup.id"
            :label="fileGroup.created_at ? new Date(fileGroup.created_at).toLocaleString() : 'Unknown Time'"
          >
            <template #dot>
              <icon-file />
            </template>
            <div class="file-group" :class="{'source-files-group': fileGroup.fileType === 'source'}">
              <div class="file-group-header">
                <h4>{{ getFileTypeText(fileGroup.fileType) }}</h4>
                <a-button 
                  type="primary" 
                  status="danger"
                  size="mini"
                  @click="confirmDeleteFileGroup(fileGroup)"
                  :loading="fileGroup.deleting"
                >
                  <template #icon><icon-delete /></template>
                  Delete Group
                </a-button>
              </div>
              <p v-if="fileGroup.description" class="file-group-description">{{ fileGroup.description }}</p>
              <a-space direction="vertical" style="width: 100%;">
                <template v-if="fileGroup.fileList && fileGroup.fileList.length > 0">
                  <a-card 
                    v-for="file in fileGroup.fileList" 
                    :key="file.id || 'unknown'"
                    hoverable
                    size="small"
                    class="file-card"
                  >
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                      <div class="file-info">
                        <span class="file-name">{{ file.name || file.filename || 'Unknown File' }}</span>
                        <div v-if="file.created_at" class="file-date">
                          {{ new Date(file.created_at).toLocaleString() }}
                        </div>
                      </div>
                      <div class="file-actions">
                        <a-button 
                          type="outline" 
                          size="mini"
                          @click="downloadFile(file.url, file.name || file.filename, file)"
                          :loading="file.downloading"
                        >
                          <template #icon><icon-download /></template>
                          Download
                        </a-button>
                        <a-button 
                          type="outline" 
                          status="danger"
                          size="mini"
                          @click="confirmDeleteFile(file, fileGroup)"
                          :loading="file.deleting"
                        >
                          <template #icon><icon-delete /></template>
                          Delete
                        </a-button>
                      </div>
                    </div>
                  </a-card>
                </template>
                <template v-else>
                  <p style="color: #999;">Empty or invalid file list</p>
                </template>
              </a-space>
            </div>
          </a-timeline-item>
        </a-timeline>
      </div>
    </a-spin>

    <!-- 上传文件对话框 -->
    <a-modal
      v-model:visible="uploadModalVisible"
      title="Upload Project Files"
      @ok="submitUploadFiles"
      @cancel="handleUploadCancel"
      :ok-loading="uploading"
    >
      <a-form :model="uploadForm">
        <a-form-item field="fileType" label="File Type" required>
          <a-select v-model="uploadForm.fileType">
            <a-option value="source">Source Files</a-option>
            <a-option value="translation">Translation Files</a-option>
            <a-option value="lqa">LQA Reports</a-option>
            <a-option value="other">Other</a-option>
          </a-select>
        </a-form-item>
        <a-form-item field="files" label="Files" required>
          <a-upload
            action="http://localhost:5000/api/upload"
            v-model:file-list="uploadedFiles"
            @change="handleFileChange"
            :headers="uploadHeaders"
            multiple
            :show-upload-button="true"
            list-type="text"
            :show-remove-button="true"
            :custom-request="customRequest"
            :limit="5"
            :tip="'Max 10MB per file'"
            :response-url-field="undefined"
          >
            <template #upload-button>
              <a-button type="primary">
                Select Files
              </a-button>
            </template>
          </a-upload>
          <div style="margin-top: 8px; color: #999;">
            Files will be automatically linked to the current project
          </div>
        </a-form-item>
        <a-form-item field="notes" label="Notes">
          <a-textarea
            v-model="uploadForm.notes"
            placeholder="File notes"
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue';
import { Message, Modal } from '@arco-design/web-vue';
import axios from 'axios';
import { IconFile, IconDownload, IconDelete, IconRefresh } from '@arco-design/web-vue/es/icon';
import { getFileTypeText } from './utils/projectUtils';

const props = defineProps({
  projectId: {
    type: Number,
    default: null
  },
  userRole: {
    type: String,
    default: ''
  },
  userId: {
    type: Number,
    default: null
  },
  visible: {
    type: Boolean,
    default: true  // 控制组件是否可见
  }
});

const emit = defineEmits(['refresh-files']);

// 状态
const projectFiles = ref([]);
const loadingFiles = ref(false);
const refreshingFiles = ref(false);
const downloadingFiles = ref(false);
const uploadModalVisible = ref(false);
const uploading = ref(false);
const uploadedFiles = ref([]);
const currentProjectId = ref(null);
const deleteModalVisible = ref(false);
const fileToDelete = ref(null);
const fileGroupToDeleteFrom = ref(null);

// 上传表单
const uploadForm = ref({
  fileType: 'source',
  notes: '',
});

// 计算属性
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`
  };
});

// 加载项目文件
const loadProjectFiles = async (projectId) => {
  if (!projectId) {
    console.error('项目ID为空，无法获取文件');
    return;
  }
  
  console.log(`开始加载项目 ${projectId} 的文件`);
  loadingFiles.value = true;
  currentProjectId.value = projectId;
  projectFiles.value = []; // 清空当前文件列表
  
  try {
    // 获取存储的令牌
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('获取项目文件失败: 未找到令牌');
      loadingFiles.value = false;
      return;
    }
    
    const headers = {
      'Authorization': `Bearer ${token}`
    };
    
    // 先尝试修复文件映射，但不阻止主流程
    try {
      console.log('尝试修复文件映射关系...');
      await fixFileMappings(true); // 静默模式
    } catch (error) {
      console.error('自动修复文件映射失败，但继续加载文件:', error);
    }
    
    // 然后获取文件
    console.log(`发送请求获取项目 ${projectId} 的文件...`);
    const response = await axios.get(`http://localhost:5000/api/project-files/${projectId}`, { headers });
    
    console.log('项目文件API返回:', response.data);
    
    if (Array.isArray(response.data)) {
      // 即使返回空数组也继续处理，确保UI正确显示
      if (response.data.length === 0) {
        console.log('项目没有关联文件，返回空数组');
        projectFiles.value = [];
        loadingFiles.value = false;
        return;
      }
      
      // 简化处理逻辑，确保所有文件组都被正确处理
      const processedData = response.data.map(fileGroup => {
        console.log('处理文件组:', fileGroup);
        
        // 基本文件组信息
        const processedFileGroup = {
          id: fileGroup.id || Math.random().toString(36).substr(2, 9),
          created_at: fileGroup.uploadTime || fileGroup.created_at || new Date().toISOString(),
          fileType: fileGroup.fileType || 'source',
          description: '',  // 初始化为空字符串
          fileList: []
        };
        
        // 设置描述文本，过滤掉自动修复相关文本
        if (fileGroup.notes) {
          const notesText = fileGroup.notes.toString();
          // 移除自动修复文本
          if (!notesText.includes('自动修复创建的文件组') && 
              !notesText.includes('Auto-fixed file group') && 
              !notesText.includes('自动修复的文件关联') && 
              !notesText.includes('Auto-fixed file association')) {
            processedFileGroup.description = notesText;
          }
        } else if (fileGroup.description) {
          const descText = fileGroup.description.toString();
          // 移除自动修复文本
          if (!descText.includes('自动修复创建的文件组') && 
              !descText.includes('Auto-fixed file group') && 
              !descText.includes('自动修复的文件关联') && 
              !descText.includes('Auto-fixed file association')) {
            processedFileGroup.description = descText;
          }
        } else {
          // 如果没有描述，使用文件类型文本
          processedFileGroup.description = getFileTypeText(fileGroup.fileType);
        }
        
        // 处理文件列表，确保能接受多种格式
        let fileList = [];
        
        // 尝试获取文件列表，支持多种格式
        if (fileGroup.fileList) {
          if (Array.isArray(fileGroup.fileList)) {
            fileList = fileGroup.fileList;
          } else if (typeof fileGroup.fileList === 'string') {
            try {
              const parsed = JSON.parse(fileGroup.fileList);
              if (Array.isArray(parsed)) {
                fileList = parsed;
              }
            } catch (e) {
              console.warn('无法解析文件列表字符串:', e);
            }
          }
        } else if (fileGroup.files) {
          // 兼容旧格式
          if (Array.isArray(fileGroup.files)) {
            fileList = fileGroup.files;
          } else if (typeof fileGroup.files === 'string') {
            try {
              const parsed = JSON.parse(fileGroup.files);
              if (Array.isArray(parsed)) {
                fileList = parsed;
              } else {
                // 可能是逗号分隔的文件名
                fileList = fileGroup.files.split(',').map(name => ({
                  name: name.trim(),
                  // 其他字段将在处理过程中添加
                }));
              }
            } catch (e) {
              // 可能是逗号分隔的文件名
              fileList = fileGroup.files.split(',').map(name => ({
                name: name.trim(),
                // 其他字段将在处理过程中添加
              }));
            }
          }
        }
        
        console.log('处理后的文件列表:', fileList);
        
        // 处理每个文件，确保字段统一
        processedFileGroup.fileList = fileList.map(file => {
          // 检查是否为有效文件对象
          if (!file || typeof file !== 'object') {
            console.warn('无效的文件对象:', file);
            return null;
          }
          
          // 确保所有必要字段
          const processedFile = {
            id: file.id || file.file_id || Math.random().toString(36).substr(2, 9),
            name: file.name || file.originalName || file.filename || 'Unknown File',
            url: file.url || file.filePath || `/api/files/${file.filename || file.id}`,
            type: file.type || file.fileType || file.mimeType || 'unknown',
            created_at: file.created_at || file.uploadTime || new Date().toISOString(),
            downloading: false
          };
          
          // 确保URL是完整的
          if (processedFile.url && !processedFile.url.startsWith('http')) {
            processedFile.url = `http://localhost:5000${processedFile.url}`;
          }
          
          return processedFile;
        }).filter(file => file !== null); // 过滤无效文件
        
        return processedFileGroup;
      });
      
      // 保留所有文件组，不再过滤，防止文件丢失
      projectFiles.value = processedData;
      console.log('最终处理的项目文件列表:', projectFiles.value);
    } else {
      console.error('返回的文件数据不是数组:', response.data);
      projectFiles.value = [];
      Message.warning('无法加载项目文件，数据格式不正确');
    }
  } catch (error) {
    console.error('获取项目文件失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.data);
      console.error('状态码:', error.response.status);
    }
    projectFiles.value = [];
    Message.error('获取项目文件失败，请检查网络连接');
  } finally {
    loadingFiles.value = false;
  }
};

// 刷新文件列表
const refreshFiles = async () => {
  if (!currentProjectId.value) {
    Message.error('Project ID does not exist, cannot refresh files');
    return;
  }
  
  refreshingFiles.value = true;
  
  try {
    await loadProjectFiles(currentProjectId.value);
    await fixFileMappings(true); // 自动修复文件映射，静默模式
    await loadProjectFiles(currentProjectId.value); // 再次加载文件以显示修复后的结果
    
    // 通知父组件文件已刷新
    emit('refresh-files');
  } catch (error) {
    console.error('刷新文件列表失败:', error);
  } finally {
    refreshingFiles.value = false;
  }
};

// 下载单个文件
const downloadFile = (url, fileName, fileObj) => {
  if (!url) {
    console.error('下载URL为空');
    Message.error('Download URL not available');
    return;
  }
  
  if (!fileName) {
    console.warn('文件名为空，使用默认文件名');
    fileName = '下载文件.txt';
  }
  
  // 如果提供了文件对象，设置下载状态
  if (fileObj) {
    fileObj.downloading = true;
  }
  
  // 创建一个下载链接
  let downloadUrl = url;
  if (!url.startsWith('http')) {
    downloadUrl = `http://localhost:5000${url}`;
  }
  const token = localStorage.getItem('token');
  
  console.log(`准备下载文件: ${fileName}, URL: ${downloadUrl}`);
  
  // 使用axios下载文件
  axios({
    url: downloadUrl,
    method: 'GET',
    responseType: 'blob',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }).then(response => {
    console.log('文件下载成功，准备创建下载链接');
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    Message.success(`File ${fileName} downloaded successfully`);
  }).catch(error => {
    console.error('Error downloading file:', error);
    
    let errorMessage = 'Failed to download file';
    if (error.response) {
      errorMessage += `: ${error.response.status} ${error.response.statusText}`;
    }
    
    Message.error(errorMessage);
  }).finally(() => {
    // 如果提供了文件对象，重置下载状态
    if (fileObj) {
      fileObj.downloading = false;
    }
  });
};

// 下载所有文件
const downloadAllFiles = async () => {
  if (!currentProjectId.value) {
    Message.error('Project ID does not exist, cannot download files');
    return;
  }
  
  if (projectFiles.value.length === 0) {
    Message.info('No files available for download');
    return;
  }
  
  downloadingFiles.value = true;
  
  try {
    // 收集当前项目所有文件的ID
    const allFileIds = [];
    
    projectFiles.value.forEach(fileGroup => {
      if (fileGroup.fileList && fileGroup.fileList.length > 0) {
        fileGroup.fileList.forEach(file => {
          if (file.id) {
            allFileIds.push(file.id);
          }
        });
      }
    });
    
    if (allFileIds.length === 0) {
      Message.info('No valid file IDs found');
      return;
    }
    
    console.log(`准备下载 ${allFileIds.length} 个项目文件`);
    
    // 构建ZIP文件名
    const zipName = `project_${currentProjectId.value}_files.zip`;
    
    // 使用axios下载ZIP文件
    const token = localStorage.getItem('token');
    
    axios({
      url: 'http://localhost:5000/api/files/download-batch',
      method: 'POST',
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        fileIds: allFileIds
      }
    }).then(response => {
      console.log('ZIP文件下载成功，准备创建下载链接');
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', zipName);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      Message.success(`Files downloaded successfully`);
    }).catch(error => {
      console.error('Error downloading files:', error);
      
      let errorMessage = 'Failed to download files';
      if (error.response) {
        errorMessage += `: ${error.response.status} ${error.response.statusText}`;
      }
      
      Message.error(errorMessage);
    }).finally(() => {
      downloadingFiles.value = false;
    });
  } catch (error) {
    console.error('批量下载文件失败:', error);
    Message.error('Failed to download files');
    downloadingFiles.value = false;
  }
};

// 自定义上传请求
const customRequest = (options) => {
  console.log('开始文件上传，options:', options);
  
  // 检查options是否存在
  if (!options) {
    console.error('错误: options为undefined');
    return;
  }
  
  // 打印详细的options结构以便调试
  console.log('上传选项完整结构:', options);
  
  // 安全获取文件对象 - Arco Design的实现可能文件在fileItem或其他字段
  const file = options.file || (options.fileItem ? options.fileItem.file : null);
  const action = options.action || 'http://localhost:5000/api/upload';
  const onProgress = options.onProgress || (() => {});
  const onSuccess = options.onSuccess || (() => {});
  const onError = options.onError || (() => {});
  
  // 如果file为null，但存在其他文件信息，尝试从其他属性提取
  if (!file && options.fileItem) {
    console.log('尝试从fileItem中提取文件信息:', options.fileItem);
  }
  
  if (!file) {
    console.error('错误: 无法找到文件对象，options:', options);
    
    // 尝试从原生DOM事件获取文件
    if (options.e && options.e.target && options.e.target.files && options.e.target.files.length > 0) {
      const domFile = options.e.target.files[0];
      console.log('从DOM事件获取文件:', domFile);
      uploadFileToServer(domFile, action, onProgress, onSuccess, onError);
      return;
    }
    
    onError(new Error('File object is missing'));
    Message.error('File object is missing, cannot upload');
    return;
  }
  
  uploadFileToServer(file, action, onProgress, onSuccess, onError);
};

// 将文件上传的核心逻辑提取到单独的函数
const uploadFileToServer = (file, action, onProgress, onSuccess, onError) => {
  if (!file.name) {
    console.error('错误: 文件名不存在', file);
    onError(new Error('File name is missing'));
    Message.error('File name is missing, cannot upload');
    return;
  }
  
  console.log('处理文件上传，文件名:', file.name, '文件类型:', file.type, '文件大小:', file.size);
  
  // 检查文件大小
  const maxFileSize = 10 * 1024 * 1024; // 10 MB
  if (file.size > maxFileSize) {
    console.error('文件太大:', file.size, '最大允许:', maxFileSize);
    onError(new Error(`File too large, max 10MB allowed`));
    Message.error(`File too large, max 10MB allowed`);
    return;
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  // 获取token
  const token = localStorage.getItem('token');
  if (!token) {
    console.error('未找到认证令牌');
    onError(new Error('Authentication token not found, please login again'));
    Message.error('Authentication token not found, please login again');
    return;
  }
  
  console.log(`开始上传文件 ${file.name} 到 ${action}`);
  
  // 使用axios执行上传，便于处理进度
  axios.post(action, formData, {
    headers: {
      'Authorization': `Bearer ${token}`
      // 不要设置Content-Type，让axios自动设置multipart/form-data和boundary
    },
    onUploadProgress: progressEvent => {
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      console.log(`上传进度: ${percentCompleted}%`);
      onProgress({ percent: percentCompleted });
    }
  })
  .then(response => {
    console.log('上传成功，服务器响应数据:', response.data);
    
    // 处理文件上传成功后，直接修改当前文件的状态
    if (response.data) {
      const fileId = response.data.file_id || response.data.id;
      console.log('从响应中提取的文件ID:', fileId);
      
      // 构建完整的响应对象
      const responseObj = {
        ...response.data,
        status: 'done',
        file_id: fileId,
        id: fileId,
        name: response.data.originalName || response.data.filename || file.name,
        url: response.data.url || `/api/files/${response.data.filename || fileId}`
      };
      
      console.log('构建的响应对象:', responseObj);
      
      // 调用成功回调
      onSuccess(responseObj);
      
      // 手动添加到上传文件列表
      addToUploadedFiles({
        ...responseObj,
        uid: responseObj.id || new Date().getTime(),
        status: 'done'
      });
      
      Message.success(`File ${file.name} uploaded successfully`);
    } else {
      // 没有接收到有效的响应数据
      console.error('上传响应数据无效:', response.data);
      onError(new Error('Invalid server response'));
      Message.error('Invalid server response');
    }
  })
  .catch(error => {
    console.error('上传失败:', error);
    
    let errorMessage = 'Upload failed';
    if (error.response) {
      console.error('错误响应:', error.response.data);
      errorMessage += `: ${error.response.status} ${error.response.statusText || ''}`;
      if (error.response.data && error.response.data.error) {
        errorMessage += ` - ${error.response.data.error}`;
      }
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    
    onError(new Error(errorMessage));
    Message.error(errorMessage);
  });
};

// 辅助函数：手动添加文件到上传列表
const addToUploadedFiles = (file) => {
  if (!file) return;
  
  console.log('手动添加文件到上传列表:', file);
  
  // 确保uploadedFiles是数组
  if (!Array.isArray(uploadedFiles.value)) {
    uploadedFiles.value = [];
  }
  
  // 检查文件是否已存在于列表中
  const fileIndex = uploadedFiles.value.findIndex(f => 
    f && ((f.uid === file.uid) || (f.name === file.name))
  );
  
  if (fileIndex !== -1) {
    // 更新已存在的文件
    console.log('更新已存在的文件:', file.name);
    const updatedFiles = [...uploadedFiles.value];
    updatedFiles[fileIndex] = {
      ...updatedFiles[fileIndex],
      ...file
    };
    uploadedFiles.value = updatedFiles;
  } else {
    // 添加新文件
    console.log('添加新文件:', file.name);
    uploadedFiles.value = [...uploadedFiles.value, file];
  }
  
  console.log('更新后的上传文件列表:', uploadedFiles.value);
};

// 处理文件上传变化 - 完全重写，适应Arco Design组件的行为
const handleFileChange = (info) => {
  console.log('文件上传变化:', info);
  
  // Arco Design可能将info直接作为fileList传递
  if (Array.isArray(info)) {
    console.log('直接接收到fileList数组');
    processFileList(info);
    return;
  }
  
  // 标准情况，info是对象且包含fileList
  if (info && info.fileList) {
    console.log('从info中提取fileList');
    processFileList(info.fileList);
    return;
  }
  
  // 处理单个文件的情况
  if (info && info.file) {
    console.log('处理单个文件变化:', info.file);
    processFile(info.file);
    return;
  }
  
  console.error('无法识别的文件变化事件格式:', info);
};

// 处理文件列表
const processFileList = (fileList) => {
  if (!Array.isArray(fileList)) {
    console.error('fileList不是数组:', fileList);
    return;
  }
  
  console.log(`处理${fileList.length}个文件`);
  
  // 创建一个新数组来存储处理后的文件
  const processedFiles = [];
  
  // 处理每个文件
  fileList.forEach(file => {
    if (!file) return;
    
    // 处理文件并添加到处理后的数组
    processedFiles.push(processFile(file, false)); // false表示不更新uploadedFiles
  });
  
  // 更新uploadedFiles
  console.log('设置处理后的文件列表:', processedFiles);
  uploadedFiles.value = processedFiles.filter(Boolean); // 过滤掉null/undefined
};

// 处理单个文件
const processFile = (file, updateList = true) => {
  if (!file) return null;
  
  const fileName = file.name || 'Unknown File';
  console.log('处理文件:', fileName, '状态:', file.status);
  
  // 创建一个新的文件对象
  const processedFile = { ...file };
  
  // 如果文件有响应，处理响应数据
  if (file.response) {
    try {
      // 提取文件ID
      let fileId = null;
      
      if (typeof file.response === 'object' && file.response !== null) {
        fileId = file.response.file_id || file.response.id;
        console.log('从对象响应提取ID:', fileId);
      } else if (typeof file.response === 'string') {
        try {
          const respObj = JSON.parse(file.response);
          fileId = respObj.file_id || respObj.id;
          console.log('从字符串响应提取ID:', fileId);
        } catch (e) {
          console.warn('无法解析响应为JSON:', file.response);
        }
      }
      
      // 设置文件ID
      if (fileId) {
        processedFile.file_id = fileId;
        processedFile.id = fileId;
      }
    } catch (error) {
      console.error('处理文件响应出错:', error);
    }
  }
  
  // 对不同的文件状态进行处理
  if (file.status === 'done') {
    console.log('文件上传完成:', fileName);
  } else if (file.status === 'error') {
    console.error('文件上传失败:', fileName);
    Message.error(`File ${fileName} uploaded failed`);
  } else if (file.status === 'uploading') {
    console.log('文件上传中:', fileName, `${file.percent || 0}%`);
  }
  
  // 如果需要更新列表，则更新
  if (updateList) {
    addToUploadedFiles(processedFile);
  }
  
  return processedFile;
};

// 提交文件上传 - 进一步改进错误处理和文件状态检查
const submitUploadFiles = async () => {
  if (!currentProjectId.value) {
    Message.error('Project ID does not exist, cannot upload files');
    return;
  }
  
  if (!uploadedFiles.value || uploadedFiles.value.length === 0) {
    Message.error('Please upload at least one file');
    return;
  }
  
  try {
    uploading.value = true;
    console.log('开始提交项目文件，项目ID:', currentProjectId.value);
    console.log('上传的文件列表:', uploadedFiles.value);
    
    // 安全检查：确保是数组
    if (!Array.isArray(uploadedFiles.value)) {
      throw new Error('Uploaded files list is not an array');
    }
    
    // 获取已上传文件的ID
    const uploadedFileIds = [];
    const fileErrors = [];
    
    // 遍历每个文件，提取文件ID
    uploadedFiles.value.forEach((file, index) => {
      if (!file) {
        console.warn(`跳过索引${index}处的无效文件`);
        return;
      }
      
      const fileName = file.name || `Unknown File-${index}`;
      console.log('检查上传文件:', fileName, '状态:', file.status);
      
      // 检查文件上传状态
      if (file.status === 'error') {
        const errorMsg = `File ${fileName} uploaded failed, cannot continue processing`;
        console.warn(errorMsg);
        fileErrors.push(errorMsg);
        return; // 跳过失败的文件
      }
      
      if (!file.status || file.status !== 'done') {
        const errorMsg = `File ${fileName} uploaded not completed, status: ${file.status || 'unknown'}`;
        console.warn(errorMsg);
        fileErrors.push(errorMsg);
        return; // 跳过未完成的文件
      }
      
      // 提取文件ID
      let fileId = null;
      
      // 从文件对象中提取ID的多种方式
      if (file.file_id) fileId = file.file_id;
      else if (file.id) fileId = file.id;
      else if (file.response) {
        if (typeof file.response === 'object' && file.response !== null) {
          fileId = file.response.file_id || file.response.id;
        } else if (typeof file.response === 'string') {
          try {
            const respObj = JSON.parse(file.response);
            fileId = respObj.file_id || respObj.id;
          } catch (e) {
            console.warn('无法解析响应JSON:', e);
          }
        }
      }
      
      if (fileId) {
        console.log('找到文件ID:', fileId, '文件名:', fileName);
        uploadedFileIds.push(fileId);
      } else {
        console.warn('无法找到文件ID，使用文件名关联:', fileName);
        fileErrors.push(`Cannot find ID for file ${fileName}`);
        // 检查是否可以使用文件名关联
        if (file.status === 'done' && fileName) {
          uploadedFileIds.push({ filename: fileName });
        }
      }
    });
    
    // 如果没有成功上传的文件ID，则报错
    if (uploadedFileIds.length === 0) {
      if (fileErrors.length > 0) {
        throw new Error(`File upload problem: ${fileErrors.join('; ')}`);
      } else {
        throw new Error('No successfully uploaded file IDs');
      }
    }
    
    console.log('准备关联到项目的文件IDs:', uploadedFileIds);
    
    // 准备项目文件数据
    const projectFileData = {
      projectId: currentProjectId.value,
      fileType: uploadForm.value.fileType,
      notes: uploadForm.value.notes || '',
      fileIds: uploadedFileIds
    };
    
    console.log('发送创建项目文件请求:', projectFileData);
    
    // 发送项目文件请求
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Token does not exist, please login again');
    }
    
    try {
      const response = await axios.post('http://localhost:5000/api/project-files', projectFileData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('创建项目文件响应:', response.data);
      
      Message.success('Project files uploaded successfully');
      uploadModalVisible.value = false;
      uploadedFiles.value = []; // 清空已上传文件列表
      
      // 刷新项目文件列表
      try {
        // 等待一段时间，确保后端处理完成
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // 再次执行文件映射修复
        await fixFileMappings(true); // 静默模式
        
        // 等待映射完成
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 加载最新的项目文件
        await loadProjectFiles(currentProjectId.value);
        
        // 通知父组件文件已更新
        emit('refresh-files');
      } catch (refreshError) {
        console.error('刷新文件列表失败:', refreshError);
        // 不影响主流程，继续完成上传
      }
    } catch (error) {
      console.error('创建项目文件失败:', error);
      let errorMessage = 'Failed to create project files';
      
      if (error.response) {
        console.error('服务器响应:', error.response.data);
        console.error('状态码:', error.response.status);
        
        errorMessage += `: ${error.response.status}`;
        if (error.response.data && error.response.data.error) {
          errorMessage += ` - ${error.response.data.error}`;
        }
      } else if (error.message) {
        errorMessage += `: ${error.message}`;
      }
      
      throw new Error(errorMessage);
    }
  } catch (error) {
    console.error('上传项目文件失败:', error);
    Message.error(error.message || 'Upload failed');
  } finally {
    uploading.value = false;
  }
};

// 修复文件映射关系
const fixFileMappings = async (silentMode = false) => {
  try {
    console.log('正在修复文件映射关系...');
    
    const token = localStorage.getItem('token');
    if (!token) {
      if (!silentMode) {
        Message.error('Please login first');
      }
      return;
    }
    
    // 添加重试机制
    let retries = 0;
    const maxRetries = 2;
    let success = false;
    let response;
    
    while (!success && retries <= maxRetries) {
      try {
        if (retries > 0) {
          console.log(`尝试第 ${retries} 次重试修复...`);
        }
        
        // 如果有当前项目ID，提供给后端进行优先修复
        const requestData = {};
        if (currentProjectId.value) {
          requestData.projectId = currentProjectId.value;
          console.log(`优先修复项目ID ${currentProjectId.value} 的文件映射`);
        }
        
        response = await axios.post('http://localhost:5000/api/fix-file-mappings', requestData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          timeout: 30000 // 30秒超时
        });
        
        success = true;
      } catch (error) {
        retries++;
        console.error(`修复尝试 ${retries} 失败:`, error);
        
        if (retries > maxRetries) {
          throw error; // 重试次数用完，抛出错误
        }
        
        // 等待1秒后重试
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    console.log('修复结果:', response.data);
    
    if (response.data.status === 'success') {
      const newMappings = response.data.after_count - response.data.before_count;
      
      if (!silentMode && newMappings > 0) {
        Message.success({
          content: `File mappings fixed! Added ${newMappings} mappings`,
          duration: 3000
        });
      }
      
      // 如果当前有项目ID，完成修复后重新加载该项目的文件
      if (currentProjectId.value && newMappings > 0 && !silentMode) {
        console.log(`修复成功，重新加载项目 ${currentProjectId.value} 的文件`);
        await loadProjectFiles(currentProjectId.value);
      }
    }
  } catch (error) {
    console.error('修复文件映射失败:', error);
    
    if (!silentMode) {
      let errorMessage = 'Failed to fix file mappings';
      if (error.response) {
        errorMessage += `: ${error.response.data?.error || error.response.statusText}`;
      } else if (error.message) {
        errorMessage += `: ${error.message}`;
      }
      
      Message.error({
        content: errorMessage,
        duration: 5000
      });
    }
  }
};

// 打开上传文件对话框
const openUploadModal = (projectIdOrProject) => {
  // 处理不同类型的参数
  let projectId;
  
  if (typeof projectIdOrProject === 'number') {
    projectId = projectIdOrProject;
  } else if (typeof projectIdOrProject === 'object' && projectIdOrProject !== null) {
    projectId = projectIdOrProject.id;
  } else {
    console.error('无效的项目ID或项目对象:', projectIdOrProject);
    Message.error('Invalid project ID, cannot upload files');
    return;
  }
  
  if (!projectId) {
    Message.error('Project ID is empty, cannot upload files');
    return;
  }
  
  // 重置表单
  uploadForm.value.fileType = 'source';
  uploadForm.value.notes = '';
  uploadedFiles.value = [];
  currentProjectId.value = projectId;
  uploadModalVisible.value = true;
  
  console.log(`打开项目 ${projectId} 的文件上传对话框`);
};

// 关闭上传对话框
const handleUploadCancel = () => {
  uploadModalVisible.value = false;
  uploading.value = false;
};

// 确认删除文件
const confirmDeleteFile = (file, fileGroup) => {
  fileToDelete.value = file;
  fileGroupToDeleteFrom.value = fileGroup;
  
  Modal.warning({
    title: 'Confirm File Deletion',
    content: `Are you sure you want to delete the file "${file.name || file.filename || 'Unknown File'}"? This action cannot be undone.`,
    okText: 'Delete',
    cancelText: 'Cancel',
    onOk: () => deleteFile(file, fileGroup)
  });
};

// 删除文件
const deleteFile = async (file, fileGroup) => {
  if (!file || !file.id) {
    Message.error('File ID does not exist, cannot delete');
    return;
  }
  
  try {
    // 设置文件删除状态
    file.deleting = true;
    
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Authentication token not found, please login again');
    }
    
    console.log(`开始删除文件，ID: ${file.id}, 名称: ${file.name || file.filename}`);
    
    // 调用删除API
    await axios.delete(`http://localhost:5000/api/files/${file.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    // 从UI中移除文件
    if (fileGroup && fileGroup.fileList) {
      const fileIndex = fileGroup.fileList.findIndex(f => f.id === file.id);
      if (fileIndex !== -1) {
        fileGroup.fileList.splice(fileIndex, 1);
        
        // 如果文件组中没有文件了，也可以考虑移除整个文件组
        if (fileGroup.fileList.length === 0) {
          const groupIndex = projectFiles.value.findIndex(g => g.id === fileGroup.id);
          if (groupIndex !== -1) {
            projectFiles.value.splice(groupIndex, 1);
          }
        }
      }
    }
    
    Message.success(`File ${file.name || file.filename} deleted successfully`);
    
    // 通知父组件文件已更新
    emit('refresh-files');
  } catch (error) {
    console.error('删除文件失败:', error);
    
    let errorMessage = 'Failed to delete file';
    if (error.response) {
      const status = error.response.status;
      if (status === 403) {
        errorMessage = 'You do not have permission to delete this file';
      } else if (status === 404) {
        errorMessage = 'File does not exist or has been deleted';
      } else if (error.response.data && error.response.data.error) {
        errorMessage += `: ${error.response.data.error}`;
      }
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    
    Message.error(errorMessage);
  } finally {
    // 重置文件删除状态
    if (file) {
      file.deleting = false;
    }
  }
};

// 确认删除文件组
const confirmDeleteFileGroup = (fileGroup) => {
  if (!fileGroup || !fileGroup.id) {
    Message.error('File group ID does not exist, cannot delete');
    return;
  }
  
  if (!fileGroup.fileList || fileGroup.fileList.length === 0) {
    Message.warning('File group is empty, no need to delete');
    return;
  }
  
  Modal.warning({
    title: 'Confirm File Group Deletion',
    content: `Are you sure you want to delete this file group? This will delete all files in the group. This action cannot be undone.`,
    okText: 'Delete',
    cancelText: 'Cancel',
    onOk: () => deleteFileGroup(fileGroup)
  });
};

// 删除整个文件组
const deleteFileGroup = async (fileGroup) => {
  if (!fileGroup || !fileGroup.id || !fileGroup.fileList) {
    Message.error('Invalid file group, cannot delete');
    return;
  }
  
  try {
    // 设置文件组删除状态
    fileGroup.deleting = true;
    
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Authentication token not found, please login again');
    }
    
    console.log(`开始删除文件组，ID: ${fileGroup.id}, 包含 ${fileGroup.fileList.length} 个文件`);
    
    // 获取所有文件ID
    const fileIds = fileGroup.fileList.map(file => file.id).filter(Boolean);
    
    if (fileIds.length === 0) {
      throw new Error('No valid file IDs found');
    }
    
    // 批量删除文件
    await axios.post('http://localhost:5000/api/files/delete-batch', 
      { fileIds },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    // 从UI中移除文件组
    const groupIndex = projectFiles.value.findIndex(g => g.id === fileGroup.id);
    if (groupIndex !== -1) {
      projectFiles.value.splice(groupIndex, 1);
    }
    
    Message.success(`File group deleted successfully, total ${fileIds.length} files`);
    
    // 通知父组件文件已更新
    emit('refresh-files');
  } catch (error) {
    console.error('删除文件组失败:', error);
    
    let errorMessage = 'Failed to delete file group';
    if (error.response) {
      if (error.response.data && error.response.data.error) {
        errorMessage += `: ${error.response.data.error}`;
      }
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    
    Message.error(errorMessage);
  } finally {
    // 重置文件组删除状态
    if (fileGroup) {
      fileGroup.deleting = false;
    }
  }
};

// 暴露方法给父组件
defineExpose({
  loadProjectFiles,
  openUploadModal,
  refreshFiles,
  // 添加兼容方法
  showProjectFiles: (project) => {
    if (project && project.id) {
      loadProjectFiles(project.id);
      // 不需要设置tabActiveKey和visible，因为这些变量不存在
      // 在这种情况下，只加载文件，用户可以通过其他按钮查看
    }
  }
});
</script>

<style scoped>
.file-manager-container {
  width: 100%;
}

.file-manager-toolbar {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-timeline {
  margin-bottom: 16px;
}

.file-group {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 6px;
  background-color: var(--color-bg-2);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.source-files-group {
  background-color: #f5f5f5;
}

.file-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border-2);
}

.file-group-description {
  margin-bottom: 12px;
  color: var(--color-text-3);
  font-size: 14px;
}

.file-card {
  margin-bottom: 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.file-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.file-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.file-date {
  font-size: 12px;
  color: var(--color-text-3);
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 文件卡片样式 */
:deep(.arco-card) {
  transition: all 0.3s ease;
}

:deep(.arco-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 文件删除和添加的过渡动画 */
.file-list-enter-active,
.file-list-leave-active {
  transition: all 0.5s ease;
}

.file-list-enter-from,
.file-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 