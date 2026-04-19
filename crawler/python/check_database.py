#!/usr/bin/env python3
"""
检查数据库中的数据
"""
import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_database():
    db_path = "E:\\VSproject\\China-University-Admission\\data\\test_university.db"

    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("检查数据库中的数据")
    print("=" * 60)

    # 检查universities表
    print("1. universities表:")
    cursor.execute("SELECT id, name, province, type, level FROM universities")
    universities = cursor.fetchall()

    for uni in universities:
        print(f"   ID: {uni[0]}, 名称: {uni[1]}, 省份: {uni[2]}, 类型: {uni[3]}, 层次: {uni[4]}")

    # 检查undergraduate_admissions表
    print("\n2. undergraduate_admissions表:")
    cursor.execute("""
        SELECT id, university_id, province, year, category, batch,
               major, min_score, min_rank, enrollment_type
        FROM undergraduate_admissions
        ORDER BY year, batch, major
    """)
    admissions = cursor.fetchall()

    print(f"   共 {len(admissions)} 条记录:")
    for adm in admissions:
        major_display = adm[6][:30] + "..." if adm[6] and len(adm[6]) > 30 else adm[6]
        print(f"   ID: {adm[0]}, 学校ID: {adm[1]}, 省份: {adm[2]}, 年份: {adm[3]}")
        print(f"      科类: {adm[4]}, 批次: {adm[5]}, 专业: {major_display}")
        print(f"      分数: {adm[7]}, 位次: {adm[8]}, 类型: {adm[9]}")
        print()

    # 检查外键约束
    print("\n3. 外键约束检查:")
    cursor.execute("PRAGMA foreign_key_list(undergraduate_admissions)")
    fks = cursor.fetchall()

    if fks:
        for fk in fks:
            print(f"   {fk[3]} -> {fk[2]}.{fk[4]}")
    else:
        print("   未找到外键约束")

    # 检查数据完整性
    print("\n4. 数据完整性检查:")

    # 检查是否有无效的university_id
    cursor.execute("""
        SELECT DISTINCT university_id
        FROM undergraduate_admissions
        WHERE university_id NOT IN (SELECT id FROM universities)
    """)
    invalid_ids = cursor.fetchall()

    if invalid_ids:
        print(f"   警告: 找到无效的university_id: {invalid_ids}")
    else:
        print("   ✓ 所有university_id都有效")

    # 检查分数范围
    cursor.execute("""
        SELECT COUNT(*)
        FROM undergraduate_admissions
        WHERE min_score IS NOT NULL AND (min_score < 200 OR min_score > 750)
    """)
    invalid_scores = cursor.fetchone()[0]

    if invalid_scores > 0:
        print(f"   警告: 找到 {invalid_scores} 条记录的分数超出合理范围 (200-750)")
    else:
        print("   ✓ 所有分数都在合理范围内 (200-750)")

    # 检查位次范围
    cursor.execute("""
        SELECT COUNT(*)
        FROM undergraduate_admissions
        WHERE min_rank IS NOT NULL AND (min_rank < 1 OR min_rank > 1000000)
    """)
    invalid_ranks = cursor.fetchone()[0]

    if invalid_ranks > 0:
        print(f"   警告: 找到 {invalid_ranks} 条记录的位次超出合理范围 (1-1000000)")
    else:
        print("   ✓ 所有位次都在合理范围内 (1-1000000)")

    conn.close()

    print("\n" + "=" * 60)
    print("数据库检查完成")

if __name__ == "__main__":
    check_database()