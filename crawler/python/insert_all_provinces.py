"""
全国各省份高校批量插入脚本
按省份逐个插入，包含去重处理
"""
import sqlite3
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = r'E:\VSproject\China-University-Admission\data\university.db'

# 全国各省份高校数据
all_provinces_schools = {
    '北京': [
        {
            'name': '北京大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '北京',
            'city': '北京市',
            'tags': '985工程',
            'website': 'https://www.pku.edu.cn',
            'description': '北京大学（Peking University），简称"北大"，位于北京市海淀区，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '清华大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '北京',
            'city': '北京市',
            'tags': '985工程',
            'website': 'https://www.tsinghua.edu.cn',
            'description': '清华大学（Tsinghua University），简称"清华"，位于北京市海淀区，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '中国人民大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '北京',
            'city': '北京市',
            'tags': '985工程',
            'website': 'https://www.ruc.edu.cn',
            'description': '中国人民大学（Renmin University of China），简称"人大"，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        }
    ],
    '上海': [
        {
            'name': '复旦大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '上海',
            'city': '上海市',
            'tags': '985工程',
            'website': 'https://www.fudan.edu.cn',
            'description': '复旦大学（Fudan University），简称"复旦"，位于上海市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '上海交通大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '上海',
            'city': '上海市',
            'tags': '985工程',
            'website': 'https://www.sjtu.edu.cn',
            'description': '上海交通大学（Shanghai Jiao Tong University），简称"上海交大"，位于上海市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '同济大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '上海',
            'city': '上海市',
            'tags': '985工程',
            'website': 'https://www.tongji.edu.cn',
            'description': '同济大学（Tongji University），简称"同济"，位于上海市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        }
    ],
    '广东': [
        {
            'name': '中山大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '广东',
            'city': '广州市',
            'tags': '985工程',
            'website': 'https://www.sysu.edu.cn',
            'description': '中山大学（Sun Yat-sen University），简称"中大"，位于广东省广州市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '华南理工大学',
            'type': '理工',
            'level': '985 211 双一流',
            'province': '广东',
            'city': '广州市',
            'tags': '985工程',
            'website': 'https://www.scut.edu.cn',
            'description': '华南理工大学（South China University of Technology），简称"华南理工"，位于广东省广州市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '暨南大学',
            'type': '综合',
            'level': '211 双一流',
            'province': '广东',
            'city': '广州市',
            'tags': '211工程',
            'website': 'https://www.jnu.edu.cn',
            'description': '暨南大学（Jinan University），简称"暨大"，位于广东省广州市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"重点建设高校。'
        }
    ],
    '江苏': [
        {
            'name': '南京大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '江苏',
            'city': '南京市',
            'tags': '985工程',
            'website': 'https://www.nju.edu.cn',
            'description': '南京大学（Nanjing University），简称"南大"，位于江苏省南京市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '东南大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '江苏',
            'city': '南京市',
            'tags': '985工程',
            'website': 'https://www.seu.edu.cn',
            'description': '东南大学（Southeast University），简称"东大"，位于江苏省南京市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '南京航空航天大学',
            'type': '理工',
            'level': '211 双一流',
            'province': '江苏',
            'city': '南京市',
            'tags': '211工程',
            'website': 'https://www.nuaa.edu.cn',
            'description': '南京航空航天大学（Nanjing University of Aeronautics and Astronautics），简称"南航"，位于江苏省南京市，是中华人民共和国工业和信息化部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"重点建设高校。'
        }
    ],
    '浙江': [
        {
            'name': '浙江大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '浙江',
            'city': '杭州市',
            'tags': '985工程',
            'website': 'https://www.zju.edu.cn',
            'description': '浙江大学（Zhejiang University），简称"浙大"，位于浙江省杭州市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '宁波大学',
            'type': '综合',
            'level': '211 双一流',
            'province': '浙江',
            'city': '宁波市',
            'tags': '211工程',
            'website': 'https://www.nbu.edu.cn',
            'description': '宁波大学（Ningbo University），简称"宁大"，位于浙江省宁波市，是浙江省人民政府与中华人民共和国教育部共建的全国重点大学，是国家"双一流"建设高校、国家"211工程"重点建设高校。'
        },
        {
            'name': '浙江工业大学',
            'type': '理工',
            'level': '普通本科',
            'province': '浙江',
            'city': '杭州市',
            'tags': '地方高水平大学',
            'website': 'https://www.zjut.edu.cn',
            'description': '浙江工业大学（Zhejiang University of Technology），简称"浙工大"，位于浙江省杭州市，是浙江省人民政府与中华人民共和国教育部共建的全国重点大学，入选"111计划"、卓越工程师教育培养计划。'
        }
    ],
    '四川': [
        {
            'name': '四川大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '四川',
            'city': '成都市',
            'tags': '985工程',
            'website': 'https://www.scu.edu.cn',
            'description': '四川大学（Sichuan University），简称"川大"，位于四川省成都市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '电子科技大学',
            'type': '理工',
            'level': '985 211 双一流',
            'province': '四川',
            'city': '成都市',
            'tags': '985工程',
            'website': 'https://www.uestc.edu.cn',
            'description': '电子科技大学（University of Electronic Science and Technology of China），简称"电子科大"，位于四川省成都市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '西南交通大学',
            'type': '理工',
            'level': '211 双一流',
            'province': '四川',
            'city': '成都市',
            'tags': '211工程',
            'website': 'https://www.swjtu.edu.cn',
            'description': '西南交通大学（Southwest Jiaotong University），简称"西南交大"，位于四川省成都市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"重点建设高校。'
        }
    ],
    '湖北': [
        {
            'name': '武汉大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '湖北',
            'city': '武汉市',
            'tags': '985工程',
            'website': 'https://www.whu.edu.cn',
            'description': '武汉大学（Wuhan University），简称"武大"，位于湖北省武汉市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '华中科技大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '湖北',
            'city': '武汉市',
            'tags': '985工程',
            'website': 'https://www.hust.edu.cn',
            'description': '华中科技大学（Huazhong University of Science and Technology），简称"华中大"，位于湖北省武汉市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '武汉理工大学',
            'type': '理工',
            'level': '211 双一流',
            'province': '湖北',
            'city': '武汉市',
            'tags': '211工程',
            'website': 'https://www.whut.edu.cn',
            'description': '武汉理工大学（Wuhan University of Technology），简称"武汉理工"，位于湖北省武汉市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"重点建设高校。'
        }
    ],
    '湖南': [
        {
            'name': '中南大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '湖南',
            'city': '长沙市',
            'tags': '985工程',
            'website': 'https://www.csu.edu.cn',
            'description': '中南大学（Central South University），简称"中南"，位于湖南省长沙市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '湖南大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '湖南',
            'city': '长沙市',
            'tags': '985工程',
            'website': 'https://www.hnu.edu.cn',
            'description': '湖南大学（Hunan University），简称"湖大"，位于湖南省长沙市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '湖南师范大学',
            'type': '师范',
            'level': '211 双一流',
            'province': '湖南',
            'city': '长沙市',
            'tags': '211工程',
            'website': 'https://www.hunnu.edu.cn',
            'description': '湖南师范大学（Hunan Normal University），简称"湖南师大"，位于湖南省长沙市，是湖南省人民政府与中华人民共和国教育部共建的全国重点大学，是国家"双一流"建设高校、国家"211工程"重点建设高校。'
        }
    ],
    '山东': [
        {
            'name': '山东大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '山东',
            'city': '济南市',
            'tags': '985工程',
            'website': 'https://www.sdu.edu.cn',
            'description': '山东大学（Shandong University），简称"山大"，位于山东省济南市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '中国海洋大学',
            'type': '农林',
            'level': '985 211 双一流',
            'province': '山东',
            'city': '青岛市',
            'tags': '985工程',
            'website': 'https://www.ouc.edu.cn',
            'description': '中国海洋大学（Ocean University of China），简称"中国海大"，位于山东省青岛市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '中国石油大学（华东）',
            'type': '理工',
            'level': '211 双一流',
            'province': '山东',
            'city': '青岛市',
            'tags': '211工程',
            'website': 'https://www.upc.edu.cn',
            'description': '中国石油大学（华东）（China University of Petroleum (East China)），简称"中石大（华东）"，位于山东省青岛市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"重点建设高校。'
        }
    ],
    '陕西': [
        {
            'name': '西安交通大学',
            'type': '综合',
            'level': '985 211 双一流',
            'province': '陕西',
            'city': '西安市',
            'tags': '985工程',
            'website': 'https://www.xjtu.edu.cn',
            'description': '西安交通大学（Xi\'an Jiaotong University），简称"西安交大"，位于陕西省西安市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '西北工业大学',
            'type': '理工',
            'level': '985 211 双一流',
            'province': '陕西',
            'city': '西安市',
            'tags': '985工程',
            'website': 'https://www.nwpu.edu.cn',
            'description': '西北工业大学（Northwestern Polytechnical University），简称"西工大"，位于陕西省西安市，是中华人民共和国工业和信息化部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"和"985工程"重点建设高校。'
        },
        {
            'name': '西安电子科技大学',
            'type': '理工',
            'level': '211 双一流',
            'province': '陕西',
            'city': '西安市',
            'tags': '211工程',
            'website': 'https://www.xidian.edu.cn',
            'description': '西安电子科技大学（Xidian University），简称"西电"，位于陕西省西安市，是中华人民共和国教育部直属的全国重点大学，是国家"双一流"建设高校、国家"211工程"重点建设高校。'
        }
    ]
}

def insert_province_schools(province, schools):
    """插入单个省份的高校数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        conn.execute('BEGIN TRANSACTION')
        
        cursor.execute("SELECT name FROM universities")
        existing_schools = set(row[0] for row in cursor.fetchall())
        
        # 使用字典去重，以name为key
        unique_schools = {}
        for school in schools:
            if school['name'] not in unique_schools:
                unique_schools[school['name']] = school
        
        new_schools = [school for school in unique_schools.values() if school['name'] not in existing_schools]
        logger.info(f"{province}：准备插入 {len(new_schools)} 所新高校（去重后）")
        
        if not new_schools:
            logger.info(f"{province}：没有新高校需要插入")
            return 0
        
        insert_query = """
        INSERT INTO universities (name, type, level, province, city, tags, website, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        data = []
        for school in new_schools:
            data.append((
                school['name'],
                school['type'],
                school['level'],
                school['province'],
                school['city'],
                school['tags'],
                school['website'],
                school['description']
            ))
        
        cursor.executemany(insert_query, data)
        conn.commit()
        
        logger.info(f"{province}：成功插入 {len(new_schools)} 所高校")
        return len(new_schools)
        
    except Exception as e:
        logger.error(f"{province}：插入失败: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def verify_insert():
    """验证插入结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM universities;")
        total = cursor.fetchone()[0]
        logger.info(f"\n数据库中共有 {total} 所高校")
        
        # 各省份高校数量
        cursor.execute("SELECT province, COUNT(*) FROM universities GROUP BY province ORDER BY COUNT(*) DESC;")
        province_counts = cursor.fetchall()
        
        logger.info("\n各省份高校数量:")
        for province, count in province_counts:
            print(f'{province}: {count} 所')
        
    except Exception as e:
        logger.error(f"验证失败: {e}")
    finally:
        conn.close()

def main():
    """主函数：按省份逐个插入高校数据"""
    logger.info("开始按省份批量插入全国高校数据...")
    
    total_inserted = 0
    for province, schools in all_provinces_schools.items():
        logger.info(f"\n处理 {province}...")
        inserted = insert_province_schools(province, schools)
        total_inserted += inserted
    
    logger.info(f"\n批量插入完成！总共成功插入 {total_inserted} 所高校")
    verify_insert()
    logger.info("全国高校数据插入完成！")

if __name__ == "__main__":
    main()
