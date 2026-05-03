# -*- coding: utf-8 -*-
"""
测试脚本：获取浙江大学2025年全国各省份录取分数线，写入 test.db

数据来源：百度高考 API (gaokao.baidu.com)
目标表：undergraduate_admissions

运行方式：python test_fetch_zju.py

省份分类：
- 3+3综合：北京、天津、上海、浙江、山东、海南 -> curriculum="3+3综合"
- 3+1+2：河北、辽宁、江苏、福建、湖北、湖南、广东、重庆等
         -> 需要分两次查询：curriculum="物理类" 和 curriculum="历史类"
- 文理分科：西藏 -> curriculum=""（默认）
"""

import sys
import os
import io

# Windows 控制台 UTF-8 处理
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import json
import sqlite3
import time
from datetime import datetime

# ==================== 配置 ====================

TARGET_SCHOOL = "浙江大学"
TARGET_YEAR = 2025
DB_PATH = r"E:\VSproject\China-University-Admission\data\test.db"

API_BASE = "https://gaokao.baidu.com/gk/gkschool/schoolscore"

ALL_PROVINCES = [
    "北京", "天津", "上海", "浙江", "山东", "海南",
    "河北", "辽宁", "江苏", "福建", "湖北", "湖南", "广东", "重庆",
    "黑龙江", "甘肃", "吉林", "安徽", "江西", "贵州", "广西",
    "山西", "河南", "陕西", "内蒙古", "四川", "云南", "宁夏", "青海",
    "新疆", "西藏",
]

# 3+3综合省份
PROVINCES_3_3 = {"北京", "天津", "上海", "浙江", "山东", "海南"}
# 3+1+2省份（需要分"物理类"和"历史类"两次查询）
PROVINCES_3_1_2 = {
    "河北", "辽宁", "江苏", "福建", "湖北", "湖南", "广东", "重庆",
    "黑龙江", "甘肃", "吉林", "安徽", "江西", "贵州", "广西",
    "山西", "河南", "陕西", "内蒙古", "四川", "云南", "宁夏", "青海", "新疆",
}


def get_curriculum_queries(province):
    """
    返回该省份需要查询的 curriculum 列表。
    3+3省份 -> ["3+3综合"]
    3+1+2省份 -> ["物理类", "历史类"]
    文理分科 -> [""]
    """
    if province in PROVINCES_3_3:
        return ["3+3综合"]
    elif province in PROVINCES_3_1_2:
        return ["物理类", "历史类"]
    else:
        return [""]


# ==================== API ====================

