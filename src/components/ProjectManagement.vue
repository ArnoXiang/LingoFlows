<template>
  <div class="project-management-container">
    <!-- 项目列表组件 -->
    <ProjectList 
      :userId="userId" 
      :userRole="userRole" 
      :projectData="projects"
      @view-project="handleViewProject"
      @edit-project="handleEditProject"
      @send-email="handleSendProjectEmail"
      @upload-files="handleUploadFiles"
      @refresh-projects="handleProjectsRefreshed"
    />

    <!-- 项目详情组件 -->
    <ProjectDetail 
      ref="projectDetailRef"
      :userRole="userRole" 
      :userId="userId"
      @update="handleProjectUpdated"
      @files-refreshed="handleFilesRefreshed"
    />
    
    <!-- 文件管理组件 -->
    <FileManager 
      ref="fileManagerRef"
      :userRole="userRole"
      :userId="userId"
      :visible="false"
    />
    
    <!-- 邮件发送组件 -->
    <EmailSender
      ref="emailSenderRef"
      :userRole="userRole"
      @sent="handleEmailSent"
    />
                </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';

import { ProjectList, ProjectDetail, FileManager, EmailSender } from './project';

const userId = ref(localStorage.getItem('userId') || null);
const userRole = ref(localStorage.getItem('userRole') || ''); 
const projects = ref([]); 

const projectDetailRef = ref(null);
const fileManagerRef = ref(null);
const emailSenderRef = ref(null);


watch([() => userId.value, () => userRole.value], () => {

  loadProjects();
});

// 初始化
onMounted(() => {
  loadProjects();
  
});

// 加载所有项目数据
const loadProjects = async () => {
  if (!userId.value) {
    console.log('未加载项目数据：用户ID为空');
    return;
  }
  
  try {
    // 获取存储的令牌
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('未找到令牌，无法获取项目数据');
      return;
    }
    
    // 设置请求头
    const headers = {
      'Authorization': `Bearer ${token}`
    };
    
    console.log('发送请求到 /api/projects，获取所有项目');
    const response = await axios.get('http://localhost:5000/api/projects', { headers });
    
    if (Array.isArray(response.data)) {
      console.log(`成功获取 ${response.data.length} 个项目`);
      projects.value = response.data;
    } else {
      console.error('返回的数据不是数组:', response.data);
      projects.value = [];
    }
  } catch (error) {
    console.error('获取项目数据失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.data);
      console.error('状态码:', error.response.status);
    }
    Message.error('Failed to fetch projects');
    projects.value = [];
  }
};

// 通过ID获取
const getProjectById = async (projectId) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('Not logged in or session expired');
      return null;
    }
    
    const headers = {
      'Authorization': `Bearer ${token}`
    };
    
    console.log(`正在获取项目ID ${projectId} 的详细信息`);
    const response = await axios.get(`http://localhost:5000/api/projects/${projectId}`, { headers });
    
    if (response.status === 200 && response.data) {
      console.log('获取到项目详情:', response.data);
      return response.data;
    } else {
      throw new Error('获取项目数据失败');
    }
  } catch (error) {
    console.error('获取项目数据失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.data);
      console.error('状态码:', error.response.status);
    }
    Message.error(`获取项目数据失败: ${error.message}`);
            return null;
          }
};

// 查看
const handleViewProject = (project, options = {}) => {
  if (projectDetailRef.value) {
    if (typeof project === 'object' && project !== null) {
      projectDetailRef.value.openDrawer(project, 'view');
      if (project.id) {
        localStorage.setItem('currentProjectId', project.id.toString());
      }
      
      if (options.showFiles) {
        setTimeout(() => {
          projectDetailRef.value.switchToFilesTab();
        }, 300);
      }
    } else if (typeof project === 'number' || (typeof project === 'object' && project.id)) {
      const projectId = typeof project === 'number' ? project : project.id;
      getProjectById(projectId).then(fullProject => {
        if (fullProject) {
          projectDetailRef.value.openDrawer(fullProject, 'view');
          localStorage.setItem('currentProjectId', projectId.toString());
          
          if (options.showFiles) {
            setTimeout(() => {
              projectDetailRef.value.switchToFilesTab();
            }, 300);
          }
        }
      });
    }
  }
};

