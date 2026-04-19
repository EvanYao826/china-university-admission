import sqlite3
import os

db_path = "E:\\VSproject\\China-University-Admission\\data\\test_university.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("数据库检查:")
print("=" * 60)

# Check universities
cursor.execute("SELECT id, name FROM universities")
unis = cursor.fetchall()
print(f"1. universities表: {len(unis)} 条记录")
for uni in unis:
    print(f"   ID: {uni[0]}, 名称: {uni[1]}")

# Check admissions
cursor.execute("SELECT COUNT(*), MIN(min_score), MAX(min_score), MIN(min_rank), MAX(min_rank) FROM undergraduate_admissions")
stats = cursor.fetchone()
print(f"\n2. undergraduate_admissions表: {stats[0]} 条记录")
print(f"   分数范围: {stats[1]} - {stats[2]}")
print(f"   位次范围: {stats[3]} - {stats[4]}")

# Check sample data
cursor.execute("SELECT university_id, province, year, batch, major, min_score, min_rank FROM undergraduate_admissions LIMIT 5")
samples = cursor.fetchall()
print(f"\n3. 样本数据 (前{len(samples)}条):")
for sample in samples:
    major = sample[4][:20] + "..." if sample[4] and len(sample[4]) > 20 else sample[4]
    print(f"   学校ID: {sample[0]}, 省份: {sample[1]}, 年份: {sample[2]}, 批次: {sample[3]}")
    print(f"   专业: {major}, 分数: {sample[5]}, 位次: {sample[6]}")
    print()

conn.close()

print("=" * 60)
print("检查完成")