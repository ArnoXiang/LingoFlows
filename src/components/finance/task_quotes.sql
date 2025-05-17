-- 项目任务报价表 - 存储特定项目任务和语言的报价信息
CREATE TABLE IF NOT EXISTS task_quotes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  projectId INT NOT NULL,                                             -- 关联的项目ID
  task ENUM('translation', 'lqa', 'translationUpdate', 'lqaReportFinalization') NOT NULL, -- 任务类型
  assignee VARCHAR(100) NOT NULL,                                     -- 任务负责人
  language VARCHAR(10) NOT NULL,                                      -- 语言代码
  quoteAmount DECIMAL(10, 2) NOT NULL,                                -- 报价金额
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',                         -- 货币代码
  wordCount INT NOT NULL DEFAULT 0,                                   -- 字数
  unitPrice DECIMAL(10, 4),                                           -- 单价(每词/每字)
  deadline DATE,                                                      -- 截止日期
  notes TEXT,                                                         -- 备注
  fileId INT,                                                         -- 关联的报价文件ID
  extractedInfo TEXT,                                                 -- 从Excel提取的特定列数据(JSON格式)
  status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending', -- 报价状态
  createTime DATETIME NOT NULL,                                       -- 创建时间
  created_by INT NOT NULL,                                            -- 创建者ID
  FOREIGN KEY (projectId) REFERENCES projectname(id) ON DELETE CASCADE,
  FOREIGN KEY (fileId) REFERENCES files(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 创建索引
CREATE INDEX idx_task_quotes_project ON task_quotes(projectId);
CREATE INDEX idx_task_quotes_language ON task_quotes(language);
CREATE INDEX idx_task_quotes_task ON task_quotes(task);
CREATE INDEX idx_task_quotes_status ON task_quotes(status);

-- 示例数据
INSERT INTO task_quotes (
  projectId, task, assignee, language, quoteAmount, currency, 
  wordCount, unitPrice, deadline, notes, status, createTime, created_by
) VALUES 
(1, 'translation', 'Translation Agency A', 'zh', 1250.00, 'USD', 5000, 0.25, DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Standard translation service', 'approved', NOW(), 1),
(1, 'lqa', 'LQA Vendor B', 'zh', 500.00, 'USD', 5000, 0.10, DATE_ADD(CURDATE(), INTERVAL 15 DAY), 'Full LQA review', 'pending', NOW(), 1),
(2, 'translation', 'Translation Agency C', 'fr', 750.00, 'EUR', 3000, 0.25, DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'Marketing content translation', 'pending', NOW(), 1),
(3, 'translation', 'Translation Agency A', 'ru', 500.00, 'USD', 2000, 0.25, DATE_ADD(CURDATE(), INTERVAL -5 DAY), 'UI translation complete', 'approved', NOW(), 1);

-- 创建视图，用于查询报价详情
CREATE OR REPLACE VIEW task_quotes_view AS
SELECT 
  tq.*,
  p.projectName,
  p.projectStatus,
  p.requestName,
  p.projectManager,
  f.originalName as fileName
FROM task_quotes tq
JOIN projectname p ON tq.projectId = p.id
LEFT JOIN files f ON tq.fileId = f.id; 