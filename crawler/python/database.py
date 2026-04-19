"""
数据库操作模块
"""
import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_CONFIG['path']
        self.connection = None

    def connect(self) -> sqlite3.Connection:
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                timeout=DATABASE_CONFIG['timeout']
            )
            # 启用外键约束
            self.connection.execute("PRAGMA foreign_keys = ON")
            logger.info(f"成功连接到数据库: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("数据库连接已关闭")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute_query(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """执行SQL查询"""
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except sqlite3.Error as e:
            logger.error(f"SQL执行失败: {e}\n查询: {query}\n参数: {params}")
            raise

    def commit(self):
        """提交事务"""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """回滚事务"""
        if self.connection:
            self.connection.rollback()

    # 高校相关操作 - 适配新表结构
    def get_university_id(self, name: str) -> Optional[int]:
        """根据高校名称获取ID"""
        query = "SELECT id FROM universities WHERE name = ?"
        cursor = self.execute_query(query, (name,))
        result = cursor.fetchone()
        return result[0] if result else None

    def add_university(self, name: str, province: str, type: str = None,
                      level: str = None, city: str = None, tags: str = None,
                      logo_url: str = None, description: str = None) -> int:
        """添加高校信息 - 适配新表结构"""
        # 检查是否已存在
        existing_id = self.get_university_id(name)
        if existing_id:
            logger.info(f"高校已存在: {name} (ID: {existing_id})")
            return existing_id

        query = """
        INSERT INTO universities (name, province, type, level, city, tags, logo_url, description, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (name, province, type, level, city, tags, logo_url, description, datetime.now())

        cursor = self.execute_query(query, params)
        self.commit()
        logger.info(f"添加高校成功: {name} (ID: {cursor.lastrowid})")
        return cursor.lastrowid

    # 本科录取数据相关操作 - 适配新表结构
    def save_undergraduate_admission_data(self, data: Dict[str, Any]) -> int:
        """保存本科录取数据 - 适配新表结构"""
        query = """
        INSERT OR REPLACE INTO undergraduate_admissions
        (university_id, province, year, category, batch, enrollment_type, major,
         min_score, min_rank, avg_score, provincial_control_line,
         subject_requirements, professional_group, source_url, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            data['university_id'],
            data['province'],
            data['year'],
            data.get('category'),
            data.get('batch'),
            data.get('enrollment_type'),
            data.get('major'),
            data.get('min_score'),
            data.get('min_rank'),
            data.get('avg_score'),
            data.get('provincial_control_line'),
            data.get('subject_requirements'),
            data.get('professional_group'),
            data.get('source_url'),
            datetime.now()
        )

        cursor = self.execute_query(query, params)
        self.commit()
        return cursor.lastrowid

    # 兼容旧接口
    def save_admission_data(self, data: Dict[str, Any]) -> int:
        """兼容旧接口，转发到新接口"""
        return self.save_undergraduate_admission_data(data)

    def batch_save_admission_data(self, data_list: List[Dict[str, Any]]) -> List[int]:
        """批量保存录取数据"""
        ids = []
        for data in data_list:
            try:
                data_id = self.save_admission_data(data)
                ids.append(data_id)
            except Exception as e:
                logger.error(f"保存数据失败: {e}\n数据: {data}")
                continue
        return ids

    def check_data_exists(self, university_id: int, year: int,
                         province: str, category: str = None, batch: str = None,
                         major: str = None, enrollment_type: str = None) -> bool:
        """检查数据是否已存在 - 适配新表结构"""
        conditions = ["university_id = ?", "year = ?", "province = ?"]
        params = [university_id, year, province]

        if category:
            conditions.append("category = ?")
            params.append(category)

        if batch:
            conditions.append("batch = ?")
            params.append(batch)

        if major:
            conditions.append("major = ?")
            params.append(major)

        if enrollment_type:
            conditions.append("enrollment_type = ?")
            params.append(enrollment_type)

        where_clause = " AND ".join(conditions)
        query = f"""
        SELECT COUNT(*) FROM undergraduate_admissions
        WHERE {where_clause}
        """

        cursor = self.execute_query(query, tuple(params))
        count = cursor.fetchone()[0]
        return count > 0

    def get_admission_stats(self, university_id: int = None, year: int = None) -> Dict[str, Any]:
        """获取录取数据统计 - 适配新表结构"""
        conditions = []
        params = []

        if university_id:
            conditions.append("university_id = ?")
            params.append(university_id)

        if year:
            conditions.append("year = ?")
            params.append(year)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT province) as province_count,
            COUNT(DISTINCT year) as year_count,
            MIN(year) as min_year,
            MAX(year) as max_year
        FROM undergraduate_admissions
        WHERE {where_clause}
        """

        cursor = self.execute_query(query, tuple(params))
        result = cursor.fetchone()

        return {
            'total_records': result[0],
            'province_count': result[1],
            'year_count': result[2],
            'min_year': result[3],
            'max_year': result[4]
        }

    # 工具方法
    def create_backup(self, backup_path: str):
        """创建数据库备份"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"数据库备份已创建: {backup_path}")
        except Exception as e:
            logger.error(f"备份失败: {e}")
            raise

    def optimize_database(self):
        """优化数据库"""
        try:
            self.execute_query("VACUUM")
            self.execute_query("ANALYZE")
            self.commit()
            logger.info("数据库优化完成")
        except sqlite3.Error as e:
            logger.error(f"数据库优化失败: {e}")