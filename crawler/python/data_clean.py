#!/usr/bin/env python3
"""
数据清洗工具
用于清洗和预处理爬取的高校录取数据
"""

import pandas as pd
import sqlite3
import re
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗器"""

    def __init__(self, db_path: str = "../data/university.db"):
        self.db_path = db_path

    def clean_gaokao_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """清洗高考录取数据"""
        cleaned_data = []
        
        for item in data:
            try:
                # 标准化高校名称
                item['university_name'] = self._normalize_university_name(item.get('university_name', ''))
                
                # 标准化省份名称
                item['province'] = self._normalize_province(item.get('province', ''))
                
                # 标准化年份
                item['year'] = self._normalize_year(item.get('year', 0))
                
                # 标准化批次
                item['batch'] = self._normalize_batch(item.get('batch', ''))
                
                # 标准化类别
                item['category'] = self._normalize_category(item.get('category', ''))
                
                # 清洗分数
                item['min_score'] = self._clean_score(item.get('min_score'))
                item['avg_score'] = self._clean_score(item.get('avg_score'))
                item['max_score'] = self._clean_score(item.get('max_score'))
                
                # 清洗位次
                item['min_rank'] = self._clean_rank(item.get('min_rank'))
                item['avg_rank'] = self._clean_rank(item.get('avg_rank'))
                item['max_rank'] = self._clean_rank(item.get('max_rank'))
                
                # 清洗招生人数
                item['admission_count'] = self._clean_count(item.get('admission_count'))
                
                # 标准化专业名称
                if 'major' in item:
                    item['major'] = self._normalize_major(item['major'])
                
                # 清洗备注
                if 'notes' in item:
                    item['notes'] = self._clean_notes(item['notes'])
                
                # 验证数据完整性
                if self._validate_gaokao_record(item):
                    cleaned_data.append(item)
                else:
                    logger.warning(f"跳过无效记录: {item}")
                    
            except Exception as e:
                logger.error(f"清洗数据时出错: {e}")
                continue
        
        # 去重
        cleaned_data = self._remove_duplicates(cleaned_data)
        
        logger.info(f"清洗完成，共处理 {len(data)} 条记录，有效记录 {len(cleaned_data)} 条")
        return cleaned_data

    def clean_graduate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """清洗研究生录取数据"""
        cleaned_data = []
        
        for item in data:
            try:
                # 标准化高校名称
                item['university_name'] = self._normalize_university_name(item.get('university_name', ''))
                
                # 标准化年份
                item['year'] = self._normalize_year(item.get('year', 0))
                
                # 标准化专业名称
                item['major'] = self._normalize_major(item.get('major', ''))
                
                # 标准化学位类型
                item['degree_type'] = self._normalize_degree_type(item.get('degree_type', ''))
                
                # 标准化学习方式
                item['study_mode'] = self._normalize_study_mode(item.get('study_mode', ''))
                
                # 清洗分数
                item['min_score'] = self._clean_score(item.get('min_score'))
                item['avg_score'] = self._clean_score(item.get('avg_score'))
                item['max_score'] = self._clean_score(item.get('max_score'))
                
                # 清洗招生人数
                item['admission_count'] = self._clean_count(item.get('admission_count'))
                
                # 清洗备注
                if 'notes' in item:
                    item['notes'] = self._clean_notes(item['notes'])
                
                # 验证数据完整性
                if self._validate_graduate_record(item):
                    cleaned_data.append(item)
                else:
                    logger.warning(f"跳过无效记录: {item}")
                    
            except Exception as e:
                logger.error(f"清洗数据时出错: {e}")
                continue
        
        # 去重
        cleaned_data = self._remove_duplicates(cleaned_data)
        
        logger.info(f"清洗完成，共处理 {len(data)} 条记录，有效记录 {len(cleaned_data)} 条")
        return cleaned_data

    def _normalize_university_name(self, name: str) -> str:
        """标准化高校名称"""
        name = name.strip()
        # 移除常见后缀
        suffixes = ['大学', '学院', '学校', '研究院']
        for suffix in suffixes:
            if name.endswith(suffix):
                break
        # 标准化简称
        name_map = {
            '清华': '清华大学',
            '北大': '北京大学',
            '浙大': '浙江大学',
            '复旦': '复旦大学',
            '上交': '上海交通大学',
            '南大': '南京大学',
            '武大': '武汉大学',
            '华科': '华中科技大学',
            '中山': '中山大学',
            '西交': '西安交通大学'
        }
        for key, value in name_map.items():
            if key in name:
                return value
        return name

    def _normalize_province(self, province: str) -> str:
        """标准化省份名称"""
        province = province.strip()
        # 移除'省'、'市'、'自治区'等后缀
        suffixes = ['省', '市', '自治区', '特别行政区']
        for suffix in suffixes:
            if province.endswith(suffix):
                province = province[:-len(suffix)]
                break
        # 标准化名称
        province_map = {
            '北京': '北京',
            '上海': '上海',
            '天津': '天津',
            '重庆': '重庆',
            '河北': '河北',
            '山西': '山西',
            '辽宁': '辽宁',
            '吉林': '吉林',
            '黑龙江': '黑龙江',
            '江苏': '江苏',
            '浙江': '浙江',
            '安徽': '安徽',
            '福建': '福建',
            '江西': '江西',
            '山东': '山东',
            '河南': '河南',
            '湖北': '湖北',
            '湖南': '湖南',
            '广东': '广东',
            '海南': '海南',
            '四川': '四川',
            '贵州': '贵州',
            '云南': '云南',
            '陕西': '陕西',
            '甘肃': '甘肃',
            '青海': '青海',
            '台湾': '台湾',
            '内蒙古': '内蒙古',
            '广西': '广西',
            '西藏': '西藏',
            '宁夏': '宁夏',
            '新疆': '新疆',
            '香港': '香港',
            '澳门': '澳门'
        }
        return province_map.get(province, province)

    def _normalize_year(self, year: Any) -> int:
        """标准化年份"""
        try:
            year = int(year)
            current_year = datetime.now().year
            if 2000 <= year <= current_year:
                return year
            return 0
        except:
            return 0

    def _normalize_batch(self, batch: str) -> str:
        """标准化批次"""
        batch = batch.strip()
        batch_map = {
            '本科一批': '本科一批',
            '一批': '本科一批',
            '一本': '本科一批',
            '本科二批': '本科二批',
            '二批': '本科二批',
            '二本': '本科二批',
            '本科三批': '本科三批',
            '三批': '本科三批',
            '三本': '本科三批',
            '专科批': '专科批',
            '专科': '专科批',
            '提前批': '提前批',
            '提前': '提前批'
        }
        for key, value in batch_map.items():
            if key in batch:
                return value
        return batch

    def _normalize_category(self, category: str) -> str:
        """标准化类别"""
        category = category.strip()
        category_map = {
            '文科': '文科',
            '文史': '文科',
            '理科': '理科',
            '理工': '理科',
            '综合改革': '综合改革',
            '综合': '综合改革',
            '艺术': '艺术',
            '体育': '体育'
        }
        for key, value in category_map.items():
            if key in category:
                return value
        return category

    def _normalize_major(self, major: str) -> str:
        """标准化专业名称"""
        major = major.strip()
        # 移除括号内容
        major = re.sub(r'\([^)]*\)', '', major)
        return major

    def _normalize_degree_type(self, degree_type: str) -> str:
        """标准化学位类型"""
        degree_type = degree_type.strip()
        if '博士' in degree_type:
            return '博士'
        elif '硕士' in degree_type:
            return '硕士'
        return degree_type

    def _normalize_study_mode(self, study_mode: str) -> str:
        """标准化学习方式"""
        study_mode = study_mode.strip()
        if '非全' in study_mode or '在职' in study_mode:
            return '非全日制'
        else:
            return '全日制'

    def _clean_score(self, score: Any) -> Optional[float]:
        """清洗分数"""
        try:
            if score is None or score == '':
                return None
            # 提取数字
            score_str = str(score)
            numbers = re.findall(r'\d+\.?\d*', score_str)
            if numbers:
                score = float(numbers[0])
                # 合理分数范围
                if 0 <= score <= 1000:
                    return score
            return None
        except:
            return None

    def _clean_rank(self, rank: Any) -> Optional[int]:
        """清洗位次"""
        try:
            if rank is None or rank == '':
                return None
            # 提取数字
            rank_str = str(rank)
            numbers = re.findall(r'\d+', rank_str)
            if numbers:
                rank = int(numbers[0])
                # 合理位次范围
                if 0 < rank <= 1000000:
                    return rank
            return None
        except:
            return None

    def _clean_count(self, count: Any) -> Optional[int]:
        """清洗招生人数"""
        try:
            if count is None or count == '':
                return None
            # 提取数字
            count_str = str(count)
            numbers = re.findall(r'\d+', count_str)
            if numbers:
                count = int(numbers[0])
                # 合理人数范围
                if count >= 0:
                    return count
            return None
        except:
            return None

    def _clean_notes(self, notes: str) -> str:
        """清洗备注"""
        if notes is None:
            return ''
        notes = str(notes)
        # 移除多余空格和换行
        notes = re.sub(r'\s+', ' ', notes).strip()
        # 限制长度
        return notes[:500]  # 最多500字符

    def _validate_gaokao_record(self, record: Dict[str, Any]) -> bool:
        """验证高考录取记录"""
        required_fields = ['university_name', 'province', 'year', 'batch', 'category']
        for field in required_fields:
            if not record.get(field):
                return False
        # 至少有一个分数或位次
        score_fields = ['min_score', 'avg_score', 'max_score', 'min_rank', 'avg_rank', 'max_rank']
        has_score_or_rank = any(record.get(field) is not None for field in score_fields)
        return has_score_or_rank

    def _validate_graduate_record(self, record: Dict[str, Any]) -> bool:
        """验证研究生录取记录"""
        required_fields = ['university_name', 'year', 'major', 'degree_type', 'study_mode']
        for field in required_fields:
            if not record.get(field):
                return False
        # 至少有招生人数
        return record.get('admission_count') is not None

    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重"""
        seen = set()
        unique_data = []
        
        for item in data:
            # 生成唯一键
            if 'batch' in item:  # 高考数据
                key = (
                    item.get('university_name'),
                    item.get('province'),
                    item.get('year'),
                    item.get('batch'),
                    item.get('category'),
                    item.get('major', '')
                )
            else:  # 研究生数据
                key = (
                    item.get('university_name'),
                    item.get('year'),
                    item.get('major'),
                    item.get('degree_type'),
                    item.get('study_mode')
                )
            
            if key not in seen:
                seen.add(key)
                unique_data.append(item)
        
        if len(unique_data) < len(data):
            logger.info(f"去重后减少 {len(data) - len(unique_data)} 条记录")
        
        return unique_data

    def clean_from_database(self):
        """从数据库中清洗数据"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # 清洗高考数据
            logger.info("开始清洗高考录取数据...")
            df_gaokao = pd.read_sql("SELECT * FROM gaokao_admissions", conn)
            
            if not df_gaokao.empty:
                # 转换为字典列表
                data = df_gaokao.to_dict('records')
                # 清洗数据
                cleaned_data = self.clean_gaokao_data(data)
                
                # 清空表并重新插入
                conn.execute("DELETE FROM gaokao_admissions")
                
                for item in cleaned_data:
                    conn.execute('''
                        INSERT INTO gaokao_admissions
                        (university_id, year, province, category, batch,
                         min_score, avg_score, max_score, min_rank, avg_rank, max_rank,
                         admission_count, major, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('university_id'), item.get('year'), item.get('province'), 
                        item.get('category'), item.get('batch'), item.get('min_score'),
                        item.get('avg_score'), item.get('max_score'), item.get('min_rank'),
                        item.get('avg_rank'), item.get('max_rank'), item.get('admission_count'),
                        item.get('major'), item.get('notes')
                    ))
                
                conn.commit()
                logger.info(f"高考数据清洗完成，共处理 {len(cleaned_data)} 条记录")
            
            # 清洗研究生数据
            logger.info("开始清洗研究生录取数据...")
            df_graduate = pd.read_sql("SELECT * FROM graduate_admissions", conn)
            
            if not df_graduate.empty:
                # 转换为字典列表
                data = df_graduate.to_dict('records')
                # 清洗数据
                cleaned_data = self.clean_graduate_data(data)
                
                # 清空表并重新插入
                conn.execute("DELETE FROM graduate_admissions")
                
                for item in cleaned_data:
                    conn.execute('''
                        INSERT INTO graduate_admissions
                        (university_id, year, major, degree_type, study_mode,
                         admission_count, min_score, avg_score, max_score, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('university_id'), item.get('year'), item.get('major'),
                        item.get('degree_type'), item.get('study_mode'), item.get('admission_count'),
                        item.get('min_score'), item.get('avg_score'), item.get('max_score'),
                        item.get('notes')
                    ))
                
                conn.commit()
                logger.info(f"研究生数据清洗完成，共处理 {len(cleaned_data)} 条记录")
                
        except Exception as e:
            logger.error(f"从数据库清洗数据时出错: {e}")
            conn.rollback()
        finally:
            conn.close()

def main():
    """主函数"""
    print("=" * 60)
    print("数据清洗工具")
    print("=" * 60)
    print("功能：")
    print("1. 清洗高考录取数据")
    print("2. 清洗研究生录取数据")
    print("3. 从数据库中清洗数据")
    print("=" * 60)

    # 创建清洗器
    cleaner = DataCleaner()

    # 示例数据
    sample_gaokao_data = [
        {
            "university_name": "清华大学",
            "province": "北京市",
            "year": "2023",
            "category": "理科",
            "batch": "本科一批",
            "min_score": "680",
            "avg_score": "690",
            "max_score": "710",
            "min_rank": "100",
            "avg_rank": "50",
            "max_rank": "10",
            "admission_count": "120",
            "major": "计算机科学与技术",
            "notes": "包含保送生"
        },
        {
            "university_name": "北京大学",
            "province": "上海",
            "year": "2022",
            "category": "文科",
            "batch": "一批",
            "min_score": "650",
            "admission_count": "80"
        }
    ]

    sample_graduate_data = [
        {
            "university_name": "浙江大学",
            "year": "2023",
            "major": "软件工程",
            "degree_type": "硕士",
            "study_mode": "全日制",
            "admission_count": "50",
            "min_score": "360",
            "avg_score": "380"
        }
    ]

    # 测试清洗高考数据
    print("\n测试清洗高考数据...")
    cleaned_gaokao = cleaner.clean_gaokao_data(sample_gaokao_data)
    for i, item in enumerate(cleaned_gaokao):
        print(f"{i+1}. {item['university_name']} - {item['province']} {item['year']}年")
        print(f"   批次: {item['batch']}, 类别: {item['category']}")
        print(f"   最低分: {item['min_score']}, 平均分: {item['avg_score']}")
        print()

    # 测试清洗研究生数据
    print("\n测试清洗研究生数据...")
    cleaned_graduate = cleaner.clean_graduate_data(sample_graduate_data)
    for i, item in enumerate(cleaned_graduate):
        print(f"{i+1}. {item['university_name']} - {item['major']}")
        print(f"   类型: {item['degree_type']}{item['study_mode']}")
        print(f"   招生人数: {item['admission_count']}")
        print()

    # 提示如何从数据库清洗
    print("\n" + "=" * 60)
    print("从数据库清洗数据:")
    print("运行: cleaner.clean_from_database()")
    print("或直接运行: python data_clean.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
