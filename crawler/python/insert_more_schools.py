"""
插入更多高校数据到数据库
"""
import sqlite3
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库连接
DB_PATH = r'E:\VSproject\China-University-Admission\data\university.db'

# 要插入的20所高校数据（新的高校）
new_schools = [
    {
        'name': '大连理工大学',
        'type': '理工',
        'level': '985 211 双一流',
        'province': '辽宁',
        'city': '大连市',
        'tags': '985工程',
        'website': 'https://www.dlut.edu.cn',
        'description': '大连理工大学（Dalian University of Technology），简称“大工”，位于辽宁省大连市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为中俄工科大学联盟、卓越大学联盟、中俄交通大学联盟、中国-西班牙大学联盟、中国人工智能教育联席会成员。'
    },
    {
        'name': '华南理工大学',
        'type': '理工',
        'level': '985 211 双一流',
        'province': '广东',
        'city': '广州市',
        'tags': '985工程',
        'website': 'https://www.scut.edu.cn',
        'description': '华南理工大学（South China University of Technology），简称“华工”，位于广东省广州市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、卓越法律人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为建筑老八校、卓越大学联盟、中俄工科大学联盟、中欧工程教育平台、粤港澳大湾区物流与供应链创新联盟成员。'
    },
    {
        'name': '中南大学',
        'type': '综合',
        'level': '985 211 双一流',
        'province': '湖南',
        'city': '长沙市',
        'tags': '985工程',
        'website': 'https://www.csu.edu.cn',
        'description': '中南大学（Central South University），简称“中南”，位于湖南省长沙市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、卓越医生教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为中俄交通大学联盟、中国-西班牙大学联盟、中国-中亚国家大学联盟、中俄综合性大学联盟、中俄工科大学联盟、长江-伏尔加河高校联盟成员。'
    },
    {
        'name': '西北工业大学',
        'type': '理工',
        'level': '985 211 双一流',
        'province': '陕西',
        'city': '西安市',
        'tags': '国防七子',
        'website': 'https://www.nwpu.edu.cn',
        'description': '西北工业大学（Northwestern Polytechnical University），简称“西工大”，位于陕西省西安市，是中华人民共和国工业和信息化部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为卓越大学联盟、中俄工科大学联盟、中俄交通大学联盟、中国-西班牙大学联盟、“一带一路”航天创新联盟成员。'
    },
    {
        'name': '同济大学',
        'type': '理工',
        'level': '985 211 双一流',
        'province': '上海',
        'city': '上海市',
        'tags': '985工程',
        'website': 'https://www.tongji.edu.cn',
        'description': '同济大学（Tongji University），简称“同济”，位于上海市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、卓越法律人才教育培养计划、卓越医生教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为建筑老八校、卓越大学联盟、中俄工科大学联盟、中欧工程教育平台、国际设计艺术院校联盟、环太平洋大学联盟、21世纪学术联盟、国际铁路联盟成员。'
    },
    {
        'name': '重庆大学',
        'type': '综合',
        'level': '985 211 双一流',
        'province': '重庆',
        'city': '重庆市',
        'tags': '985工程',
        'website': 'https://www.cqu.edu.cn',
        'description': '重庆大学（Chongqing University），简称“重大”，位于重庆市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、卓越法律人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为卓越大学联盟、中俄工科大学联盟、一带一路高校联盟、长江—伏尔加河高校联盟、中国-西班牙大学联盟成员。'
    },
    {
        'name': '中国农业大学',
        'type': '农林',
        'level': '985 211 双一流',
        'province': '北京',
        'city': '北京市',
        'tags': '985工程',
        'website': 'https://www.cau.edu.cn',
        'description': '中国农业大学（China Agricultural University），简称“中国农大”，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、卓越农林人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为北京高科大学联盟、丝绸之路农业教育科技创新联盟成员。'
    },
    {
        'name': '中国海洋大学',
        'type': '综合',
        'level': '985 211 双一流',
        'province': '山东',
        'city': '青岛市',
        'tags': '985工程',
        'website': 'https://www.ouc.edu.cn',
        'description': '中国海洋大学（Ocean University of China），简称“海大”，位于山东省青岛市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、卓越农林人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为国际涉海大学联盟、中国高校行星科学联盟成员。'
    },
    {
        'name': '北京师范大学',
        'type': '师范',
        'level': '985 211 双一流',
        'province': '北京',
        'city': '北京市',
        'tags': '985工程',
        'website': 'https://www.bnu.edu.cn',
        'description': '北京师范大学（Beijing Normal University），简称“北师大”，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越法律人才教育培养计划、卓越教师培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为中国高校行星科学联盟、京港大学联盟、粤港澳大湾区物流与供应链创新联盟成员。'
    },
    {
        'name': '华东师范大学',
        'type': '师范',
        'level': '985 211 双一流',
        'province': '上海',
        'city': '上海市',
        'tags': '985工程',
        'website': 'https://www.ecnu.edu.cn',
        'description': '华东师范大学（East China Normal University），简称“华东师大”，位于上海市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”和“985工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越教师培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为亚太国际教育协会、中日人文交流大学联盟、沪港大学联盟成员。'
    },
    {
        'name': '北京科技大学',
        'type': '理工',
        'level': '211 双一流',
        'province': '北京',
        'city': '北京市',
        'tags': '211工程',
        'website': 'https://www.ustb.edu.cn',
        'description': '北京科技大学（University of Science and Technology Beijing），简称“北科大”，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越工程师教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为北京高科大学联盟、卓越大学联盟、中俄工科大学联盟成员。'
    },
    {
        'name': '北京交通大学',
        'type': '理工',
        'level': '211 双一流',
        'province': '北京',
        'city': '北京市',
        'tags': '211工程',
        'website': 'https://www.bjtu.edu.cn',
        'description': '北京交通大学（Beijing Jiaotong University），简称“北京交大”，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越工程师教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为中俄交通大学联盟、中国-西班牙大学联盟成员。'
    },
    {
        'name': '北京邮电大学',
        'type': '理工',
        'level': '211 双一流',
        'province': '北京',
        'city': '北京市',
        'tags': '211工程',
        'website': 'https://www.bupt.edu.cn',
        'description': '北京邮电大学（Beijing University of Posts and Telecommunications），简称“北邮”，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越工程师教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为北京高科大学联盟成员。'
    },
    {
        'name': '北京化工大学',
        'type': '理工',
        'level': '211 双一流',
        'province': '北京',
        'city': '北京市',
        'tags': '211工程',
        'website': 'https://www.buct.edu.cn',
        'description': '北京化工大学（Beijing University of Chemical Technology），简称“北化”，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越工程师教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为北京高科大学联盟成员。'
    },
    {
        'name': '北京外国语大学',
        'type': '语言',
        'level': '211 双一流',
        'province': '北京',
        'city': '北京市',
        'tags': '211工程',
        'website': 'https://www.bfsu.edu.cn',
        'description': '北京外国语大学（Beijing Foreign Studies University），简称“北外”，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越法律人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为国际大学翻译学院联合会、国际高等教育协会成员。'
    },
    {
        'name': '上海外国语大学',
        'type': '语言',
        'level': '211 双一流',
        'province': '上海',
        'city': '上海市',
        'tags': '211工程',
        'website': 'https://www.shisu.edu.cn',
        'description': '上海外国语大学（Shanghai International Studies University），简称“上外”，位于上海市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越法律人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为国际大学翻译学院联合会、国际高等教育协会成员。'
    },
    {
        'name': '上海财经大学',
        'type': '财经',
        'level': '211 双一流',
        'province': '上海',
        'city': '上海市',
        'tags': '211工程',
        'website': 'https://www.shufe.edu.cn',
        'description': '上海财经大学（Shanghai University of Finance and Economics），简称“上海财大”，位于上海市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越法律人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为中国金融教育发展基金会、中国会计学会、中国审计学会成员。'
    },
    {
        'name': '中央财经大学',
        'type': '财经',
        'level': '211 双一流',
        'province': '北京',
        'city': '北京市',
        'tags': '211工程',
        'website': 'https://www.cufe.edu.cn',
        'description': '中央财经大学（Central University of Finance and Economics），简称“中央财大”，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越法律人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为中国金融教育发展基金会、中国会计学会、中国审计学会成员。'
    },
    {
        'name': '对外经济贸易大学',
        'type': '财经',
        'level': '211 双一流',
        'province': '北京',
        'city': '北京市',
        'tags': '211工程',
        'website': 'https://www.uibe.edu.cn',
        'description': '对外经济贸易大学（University of International Business and Economics），简称“贸大”，位于北京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越法律人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为中国金融教育发展基金会、中国会计学会、中国审计学会成员。'
    },
    {
        'name': '西南财经大学',
        'type': '财经',
        'level': '211 双一流',
        'province': '四川',
        'city': '成都市',
        'tags': '211工程',
        'website': 'https://www.swufe.edu.cn',
        'description': '西南财经大学（Southwestern University of Finance and Economics），简称“西财”，位于四川省成都市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”建设高校、国家“211工程”重点建设高校，入选国家“111计划”、卓越法律人才教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，为中国金融教育发展基金会、中国会计学会、中国审计学会成员。'
    }
]

