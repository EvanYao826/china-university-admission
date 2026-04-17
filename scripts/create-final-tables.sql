-- ============================================
-- 中国高校录取数据查询系统 - 优化版数据库设计
-- 修复了字段命名、冗余字段、索引不足等问题
-- ============================================

-- 1. 学校基本信息表（优化版）
CREATE TABLE IF NOT EXISTS schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                -- 学校名称
    type TEXT NOT NULL,                       -- 学校类型：综合类/理工类/师范类/医药类/农林类
    level TEXT NOT NULL,                      -- 学校层次：985/211/双一流/普通本科
    province TEXT NOT NULL,                   -- 所在省份
    city TEXT,                                -- 所在城市（新增）
    description TEXT,                         -- 学校简介
    nature TEXT DEFAULT '公办、全日制普通高等学校', -- 院校性质
    education_level TEXT DEFAULT '本科、硕士、博士', -- 办学层次
    address TEXT,                             -- 详细地址
    website TEXT,                             -- 学校官网（新增）
    phone TEXT,                               -- 联系电话
    tags TEXT,                                -- 特色标签，逗号分隔：985,211,双一流,强基计划
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 本科生历年整体录取分数线（分省份、专业组）- 优化版
CREATE TABLE IF NOT EXISTS undergraduate_yearly_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    year INTEGER NOT NULL,                    -- 年份：2024, 2023等
    province TEXT NOT NULL,                   -- 招生省份
    batch TEXT NOT NULL,                      -- 录取批次：本科一批/本科二批/本科批
    enrollment_type TEXT DEFAULT '普通类',     -- 招生类型：普通类/国家专项/高校专项等
    professional_group TEXT,                  -- 专业组代码：如(01)、(02)
    subject_category TEXT,                    -- 科目类别：文科/理科/历史类/物理类（更准确）
    subject_requirement TEXT,                 -- 选科要求：不限/物理必选/化学必选等
    min_score INTEGER,                        -- 最低分
    min_rank INTEGER,                         -- 最低位次
    avg_score REAL,                           -- 平均分
    provincial_control INTEGER,               -- 该省该批次省控线
    data_source TEXT DEFAULT 'EOL教育在线',    -- 数据来源
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    UNIQUE(school_id, year, province, batch, enrollment_type, professional_group, subject_category)
);

-- 3. 本科各专业录取分数线（分省份）- 优化版
CREATE TABLE IF NOT EXISTS undergraduate_major_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    province TEXT NOT NULL,
    major_name TEXT NOT NULL,                 -- 专业名称
    batch TEXT NOT NULL,
    avg_score REAL,
    min_score INTEGER,
    min_rank INTEGER,
    major_group TEXT,                         -- 专业组（与professional_group对应）
    subject_requirement TEXT,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    UNIQUE(school_id, year, province, major_name, batch)
);

-- 4. 研究生招生简章/宏观信息表 - 优化版
CREATE TABLE IF NOT EXISTS postgraduate_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    enrollment_plan TEXT,                     -- 计划招生人数
    registration_start DATE,                  -- 网上报名开始时间
    registration_end DATE,                    -- 网上报名结束时间
    exam_date_start DATE,                     -- 初试开始日期
    exam_date_end DATE,                       -- 初试结束日期
    majors_offered TEXT,                      -- 招生专业（文本描述）
    contact_phone TEXT,                       -- 研招办电话
    official_website TEXT,                    -- 官方网址
    important_notes TEXT,                     -- 重要提示
    brochure_url TEXT,                        -- 招生简章链接
    publish_date DATE,                        -- 发布日期（新增）
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    UNIQUE(school_id, year)
);

