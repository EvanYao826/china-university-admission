"""
工具函数模块
"""
import re
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def format_province_name(province: str) -> str:
    """标准化省份名称"""
    province_map = {
        '北京市': '北京', '天津市': '天津', '上海市': '上海', '重庆市': '重庆',
        '河北省': '河北', '山西省': '山西', '辽宁省': '辽宁', '吉林省': '吉林',
        '黑龙江省': '黑龙江', '江苏省': '江苏', '浙江省': '浙江', '安徽省': '安徽',
        '福建省': '福建', '江西省': '江西', '山东省': '山东', '河南省': '河南',
        '湖北省': '湖北', '湖南省': '湖南', '广东省': '广东', '海南省': '海南',
        '四川省': '四川', '贵州省': '贵州', '云南省': '云南', '陕西省': '陕西',
        '甘肃省': '甘肃', '青海省': '青海', '台湾省': '台湾', '内蒙古自治区': '内蒙古',
        '广西壮族自治区': '广西', '西藏自治区': '西藏', '宁夏回族自治区': '宁夏',
        '新疆维吾尔自治区': '新疆', '香港特别行政区': '香港', '澳门特别行政区': '澳门'
    }

    # 去除空格和特殊字符
    province = province.strip().replace('省', '').replace('市', '').replace('自治区', '').replace('特别行政区', '')

    # 映射标准化名称
    return province_map.get(province + '省', province_map.get(province + '市', province))

def parse_score_text(text: str) -> Dict[str, Optional[float]]:
    """解析分数文本"""
    result = {
        'min_score': None,
        'avg_score': None,
        'max_score': None
    }

    if not text:
        return result

    # 尝试匹配各种格式
    patterns = [
        # 格式: 最低:XXX 平均:XXX 最高:XXX
        r'最低[:：]?\s*(\d+(?:\.\d+)?)[^\d]*平均[:：]?\s*(\d+(?:\.\d+)?)[^\d]*最高[:：]?\s*(\d+(?:\.\d+)?)',
        # 格式: XXX-XXX-XXX
        r'(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)',
        # 格式: 最低XXX分
        r'最低[:：]?\s*(\d+(?:\.\d+)?)',
        # 格式: 平均XXX分
        r'平均[:：]?\s*(\d+(?:\.\d+)?)',
        # 格式: 最高XXX分
        r'最高[:：]?\s*(\d+(?:\.\d+)?)',
        # 简单数字
        r'(\d+(?:\.\d+)?)'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            if isinstance(matches[0], tuple):
                values = matches[0]
                if len(values) >= 3:
                    result['min_score'] = float(values[0]) if values[0] else None
                    result['avg_score'] = float(values[1]) if values[1] else None
                    result['max_score'] = float(values[2]) if values[2] else None
                elif len(values) >= 1:
                    result['min_score'] = float(values[0]) if values[0] else None
            else:
                # 单个匹配
                result['min_score'] = float(matches[0]) if matches[0] else None
            break

    return result

def parse_rank_text(text: str) -> Dict[str, Optional[int]]:
    """解析位次文本"""
    result = {
        'min_rank': None,
        'avg_rank': None,
        'max_rank': None
    }

    if not text:
        return result

    # 提取所有数字
    numbers = re.findall(r'\d+', text.replace(',', ''))
    numbers = [int(n) for n in numbers]

    if numbers:
        if len(numbers) >= 3:
            result['min_rank'] = numbers[0]
            result['avg_rank'] = numbers[1]
            result['max_rank'] = numbers[2]
        elif len(numbers) >= 1:
            result['min_rank'] = numbers[0]

    return result

def validate_admission_data(data: Dict[str, Any]) -> bool:
    """验证录取数据"""
    required_fields = ['university_id', 'year', 'province', 'category', 'batch']

    # 检查必需字段
    for field in required_fields:
        if field not in data or data[field] is None:
            logger.warning(f"数据缺少必需字段: {field}")
            return False

    # 验证年份
    if not (2000 <= data['year'] <= datetime.now().year):
        logger.warning(f"年份无效: {data['year']}")
        return False

    # 验证分数（如果存在）
    score_fields = ['min_score', 'avg_score', 'max_score']
    for field in score_fields:
        if field in data and data[field] is not None:
            score = data[field]
            if not (0 <= score <= 900):  # 高考分数合理范围
                logger.warning(f"分数超出合理范围: {field}={score}")
                return False

    # 验证位次（如果存在）
    rank_fields = ['min_rank', 'avg_rank', 'max_rank']
    for field in rank_fields:
        if field in data and data[field] is not None:
            rank = data[field]
            if not (1 <= rank <= 1000000):  # 位次合理范围
                logger.warning(f"位次超出合理范围: {field}={rank}")
                return False

    return True

def generate_data_summary(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成数据摘要"""
    if not data_list:
        return {}

    summary = {
        'total_records': len(data_list),
        'years': set(),
        'provinces': set(),
        'categories': set(),
        'batches': set(),
        'score_stats': {
            'min': float('inf'),
            'max': float('-inf'),
            'total': 0,
            'count': 0
        }
    }

    for data in data_list:
        # 收集分类信息
        summary['years'].add(data.get('year'))
        summary['provinces'].add(data.get('province'))
        summary['categories'].add(data.get('category'))
        summary['batches'].add(data.get('batch'))

        # 统计分数
        scores = [data.get('min_score'), data.get('avg_score'), data.get('max_score')]
        for score in scores:
            if score is not None:
                summary['score_stats']['min'] = min(summary['score_stats']['min'], score)
                summary['score_stats']['max'] = max(summary['score_stats']['max'], score)
                summary['score_stats']['total'] += score
                summary['score_stats']['count'] += 1

    # 转换集合为列表
    summary['years'] = sorted(list(summary['years']))
    summary['provinces'] = sorted(list(summary['provinces']))
    summary['categories'] = sorted(list(summary['categories']))
    summary['batches'] = sorted(list(summary['batches']))

    # 计算平均分
    if summary['score_stats']['count'] > 0:
        summary['score_stats']['avg'] = summary['score_stats']['total'] / summary['score_stats']['count']
    else:
        summary['score_stats']['avg'] = None
        summary['score_stats']['min'] = None
        summary['score_stats']['max'] = None

    return summary

def save_to_json(data: Any, filename: str, indent: int = 2):
    """保存数据到JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        logger.info(f"数据已保存到: {filename}")
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败: {e}")
        return False

def load_from_json(filename: str) -> Any:
    """从JSON文件加载数据"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载JSON文件失败: {e}")
        return None

def format_duration(seconds: float) -> str:
    """格式化时间间隔"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"

def create_backup_file(filepath: str) -> str:
    """创建备份文件"""
    import os
    import shutil
    from datetime import datetime

    if not os.path.exists(filepath):
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    filename = os.path.basename(filepath)
    backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
    backup_path = os.path.join(backup_dir, backup_name)

    try:
        shutil.copy2(filepath, backup_path)
        logger.info(f"备份已创建: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"创建备份失败: {e}")
        return None