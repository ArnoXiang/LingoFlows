# LingoFlows 数据库结构

## 数据库概述

LingoFlows 使用关系型数据库设计，包含用户管理、项目管理、文件管理、通信管理、财务管理等多个模块。数据库名称为 `l10n_management`。

```
┌─────────────────────┐       ┌───────────────────────────┐       ┌─────────────────────┐                               
│       users         │       │        projectname        │       │      requests       │
├─────────────────────┤       ├───────────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)                   │       │ id (PK)             │
│ username            │◄──────┤ created_by (FK)           │◄──────┤ project_id (FK)     │
│ password            │       │ projectName               │       │ requestName         │
│ name                │       │ projectStatus             │       │ requestBackground   │
│ role                │       │ requestName               │       │ sourceLanguage      │
│ email               │       │ projectManager            │       │ targetLanguages     │
│ created_at          │       │ createTime                │       │ wordCount           │
└─────────────────────┘       │ sourceLanguage            │       │ additionalRequirements│
          ▲                   │ targetLanguages           │       │ expectedDeliveryDate│
          │                   │ wordCount                 │       │ createTime          │
          │                   │ expectedDeliveryDate      │       │ updateTime          │
          │                   │ additionalRequirements    │       │ created_by (FK)     │
          │                   │ taskTranslation           │       │ taskLQA             │
          │                   │ taskTranslationUpdate     │       │ taskTranslationUpdate│
          │                   │ taskLQAReportFinalization │       │ taskLQAReportFinalization│
          │                   └───────────────────────────┘       └─────────────────────┘
          │                               ▲
          │                               │
          │                               │
┌─────────────────────┐       ┌───────────────────────────┐
│   file_permissions  │       │  project_task_assignments │
├─────────────────────┤       ├───────────────────────────┤
│ id (PK)             │       │ id (PK)                   │
│ file_id (FK)        │       │ project_id (FK)           │
│ user_id (FK)        │       │ task_type                 │
│ can_view            │       │ language                  │
│ can_download        │       │ assignee                  │
│ can_edit            │       │ deadline                  │
│ can_delete          │       │ notes                     │
└─────────────────────┘       │ createTime                │
                              │ created_by (FK)           │
                              └───────────────────────────┘
                                                
┌─────────────────────┐       ┌───────────────────────────┐       ┌─────────────────────┐
│       files         │       │      project_files        │       │project_file_mappings│
├─────────────────────┤       ├───────────────────────────┤       ├─────────────────────┤
│ id (PK)             │◄──────┤ id (PK)                   │◄──────┤ id (PK)             │
│ filename            │       │ projectId (FK)            │       │ project_file_id (FK)│
│ originalName        │       │ fileType                  │       │ file_id (FK)        │
│ fileType            │       │ notes                     │       └─────────────────────┘
│ fileSize            │       │ files                     │
│ filePath            │       │ uploadTime                │
│ fileContent         │       │ created_by (FK)           │
│ uploadTime          │       └───────────────────────────┘
│ uploaded_by (FK)    │
│ isDeleted           │
└─────────────────────┘
          ▲
          │
          │
┌─────────────────────┐       ┌───────────────────────────┐
│   email_attachments │       │         emails            │
├─────────────────────┤       ├───────────────────────────┤
│ id (PK)             │       │ id (PK)                   │
│ email_id (FK)       │◄──────┤ projectId (FK)            │
│ file_id (FK)        │       │ toRecipient               │
└─────────────────────┘       │ ccRecipient               │
                              │ subject                   │
                              │ content                   │
                              │ sendTime                  │
                              │ sent_by (FK)              │
                              └───────────────────────────┘

┌─────────────────────┐       ┌───────────────────────────┐
│      quotes         │       │        messages           │
├─────────────────────┤       ├───────────────────────────┤
│ id (PK)             │       │ id (PK)                   │
│ projectId (FK)      │       │ sender                    │
│ lspName             │       │ text                      │
│ quoteAmount         │       │ created_at                │
│ currency            │       └───────────────────────────┘
│ wordCount           │
│ quoteDate           │
│ status              │
│ notes               │
│ createTime          │
│ created_by (FK)     │
└─────────────────────┘
```

## 详细表结构

### 1. 用户管理
- **users**: 存储系统用户信息
  - `id`: 主键
  - `username`: 用户名(唯一)
  - `password`: 密码
  - `name`: 姓名
  - `role`: 角色(LM - 本地化管理员, BO - 业务拥有者)
  - `email`: 电子邮件
  - `created_at`: 创建时间

### 2. 项目管理
- **projectname**: 存储项目基本信息
  - `id`: 主键
  - `projectName`: 项目名称
  - `projectStatus`: 项目状态(pending, in_progress, completed, cancelled)
  - `requestName`: 关联请求名称
  - `projectManager`: 项目经理
  - `createTime`: 创建时间
  - `sourceLanguage`: 源语言
  - `targetLanguages`: 目标语言(逗号分隔)
  - `wordCount`: 字数统计
  - `expectedDeliveryDate`: 预期交付日期
  - `additionalRequirements`: 额外需求
  - `taskTranslation`, `taskLQA`, `taskTranslationUpdate`, `taskLQAReportFinalization`: 各任务类型状态
  - `created_by`: 创建者ID(外键)

