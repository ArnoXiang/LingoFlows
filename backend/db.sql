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
  files TEXT,
  status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
  createTime DATETIME NOT NULL,
  updateTime DATETIME,
  created_by INT
);

-- 项目文件表
CREATE TABLE IF NOT EXISTS project_files (
  id INT AUTO_INCREMENT PRIMARY KEY,
  projectId INT NOT NULL,
  fileType ENUM('source', 'translation', 'lqa', 'other') NOT NULL,
  notes TEXT,
  files TEXT NOT NULL,
  uploadTime DATETIME NOT NULL,
  created_by INT,
  FOREIGN KEY (projectId) REFERENCES projectname(id) ON DELETE CASCADE
);

-- 邮件表
CREATE TABLE IF NOT EXISTS emails (
  id INT AUTO_INCREMENT PRIMARY KEY,
  projectId INT NOT NULL,
  toRecipient VARCHAR(255) NOT NULL,
  ccRecipient TEXT,
  subject VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  attachments TEXT,
  sendTime DATETIME NOT NULL,
  sent_by INT,
  FOREIGN KEY (projectId) REFERENCES projectname(id) ON DELETE CASCADE
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
  created_by INT,
  FOREIGN KEY (projectId) REFERENCES projectname(id) ON DELETE CASCADE
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
INSERT INTO projectname (projectName, projectStatus, requestName, projectManager, createTime, sourceLanguage, targetLanguages, wordCount, expectedDeliveryDate, taskTranslation, taskLQA, taskTranslationUpdate, taskLQAReportFinalization)
VALUES 
('产品手册翻译项目', 'in_progress', '产品手册翻译请求', 'Yizhuo Xiang', NOW(), 'en', 'zh,ja,ko', 5000, DATE_ADD(CURDATE(), INTERVAL 14 DAY), 'in_progress', 'not_started', 'not_started', 'not_started'),
('营销材料本地化', 'pending', '营销材料翻译请求', 'Yizhuo Xiang', NOW(), 'en', 'fr,de,es', 3000, DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'not_started', 'not_started', 'not_started', 'not_started'),
('软件界面翻译', 'completed', '软件界面翻译请求', 'Yizhuo Xiang', NOW(), 'en', 'zh,ru', 2000, DATE_ADD(CURDATE(), INTERVAL -7 DAY), 'completed', 'completed', 'completed', 'completed');

-- 更新为与app.py中一致的默认用户
INSERT INTO users (username, password, name, role, email)
VALUES 
('admin', 'admin123', 'Admin User', 'LM', 'admin@example.com'),
('bo1', 'bo123', 'Business Owner 1', 'BO', 'bo1@example.com'),
('bo2', 'bo123', 'Business Owner 2', 'BO', 'bo2@example.com');