-- 5. 研究生复试基本分数线表（按学科门类/专业）- 优化版
CREATE TABLE IF NOT EXISTS postgraduate_reply_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    line_type TEXT NOT NULL DEFAULT '普通复试线', -- 招生类型：普通复试线/调剂信息/专项计划
    degree_type TEXT NOT NULL DEFAULT '学术学位',  -- 学位类型：学术学位/专业学位（新增）
    category_code TEXT NOT NULL,                  -- 学科门类代码：01, 02, 03等
    category_name TEXT NOT NULL,                  -- 学科门类名称：哲学、经济学等
    major_name TEXT,                              -- 专业名称（专业学位用）
    politics INTEGER,                             -- 政治最低分
    foreign_language INTEGER,                     -- 外国语最低分
    professional_subject1 INTEGER,                -- 专业课1/业务课1（英文字段名）
    professional_subject2 INTEGER,                -- 专业课2/业务课2
    total_score INTEGER,                          -- 总分要求
    remarks TEXT,                                 -- 备注
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    UNIQUE(school_id, year, line_type, category_code, degree_type, major_name)
);

-- ============================================
-- 索引优化（大幅提升查询性能）
-- ============================================

-- schools表索引
CREATE INDEX IF NOT EXISTS idx_schools_province ON schools(province);
CREATE INDEX IF NOT EXISTS idx_schools_type ON schools(type);
CREATE INDEX IF NOT EXISTS idx_schools_level ON schools(level);
CREATE INDEX IF NOT EXISTS idx_schools_name ON schools(name);

-- undergraduate_yearly_scores表索引
CREATE INDEX IF NOT EXISTS idx_undergrad_yearly_school ON undergraduate_yearly_scores(school_id);
CREATE INDEX IF NOT EXISTS idx_undergrad_yearly_province ON undergraduate_yearly_scores(province);
CREATE INDEX IF NOT EXISTS idx_undergrad_yearly_year ON undergraduate_yearly_scores(year);
CREATE INDEX IF NOT EXISTS idx_undergrad_yearly_batch ON undergraduate_yearly_scores(batch);
CREATE INDEX IF NOT EXISTS idx_undergrad_yearly_subject ON undergraduate_yearly_scores(subject_category);

-- undergraduate_major_scores表索引
CREATE INDEX IF NOT EXISTS idx_undergrad_major_school ON undergraduate_major_scores(school_id);
CREATE INDEX IF NOT EXISTS idx_undergrad_major_province ON undergraduate_major_scores(province);
CREATE INDEX IF NOT EXISTS idx_undergrad_major_year ON undergraduate_major_scores(year);
CREATE INDEX IF NOT EXISTS idx_undergrad_major_name ON undergraduate_major_scores(major_name);

-- postgraduate_info表索引
CREATE INDEX IF NOT EXISTS idx_postgrad_info_school ON postgraduate_info(school_id);
CREATE INDEX IF NOT EXISTS idx_postgrad_info_year ON postgraduate_info(year);

-- postgraduate_reply_lines表索引
CREATE INDEX IF NOT EXISTS idx_postgrad_reply_school ON postgraduate_reply_lines(school_id);
CREATE INDEX IF NOT EXISTS idx_postgrad_reply_year ON postgraduate_reply_lines(year);
CREATE INDEX IF NOT EXISTS idx_postgrad_reply_type ON postgraduate_reply_lines(line_type);
CREATE INDEX IF NOT EXISTS idx_postgrad_reply_category ON postgraduate_reply_lines(category_code);
CREATE INDEX IF NOT EXISTS idx_postgrad_reply_degree ON postgraduate_reply_lines(degree_type);

-- ============================================
-- 视图（简化复杂查询）
-- ============================================

-- 高校基本信息视图（包含统计信息）
CREATE VIEW IF NOT EXISTS vw_schools_summary AS
SELECT
    s.id,
    s.name,
    s.type,
    s.level,
    s.province,
    s.city,
    COUNT(DISTINCT uys.year) as years_available,
    COUNT(DISTINCT uys.province) as provinces_available,
    MIN(uys.year) as earliest_year,
    MAX(uys.year) as latest_year
FROM schools s
LEFT JOIN undergraduate_yearly_scores uys ON s.id = uys.school_id
GROUP BY s.id, s.name, s.type, s.level, s.province, s.city;

