import os
import re
from datetime import datetime

# 日志文件路径
LOG_FILE = 'logs/flask_app.log'

def extract_logs():
    """提取并读取日志文件的最后100行"""
    if not os.path.exists(LOG_FILE):
        print(f"日志文件不存在: {LOG_FILE}")
        return []
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            # 读取最后1000行作为样本
            lines = f.readlines()[-1000:]
            return lines
    except Exception as e:
        print(f"读取日志文件时出错: {str(e)}")
        return []

def analyze_logs(lines):
    """分析日志行，查找与请求创建和文件关联相关的条目"""
    # 定义正则表达式模式
    request_pattern = r"收到创建请求: (.+)"
    file_ids_pattern = r"文件IDs: \[([\d, ]+)\]"
    file_query_pattern = r"执行查询: (.+)"
    found_files_pattern = r"找到的文件IDs: \[([\d, ]+)\]"
    project_file_create_pattern = r"创建项目文件记录成功，ID: (\d+)"
    file_mapping_pattern = r"创建文件映射: 项目文件ID (\d+) -> 文件ID (\d+)"
    error_pattern = r"ERROR - (.+)"
    warning_pattern = r"WARNING - (.+)"
    
    # 收集匹配项
    requests = []
    file_ids = []
    queries = []
    found_files = []
    project_files = []
    file_mappings = []
    errors = []
    warnings = []
    
    for line in lines:
        # 尝试匹配各种模式
        req_match = re.search(request_pattern, line)
        if req_match:
            timestamp = re.match(r"^([\d-]+ [\d:,]+)", line)
            requests.append((timestamp.group(1) if timestamp else "", req_match.group(1)))
            continue
            
        file_ids_match = re.search(file_ids_pattern, line)
        if file_ids_match:
            file_ids.append(file_ids_match.group(1))
            continue
            
        query_match = re.search(file_query_pattern, line)
        if query_match:
            queries.append(query_match.group(1))
            continue
            
        found_match = re.search(found_files_pattern, line)
        if found_match:
            found_files.append(found_match.group(1))
            continue
            
        create_match = re.search(project_file_create_pattern, line)
        if create_match:
            project_files.append(create_match.group(1))
            continue
            
        mapping_match = re.search(file_mapping_pattern, line)
        if mapping_match:
            file_mappings.append((mapping_match.group(1), mapping_match.group(2)))
            continue
            
        error_match = re.search(error_pattern, line)
        if error_match:
            errors.append(error_match.group(1))
            continue
            
        warning_match = re.search(warning_pattern, line)
        if warning_match:
            warnings.append(warning_match.group(1))
    
    # 输出结果
    print(f"找到 {len(requests)} 个请求创建记录")
    if requests:
        print("\n最近的请求创建:")
        for i, (timestamp, req) in enumerate(requests[-3:]):
            print(f"[{timestamp}] {req}")
    
    if file_ids:
        print("\n提取的文件IDs:")
        for ids in file_ids[-3:]:
            print(f"文件IDs: [{ids}]")
    
    if queries:
        print("\n执行的SQL查询:")
        for query in queries[-3:]:
            print(f"查询: {query}")
    
    if found_files:
        print("\n找到的文件:")
        for files in found_files[-3:]:
            print(f"文件IDs: [{files}]")
    
    if project_files:
        print("\n创建的项目文件记录:")
        for pf_id in project_files[-3:]:
            print(f"项目文件ID: {pf_id}")
    
    if file_mappings:
        print("\n创建的文件映射:")
        for pf_id, f_id in file_mappings[-5:]:
            print(f"项目文件ID {pf_id} -> 文件ID {f_id}")
    
    if warnings:
        print("\n警告:")
        for warning in warnings[-5:]:
            print(f"- {warning}")
    
    if errors:
        print("\n错误:")
        for error in errors[-5:]:
            print(f"- {error}")

if __name__ == "__main__":
    print("=== 分析请求创建和文件关联日志 ===")
    log_lines = extract_logs()
    if log_lines:
        print(f"读取了 {len(log_lines)} 行日志")
        analyze_logs(log_lines)
    else:
        print("没有找到有效的日志行")
    print("\n=== 分析完成 ===") 