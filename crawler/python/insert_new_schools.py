"""
添加新高校到数据库
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

# 新高校信息
new_schools = [
    {
        'name': '北京航空航天大学',
        'province': '北京',
        'city': '北京市海淀区',
        'type': '理工',
        'level': '985 211 双一流',
        'tags': '国防七子,985工程,211工程,双一流',
        'website': 'https://www.buaa.edu.cn',
        'description': '北京航空航天大学（Beihang University），简称“北航”，位于北京市，是中华人民共和国工业和信息化部直属的全国重点大学，位列国家“双一流”、“985工程”、“211工程”重点建设高校，入选珠峰计划、2011计划、111计划、卓越工程师教育培养计划、国家建设高水平大学公派研究生项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校、强基计划试点高校，为国际宇航联合会、中欧精英大学联盟、中国-西班牙大学联盟、中俄工科大学联盟、中国高校行星科学联盟、“一带路”航天创新联盟、国际航空航天教育协会成员。'
    },
    {
        'name': '北京理工大学',
        'province': '北京',
        'city': '北京市海淀区',
        'type': '理工',
        'level': '985 211 双一流',
        'tags': '国防七子,985工程,211工程,双一流',
        'website': 'https://www.bit.edu.cn',
        'description': '北京理工大学（Beijing Institute of Technology），简称“北理工”，位于北京市，是中华人民共和国工业和信息化部直属的全国重点大学，位列国家“双一流”、“985工程”、“211工程”，入选高等学校学科创新引智计划、高等学校创新能力提升计划、卓越工程师教育培养计划、国家建设高水平大学公派研究生项目、国家大学生创新性实验计划、国家级大学生创新创业训练计划、新工科研究与实践项目、中国政府奖学金来华留学生接收院校，是工业和信息化部高校联盟、卓越大学联盟、中俄工科大学联盟、北京高科大学联盟、中国人工智能教育联席会成员。'
    },
    {
        'name': '哈尔滨工业大学',
        'province': '黑龙江',
        'city': '哈尔滨市南岗区',
        'type': '理工',
        'level': '985 211 双一流',
        'tags': '国防七子,985工程,211工程,双一流,C9联盟',
        'website': 'https://www.hit.edu.cn',
        'description': '哈尔滨工业大学（Harbin Institute of Technology），简称“哈工大”，位于黑龙江省哈尔滨市，是中华人民共和国工业和信息化部直属的全国重点大学，位列国家“双一流”、“985工程”、“211工程”，九校联盟、环太平洋大学联盟、中国大学校长联谊会、卓越大学联盟、全球能源互联网大学联盟、中俄工科大学联盟、中国-西班牙大学联盟、中国-中东欧国家高校联合会、中国人工智能教育联席会成员。'
    },
    {
        'name': '中山大学',
        'province': '广东',
        'city': '广州市海珠区',
        'type': '综合',
        'level': '985 211 双一流',
        'tags': '985工程,211工程,双一流',
        'website': 'https://www.sysu.edu.cn',
        'description': '中山大学（Sun Yat-sen University），简称“中大”，位于广东省广州市，由中华人民共和国教育部直属，是教育部、国家国防科技工业局和广东省共建的综合性全国重点大学，位列国家“双一流”、“985工程”、“211工程”，入选国家“珠峰计划”、“111计划”、“2011计划”、卓越法律人才教育培养计划、卓越医生教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校、国家大学生文化素质教育基地、国家创新人才培养示范基地、国家国际科技合作基地、首批高等学校科技成果转化和技术转移基地，是环太平洋大学联盟、中国高校行星科学联盟、中国人工智能教育联席会、粤港澳高校联盟成员。'
    },
    {
        'name': '南开大学',
        'province': '天津',
        'city': '天津市南开区',
        'type': '综合',
        'level': '985 211 双一流',
        'tags': '985工程,211工程,双一流',
        'website': 'https://www.nankai.edu.cn',
        'description': '南开大学（Nankai University），简称“南开”，位于天津市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”、“985工程”、“211工程”重点建设高校，入选国家“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越法律人才教育培养计划、国家建设高水平大学公派研究生项目、全国深化创新创业教育改革示范高校、中国政府奖学金来华留学生接收院校、学位授权自主审核单位，为国际公立大学论坛成员，是“学府北辰”之一。'
    },
    {
        'name': '四川大学',
        'province': '四川',
        'city': '成都市武侯区',
        'type': '综合',
        'level': '985 211 双一流',
        'tags': '985工程,211工程,双一流',
        'website': 'https://www.scu.edu.cn',
        'description': '四川大学（Sichuan University），简称“川大”，位于四川省成都市，是中华人民共和国教育部直属、中央直管副部级建制的全国重点大学，是国家“双一流”、“985工程”、“211工程”重点建设高校，入选“珠峰计划”、“2011计划”、“111计划”、“强基计划”、卓越工程师教育培养计划、卓越医生教育培养计划、卓越法律人才教育培养计划、国家建设高水平大学公派研究生项目、全国深化创新创业教育改革示范高校，为学位授权自主审核单位、中国研究生院院长联席会成员、医学“双一流”建设联盟成员、自主划线高校，是国家布局在中国西部重点建设的高水平研究型综合大学。'
    },
    {
        'name': '山东大学',
        'province': '山东',
        'city': '济南市历下区',
        'type': '综合',
        'level': '985 211 双一流',
        'tags': '985工程,211工程,双一流',
        'website': 'https://www.sdu.edu.cn',
        'description': '山东大学（Shandong University），简称“山大”，位于山东省济南市，是中华人民共和国教育部直属的综合性全国重点大学，位列国家“双一流”、“985工程”、“211工程”，入选“2011计划”、“珠峰计划”、“强基计划”、“111计划”、卓越工程师教育培养计划、卓越医生教育培养计划、卓越法律人才教育培养计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、教育部来华留学示范基地、学位授权自主审核单位，为全球能源互联网大学联盟成员。'
    },
    {
        'name': '厦门大学',
        'province': '福建',
        'city': '厦门市思明区',
        'type': '综合',
        'level': '985 211 双一流',
        'tags': '985工程,211工程,双一流',
        'website': 'https://www.xmu.edu.cn',
        'description': '厦门大学（Xiamen University），简称“厦大”，位于福建省厦门市，是中华人民共和国教育部直属的全国重点大学，由教育部、福建省和厦门市共建，是国家“双一流”、“211工程”、“985工程”重点建设高校，入选国家“2011计划”、“珠峰计划”、“强基计划”、“111计划”、卓越工程师教育培养计划、卓越法律人才教育培养计划、卓越医生教育培养计划、国家建设高水平大学公派研究生项目、国家大学生文化素质教育基地，是全国首批深化创新创业教育改革示范高校，全国大学生创新创业实践联盟牵头发起高校，中欧商校联盟、中国人工智能教育联席会创始成员，大学通识教育联盟、CDIO工程教育联盟成员，被誉为“南方之强”。'
    },
    {
        'name': '东南大学',
        'province': '江苏',
        'city': '南京市玄武区',
        'type': '理工',
        'level': '985 211 双一流',
        'tags': '985工程,211工程,双一流',
        'website': 'https://www.seu.edu.cn',
        'description': '东南大学（Southeast University），简称“东大”，位于江苏省南京市，是中华人民共和国教育部直属的全国重点大学，是国家“双一流”、“985工程”、“211工程”重点建设高校，入选“2011计划”、“111计划”、卓越工程师教育培养计划、卓越医生教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、全国深化创新创业教育改革示范高校、中国政府奖学金来华留学生接收院校、教育部来华留学示范基地，是“建筑老八校”之一，是国务院首批批准可授予博士、硕士、学士学位的单位。'
    },
    {
        'name': '吉林大学',
        'province': '吉林',
        'city': '长春市朝阳区',
        'type': '综合',
        'level': '985 211 双一流',
        'tags': '985工程,211工程,双一流',
        'website': 'https://www.jlu.edu.cn',
        'description': '吉林大学（Jilin University），简称“吉大”，位于吉林省长春市，是中华人民共和国教育部直属的综合性全国重点大学，中央直管副部级建制，位列国家“双一流”、“211工程”、“985工程”，入选珠峰计划、2011计划、111计划、卓越法律人才教育培养计划、卓越工程师教育培养计划、卓越医生教育培养计划、国家建设高水平大学公派研究生项目、国家大学生创新性实验计划、新工科研究与实践项目、全国深化创新创业教育改革示范高校、中国政府奖学金来华留学生接收院校，为亚太国际教育协会、21世纪学术联盟、中俄交通大学联盟、粤港澳大湾区物流与供应链创新联盟成员。'
    }
]

def insert_new_schools():
    """插入新高校到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        for school in new_schools:
            # 检查是否已存在
            check_query = "SELECT id FROM universities WHERE name = ?"
            cursor.execute(check_query, (school['name'],))
            result = cursor.fetchone()
            
            if result:
                logger.info(f"高校已存在: {school['name']} (ID: {result[0]})")
                continue
            
            # 插入新高校
            insert_query = """
            INSERT INTO universities 
            (name, province, city, type, level, tags, website, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                school['name'],
                school['province'],
                school['city'],
                school['type'],
                school['level'],
                school['tags'],
                school['website'],
                school['description']
            ))
            
            logger.info(f"插入高校成功: {school['name']} (ID: {cursor.lastrowid})")
        
        conn.commit()
        logger.info("所有新高校插入完成")
        
    except Exception as e:
        logger.error(f"插入高校失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_insert():
    """验证插入结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查询所有高校信息
        cursor.execute("SELECT id, name, province, website, level FROM universities ORDER BY id DESC LIMIT 15")
        results = cursor.fetchall()
        
        logger.info("\n验证插入结果 (最新15所高校):")
        for row in results:
            school_id, name, province, website, level = row
            logger.info(f"ID: {school_id}, 名称: {name}, 省份: {province}, 网站: {website}, 层次: {level}")
        
        # 统计总数
        cursor.execute("SELECT COUNT(*) FROM universities")
        total = cursor.fetchone()[0]
        logger.info(f"\n数据库中共有 {total} 所高校")
        
    except Exception as e:
        logger.error(f"验证失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("开始插入新高校...")
    insert_new_schools()
    verify_insert()
    logger.info("插入完成！")
