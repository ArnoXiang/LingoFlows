#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件映射测试脚本
此脚本模拟文件映射修复过程的核心逻辑，不依赖数据库连接
"""

import json
from datetime import datetime

def log(message):
    """打印带时间戳的日志信息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

# 模拟数据
files = [
    {"id": 1, "originalName": "文档1.docx", "uploaded_by": 1},
    {"id": 2, "originalName": "文档2.docx", "uploaded_by": 1},
    {"id": 3, "originalName": "文档3.docx", "uploaded_by": 2},
    {"id": 4, "originalName": "文档4.docx", "uploaded_by": 2},
    {"id": 5, "originalName": "文档5.docx", "uploaded_by": 1},
    {"id": 6, "originalName": "文档6.docx", "uploaded_by": 1},
    {"id": 7, "originalName": "文档7.docx", "uploaded_by": 3},
    {"id": 8, "originalName": "文档8.docx", "uploaded_by": 3},
    {"id": 9, "originalName": "文档9.docx", "uploaded_by": 1}
]

project_files = [
    {"id": 1, "projectId": 1, "files": "文档1.docx, 文档2.docx", "created_by": 1},
    {"id": 2, "projectId": 2, "files": "文档3.docx, 文档4.docx", "created_by": 2},
    {"id": 3, "projectId": 1, "files": "文档5.docx, 文档6.docx", "created_by": 1}
]

mappings = [
    {"id": 1, "project_file_id": 1, "file_id": 1},
    {"id": 2, "project_file_id": 1, "file_id": 2},
    {"id": 3, "project_file_id": 2, "file_id": 3},
    # 文档4没有映射
    # 文档5和文档6没有映射
    # 文档7、文档8和文档9没有任何映射，也没有对应的项目文件记录
]

projects = [
    {"id": 1, "projectName": "项目1", "created_by": 1},
    {"id": 2, "projectName": "项目2", "created_by": 2},
    {"id": 3, "projectName": "项目3", "created_by": 3}
]

def print_status():
    """打印当前状态"""
    log("当前状态:")
    log(f"- 文件数量: {len(files)}")
    log(f"- 项目文件数量: {len(project_files)}")
    log(f"- 映射数量: {len(mappings)}")
    
    # 计算未映射的文件
    mapped_file_ids = set(m["file_id"] for m in mappings)
    unmapped_files = [f for f in files if f["id"] not in mapped_file_ids]
    log(f"- 未映射文件数量: {len(unmapped_files)}")
    if unmapped_files:
        log("  未映射文件:")
        for f in unmapped_files:
            log(f"  - ID: {f['id']}, 名称: {f['originalName']}, 上传者: {f['uploaded_by']}")

