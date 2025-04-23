from typing import List, Union, Dict
from pathlib import Path
from collections import defaultdict
import json
import re

def extract_text_from_json(file_path):
    # 读取并解析JSON文件
    with open(file_path, 'r', encoding='utf-8') as file:
        # 假设JSON数据是一个数组，每个元素都是一个包含text字段的对象
        data = json.load(file)  # 这里data应该是一个列表，列表中的每个元素都是一个字典

    extracted_texts = []

    # 遍历数据列表，提取每个对象的text字段
    for item in data:
        if 'text' in item:
            extracted_texts.append(item['text'])

    return extracted_texts


def safe_convert(value):
    """安全转换数值，处理空值和千分位"""
    if not value or value == '-':
        return None
    try:
        return float(value.replace(',', ''))
    except ValueError:
        return value  # 返回原始字符串如果转换失败


def extract_metal_data(json_data, metal_name):
    """
    从包含Olympic Dam数据的JSON中提取指定金属的资源量
    参数：
        json_data - 包含矿业数据的JSON数组
        metal_name - 需要查询的金属名称（如'Cu', 'Au', 'Mo'）
    返回：
        包含resources和reserves的字典，结构：
        {
            'resources': [meas_mt, meas_grade, meas_ppm, meas_gpt],
            'reserves': [ind_mt, ind_grade, ind_ppm]
        }
    """
    # 1. 定位包含Olympic Dam的记录
    target_entry = None
    for entry in json_data:
        if 'text' in entry and 'Olympic Dam' in entry['text']:
            target_entry = entry
            break

    print(json_data)

    if not target_entry:
        raise ValueError("Olympic Dam数据未找到")

    # 2. 解析表格数据
    text_content = target_entry['text']
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]

    # 检查有效表格结构
    if len(lines) < 3:
        raise ValueError("表格结构不完整")

    # 3. 解析表头确定列索引
    header_line = lines[0]
    headers = [h.strip() for h in header_line.split('| ') if h.strip()]

    # 动态检测列位置
    col_mapping = {
        'metal_col': None,
        'meas_mt': None,
        'meas_grade': None,
        'meas_ppm': None,
        'meas_gpt': None,
        'ind_mt': None,
        'ind_grade': None,
        'ind_ppm': None
    }

    # 根据金属类型匹配列名
    grade_pattern = re.compile(rf"%{metal_name}", re.IGNORECASE)
    ppm_pattern = re.compile(rf"ppm{metal_name}", re.IGNORECASE)
    gpt_pattern = re.compile(rf"g/t{metal_name}", re.IGNORECASE)

    for idx, col in enumerate(headers):
        if 'Ore type' in col:
            col_mapping['metal_col'] = idx
        elif 'Measured' in col:
            if 'Mt' in col:
                col_mapping['meas_mt'] = idx
            elif grade_pattern.search(col):
                col_mapping['meas_grade'] = idx
            elif ppm_pattern.search(col):
                col_mapping['meas_ppm'] = idx
            elif gpt_pattern.search(col):
                col_mapping['meas_gpt'] = idx
        elif 'Indicated' in col:
            if 'Mt' in col:
                col_mapping['ind_mt'] = idx
            elif grade_pattern.search(col):
                col_mapping['ind_grade'] = idx
            elif ppm_pattern.search(col):
                col_mapping['ind_ppm'] = idx

    # 4. 提取数据行
    results = []
    for line in lines[2:]:  # 跳过表头和分隔线
        columns = [col.strip() for col in line.split('|') if col.strip()]

        # 匹配金属行（包含指定金属名称）
        if (col_mapping['metal_col'] is not None and
                len(columns) > col_mapping['metal_col'] and
                metal_name.lower() in columns[col_mapping['metal_col']].lower()):
            # 提取测量资源
            meas_values = [
                safe_convert(columns[col_mapping['meas_mt']]),
                safe_convert(columns[col_mapping['meas_grade']]),
                safe_convert(columns[col_mapping['meas_ppm']]),
                safe_convert(columns[col_mapping['meas_gpt']])
            ]

            # 提取指示资源
            ind_values = [
                safe_convert(columns[col_mapping['ind_mt']]),
                safe_convert(columns[col_mapping['ind_grade']]),
                safe_convert(columns[col_mapping['ind_ppm']])
            ]

            results.append({
                'resources': meas_values,
                'reserves': ind_values
            })

    if not results:
        raise ValueError(f"未找到{metal_name}相关数据")

    return results


# 测试
if __name__ == '__main__':
    with open("D:\\postgraduate\\LLM Engineer\\RAG\\RAG-Challenge-2\\data\\test_set\\databases_ser_tab\\chunked_reports"
              "\\240827_bhpannualreport2024.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    try:
        copper_data = extract_metal_data(data, 'Cu')
        print("该矿物资源数据：")
        for entry in copper_data:
            print(f"Resources: {entry['resources']}")
            print(f"Reserves: {entry['reserves']}")

    except ValueError as e:
        print(f"错误：{str(e)}")