def insert_schools():
    """插入高校数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        for school in new_schools:
            # 检查高校是否已存在
            cursor.execute("SELECT id FROM universities WHERE name = ?", (school['name'],))
            if cursor.fetchone():
                logger.info(f"高校已存在: {school['name']}")
                continue
            
            # 插入高校信息
            insert_query = """
            INSERT INTO universities (name, type, level, province, city, tags, website, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                school['name'],
                school['type'],
                school['level'],
                school['province'],
                school['city'],
                school['tags'],
                school['website'],
                school['description']
            ))
            
            logger.info(f"插入高校成功: {school['name']}")
        
        conn.commit()
        logger.info("所有高校数据插入完成")
        
    except Exception as e:
        logger.error(f"插入高校数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_insert():
    """验证插入结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查询最新插入的高校
        cursor.execute("SELECT id, name, province FROM universities ORDER BY id DESC LIMIT 20;")
        results = cursor.fetchall()
        
        logger.info("\n验证插入结果:")
        for row in results:
            school_id, name, province = row
            logger.info(f"ID: {school_id}, 名称: {name}, 省份: {province}")
        
        # 查询总记录数
        cursor.execute("SELECT COUNT(*) FROM universities;")
        total = cursor.fetchone()[0]
        logger.info(f"\n数据库中共有 {total} 所高校")
        
    except Exception as e:
        logger.error(f"验证失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("开始插入高校数据...")
    insert_schools()
    verify_insert()
    logger.info("插入完成！")