- **project_task_assignments**: 项目任务分配表
  - `id`: 主键
  - `project_id`: 项目ID(外键)
  - `task_type`: 任务类型(translation, lqa, translationUpdate, lqaReportFinalization)
  - `language`: 语言代码
  - `assignee`: 任务负责人
  - `deadline`: 截止日期
  - `notes`: 备注
  - `createTime`: 创建时间
  - `created_by`: 创建者ID(外键)

### 3. 请求管理
- **requests**: 存储翻译请求信息
  - `id`: 主键
  - `requestName`: 请求名称
  - `requestBackground`: 请求背景
  - `sourceLanguage`: 源语言
  - `targetLanguages`: 目标语言(逗号分隔)
  - `wordCount`: 字数统计
  - `additionalRequirements`: 额外需求
  - `expectedDeliveryDate`: 预期交付日期
  - `status`: 状态(pending, approved, rejected)
  - `createTime`: 创建时间
  - `updateTime`: 更新时间
  - `project_id`: 关联项目ID(外键)
  - `created_by`: 创建者ID(外键)

### 4. 文件管理
- **files**: 存储所有上传的文件
  - `id`: 主键
  - `filename`: 系统存储文件名(UUID生成)
  - `originalName`: 原始文件名
  - `fileType`: 文件MIME类型
  - `fileSize`: 文件大小(字节)
  - `filePath`: 服务器路径
  - `fileContent`: 文件内容(BLOB)
  - `uploadTime`: 上传时间
  - `uploaded_by`: 上传者ID(外键)
  - `isDeleted`: 软删除标记

- **project_files**: 项目文件分组
  - `id`: 主键
  - `projectId`: 项目ID(外键)
  - `fileType`: 文件用途类型(source, translation, lqa, other)
  - `notes`: 文件说明
  - `files`: 文件名列表(逗号分隔)
  - `uploadTime`: 关联时间
  - `created_by`: 关联人ID(外键)

- **project_file_mappings**: 项目文件多对多关联表
  - `id`: 主键
  - `project_file_id`: 项目文件ID(外键)
  - `file_id`: 文件ID(外键)

- **file_permissions**: 文件权限控制表
  - `id`: 主键
  - `file_id`: 文件ID(外键)
  - `user_id`: 用户ID(外键)
  - `can_view`, `can_download`, `can_edit`, `can_delete`: 权限标记

### 5. 通信管理
- **emails**: 存储发送的邮件
  - `id`: 主键
  - `projectId`: 项目ID(外键)
  - `toRecipient`: 收件人
  - `ccRecipient`: 抄送人
  - `subject`: 主题
  - `content`: 内容
  - `sendTime`: 发送时间
  - `sent_by`: 发送者ID(外键)

- **email_attachments**: 邮件附件关联表
  - `id`: 主键
  - `email_id`: 邮件ID(外键)
  - `file_id`: 文件ID(外键)

### 6. 财务管理
- **quotes**: 项目报价表
  - `id`: 主键
  - `projectId`: 项目ID(外键)
  - `lspName`: 语言服务提供商名称
  - `quoteAmount`: 报价金额
  - `currency`: 货币代码
  - `wordCount`: 字数统计
  - `quoteDate`: 报价日期
  - `status`: 状态(pending, approved, rejected)
  - `notes`: 备注
  - `createTime`: 创建时间
  - `created_by`: 创建者ID(外键)

### 7. 聊天功能
- **messages**: 聊天记录表
  - `id`: 主键
  - `sender`: 发送者
  - `text`: 消息内容
  - `created_at`: 创建时间

## 核心关系说明

1. **用户与项目**: 用户可以创建多个项目，一个项目只属于一个创建者
2. **项目与任务分配**: 一个项目可以有多个任务分配记录，按语言和任务类型细分
3. **项目与文件**: 通过project_files和project_file_mappings实现多对多关联
4. **项目与邮件**: 一个项目可以关联多封邮件
5. **项目与报价**: 一个项目可以有多个报价记录
6. **文件与权限**: 通过file_permissions实现基于用户的精细权限控制

## 数据库索引
- 在project_task_assignments表上创建了三个索引:
  - `idx_task_assignments_project`: 加速按项目ID查询
  - `idx_task_assignments_task`: 加速按任务类型查询
  - `idx_task_assignments_language`: 加速按语言查询

## 特点与设计思想

1. **多语言支持**: 数据结构设计支持多语言本地化项目管理
2. **细粒度权限控制**: 通过file_permissions表实现文件级别的精细权限管理
3. **软删除机制**: 文件使用isDeleted标记实现软删除，避免数据丢失
4. **完整追踪**: 所有重要操作都记录创建者和时间戳，确保数据可追溯性
5. **关系完整性**: 使用外键约束确保数据的关系完整性
