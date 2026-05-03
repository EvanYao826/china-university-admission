# -*- coding: utf-8 -*-
"""
逐校批量导入脚本：从百度高考 API 获取 2023-2025 年全国高校录取分数线

数据来源: gaokao.baidu.com
目标表: undergraduate_admissions
运行方式: python fetch_all_admissions.py

功能:
  - 以 universities 表中高校为主序，年份(23/24/25)为次序
  - 遍历全国 31 个省份
  - 3+3 省份查 "3+3综合"，3+1+2 省份分别查 "物理类" 和 "历史类"
  - 自动跳过已存在记录（断点续传）
  - 进度保存到 progress.json，可中断后继续
  - 每所学校完成后打印汇总

预估耗时: 每校约 60-90 秒，1167 校约 20-25 小时
建议分批运行，或后台执行
"""

import sys
import os
import io

# Windows 控制台 UTF-8
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

DB_PATH = r"E:\VSproject\China-University-Admission\data\test.db"
PROGRESS_FILE = r"E:\VSproject\China-University-Admission\data\fetch_progress.json"

# 获取年份
YEARS = [2023, 2024, 2025]

# 请求间隔（秒），避免被封
REQUEST_DELAY = 0.5
# 每所学校完成后额外等待（秒）
SCHOOL_DELAY = 1.0
# 无数据时的等待（秒）
NO_DATA_DELAY = 0.3

# 百度高考 API
API_BASE = "https://gaokao.baidu.com/gk/gkschool/schoolscore"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://gaokao.baidu.com/",
}

# ==================== 省份配置 ====================

ALL_PROVINCES = [
    "北京", "天津", "上海", "浙江", "山东", "海南",
    "河北", "辽宁", "江苏", "福建", "湖北", "湖南", "广东", "重庆",
    "黑龙江", "甘肃", "吉林", "安徽", "江西", "贵州", "广西",
    "山西", "河南", "陕西", "内蒙古", "四川", "云南", "宁夏", "青海",
    "新疆", "西藏",
]

PROVINCES_3_3 = {"北京", "天津", "上海", "浙江", "山东", "海南"}
PROVINCES_3_1_2 = {
    "河北", "辽宁", "江苏", "福建", "湖北", "湖南", "广东", "重庆",
    "黑龙江", "甘肃", "吉林", "安徽", "江西", "贵州", "广西",
    "山西", "河南", "陕西", "内蒙古", "四川", "云南", "宁夏", "青海", "新疆",
}


def get_curriculum_queries(province):
    """返回该省份需要查询的 curriculum 列表"""
    if province in PROVINCES_3_3:
        return ["3+3综合"]
    elif province in PROVINCES_3_1_2:
        return ["物理类", "历史类"]
    else:
        return [""]


# ==================== 进度管理 ====================

def load_progress():
    """加载进度文件，返回已处理到的 university_id"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("last_university_id", 0), data.get("stats", {})
    return 0, {}


def save_progress(university_id, stats):
    """保存进度"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "last_university_id": university_id,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": stats,
        }, f, ensure_ascii=False, indent=2)


# ==================== API ====================

