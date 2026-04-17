#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

console.log(`
📊 数据库初始化工具
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

// 如果数据库已存在，询问是否覆盖
if (fs.existsSync(dbPath)) {
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  rl.question('⚠️  数据库已存在，是否覆盖？(y/N): ', (answer) => {
    if (answer.toLowerCase() === 'y') {
      console.log('🗑️  删除现有数据库...');
      fs.unlinkSync(dbPath);
      createDatabase();
    } else {
      console.log('✅ 保留现有数据库');
      process.exit(0);
    }
    rl.close();
  });
} else {
  createDatabase();
}

function createDatabase() {
  try {
    console.log('🔄 创建数据库...');
    const db = new Database(dbPath);

    // 创建表结构
    console.log('📋 创建表结构...');

    // 高校表
    db.exec(`
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
      )
    `);

    // 高考录取表
    db.exec(`
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
      )
    `);

    // 研究生录取表
    db.exec(`
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
      )
    `);

    // 创建索引
    console.log('🔍 创建索引...');
    db.exec(`
      CREATE INDEX idx_universities_province ON universities(province);
      CREATE INDEX idx_universities_type ON universities(type);
      CREATE INDEX idx_universities_level ON universities(level);
      CREATE INDEX idx_gaokao_university_year ON gaokao_admissions(university_id, year);
      CREATE INDEX idx_gaokao_province_year ON gaokao_admissions(province, year);
      CREATE INDEX idx_graduate_university_year ON graduate_admissions(university_id, year);
    `);

    // 插入示例数据
    console.log('📝 插入示例数据...');
    insertSampleData(db);

    // 验证数据
    console.log('✅ 验证数据完整性...');
    const universityCount = db.prepare('SELECT COUNT(*) as count FROM universities').get().count;
    const gaokaoCount = db.prepare('SELECT COUNT(*) as count FROM gaokao_admissions').get().count;
    const graduateCount = db.prepare('SELECT COUNT(*) as count FROM graduate_admissions').get().count;

    console.log(`
📊 数据库初始化完成！
================================
🏫 高校数量：${universityCount}
📚 高考记录：${gaokaoCount}
🎓 研究生记录：${graduateCount}
📁 数据库文件：${dbPath}
================================

💡 下一步：
1. 启动服务器：npm run dev
2. 访问前端：http://localhost:5173
3. 查看API文档：http://localhost:3000/api
`);

    db.close();

  } catch (error) {
    console.error('❌ 数据库初始化失败:', error.message);
    process.exit(1);
  }
}

function insertSampleData(db) {
  // 插入示例高校数据
  const insertUniversity = db.prepare(`
    INSERT OR IGNORE INTO universities (name, province, city, type, level, website, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  const universities = [
    {
      name: '清华大学',
      province: '北京',
      city: '北京',
      type: '综合',
      level: '985',
      website: 'https://www.tsinghua.edu.cn',
      description: '中国著名高等学府，世界一流大学建设高校'
    },
    {
      name: '北京大学',
      province: '北京',
      city: '北京',
      type: '综合',
      level: '985',
      website: 'https://www.pku.edu.cn',
      description: '中国第一所国立综合性大学，世界一流大学建设高校'
    },
    {
      name: '浙江大学',
      province: '浙江',
      city: '杭州',
      type: '综合',
      level: '985',
      website: 'https://www.zju.edu.cn',
      description: '中国著名高等学府，C9联盟成员'
    },
    {
      name: '复旦大学',
      province: '上海',
      city: '上海',
      type: '综合',
      level: '985',
      website: 'https://www.fudan.edu.cn',
      description: '中国著名高等学府，世界一流大学建设高校'
    },
    {
      name: '上海交通大学',
      province: '上海',
      city: '上海',
      type: '理工',
      level: '985',
      website: 'https://www.sjtu.edu.cn',
      description: '中国著名高等学府，C9联盟成员'
    }
  ];

  universities.forEach(uni => {
    insertUniversity.run(
      uni.name,
      uni.province,
      uni.city,
      uni.type,
      uni.level,
      uni.website,
      uni.description
    );
  });

  // 获取插入的高校ID
  const universityIds = db.prepare('SELECT id, name FROM universities').all();

  // 插入示例高考数据
  const insertGaokao = db.prepare(`
    INSERT OR IGNORE INTO gaokao_admissions
    (university_id, year, province, category, batch, min_score, avg_score, max_score, min_rank, avg_rank, max_rank, admission_count, major)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  // 为每个高校插入一些示例高考数据
  universityIds.forEach((uni, index) => {
    const baseScore = 650 + index * 10;

    // 理科数据
    insertGaokao.run(
      uni.id,
      2023,
      '北京',
      '理科',
      '本科一批',
      baseScore - 10,
      baseScore,
      baseScore + 10,
      1000 + index * 100,
      800 + index * 100,
      600 + index * 100,
      100 + index * 20,
      null
    );

    insertGaokao.run(
      uni.id,
      2023,
      '浙江',
      '理科',
      '本科一批',
      baseScore - 5,
      baseScore + 5,
      baseScore + 15,
      1200 + index * 100,
      1000 + index * 100,
      800 + index * 100,
      80 + index * 15,
      null
    );

    // 文科数据
    insertGaokao.run(
      uni.id,
      2023,
      '北京',
      '文科',
      '本科一批',
      baseScore - 15,
      baseScore - 5,
      baseScore + 5,
      1500 + index * 100,
      1300 + index * 100,
      1100 + index * 100,
      60 + index * 10,
      null
    );

    // 2022年数据
    insertGaokao.run(
      uni.id,
      2022,
      '北京',
      '理科',
      '本科一批',
      baseScore - 15,
      baseScore - 5,
      baseScore + 5,
      1100 + index * 100,
      900 + index * 100,
      700 + index * 100,
      90 + index * 18,
      null
    );
  });

  // 插入示例研究生数据
  const insertGraduate = db.prepare(`
    INSERT OR IGNORE INTO graduate_admissions
    (university_id, year, major, degree_type, study_mode, admission_count, min_score, avg_score, max_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  const majors = [
    '计算机科学与技术',
    '软件工程',
    '电子信息工程',
    '机械工程',
    '材料科学与工程',
    '经济学',
    '金融学',
    '工商管理',
    '法学',
    '临床医学'
  ];

  universityIds.forEach((uni, uniIndex) => {
    majors.forEach((major, majorIndex) => {
      const baseScore = 380 + uniIndex * 5 + majorIndex * 2;

      // 硕士
      insertGraduate.run(
        uni.id,
        2023,
        major,
        '硕士',
        '全日制',
        20 + uniIndex + majorIndex,
        baseScore - 10,
        baseScore,
        baseScore + 10
      );

      // 博士
      if (uniIndex % 2 === 0) {
        insertGraduate.run(
          uni.id,
          2023,
          major,
          '博士',
          '全日制',
          5 + uniIndex,
          baseScore - 5,
          baseScore + 5,
          baseScore + 15
        );
      }

      // 2022年数据
      insertGraduate.run(
        uni.id,
        2022,
        major,
        '硕士',
        '全日制',
        18 + uniIndex + majorIndex,
        baseScore - 12,
        baseScore - 2,
        baseScore + 8
      );
    });
  });
}