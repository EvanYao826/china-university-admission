"""
修复Python模块导入问题
将相对导入改为绝对导入
"""
import os

# 修复 crawler.py
crawler_path = r'E:\VSproject\China-University-Admission\crawler\python\crawler.py'
with open(crawler_path, 'r', encoding='utf-8') as f:
    crawler_content = f.read()

crawler_content = crawler_content.replace('from .config import', 'from config import')

with open(crawler_path, 'w', encoding='utf-8') as f:
    f.write(crawler_content)

print("crawler.py 修复完成")

# 修复 database.py
database_path = r'E:\VSproject\China-University-Admission\crawler\python\database.py'
with open(database_path, 'r', encoding='utf-8') as f:
    database_content = f.read()

database_content = database_content.replace('from .config import', 'from config import')

with open(database_path, 'w', encoding='utf-8') as f:
    f.write(database_content)

print("database.py 修复完成")
print("所有导入问题已修复")