def fix_mappings():
    """修复文件映射"""
    log("开始修复文件映射...")
    
    # 查找未映射的文件
    mapped_file_ids = set(m["file_id"] for m in mappings)
    unmapped_files = [f for f in files if f["id"] not in mapped_file_ids]
    
    if not unmapped_files:
        log("没有找到未映射的文件")
        return
    
    log(f"找到 {len(unmapped_files)} 个未映射的文件")
    
    # 按上传者分组
    files_by_uploader = {}
    for file in unmapped_files:
        uploader_id = file["uploaded_by"]
        if uploader_id not in files_by_uploader:
            files_by_uploader[uploader_id] = []
        files_by_uploader[uploader_id].append(file)
    
    # 为每个上传者处理文件
    fixed_count = 0
    for uploader_id, files_group in files_by_uploader.items():
        log(f"处理上传者 {uploader_id} 的 {len(files_group)} 个文件")
        
        # 查找该用户的项目
        user_projects = [p for p in projects if p["created_by"] == uploader_id]
        if not user_projects:
            log(f"用户 {uploader_id} 没有关联的项目")
            continue
        
        # 获取最近的项目
        latest_project = user_projects[0]
        project_id = latest_project["id"]
        
        # 查找该项目的项目文件
        project_file_records = [pf for pf in project_files if pf["projectId"] == project_id]
        
        project_file_id = None
        if project_file_records:
            # 使用现有项目文件
            project_file = project_file_records[0]
            project_file_id = project_file["id"]
            log(f"使用现有项目文件记录 ID: {project_file_id}")
            
            # 更新files字段
            existing_files = project_file["files"] or ""
            file_names = [f["originalName"] for f in files_group]
            new_files = ", ".join(file_names)
            
            if existing_files:
                updated_files = f"{existing_files}, {new_files}"
            else:
                updated_files = new_files
            
            project_file["files"] = updated_files
            log(f"更新项目文件记录的files字段: {updated_files}")
        else:
            # 创建新的项目文件记录
            file_names = [f["originalName"] for f in files_group]
            files_str = ", ".join(file_names)
            
            new_project_file = {
                "id": len(project_files) + 1,
                "projectId": project_id,
                "files": files_str,
                "created_by": uploader_id
            }
            project_files.append(new_project_file)
            project_file_id = new_project_file["id"]
            log(f"创建新项目文件记录，ID: {project_file_id}")
        
        # 为每个文件创建映射
        for file in files_group:
            # 检查映射是否已存在
            if any(m["project_file_id"] == project_file_id and m["file_id"] == file["id"] for m in mappings):
                log(f"映射已存在: 项目文件ID {project_file_id} -> 文件ID {file['id']}")
                continue
            
            # 创建新映射
            new_mapping = {
                "id": len(mappings) + 1,
                "project_file_id": project_file_id,
                "file_id": file["id"]
            }
            mappings.append(new_mapping)
            log(f"创建映射: 项目文件ID {project_file_id} -> 文件ID {file['id']} (文件名: {file['originalName']})")
            fixed_count += 1
    
    log(f"修复了 {fixed_count} 个文件映射")
    
    # 检查project_files表中的files字段与映射的一致性
    log("检查项目文件的files字段与映射的一致性...")
    
    for pf in project_files:
        if not pf.get("files"):
            continue
        
        file_names = [name.strip() for name in pf["files"].split(",") if name.strip()]
        if not file_names:
            continue
        
        log(f"项目文件 {pf['id']} 的files字段包含 {len(file_names)} 个文件名")
        
        # 查找已存在的映射
        existing_mappings = [m for m in mappings if m["project_file_id"] == pf["id"]]
        existing_file_ids = [m["file_id"] for m in existing_mappings]
        
        # 查找这些文件ID对应的文件名
        existing_files = [f for f in files if f["id"] in existing_file_ids]
        existing_file_names = [f["originalName"] for f in existing_files]
        
        # 找出需要添加映射的文件名
        missing_file_names = [name for name in file_names if name not in existing_file_names]
        
        if not missing_file_names:
            continue
        
        log(f"项目文件 {pf['id']} 有 {len(missing_file_names)} 个文件名缺少映射")
        
        # 查找匹配的文件
        found_files = [f for f in files if f["originalName"] in missing_file_names]
        
        if not found_files:
            continue
        
        log(f"找到 {len(found_files)} 个匹配的文件")
        
        # 创建映射
        for file in found_files:
            # 检查映射是否已存在
            if any(m["project_file_id"] == pf["id"] and m["file_id"] == file["id"] for m in mappings):
                log(f"映射已存在: 项目文件ID {pf['id']} -> 文件ID {file['id']}")
                continue
            
            # 创建新映射
            new_mapping = {
                "id": len(mappings) + 1,
                "project_file_id": pf["id"],
                "file_id": file["id"]
            }
            mappings.append(new_mapping)
            log(f"创建映射: 项目文件ID {pf['id']} -> 文件ID {file['id']} (文件名: {file['originalName']})")
            fixed_count += 1

def main():
    """主函数"""
    log("开始文件映射测试")
    
    # 打印初始状态
    print_status()
    
    # 修复映射
    fix_mappings()
    
    # 打印修复后的状态
    print_status()
    
    log("测试完成")

if __name__ == "__main__":
    main() 