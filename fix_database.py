#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import os
import json
import traceback
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'db': 'l10n_management',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def log(message):
    """打印带时间戳的日志信息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def check_table_structure():
    """检查数据库表结构是否正确"""
    log("开始检查数据库表结构...")
    conn = pymysql.connect(**DB_CONFIG)
    
    try:
        with conn.cursor() as cursor:
            # 检查project_files表是否有files字段
            cursor.execute("SHOW COLUMNS FROM project_files LIKE 'files'")
            has_files_column = cursor.fetchone() is not None
            log(f"project_files表是否有files列: {has_files_column}")
            
            if not has_files_column:
                log("向project_files表添加files列...")
                cursor.execute("ALTER TABLE project_files ADD COLUMN files TEXT AFTER notes")
                conn.commit()
                log("files列添加成功")
            
            # 检查project_file_mappings表结构
            cursor.execute("SHOW COLUMNS FROM project_file_mappings")
            mapping_columns = [col['Field'] for col in cursor.fetchall()]
            log(f"project_file_mappings表的列: {mapping_columns}")
            
            # 检查外键约束
            cursor.execute("SHOW CREATE TABLE project_file_mappings")
            table_def = cursor.fetchone()
            log(f"project_file_mappings表定义: {table_def}")
            
            return True
            
    except Exception as e:
        log(f"检查表结构时出错: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        conn.close()

def rebuild_file_mappings():
    """重建文件映射关系"""
    log("开始重建文件映射关系...")
    conn = pymysql.connect(**DB_CONFIG)
    
    try:
        with conn.cursor() as cursor:
            # 清空现有映射
            cursor.execute("TRUNCATE TABLE project_file_mappings")
            log("已清空project_file_mappings表")
            
            # 获取所有project_files记录
            cursor.execute("SELECT id, projectId, files, created_by FROM project_files")
            project_files = cursor.fetchall()
            log(f"找到 {len(project_files)} 个项目文件记录")
            
            # 重建映射关系
            for pf in project_files:
                project_file_id = pf['id']
                
                # 尝试从files字段获取文件名
                if pf.get('files'):
                    file_names = [name.strip() for name in pf['files'].split(',') if name.strip()]
                    log(f"项目文件ID {project_file_id} 的files字段包含 {len(file_names)} 个文件名")
                    
                    # 根据文件名找到对应的文件ID
                    if file_names:
                        placeholders = ', '.join(['%s'] * len(file_names))
                        query = f"""
                            SELECT id, originalName 
                            FROM files 
                            WHERE originalName IN ({placeholders}) AND isDeleted = FALSE
                        """
                        cursor.execute(query, file_names)
                        found_files = cursor.fetchall()
                        log(f"找到 {len(found_files)} 个匹配的文件记录")
                        
                        # 创建映射
                        for file in found_files:
                            try:
                                cursor.execute("""
                                    INSERT INTO project_file_mappings (project_file_id, file_id)
                                    VALUES (%s, %s)
                                """, (project_file_id, file['id']))
                                log(f"创建映射: 项目文件ID {project_file_id} -> 文件ID {file['id']} (文件名: {file['originalName']})")
                            except Exception as e:
                                log(f"创建映射时出错: {str(e)}")
                
            conn.commit()
            log("文件映射关系重建完成")
            
            # 验证结果
            cursor.execute("SELECT COUNT(*) as count FROM project_file_mappings")
            mapping_count = cursor.fetchone()['count']
            log(f"现在有 {mapping_count} 个文件映射记录")
            
            return True
            
    except Exception as e:
        log(f"重建文件映射时出错: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        conn.close()

def verify_mappings():
    """验证文件映射是否正确"""
    log("开始验证文件映射...")
    conn = pymysql.connect(**DB_CONFIG)
    
    try:
        with conn.cursor() as cursor:
            # 检查每个项目文件是否有对应的映射
            cursor.execute("""
                SELECT pf.id, pf.projectId, pf.files, 
                       COUNT(pfm.id) as mapping_count
                FROM project_files pf
                LEFT JOIN project_file_mappings pfm ON pf.id = pfm.project_file_id
                GROUP BY pf.id
            """)
            results = cursor.fetchall()
            
            for result in results:
                if result['mapping_count'] == 0:
                    log(f"警告: 项目文件ID {result['id']} (项目ID: {result['projectId']}) 没有文件映射")
                else:
                    log(f"项目文件ID {result['id']} 有 {result['mapping_count']} 个文件映射")
            
            # 检查是否有孤立的映射
            cursor.execute("""
                SELECT pfm.id, pfm.project_file_id, pfm.file_id
                FROM project_file_mappings pfm
                LEFT JOIN project_files pf ON pfm.project_file_id = pf.id
                WHERE pf.id IS NULL
            """)
            orphaned_mappings = cursor.fetchall()
            
            if orphaned_mappings:
                log(f"警告: 找到 {len(orphaned_mappings)} 个孤立的映射记录")
                for mapping in orphaned_mappings:
                    log(f"孤立映射ID: {mapping['id']}, 引用的项目文件ID: {mapping['project_file_id']}")
            else:
                log("没有发现孤立的映射记录")
            
            return True
            
    except Exception as e:
        log(f"验证文件映射时出错: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        conn.close()

def fix_missing_file_mappings():
    """尝试修复丢失的文件映射"""
    log("开始修复丢失的文件映射...")
    conn = pymysql.connect(**DB_CONFIG)
    
    try:
        with conn.cursor() as cursor:
            # 查找所有缺少映射的项目文件
            cursor.execute("""
                SELECT pf.id, pf.projectId, pf.files, pf.created_by
                FROM project_files pf
                LEFT JOIN project_file_mappings pfm ON pf.id = pfm.project_file_id
                WHERE pfm.id IS NULL AND pf.files IS NOT NULL AND pf.files != ''
            """)
            missing_mappings = cursor.fetchall()
            
            if not missing_mappings:
                log("没有找到缺少映射的项目文件")
                return True
            
            log(f"找到 {len(missing_mappings)} 个缺少映射的项目文件")
            
            fixed_count = 0
            for pf in missing_mappings:
                project_file_id = pf['id']
                files_str = pf['files']
                created_by = pf['created_by']
                
                if not files_str:
                    continue
                
                log(f"处理项目文件ID {project_file_id}, files: {files_str}")
                
                # 解析文件名
                file_names = [name.strip() for name in files_str.split(',') if name.strip()]
                
                if not file_names:
                    continue
                
                # 查找用户上传的匹配文件
                placeholders = ', '.join(['%s'] * len(file_names))
                query = f"""
                    SELECT id, originalName 
                    FROM files 
                    WHERE originalName IN ({placeholders}) AND uploaded_by = %s AND isDeleted = FALSE
                """
                params = file_names + [created_by]
                cursor.execute(query, params)
                found_files = cursor.fetchall()
                
                if not found_files:
                    log(f"未找到项目文件ID {project_file_id} 的匹配文件")
                    continue
                
                log(f"找到 {len(found_files)} 个匹配的文件")
                
                # 创建映射
                for file in found_files:
                    try:
                        cursor.execute("""
                            INSERT INTO project_file_mappings (project_file_id, file_id)
                            VALUES (%s, %s)
                        """, (project_file_id, file['id']))
                        log(f"创建映射: 项目文件ID {project_file_id} -> 文件ID {file['id']} (文件名: {file['originalName']})")
                        fixed_count += 1
                    except Exception as e:
                        log(f"创建映射时出错: {str(e)}")
            
            conn.commit()
            log(f"修复了 {fixed_count} 个文件映射")
            
            return True
            
    except Exception as e:
        log(f"修复文件映射时出错: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    log("开始数据库修复流程...")
    
    # 1. 检查表结构
    if not check_table_structure():
        log("表结构检查失败，终止修复流程")
        return
    
    # 2. 尝试修复丢失的文件映射
    if not fix_missing_file_mappings():
        log("修复丢失的文件映射失败")
    
    # 3. 验证映射是否正确
    if not verify_mappings():
        log("验证文件映射失败")
    
    log("数据库修复流程完成")

if __name__ == "__main__":
    main() 