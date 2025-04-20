<template>
  <div class="project-management-container">
    <!-- 引入项目列表组件 -->
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

    <!-- 引入项目详情组件 -->
    <ProjectDetail 
      ref="projectDetailRef"
      :userRole="userRole" 
      :userId="userId"
      @update="handleProjectUpdated"
      @files-refreshed="handleFilesRefreshed"
    />
    
    <!-- 引入文件管理组件，将可见性设置为false，避免在页面底部显示 -->
    <FileManager 
      ref="fileManagerRef"
      :userRole="userRole"
      :userId="userId"
      :visible="false"
    />
    
    <!-- 引入邮件发送组件 -->
    <EmailSender
      ref="emailSenderRef"
      :userRole="userRole"
      @sent="handleEmailSent"
    />
                </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
// 移除 useRoute 导入，因为似乎没有正确配置Vue Router
// import { useRoute } from 'vue-router';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';

// 使用索引文件统一导入所有组件
import { ProjectList, ProjectDetail, FileManager, EmailSender } from './project';

// 用户信息和权限
const userId = ref(localStorage.getItem('userId') || null);
const userRole = ref(localStorage.getItem('userRole') || ''); // 可能的值: 'LM', 'PM', 'Translator', 'Revisor'
const projects = ref([]); // 存储项目列表

// 组件引用
const projectDetailRef = ref(null);
const fileManagerRef = ref(null);
const emailSenderRef = ref(null);

// 监听用户状态变化
watch([() => userId.value, () => userRole.value], () => {
  console.log('用户状态变化，重新加载项目数据');
  loadProjects();
});

// 初始化
onMounted(() => {
  // 只加载项目列表数据，不自动打开项目详情
  loadProjects();
  
  // 注释掉自动打开抽屉的代码
  /*
  // 获取本地存储的项目ID（如果有）
  const storedProjectId = localStorage.getItem('currentProjectId');
  
  // 首先加载所有项目数据
  loadProjects().then(() => {
    // 加载完毕后，如果有存储的项目ID，则打开项目详情
    if (storedProjectId) {
      const projectId = parseInt(storedProjectId);
      if (!isNaN(projectId)) {
        // 查找本地项目列表中是否已有此项目
        const existingProject = projects.value.find(p => p.id === projectId);
        if (existingProject) {
          // 如果已有，直接使用
          handleViewProject(existingProject);
        } else {
          // 如果没有，通过API获取
          getProjectById(projectId).then(project => {
            if (project) {
              handleViewProject(project);
            }
          }).catch(error => {
            console.error('获取项目数据失败:', error);
          });
        }
      }
    }
  });
  */
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
    Message.error('获取项目列表失败 / Failed to fetch projects');
    projects.value = [];
  }
};

// 通过ID获取项目数据
const getProjectById = async (projectId) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      Message.error('未登录或会话已过期 / Not logged in or session expired');
      return null;
    }
    
    // 设置请求头
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

// 处理查看项目
const handleViewProject = (project, options = {}) => {
  if (projectDetailRef.value) {
    if (typeof project === 'object' && project !== null) {
      projectDetailRef.value.openDrawer(project, 'view');
      // 存储当前项目ID到本地存储
      if (project.id) {
        localStorage.setItem('currentProjectId', project.id.toString());
      }
      
      // 如果需要查看文件标签页，等待抽屉打开后再切换
      if (options.showFiles) {
        setTimeout(() => {
          projectDetailRef.value.switchToFilesTab();
        }, 300);
      }
    } else if (typeof project === 'number' || (typeof project === 'object' && project.id)) {
      // 如果只有项目ID，则先获取完整的项目数据
      const projectId = typeof project === 'number' ? project : project.id;
      getProjectById(projectId).then(fullProject => {
        if (fullProject) {
          projectDetailRef.value.openDrawer(fullProject, 'view');
          localStorage.setItem('currentProjectId', projectId.toString());
          
          // 如果需要查看文件标签页，等待抽屉打开后再切换
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

// 处理编辑项目
const handleEditProject = (project) => {
  if (projectDetailRef.value) {
    if (typeof project === 'object' && project !== null) {
      projectDetailRef.value.openDrawer(project, 'edit');
      // 存储当前项目ID到本地存储
      if (project.id) {
        localStorage.setItem('currentProjectId', project.id.toString());
      }
    } else if (typeof project === 'number' || (typeof project === 'object' && project.id)) {
      // 如果只有项目ID，则先获取完整的项目数据
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

// 处理项目更新
const handleProjectUpdated = (updatedProject) => {
  Message.success('项目已更新 / Project has been updated');
  
  // 更新后立即刷新项目列表
  loadProjects().then(() => {
    // 在项目列表数据中找到并更新相应项目
    const index = projects.value.findIndex(p => p.id === updatedProject.id);
    if (index !== -1) {
      console.log('更新项目列表中的项目数据:', updatedProject);
      // 确保UI更新 - 直接修改数组中的元素
      projects.value.splice(index, 1, updatedProject);
      
      // 触发视图更新 - 创建数组的浅拷贝以确保Vue检测到变化
      projects.value = [...projects.value];
      
      console.log('通知刷新项目列表:', projects.value.length, '个项目');
    }
  });
};

// 处理发送项目邮件
const handleSendProjectEmail = (project) => {
  if (emailSenderRef.value) {
    if (typeof project === 'object' && project !== null) {
      emailSenderRef.value.openEmailModal(project);
    } else if (typeof project === 'number' || (typeof project === 'object' && project.id)) {
      // 如果只有项目ID，则先获取完整的项目数据
      const projectId = typeof project === 'number' ? project : project.id;
      getProjectById(projectId).then(fullProject => {
        if (fullProject) {
          emailSenderRef.value.openEmailModal(fullProject);
        }
      });
    }
  }
};

// 处理邮件发送完成
const handleEmailSent = (emailData) => {
  Message.success('邮件已发送 / Email has been sent');
};

// 处理文件上传
const handleUploadFiles = (project) => {
  if (!projectDetailRef.value || !fileManagerRef.value) {
    console.error('组件引用不存在，无法上传文件');
    Message.error('上传功能不可用，请刷新页面重试');
    return;
  }
  
  console.log('处理文件上传，项目:', project);
  
  // 获取项目ID
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
  
  // 首先获取完整的项目信息
  getProjectById(projectId).then(fullProject => {
    if (!fullProject) {
      console.error('获取项目详情失败');
      Message.error('获取项目详情失败，无法上传文件');
      return;
    }
    
    // 打开项目详情抽屉，并切换到文件标签页
    projectDetailRef.value.openDrawer(fullProject, 'view');
    
    // 等待抽屉打开
    setTimeout(() => {
      // 切换到文件标签页
      projectDetailRef.value.switchToFilesTab();
      
      // 再等待一段时间，确保文件标签页已加载
      setTimeout(() => {
        // 打开上传模态框
        fileManagerRef.value.openUploadModal(fullProject.id);
      }, 500);
    }, 300);
  }).catch(error => {
    console.error('获取项目详情失败:', error);
    Message.error('获取项目详情失败，无法上传文件');
  });
};

// 处理项目列表刷新
const handleProjectsRefreshed = (refreshedProjects) => {
  console.log('项目列表已刷新，获取到', refreshedProjects.length, '个项目');
  projects.value = refreshedProjects;
};

// 处理文件刷新
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
  /* 添加溢出滚动，这是唯一需要滚动的容器 */
  overflow-y: auto;
}

/* 移除其他样式，因为都已经移动到各自的组件中 */
</style>