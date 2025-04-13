CREATE DATABASE IF NOT EXISTS l10n_management;

USE l10n_management;

-- 项目表
CREATE TABLE IF NOT EXISTS projectname (
  id INT AUTO_INCREMENT PRIMARY KEY,
  projectName VARCHAR(255) NOT NULL,
  projectStatus ENUM('pending', 'in_progress', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
  requestName VARCHAR(255) NOT NULL,
  projectManager VARCHAR(100) NOT NULL,
  createTime DATETIME NOT NULL,
  sourceLanguage VARCHAR(10) NOT NULL,
  targetLanguages TEXT NOT NULL,
  wordCount INT NOT NULL DEFAULT 0,
  expectedDeliveryDate DATE,
  additionalRequirements TEXT,
  taskTranslation ENUM('not_started', 'in_progress', 'completed') NOT NULL DEFAULT 'not_started',
  taskLQA ENUM('not_started', 'in_progress', 'completed') NOT NULL DEFAULT 'not_started',
  taskTranslationUpdate ENUM('not_started', 'in_progress', 'completed') NOT NULL DEFAULT 'not_started',
  taskLQAReportFinalization ENUM('not_started', 'in_progress', 'completed') NOT NULL DEFAULT 'not_started',
  created_by INT
);

-- 项目任务分配表 - 存储每个项目中特定任务和语言的分配信息
CREATE TABLE IF NOT EXISTS project_task_assignments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id INT NOT NULL,                          -- 关联的项目ID
  task_type ENUM('translation', 'lqa', 'translationUpdate', 'lqaReportFinalization') NOT NULL, -- 任务类型
  language VARCHAR(10) NOT NULL,                    -- 语言代码
  assignee VARCHAR(100) NOT NULL,                   -- 任务负责人
  deadline DATE,                                    -- 截止日期
  notes TEXT,                                       -- 备注
  createTime DATETIME NOT NULL,                     -- 创建时间
  created_by INT NOT NULL,                          -- 创建者ID
  FOREIGN KEY (project_id) REFERENCES projectname(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 创建任务分配表的索引
CREATE INDEX idx_task_assignments_project ON project_task_assignments(project_id);
CREATE INDEX idx_task_assignments_task ON project_task_assignments(task_type);
CREATE INDEX idx_task_assignments_language ON project_task_assignments(language);

-- 请求表
CREATE TABLE IF NOT EXISTS requests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  requestName VARCHAR(255) NOT NULL,
  requestBackground TEXT NOT NULL,
  sourceLanguage VARCHAR(10) NOT NULL,
  targetLanguages TEXT NOT NULL,
  wordCount INT NOT NULL DEFAULT 0,
  additionalRequirements TEXT,
  expectedDeliveryDate DATE,
  status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
  createTime DATETIME NOT NULL,
  updateTime DATETIME,
  project_id INT, -- 关联的项目ID
  created_by INT,
  FOREIGN KEY (project_id) REFERENCES projectname(id) ON DELETE SET NULL
);

-- 文件表 - 新增，用于存储所有上传的文件
CREATE TABLE IF NOT EXISTS files (
  id INT AUTO_INCREMENT PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,          -- 存储在系统中的文件名（UUID生成）
  originalName VARCHAR(255) NOT NULL,      -- 原始文件名
  fileType VARCHAR(100),                   -- 文件MIME类型
  fileSize INT,                            -- 文件大小（字节）
  filePath VARCHAR(255) NOT NULL,          -- 文件在服务器上的路径
  fileContent LONGBLOB,                    -- 文件内容（二进制）- 可选，用于小文件
  uploadTime DATETIME NOT NULL,            -- 上传时间
  uploaded_by INT NOT NULL,                -- 上传者ID
  isDeleted BOOLEAN DEFAULT FALSE,         -- 软删除标记
  FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- 项目文件表 - 修改结构，关联到文件表
CREATE TABLE IF NOT EXISTS project_files (
  id INT AUTO_INCREMENT PRIMARY KEY,
  projectId INT NOT NULL,
  fileType ENUM('source', 'translation', 'lqa', 'other') NOT NULL, -- 文件在项目中的用途类型
  notes TEXT,                             -- 文件说明/备注
  files TEXT,                             -- 文件名列表，用逗号分隔
  uploadTime DATETIME NOT NULL,           -- 关联到项目的时间
  created_by INT NOT NULL,                -- 关联人ID
  FOREIGN KEY (projectId) REFERENCES projectname(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 项目文件关联表 - 新增，用于多对多关系
CREATE TABLE IF NOT EXISTS project_file_mappings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_file_id INT NOT NULL,           -- 项目文件ID
  file_id INT NOT NULL,                   -- 文件ID
  FOREIGN KEY (project_file_id) REFERENCES project_files(id) ON DELETE CASCADE,
  FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);

-- 邮件表
CREATE TABLE IF NOT EXISTS emails (
  id INT AUTO_INCREMENT PRIMARY KEY,
  projectId INT NOT NULL,
  toRecipient VARCHAR(255) NOT NULL,
  ccRecipient TEXT,
  subject VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  sendTime DATETIME NOT NULL,
  sent_by INT NOT NULL,
  FOREIGN KEY (projectId) REFERENCES projectname(id) ON DELETE CASCADE,
  FOREIGN KEY (sent_by) REFERENCES users(id)
);

-- 邮件附件关联表 - 新增，用于关联邮件和附件
CREATE TABLE IF NOT EXISTS email_attachments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email_id INT NOT NULL,
  file_id INT NOT NULL, 
  FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE,
  FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);

-- 报价表
CREATE TABLE IF NOT EXISTS quotes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  projectId INT NOT NULL,
  lspName VARCHAR(255) NOT NULL,
  quoteAmount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',
  wordCount INT NOT NULL DEFAULT 0,
  quoteDate DATE NOT NULL,
  status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
  notes TEXT,
  createTime DATETIME NOT NULL,
  created_by INT NOT NULL,
  FOREIGN KEY (projectId) REFERENCES projectname(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 文件共享权限表 - 新增，用于精细控制文件访问权限
CREATE TABLE IF NOT EXISTS file_permissions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  file_id INT NOT NULL,
  user_id INT NOT NULL,
  can_view BOOLEAN DEFAULT TRUE,
  can_download BOOLEAN DEFAULT TRUE,
  can_edit BOOLEAN DEFAULT FALSE,
  can_delete BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 用户表 (更新为与app.py中一致的结构)
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL,
  name VARCHAR(100) NOT NULL,
  role ENUM('LM', 'BO') NOT NULL,
  email VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 聊天记录表
CREATE TABLE IF NOT EXISTS messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sender VARCHAR(50) NOT NULL,
  text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入一些示例数据
INSERT INTO users (username, password, name, role, email)
VALUES 
('admin', 'admin123', 'Admin User', 'LM', 'admin@example.com'),
('bo1', 'bo123', 'Business Owner 1', 'BO', 'bo1@example.com'),
('bo2', 'bo123', 'Business Owner 2', 'BO', 'bo2@example.com');

INSERT INTO projectname (projectName, projectStatus, requestName, projectManager, createTime, sourceLanguage, targetLanguages, wordCount, expectedDeliveryDate, taskTranslation, taskLQA, taskTranslationUpdate, taskLQAReportFinalization)
VALUES 
('产品手册翻译项目', 'in_progress', '产品手册翻译请求', 'Yizhuo Xiang', NOW(), 'en', 'zh,ja,ko', 5000, DATE_ADD(CURDATE(), INTERVAL 14 DAY), 'in_progress', 'not_started', 'not_started', 'not_started'),
('营销材料本地化', 'pending', '营销材料翻译请求', 'Yizhuo Xiang', NOW(), 'en', 'fr,de,es', 3000, DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'not_started', 'not_started', 'not_started', 'not_started'),
('软件界面翻译', 'completed', '软件界面翻译请求', 'Yizhuo Xiang', NOW(), 'en', 'zh,ru', 2000, DATE_ADD(CURDATE(), INTERVAL -7 DAY), 'completed', 'completed', 'completed', 'completed');