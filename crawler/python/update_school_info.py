"""
补充高校详细信息到数据库
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

# 高校详细信息
school_info = {
    1: {
        'name': '清华大学',
        'website': 'https://www.tsinghua.edu.cn',
        'level': '985 211 双一流',
        'description': '清华大学（Tsinghua University），简称“清华”，位于北京市海淀区，是中华人民共和国教育部直属的全国重点大学，中央直管高校。由教育部与北京市重点共建。国家首批“双一流”A类、“985工程”、“211工程”重点建设高校，九校联盟、松联盟、中国大学校长联谊会、环太平洋大学联盟、亚洲大学联盟等成员，被誉为“红色工程师的摇篮”。'
    },
    2: {
        'name': '北京大学',
        'website': 'https://www.pku.edu.cn',
        'level': '985 211 双一流',
        'description': '北京大学（Peking University），简称“北大”，位于北京市海淀区，是中华人民共和国教育部直属的全国重点大学，中央直管高校。位列“双一流”、“985工程”、“211工程”，九校联盟、松联盟、中国大学校长联谊会、京港大学联盟、全球大学高研院联盟、亚洲大学联盟、东亚研究型大学协会、国际研究型大学联盟、环太平洋大学联盟、全球大学校长论坛、21世纪学术联盟、东亚四大学论坛、国际公立大学论坛等。'
    },
    3: {
        'name': '浙江大学',
        'website': 'https://www.zju.edu.cn',
        'level': '985 211 双一流',
        'description': '浙江大学（Zhejiang University），简称“浙大”，位于浙江省杭州市，是中华人民共和国教育部直属的综合性全国重点大学，中央直管副部级建制，位列“双一流”、“211工程”、“985工程”，九校联盟、环太平洋大学联盟、世界大学联盟、全球大学校长论坛、全球高校人工智能学术联盟、国际应用科技开发协作网、新工科教育国际联盟、全球能源互联网大学联盟、CDIO工程教育联盟、医学“双一流”建设联盟成员。'
    },
    4: {
        'name': '上海交通大学',
        'website': 'https://www.sjtu.edu.cn',
        'level': '985 211 双一流',
        'description': '上海交通大学（Shanghai Jiao Tong University），简称“上海交大”，位于上海市，是中华人民共和国教育部直属、中央直管副部级建制的综合性全国重点大学，位列“双一流”、“985工程”、“211工程”，九校联盟、环太平洋大学联盟、21世纪学术联盟、中国大学校长联谊会、国际应用科技开发协作网、新工科教育国际联盟、全球能源互联网大学联盟、CDIO工程教育联盟成员。'
    },
    5: {
        'name': '复旦大学',
        'website': 'https://www.fudan.edu.cn',
        'level': '985 211 双一流',
        'description': '复旦大学（Fudan University），简称“复旦”，位于上海市，是中华人民共和国教育部直属、中央直管副部级建制的全国重点大学，世界一流大学建设高校（A类），国家“985工程”、“211工程”重点建设高校，九校联盟、环太平洋大学联盟、中国大学校长联谊会、东亚研究型大学协会、新工科教育国际联盟、医学“双一流”建设联盟、长三角研究型大学联盟成员。'
    },
    6: {
        'name': '南京大学',
        'website': 'https://www.nju.edu.cn',
        'level': '985 211 双一流',
        'description': '南京大学（Nanjing University），简称“南大”，位于江苏省南京市，是中华人民共和国教育部直属的全国重点大学，中央直管副部级建制，位列“双一流”、“985工程”、“211工程”，九校联盟、中国大学校长联谊会、环太平洋大学联盟、21世纪学术联盟、国际应用科技开发协作网、东亚研究型大学协会、新工科教育国际联盟、全球能源互联网大学联盟成员。'
    },
    7: {
        'name': '华中科技大学',
        'website': 'https://www.hust.edu.cn',
        'level': '985 211 双一流',
        'description': '华中科技大学（Huazhong University of Science and Technology），简称“华科大”，位于湖北省武汉市，是中华人民共和国教育部直属的综合性研究型全国重点大学，中央直管副部级高校，国家“双一流”、“985工程”、“211工程”重点建设高校，入选“强基计划”、“111计划”、卓越工程师教育培养计划、卓越医生教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、全国深化创新创业教育改革示范高校、中国政府奖学金来华留学生接收院校、国家大学生文化素质教育基地、学位授权自主审核单位。'
    },
    8: {
        'name': '武汉大学',
        'website': 'https://www.whu.edu.cn',
        'level': '985 211 双一流',
        'description': '武汉大学（Wuhan University），简称“武大”，位于湖北省武汉市，是中华人民共和国教育部直属的综合性全国重点大学，位列“双一流”、“985工程”、“211工程”，入选“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、卓越法律人才教育培养计划、卓越医生教育培养计划、国家建设高水平大学公派研究生项目、国家级新工科研究与实践项目、国家级大学生创新创业训练计划、国家大学生文化素质教育基地、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校、国家大学生创新性实验计划，是九校联盟、中国大学校长联谊会、环太平洋大学联盟、卓越大学联盟、全球大学高研院联盟、亚太国际教育协会、中俄综合性大学联盟、CDIO工程教育联盟、医学“双一流”建设联盟成员。'
    },
    9: {
        'name': '西安交通大学',
        'website': 'https://www.xjtu.edu.cn',
        'level': '985 211 双一流',
        'description': '西安交通大学（Xi’an Jiaotong University），简称“西安交大”，位于陕西省西安市，是中华人民共和国教育部直属的综合性研究型全国重点大学，由教育部与国家国防科技工业局共建，位列国家“双一流”、“985工程”、“211工程”，入选“珠峰计划”、“强基计划”、“2011计划”、“111计划”、卓越工程师教育培养计划、卓越医生教育培养计划、国家大学生创新性实验计划、国家级大学生创新创业训练计划、国家建设高水平大学公派研究生项目、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校，是九校联盟、中国大学校长联谊会、环太平洋大学联盟、21世纪学术联盟、全球能源互联网大学联盟、中俄交通大学联盟、CDIO工程教育联盟、医学“双一流”建设联盟成员。'
    },
    10: {
        'name': '中国科学技术大学',
        'website': 'https://www.ustc.edu.cn',
        'level': '985 211 双一流',
        'description': '中国科学技术大学（University of Science and Technology of China），简称“中国科大”，位于安徽省合肥市，是中国科学院直属的一所以前沿科学和高新技术为主，兼有医学、特色管理和人文学科的综合性全国重点大学，中央直管副部级建制，由中国科学院、教育部和安徽省三方共建；位列国家“双一流”、“985工程”、“211工程”，入选“珠峰计划”、“强基计划”、“111计划”、“2011计划”、卓越工程师教育培养计划、中国政府奖学金来华留学生接收院校、国家建设高水平大学公派研究生项目、全国深化创新创业教育改革示范高校、中国科学院知识创新工程，是九校联盟、环太平洋大学联盟、中国大学校长联谊会、东亚研究型大学协会成员。'
    }
}

def update_school_info():
    """更新高校信息"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        for school_id, info in school_info.items():
            # 更新高校信息
            update_query = """
            UPDATE universities 
            SET website = ?, level = ?, description = ? 
            WHERE id = ?
            """
            cursor.execute(update_query, (
                info['website'],
                info['level'],
                info['description'],
                school_id
            ))
            
            logger.info(f"更新高校信息成功: {info['name']} (ID: {school_id})")
        
        conn.commit()
        logger.info("所有高校信息更新完成")
        
    except Exception as e:
        logger.error(f"更新高校信息失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_update():
    """验证更新结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查询所有高校信息
        cursor.execute("SELECT id, name, website, level FROM universities")
        results = cursor.fetchall()
        
        logger.info("\n验证更新结果:")
        for row in results:
            school_id, name, website, level = row
            logger.info(f"ID: {school_id}, 名称: {name}, 网站: {website}, 层次: {level}")
        
    except Exception as e:
        logger.error(f"验证失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("开始更新高校信息...")
    update_school_info()
    verify_update()
    logger.info("更新完成！")
