# -*- coding: utf-8 -*-
"""
批量导入 id=44-53 共10所高校的2023-2025录取数据

目标学校：
  44 北京化工大学
  45 北京外国语大学
  46 上海外国语大学
  47 上海财经大学
  48 中央财经大学
  49 对外经济贸易大学
  50 西南财经大学
  51 暨南大学
  52 华侨大学
  53 深圳大学
"""

import sys, os, io

TARGET_IDS = [44, 45, 46, 47, 48, 49, 50, 51, 52, 53]

if sys.platform == 'win32':
    try:
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests, json, sqlite3, time
from datetime import datetime

DB_PATH = r"E:\VSproject\China-University-Admission\data\test.db"
API_BASE = "https://gaokao.baidu.com/gk/gkschool/schoolscore"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://gaokao.baidu.com/",
}

YEARS = [2023, 2024, 2025]

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

def get_curriculums(province):
    if province in PROVINCES_3_3:
        return ["3+3综合"]
    elif province in PROVINCES_3_1_2:
        return ["物理类", "历史类"]
    else:
        return [""]

def fetch(school, province, year, cur=""):
    params = {"school": school, "province": province, "year": year}
    if cur:
        params["curriculum"] = cur
    try:
        resp = requests.get(API_BASE, params=params, headers=HEADERS, timeout=15)
        data = resp.json()
        if data.get("errno") != 0:
            return []
        dl = data.get("data", {}).get("school_score", {}).get("dataList")
        return dl if dl else []
    except:
        return []

def batch_insert(uid, records, province):
    if not records:
        return 0
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0

    for rec in records:
        category = rec.get("curriculum", "")
        batch_name = rec.get("batchName", "")
        year = int(rec.get("year", 0))

        cur.execute("""
            SELECT COUNT(*) FROM undergraduate_admissions 
            WHERE university_id=? AND province=? AND year=? AND category=? AND batch=?
        """, (uid, province, year, category, batch_name))
        if cur.fetchone()[0] > 0:
            continue

        min_score = None
        try: min_score = float(rec.get("minScore", ""))
        except: pass

        min_rank = None
        try: min_rank = int(rec.get("minScoreOrder", ""))
        except: pass

        pcl = None
        try: pcl = float(rec.get("minCha", ""))
        except: pass

        enroll_type = rec.get("enrollType", "")

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


def main():
    print("=" * 60)
    print("  10所高校(44-53) - 2023-2025录取数据导入")
    print("=" * 60)

    # 获取学校名
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    schools = []
    for uid in TARGET_IDS:
        cur.execute("SELECT name FROM universities WHERE id=?", (uid,))
        row = cur.fetchone()
        if row:
            schools.append((uid, row[0]))
    conn.close()

    print(f"\n  目标: {len(schools)} 所高校, 年份: {YEARS}")
    print(f"  省份: {len(ALL_PROVINCES)} 个")
    print(f"  预估API调用: ~{len(schools) * len(ALL_PROVINCES) * len(YEARS)} 次")
    print()

    grand_new = 0
    grand_skip = 0
    grand_api = 0
    t_start = datetime.now()

    for idx, (uid, name) in enumerate(schools, 1):
        print(f"  [{idx}/{len(schools)}] {name} (id={uid})", flush=True)

        school_new = 0
        school_skip = 0
        school_api = 0
        t0 = time.time()

        for year in YEARS:
            year_new = 0
            for province in ALL_PROVINCES:
                for cur in get_curriculums(province):
                    school_api += 1
                    data = fetch(name, province, year, cur)
                    if not data:
                        time.sleep(0.3)
                        continue
                    new = batch_insert(uid, data, province)
                    year_new += new
                    school_new += new
                    school_skip += len(data) - new
                    time.sleep(0.5)

            # 年份级打印
            if year_new > 0:
                print(f"      {year}年: +{year_new} 条", flush=True)

        grand_new += school_new
        grand_skip += school_skip
        grand_api += school_api
        elapsed = time.time() - t0

        if school_new > 0 or school_skip > 0:
            print(f"      => +{school_new} 新增, {school_skip} 跳过, {school_api}次API, {elapsed:.0f}s")
        else:
            print(f"      => 无数据, {school_api}次API, {elapsed:.0f}s")

        time.sleep(1)

    # 汇总
    elapsed = (datetime.now() - t_start).total_seconds()
    print("\n" + "=" * 60)
    print("  汇总")
    print("=" * 60)
    print(f"  处理: {len(schools)} 所高校")
    print(f"  新增: {grand_new} 条")
    print(f"  跳过: {grand_skip} 条")
    print(f"  API调用: {grand_api} 次")
    print(f"  耗时: {elapsed/60:.1f} 分钟")

    # 验证
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM undergraduate_admissions")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT university_id) FROM undergraduate_admissions")
    uni_count = cur.fetchone()[0]
    conn.close()
    print(f"\n  数据库总记录: {total}, 有记录高校数: {uni_count}")
    print("\n  完成!")


if __name__ == "__main__":
    main()
