-- 中国高校录取数据查询系统数据库结构
-- 版本：1.0.0
-- 创建日期：2024-01-01

-- 高校基本信息表
CREATE TABLE universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    province TEXT NOT NULL,
    city TEXT NOT NULL,
    type TEXT CHECK(type IN ('综合', '理工', '师范', '农林', '医药', '财经', '政法', '艺术', '体育', '民族', '语言', '其他')) NOT NULL,
    level TEXT CHECK(level IN ('985', '211', '双一流', '普通本科', '专科')) NOT NULL,
    website TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 高考录取数据表
CREATE TABLE gaokao_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    province TEXT NOT NULL,
    category TEXT CHECK(category IN ('文科', '理科', '综合改革', '艺术', '体育')) NOT NULL,
    batch TEXT CHECK(batch IN ('本科一批', '本科二批', '专科批', '提前批')) NOT NULL,
    min_score REAL,
    avg_score REAL,
    max_score REAL,
    min_rank INTEGER,
    avg_rank INTEGER,
    max_rank INTEGER,
    admission_count INTEGER,
    major TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, year, province, category, batch, major)
);

-- 研究生录取数据表
CREATE TABLE graduate_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    major TEXT NOT NULL,
    degree_type TEXT CHECK(degree_type IN ('硕士', '博士')) NOT NULL,
    study_mode TEXT CHECK(study_mode IN ('全日制', '非全日制')) NOT NULL,
    admission_count INTEGER NOT NULL,
    min_score REAL,
    avg_score REAL,
    max_score REAL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, year, major, degree_type, study_mode)
);

-- 索引
CREATE INDEX idx_universities_province ON universities(province);
CREATE INDEX idx_universities_type ON universities(type);
CREATE INDEX idx_universities_level ON universities(level);
CREATE INDEX idx_gaokao_university_year ON gaokao_admissions(university_id, year);
CREATE INDEX idx_gaokao_province_year ON gaokao_admissions(province, year);
CREATE INDEX idx_graduate_university_year ON graduate_admissions(university_id, year);

-- 示例数据
INSERT INTO universities (name, province, city, type, level, website, description) VALUES
('清华大学', '北京', '北京', '综合', '985', 'https://www.tsinghua.edu.cn', '中国著名高等学府，世界一流大学建设高校'),
('北京大学', '北京', '北京', '综合', '985', 'https://www.pku.edu.cn', '中国第一所国立综合性大学，世界一流大学建设高校'),
('浙江大学', '浙江', '杭州', '综合', '985', 'https://www.zju.edu.cn', '中国著名高等学府，C9联盟成员'),
('复旦大学', '上海', '上海', '综合', '985', 'https://www.fudan.edu.cn', '中国著名高等学府，世界一流大学建设高校'),
('上海交通大学', '上海', '上海', '理工', '985', 'https://www.sjtu.edu.cn', '中国著名高等学府，C9联盟成员'),
('南京大学', '江苏', '南京', '综合', '985', 'https://www.nju.edu.cn', '中国著名高等学府，世界一流大学建设高校'),
('武汉大学', '湖北', '武汉', '综合', '985', 'https://www.whu.edu.cn', '中国著名高等学府，世界一流大学建设高校'),
('华中科技大学', '湖北', '武汉', '理工', '985', 'https://www.hust.edu.cn', '中国著名高等学府，世界一流大学建设高校'),
('中山大学', '广东', '广州', '综合', '985', 'https://www.sysu.edu.cn', '中国著名高等学府，世界一流大学建设高校'),
('西安交通大学', '陕西', '西安', '理工', '985', 'https://www.xjtu.edu.cn', '中国著名高等学府，C9联盟成员');

-- 注意：实际使用时需要导入真实的录取数据
-- 这里只创建表结构，数据需要通过爬虫或手动导入