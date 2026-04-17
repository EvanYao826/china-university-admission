-- 优化后的数据库表结构
-- 1. 高校基本信息表
CREATE TABLE IF NOT EXISTS universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,               -- 综合类/理工类/师范类/医药类/农林类
    level TEXT NOT NULL,              -- 985/211/双一流/普通本科
    province TEXT NOT NULL,           -- 所在省份
    city TEXT,                        -- 所在城市
    description TEXT,                 -- 学校简介
    nature TEXT DEFAULT '公办、全日制普通高等学校', -- 院校性质
    education_level TEXT DEFAULT '本科、硕士、博士', -- 办学层次
    address TEXT,                     -- 详细地址
    website TEXT,                     -- 学校官网
    phone TEXT,                       -- 联系电话
    tags TEXT,                        -- 特色标签，逗号分隔
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 本科生历年录取分数线（整体）
CREATE TABLE IF NOT EXISTS undergraduate_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    province TEXT NOT NULL,           -- 招生省份
    category TEXT NOT NULL,           -- 文科/理科/历史类/物理类
    batch TEXT NOT NULL,              -- 录取批次：本科一批/本科二批等
    enrollment_type TEXT DEFAULT '普通类', -- 招生类型
    min_score INTEGER,                -- 最低分
    min_rank INTEGER,                 -- 最低位次
    avg_score REAL,                   -- 平均分
    provincial_control INTEGER,       -- 省控线
    subject_requirement TEXT,         -- 选科要求
    data_source TEXT DEFAULT 'EOL教育在线',
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, year, province, category, batch)
);

-- 3. 本科专业录取分数线
CREATE TABLE IF NOT EXISTS undergraduate_major_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    province TEXT NOT NULL,
    major_name TEXT NOT NULL,         -- 专业名称
    batch TEXT NOT NULL,
    avg_score REAL,
    min_score INTEGER,
    min_rank INTEGER,
    major_group TEXT,                 -- 专业组
    subject_requirement TEXT,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, year, province, major_name, batch)
);

-- 4. 研究生招生信息
CREATE TABLE IF NOT EXISTS postgraduate_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    line_type TEXT NOT NULL,          -- 普通复试线/调剂信息/专项计划
    category_code TEXT,               -- 学科门类代码：01/02/03等
    category_name TEXT NOT NULL,      -- 学科门类名称：哲学/经济学等
    degree_type TEXT DEFAULT '学术学位', -- 学术学位/专业学位
    major_name TEXT,                  -- 专业名称（专业学位用）
    politics INTEGER,                 -- 政治最低分
    foreign_language INTEGER,         -- 外国语最低分
    subject1 INTEGER,                 -- 专业课1/业务课1
    subject2 INTEGER,                 -- 专业课2/业务课2（可为NULL）
    total_score INTEGER,              -- 总分要求
    remarks TEXT,                     -- 备注
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, year, line_type, category_code, degree_type, major_name)
);

-- 5. 研究生招生简章信息
CREATE TABLE IF NOT EXISTS postgraduate_brochures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    enrollment_plan TEXT,             -- 计划招生人数
    registration_start DATE,          -- 报名开始时间
    registration_end DATE,            -- 报名结束时间
    exam_date_start DATE,             -- 初试开始日期
    exam_date_end DATE,               -- 初试结束日期
    contact_phone TEXT,               -- 研招办电话
    official_website TEXT,            -- 官方网址
    important_notes TEXT,             -- 重要提示
    brochure_url TEXT,                -- 招生简章链接
    publish_date DATE,                -- 发布日期
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, year)
);

-- 创建索引优化查询性能
CREATE INDEX idx_universities_province ON universities(province);
CREATE INDEX idx_universities_type ON universities(type);
CREATE INDEX idx_universities_level ON universities(level);

CREATE INDEX idx_undergrad_uni_year ON undergraduate_admissions(university_id, year);
CREATE INDEX idx_undergrad_province ON undergraduate_admissions(province);
CREATE INDEX idx_undergrad_category ON undergraduate_admissions(category);

CREATE INDEX idx_undergrad_major_uni_year ON undergraduate_major_admissions(university_id, year);
CREATE INDEX idx_undergrad_major_province ON undergraduate_major_admissions(province);

CREATE INDEX idx_postgrad_uni_year ON postgraduate_admissions(university_id, year);
CREATE INDEX idx_postgrad_line_type ON postgraduate_admissions(line_type);
CREATE INDEX idx_postgrad_category ON postgraduate_admissions(category_code);

-- 插入示例数据（北京大学）
INSERT OR IGNORE INTO universities (name, type, level, province, city, description, address, website, phone, tags) VALUES
('北京大学', '综合类', '985', '北京市', '北京', '北京大学创立于1898年，初名京师大学堂，是中国近代第一所国立综合性大学，以深厚的学术底蕴、顶尖的科研实力和卓越的人才培养享誉全球。学校是国家"211工程"、"985工程"、"双一流"重点建设高校，始终走在中国高等教育发展的最前沿。', '北京市海淀区颐和园路5号', 'https://www.pku.edu.cn', '010-62751415', '985,211,双一流,强基计划,部属院校');

-- 插入本科生录取数据示例
INSERT OR IGNORE INTO undergraduate_admissions (university_id, year, province, category, batch, min_score, min_rank, provincial_control) VALUES
(1, 2024, '河南', '文科', '本科一批', 652, 76, 521),
(1, 2023, '河南', '文科', '本科一批', 672, 46, 547),
(1, 2022, '河南', '文科', '本科一批', 639, 59, 527),
(1, 2021, '河南', '文科', '本科一批', 669, 52, 558);

-- 插入研究生复试线示例
INSERT OR IGNORE INTO postgraduate_admissions (university_id, year, line_type, category_code, category_name, politics, foreign_language, subject1, subject2, total_score, remarks) VALUES
(1, 2026, '普通复试线', '01', '哲学', 55, 55, 90, 90, 345, '招生院系自主确定复试要求'),
(1, 2026, '普通复试线', '02', '经济学', 55, 55, 90, 90, 375, '招生院系自主确定复试要求'),
(1, 2026, '普通复试线', '03', '法学', 55, 55, 90, 90, 345, '招生院系自主确定复试要求');

-- 插入研究生招生简章示例
INSERT OR IGNORE INTO postgraduate_brochures (university_id, year, contact_phone, official_website, publish_date) VALUES
(1, 2026, '010-62751354', 'https://admission.pku.edu.cn', '2026-03-13');