def fetch_school_score(school, province, year, curriculum=""):
    """调用百度高考 API"""
    params = {"school": school, "province": province, "year": year}
    if curriculum:
        params["curriculum"] = curriculum

    try:
        resp = requests.get(API_BASE, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if data.get("errno") != 0:
            return []

        dl = data.get("data", {}).get("school_score", {}).get("dataList")
        return dl if dl else []

    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.RequestException:
        return []
    except (json.JSONDecodeError, KeyError):
        return []


# ==================== 数据库 ====================

def get_all_universities(db_path):
    """获取所有高校，按 id 排序"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM universities ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def record_exists(db_path, uid, province, year, category, batch):
    """检查记录是否已存在"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM undergraduate_admissions 
        WHERE university_id=? AND province=? AND year=? AND category=? AND batch=?
    """, (uid, province, year, category, batch))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def batch_insert(db_path, uid, records, province):
    """批量插入记录，返回新增条数"""
    if not records:
        return 0

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0

    for rec in records:
        category = rec.get("curriculum", "")
        batch_name = rec.get("batchName", "")

        # 检查重复
        cur.execute("""
            SELECT COUNT(*) FROM undergraduate_admissions 
            WHERE university_id=? AND province=? AND year=? AND category=? AND batch=?
        """, (uid, province, int(rec.get("year", 0)), category, batch_name))
        if cur.fetchone()[0] > 0:
            continue

        # 解析数值
        min_score = None
        if rec.get("minScore"):
            try:
                min_score = float(rec["minScore"])
            except (ValueError, TypeError):
                pass

        min_rank = None
        if rec.get("minScoreOrder"):
            try:
                min_rank = int(rec["minScoreOrder"])
            except (ValueError, TypeError):
                pass

        pcl = None
        if rec.get("minCha"):
            try:
                pcl = float(rec["minCha"])
            except (ValueError, TypeError):
                pass

        enroll_type = rec.get("enrollType", "")
        year = int(rec.get("year", 0))

        cur.execute("""
            INSERT INTO undergraduate_admissions 
            (university_id, province, year, category, batch, enrollment_type,
             min_score, min_rank, provincial_control_line,
             source_url, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (uid, province, year, category, batch_name, enroll_type,
              min_score, min_rank, pcl,
              "gaokao.baidu.com/schoolscore", now, now))
        inserted += 1

    conn.commit()
    conn.close()
    return inserted


# ==================== 主流程 ====================

def process_one_school(uid, school_name):
    """处理一所高校，返回 (新增数, 跳过数, API调用数)"""
    total_new = 0
    total_skip = 0
    api_calls = 0
    has_any_data = False

    for year in YEARS:
        for province in ALL_PROVINCES:
            queries = get_curriculum_queries(province)
            for cur in queries:
                api_calls += 1
                data = fetch_school_score(school_name, province, year, cur)

                if not data:
                    time.sleep(NO_DATA_DELAY)
                    continue

                has_any_data = True

                # 批量插入
                new = batch_insert(DB_PATH, uid, data, province)
                total_new += new

                # 统计跳过的
                skip = len(data) - new
                total_skip += skip

                # 有数据时的间隔
                time.sleep(REQUEST_DELAY)

    return total_new, total_skip, api_calls, has_any_data


def main():
    print("=" * 60)
    print("  逐校批量导入 - 百度高考 2023-2025")
    print("=" * 60)

    # 加载高校列表
    universities = get_all_universities(DB_PATH)
    total_schools = len(universities)
    print(f"\n  数据库中共 {total_schools} 所高校")

    # 加载进度
    last_id, stats = load_progress()
    if last_id > 0:
        print(f"  上次处理到 university_id = {last_id}，从此处继续")
    else:
        print(f"  从头开始")

    # 统计
    grand_total_new = stats.get("total_new", 0)
    grand_total_skip = stats.get("total_skip", 0)
    grand_total_api = stats.get("total_api_calls", 0)
    schools_done = stats.get("schools_done", 0)
    schools_with_data = stats.get("schools_with_data", 0)

    start_time = datetime.now()
    processed_this_run = 0

    for idx, (uid, school_name) in enumerate(universities, 1):
        # 跳过已处理的
        if uid <= last_id:
            continue

        processed_this_run += 1
        schools_done += 1

        print(f"\n  [{schools_done}/{total_schools}] {school_name} (id={uid})")
        print(f"      年份: {YEARS}, 省份: {len(ALL_PROVINCES)}个", flush=True)

        t0 = time.time()
        new, skip, api_calls, has_data = process_one_school(uid, school_name)
        elapsed = time.time() - t0

        grand_total_new += new
        grand_total_skip += skip
        grand_total_api += api_calls

        if has_data:
            schools_with_data += 1

        # 每所学校完成后打印
        if new > 0 or skip > 0:
            print(f"      +{new} 新增, {skip} 跳过, {api_calls} 次API, {elapsed:.1f}s")
        else:
            print(f"      无数据 ({api_calls} 次API, {elapsed:.1f}s)")

        # 保存进度（每所学校）
        save_progress(uid, {
            "total_new": grand_total_new,
            "total_skip": grand_total_skip,
            "total_api_calls": grand_total_api,
            "schools_done": schools_done,
            "schools_with_data": schools_with_data,
        })

        # 每所学校之间的间隔
        time.sleep(SCHOOL_DELAY)

        # 每 50 打印中间汇总
        if processed_this_run % 50 == 0:
            elapsed_total = (datetime.now() - start_time).total_seconds()
            print(f"\n  --- 中间汇总 ({processed_this_run} 所) ---")
            print(f"  新增: {grand_total_new}, 跳过: {grand_total_skip}")
            print(f"  有数据高校: {schools_with_data}/{schools_done}")
            print(f"  本轮耗时: {elapsed_total/60:.1f} 分钟")
            print(f"  " + "-" * 40)

    # 最终汇总
    elapsed_total = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("  最终汇总")
    print("=" * 60)
    print(f"  本次处理: {processed_this_run} 所高校")
    print(f"  累计处理: {schools_done}/{total_schools} 所高校")
    print(f"  有数据高校: {schools_with_data}")
    print(f"  累计新增: {grand_total_new} 条")
    print(f"  累计跳过: {grand_total_skip} 条")
    print(f"  累计API调用: {grand_total_api} 次")
    print(f"  本轮耗时: {elapsed_total/60:.1f} 分钟")

    # 验证数据库总量
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM undergraduate_admissions")
    total_records = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT university_id) FROM undergraduate_admissions")
    total_uni = cur.fetchone()[0]
    conn.close()
    print(f"\n  数据库总记录: {total_records}")
    print(f"  有记录高校数: {total_uni}")

    print("\n  完成!")


if __name__ == "__main__":
    main()