def fetch_school_score(school, province, year, curriculum=""):
    params = {"school": school, "province": province, "year": year}
    if curriculum:
        params["curriculum"] = curriculum

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://gaokao.baidu.com/",
    }

    try:
        resp = requests.get(API_BASE, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if data.get("errno") != 0:
            return []

        school_score = data.get("data", {}).get("school_score", {})
        data_list = school_score.get("dataList")
        return data_list if data_list else []

    except requests.exceptions.Timeout:
        print(f"      [超时] {province} {curriculum}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"      [网络错误] {province} {curriculum}: {e}")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"      [解析错误] {province} {curriculum}: {e}")
        return []


# ==================== DB ====================

def get_university_id(db_path, school_name):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM universities WHERE name = ?", (school_name,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    raise ValueError(f"universities 表中未找到 '{school_name}'")


def record_exists(db_path, university_id, province, year, category, batch):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM undergraduate_admissions 
        WHERE university_id = ? AND province = ? AND year = ? 
          AND category = ? AND batch = ?
    """, (university_id, province, year, category, batch))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def insert_admission(db_path, university_id, record, province):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    category = record.get("curriculum", "")
    batch_name = record.get("batchName", "")
    enroll_type = record.get("enrollType", "")

    min_score = None
    if record.get("minScore"):
        try:
            min_score = float(record["minScore"])
        except (ValueError, TypeError):
            pass

    min_rank = None
    if record.get("minScoreOrder"):
        try:
            min_rank = int(record["minScoreOrder"])
        except (ValueError, TypeError):
            pass

    provincial_control_line = None
    if record.get("minCha"):
        try:
            provincial_control_line = float(record["minCha"])
        except (ValueError, TypeError):
            pass

    year = int(record.get("year", TARGET_YEAR))

    cur.execute("""
        INSERT INTO undergraduate_admissions 
        (university_id, province, year, category, batch, enrollment_type, 
         min_score, min_rank, provincial_control_line, 
         source_url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        university_id, province, year, category, batch_name, enroll_type,
        min_score, min_rank, provincial_control_line,
        "gaokao.baidu.com/schoolscore", now, now
    ))

    conn.commit()
    conn.close()


# ==================== Main ====================

def main():
    print("=" * 60)
    print(f"  获取 {TARGET_SCHOOL} {TARGET_YEAR}年全国录取分数线")
    print("=" * 60)

    try:
        uid = get_university_id(DB_PATH, TARGET_SCHOOL)
        print(f"\n[OK] {TARGET_SCHOOL} university_id = {uid}")
    except ValueError as e:
        print(f"\n[ERR] {e}")
        sys.exit(1)

    total_inserted = 0
    total_skipped = 0
    total_no_data = 0
    results = []
    start_time = datetime.now()

    for i, province in enumerate(ALL_PROVINCES, 1):
        queries = get_curriculum_queries(province)
        province_label = "/".join(queries)
        print(f"\n[{i}/{len(ALL_PROVINCES)}] {province} (curriculum={province_label})")

        prov_inserted = 0
        prov_skipped = 0
        all_empty = True

        for cur in queries:
            data_list = fetch_school_score(TARGET_SCHOOL, province, TARGET_YEAR, cur)
            if not data_list:
                continue
            all_empty = False

            for record in data_list:
                category = record.get("curriculum", "")
                batch_name = record.get("batchName", "")

                if record_exists(DB_PATH, uid, province, TARGET_YEAR, category, batch_name):
                    prov_skipped += 1
                    continue

                insert_admission(DB_PATH, uid, record, province)
                prov_inserted += 1

                ms = record.get("minScore", "-")
                mr = record.get("minScoreOrder", "-")
                et = record.get("enrollType", "")
                print(f"    + {batch_name} | {category} | {et} | 分:{ms} 位次:{mr}")

            time.sleep(0.5)

        total_inserted += prov_inserted
        total_skipped += prov_skipped

        if all_empty:
            total_no_data += 1
            results.append((province, 0, 0, "无数据"))
            print(f"    无数据")
        else:
            results.append((province, prov_inserted, prov_skipped, "OK"))
            print(f"    => +{prov_inserted} 跳过{prov_skipped}")

        time.sleep(0.5)

    # 汇总
    elapsed = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("  汇总报告")
    print("=" * 60)
    print(f"  学校: {TARGET_SCHOOL}")
    print(f"  年份: {TARGET_YEAR}")
    print(f"  省份数: {len(ALL_PROVINCES)}")
    print(f"  新增: {total_inserted} 条")
    print(f"  跳过重复: {total_skipped} 条")
    print(f"  无数据省份: {total_no_data} 个")
    print(f"  耗时: {elapsed:.1f} 秒")

    print(f"\n  {'省份':<6} {'新增':>4} {'跳过':>4}  {'状态'}")
    print("  " + "-" * 28)
    for prov, ins, skp, st in results:
        mark = "+" if ins > 0 or skp > 0 else "!"
        print(f"  {mark} {prov:<5} {ins:>4} {skp:>4}  {st}")

    # 验证数据库
    print("\n  验证数据库...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM undergraduate_admissions WHERE university_id = ?", (uid,))
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT province) FROM undergraduate_admissions WHERE university_id = ?", (uid,))
    prov_count = cur.fetchone()[0]
    print(f"  {TARGET_SCHOOL} 共 {total} 条记录，覆盖 {prov_count} 个省份")
    conn.close()

    print("\n完成!")


if __name__ == "__main__":
    main()
