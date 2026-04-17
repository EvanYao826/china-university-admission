#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

console.log(`
📊 数据库初始化工具（新结构）
================================
正在初始化数据库...
`);

// 检查数据目录
const dataDir = path.join(__dirname, '../data');
if (!fs.existsSync(dataDir)) {
  console.log('📁 创建数据目录...');
  fs.mkdirSync(dataDir, { recursive: true });
}

// 数据库文件路径
const dbPath = path.join(dataDir, 'university.db');

// 如果数据库已存在，删除它
if (fs.existsSync(dbPath)) {
  console.log('🗑️  删除现有数据库...');
  fs.unlinkSync(dbPath);
}

try {
  console.log('🔄 创建数据库...');
  const db = new Database(dbPath);

  // 启用外键约束
  db.pragma('foreign_keys = ON');

  // 1. 创建 schools 表
  console.log('📋 创建 schools 表...');
  db.exec(`
    CREATE TABLE schools (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      type TEXT,
      level TEXT,
      province TEXT,
      description TEXT,
      nature TEXT,
      education_level TEXT,
      category TEXT,
      address TEXT,
      tags TEXT,
      phone TEXT
    )
  `);

  // 2. 创建 undergraduate_yearly_scores 表
  console.log('📋 创建 undergraduate_yearly_scores 表...');
  db.exec(`
    CREATE TABLE undergraduate_yearly_scores (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      school_id INTEGER NOT NULL,
      year INTEGER NOT NULL,
      province TEXT NOT NULL,
      batch TEXT,
      enrollment_type TEXT,
      professional_group TEXT,
      subject_requirement TEXT,
      min_score INTEGER,
      min_rank INTEGER,
      avg_score REAL,
      provincial_control INTEGER,
      data_source TEXT,
      FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
    )
  `);

  // 3. 创建 undergraduate_major_scores 表
  console.log('📋 创建 undergraduate_major_scores 表...');
  db.exec(`
    CREATE TABLE undergraduate_major_scores (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      school_id INTEGER NOT NULL,
      year INTEGER NOT NULL,
      province TEXT NOT NULL,
      major_name TEXT NOT NULL,
      batch TEXT,
      avg_score REAL,
      min_score INTEGER,
      min_rank INTEGER,
      major_group TEXT,
      subject_requirement TEXT,
      FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
    )
  `);

  // 4. 创建 postgraduate_info 表
  console.log('📋 创建 postgraduate_info 表...');
  db.exec(`
    CREATE TABLE postgraduate_info (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      school_id INTEGER NOT NULL,
      year INTEGER NOT NULL,
      enrollment_plan TEXT,
      registration_start DATE,
      registration_end DATE,
      exam_date_start DATE,
      exam_date_end DATE,
      majors_offered TEXT,
      contact_phone TEXT,
      official_website TEXT,
      important_notes TEXT,
      brochure_url TEXT,
      FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
    )
  `);

  // 5. 创建 postgraduate_reply_lines 表
  console.log('📋 创建 postgraduate_reply_lines 表...');
  db.exec(`
    CREATE TABLE postgraduate_reply_lines (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      school_id INTEGER NOT NULL,
      year INTEGER NOT NULL,
      line_type TEXT DEFAULT '普通复试线',
      category_name TEXT NOT NULL,
      category_code TEXT,
      politics INTEGER,
      foreign_language INTEGER,
      专业课1 INTEGER,
      专业课2 INTEGER,
      total_score INTEGER,
      remarks TEXT,
      FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
    )
  `);

  // 创建索引
  console.log('🔍 创建索引...');
  db.exec(`
    CREATE INDEX idx_undergrad_yearly_school_province_year ON undergraduate_yearly_scores(school_id, province, year);
    CREATE INDEX idx_undergrad_major_school_province_year ON undergraduate_major_scores(school_id, province, year);
    CREATE INDEX idx_postgrad_info_school_year ON postgraduate_info(school_id, year);
    CREATE INDEX idx_postgrad_reply_school_year ON postgraduate_reply_lines(school_id, year);
  `);

  // 验证表结构
  console.log('✅ 验证数据库结构...');
  const tables = db.prepare(`
    SELECT name FROM sqlite_master WHERE type='table'
  `).all();

  console.log(`
📊 数据库初始化完成！
================================
数据库文件：${dbPath}
创建的表：
${tables.map(t => `  - ${t.name}`).join('\n')}
================================

💡 下一步：
1. 启动服务器：npm run dev
2. 访问前端：http://localhost:5173
3. 开始添加学校和录取数据
`);

  db.close();

} catch (error) {
  console.error('❌ 数据库初始化失败:', error.message);
  process.exit(1);
}
