"""
简单测试数据库连接
"""
import sqlite3
import os

db_path = r'E:\VSproject\China-University-Admission\data\test_university.db'

print(f"测试数据库: {db_path}")
print(f"文件存在: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print(f"找到 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table[0]}")

            # 检查表结构
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print(f"    列: {[col[1] for col in columns]}")

        conn.close()
        print("数据库连接成功")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
else:
    print("数据库文件不存在")