// 编辑
const handleEditProject = (project) => {
  if (projectDetailRef.value) {
    if (typeof project === 'object' && project !== null) {
      projectDetailRef.value.openDrawer(project, 'edit');

      if (project.id) {
        localStorage.setItem('currentProjectId', project.id.toString());
      }
    } else if (typeof project === 'number' || (typeof project === 'object' && project.id)) {

      const projectId = typeof project === 'number' ? project : project.id;
      getProjectById(projectId).then(fullProject => {
        if (fullProject) {
          projectDetailRef.value.openDrawer(fullProject, 'edit');
          localStorage.setItem('currentProjectId', projectId.toString());
        }
      });
    }
  }
};

// 更新（删除先）
const handleProjectUpdated = (updatedProject) => {
  if (updatedProject && updatedProject.deleted) {
    Message.success('Project has been deleted');
    
    loadProjects().then(() => {
      const index = projects.value.findIndex(p => p.id === updatedProject.projectId);
      if (index !== -1) {
        console.log('从项目列表中移除已删除的项目:', updatedProject.projectId);
        // 移除
        projects.value.splice(index, 1);
        
        projects.value = [...projects.value];
        
        console.log('项目删除后刷新项目列表:', projects.value.length, '个项目');
      }
    });
    return;
  }
  
  // 正常更新
  Message.success('Project has been updated');
  
  // 更新后立即刷新
  loadProjects().then(() => {
    const index = projects.value.findIndex(p => p.id === updatedProject.id);
    if (index !== -1) {
      console.log('更新项目列表中的项目数据:', updatedProject);
      projects.value.splice(index, 1, updatedProject);
      projects.value = [...projects.value];
      
      console.log('通知刷新项目列表:', projects.value.length, '个项目');
    }
  });
};

// 发送邮件
const handleSendProjectEmail = (project) => {
  if (emailSenderRef.value) {
    if (typeof project === 'object' && project !== null) {
      emailSenderRef.value.openEmailModal(project);
    } else if (typeof project === 'number' || (typeof project === 'object' && project.id)) {
      const projectId = typeof project === 'number' ? project : project.id;
      getProjectById(projectId).then(fullProject => {
        if (fullProject) {
          emailSenderRef.value.openEmailModal(fullProject);
        }
      });
    }
  }
};

// 发送完毕
const handleEmailSent = (emailData) => {
  Message.success('Email has been sent');
};

// 文件上传
const handleUploadFiles = (project) => {
  if (!projectDetailRef.value || !fileManagerRef.value) {
    console.error('组件引用不存在，无法上传文件');
    Message.error('上传功能不可用，请刷新页面重试');
    return;
  }
  
  console.log('处理文件上传，项目:', project);
  
  // 获取ID
  let projectId;
  if (typeof project === 'object' && project !== null) {
    projectId = project.id;
  } else if (typeof project === 'number') {
    projectId = project;
  } else {
    console.error('无效的项目参数:', project);
    Message.error('无效的项目，无法上传文件');
    return;
  }
  
  if (!projectId) {
    console.error('项目ID不存在');
    Message.error('项目ID不存在，无法上传文件');
    return;
  }
  
  // 获取完整信息
  getProjectById(projectId).then(fullProject => {
    if (!fullProject) {
      console.error('获取项目详情失败');
      Message.error('获取项目详情失败，无法上传文件');
      return;
    }
    
    projectDetailRef.value.openDrawer(fullProject, 'view');
    

    setTimeout(() => {
      projectDetailRef.value.switchToFilesTab();
      setTimeout(() => {
        fileManagerRef.value.openUploadModal(fullProject.id);
      }, 500);
    }, 300);
  }).catch(error => {
    console.error('获取项目详情失败:', error);
    Message.error('获取项目详情失败，无法上传文件');
  });
};

const handleProjectsRefreshed = (refreshedProjects) => {
  console.log('项目列表已刷新，获取到', refreshedProjects.length, '个项目');
  projects.value = refreshedProjects;
};

const handleFilesRefreshed = () => {
  console.log('项目文件已刷新');
};
</script>

<style scoped>
.project-management-container {
  width: 100%;
  height: 100%;
  padding: 20px;
  background-color: var(--color-bg-2);
  overflow-y: auto;
}
</style>