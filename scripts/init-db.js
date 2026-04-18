const Database = require('better-sqlite3');
const path = require('path');

// 数据库路径
const dbPath = path.join(__dirname, '../data/university.db');

// 连接数据库
const db = new Database(dbPath);
db.pragma('foreign_keys = ON');

// 创建 universities 表
console.log('创建 universities 表...');
db.exec(`
CREATE TABLE IF NOT EXISTS universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT,
    level TEXT,
    province TEXT NOT NULL,
    city TEXT,
    tags TEXT,
    logo_url TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
`);

// 创建 undergraduate_admissions 表
console.log('创建 undergraduate_admissions 表...');
db.exec(`
CREATE TABLE IF NOT EXISTS undergraduate_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    province TEXT NOT NULL,
    year INTEGER NOT NULL,
    category TEXT,
    batch TEXT,
    enrollment_type TEXT,
    major TEXT,
    min_score REAL,
    min_rank INTEGER,
    avg_score REAL,
    provincial_control_line REAL,
    subject_requirements TEXT,
    professional_group TEXT,
    source_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, province, year, category, batch, major, enrollment_type)
);
`);

// 创建 postgraduate_admissions 表
console.log('创建 postgraduate_admissions 表...');
db.exec(`
CREATE TABLE IF NOT EXISTS postgraduate_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    degree_type TEXT,
    discipline_category TEXT,
    admission_type TEXT,
    political_score REAL,
    foreign_language_score REAL,
    subject1_score REAL,
    subject2_score REAL,
    total_score REAL,
    remarks TEXT,
    adjustment_info TEXT,
    source_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, year, degree_type, discipline_category, admission_type)
);
`);

// 创建索引
console.log('创建索引...');
db.exec(`
CREATE INDEX IF NOT EXISTS idx_undergrad_univ_prov_year ON undergraduate_admissions(university_id, province, year);
CREATE INDEX IF NOT EXISTS idx_undergrad_prov_year ON undergraduate_admissions(province, year);
CREATE INDEX IF NOT EXISTS idx_undergrad_univ_year ON undergraduate_admissions(university_id, year);
CREATE INDEX IF NOT EXISTS idx_undergrad_major ON undergraduate_admissions(major);
CREATE INDEX IF NOT EXISTS idx_postgrad_univ_year ON postgraduate_admissions(university_id, year);
CREATE INDEX IF NOT EXISTS idx_postgrad_year ON postgraduate_admissions(year);
`);

// 插入示例数据
console.log('插入示例数据...');
try {
    // 插入大学数据
    const universities = [
        { name: '清华大学', type: '综合', level: '985', province: '北京', city: '北京市海淀区', tags: '强基计划,C9联盟' },
        { name: '北京大学', type: '综合', level: '985', province: '北京', city: '北京市海淀区', tags: '强基计划,C9联盟' },
        { name: '浙江大学', type: '综合', level: '985', province: '浙江', city: '浙江省杭州', tags: 'C9联盟' },
        { name: '上海交通大学', type: '综合', level: '985', province: '上海', city: '上海市', tags: 'C9联盟' },
        { name: '复旦大学', type: '综合', level: '985', province: '上海', city: '上海市', tags: 'C9联盟' },
        { name: '南京大学', type: '综合', level: '985', province: '江苏', city: '江苏省南京', tags: 'C9联盟' },
        { name: '华中科技大学', type: '综合', level: '985', province: '湖北', city: '湖北省武汉' },
        { name: '武汉大学', type: '综合', level: '985', province: '湖北', city: '湖北省武汉' },
        { name: '西安交通大学', type: '综合', level: '985', province: '陕西', city: '陕西省西安', tags: 'C9联盟' },
        { name: '中国科学技术大学', type: '理工', level: '985', province: '安徽', city: '安徽省合肥', tags: 'C9联盟' }
    ];

    const insertUniversity = db.prepare(`
        INSERT OR IGNORE INTO universities (name, type, level, province, city, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    `);

    universities.forEach(uni => {
        insertUniversity.run(uni.name, uni.type, uni.level, uni.province, uni.city, uni.tags);
    });

    // 插入本科录取数据
    const insertUndergraduate = db.prepare(`
        INSERT OR IGNORE INTO undergraduate_admissions 
        (university_id, province, year, category, batch, min_score, min_rank)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    // 为清华大学插入示例数据
    insertUndergraduate.run(1, '北京', 2024, '物理类', '本科批', 698, 100);
    insertUndergraduate.run(1, '北京', 2023, '物理类', '本科批', 695, 120);
    insertUndergraduate.run(1, '上海', 2024, '综合改革', '本科批', 580, 2684);
    insertUndergraduate.run(1, '浙江', 2024, '综合改革', '本科批', 664, 6791);

    // 为北京大学插入示例数据
    insertUndergraduate.run(2, '北京', 2024, '物理类', '本科批', 690, 150);
    insertUndergraduate.run(2, '北京', 2023, '物理类', '本科批', 688, 180);

    // 插入研究生录取数据
    const insertPostgraduate = db.prepare(`
        INSERT OR IGNORE INTO postgraduate_admissions
        (university_id, year, degree_type, discipline_category, admission_type, total_score)
        VALUES (?, ?, ?, ?, ?, ?)
    `);

    // 为清华大学插入研究生数据
    insertPostgraduate.run(1, 2025, '学术学位', '工学', '普通复试线', 320);
    insertPostgraduate.run(1, 2025, '学术学位', '理学', '普通复试线', 310);
    insertPostgraduate.run(1, 2025, '专业学位', '工程', '普通复试线', 300);

    console.log('数据库初始化完成！');
} catch (error) {
    console.error('插入数据时出错:', error);
} finally {
    db.close();
}