-- 本科生录取数据汇总视图
CREATE VIEW IF NOT EXISTS vw_undergrad_summary AS
SELECT
    s.name as school_name,
    uys.year,
    uys.province,
    uys.batch,
    uys.subject_category,
    COUNT(*) as record_count,
    AVG(uys.min_score) as avg_min_score,
    AVG(uys.avg_score) as avg_avg_score
FROM undergraduate_yearly_scores uys
JOIN schools s ON uys.school_id = s.id
GROUP BY s.name, uys.year, uys.province, uys.batch, uys.subject_category;

-- ============================================
-- 触发器（自动更新updated_at）
-- ============================================

CREATE TRIGGER IF NOT EXISTS trg_schools_update
AFTER UPDATE ON schools
BEGIN
    UPDATE schools SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================
-- 插入示例数据（验证用）
-- ============================================

-- 插入北京大学数据
INSERT OR IGNORE INTO schools (
    name, type, level, province, city, description, address, website, phone, tags
) VALUES (
    '北京大学',
    '综合类',
    '985',
    '北京市',
    '北京',
    '北京大学创立于1898年，初名京师大学堂，是中国近代第一所国立综合性大学，以深厚的学术底蕴、顶尖的科研实力和卓越的人才培养享誉全球。学校是国家"211工程"、"985工程"、"双一流"重点建设高校，始终走在中国高等教育发展的最前沿。',
    '北京市海淀区颐和园路5号',
    'https://www.pku.edu.cn',
    '010-62751415',
    '985,211,双一流,强基计划,部属院校'
);

-- 插入清华大学数据
INSERT OR IGNORE INTO schools (
    name, type, level, province, city, description, address, website, phone, tags
) VALUES (
    '清华大学',
    '综合类',
    '985',
    '北京市',
    '北京',
    '清华大学是中国著名高等学府，世界一流大学建设高校，C9联盟成员。',
    '北京市海淀区清华园',
    'https://www.tsinghua.edu.cn',
    '010-62793001',
    '985,211,双一流,C9联盟'
);

-- 插入本科生录取数据示例
INSERT OR IGNORE INTO undergraduate_yearly_scores (
    school_id, year, province, batch, enrollment_type, subject_category,
    min_score, min_rank, provincial_control
) VALUES
    (1, 2024, '河南', '本科一批', '普通类', '文科', 652, 76, 521),
    (1, 2023, '河南', '本科一批', '普通类', '文科', 672, 46, 547),
    (1, 2022, '河南', '本科一批', '普通类', '文科', 639, 59, 527),
    (2, 2024, '河南', '本科一批', '普通类', '理科', 680, 120, 521);

-- 插入研究生复试线示例
INSERT OR IGNORE INTO postgraduate_reply_lines (
    school_id, year, line_type, degree_type, category_code, category_name,
    politics, foreign_language, professional_subject1, professional_subject2, total_score, remarks
) VALUES
    (1, 2026, '普通复试线', '学术学位', '01', '哲学', 55, 55, 90, 90, 345, '招生院系自主确定复试要求'),
    (1, 2026, '普通复试线', '学术学位', '02', '经济学', 55, 55, 90, 90, 375, '招生院系自主确定复试要求'),
    (1, 2026, '调剂信息', '学术学位', '07', '理学', 50, 50, 80, 80, 300, '接受调剂');

-- ============================================
-- 验证语句
-- ============================================

-- 验证表创建
SELECT '✅ 表创建验证' as check_item;
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- 验证数据插入
SELECT '✅ 数据插入验证' as check_item;
SELECT '学校数量:' as item, COUNT(*) as count FROM schools
UNION ALL
SELECT '本科生数据:', COUNT(*) FROM undergraduate_yearly_scores
UNION ALL
SELECT '研究生数据:', COUNT(*) FROM postgraduate_reply_lines;

-- 验证索引
SELECT '✅ 索引验证' as check_item;
SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name;