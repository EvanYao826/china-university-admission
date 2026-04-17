#!/usr/bin/env node

const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '../data/university.db');

try {
  console.log('连接数据库...');
  const db = new Database(dbPath);
  db.pragma('foreign_keys = ON');

  console.log('插入示例学校数据...');

  const schools = [
    {
      name: '北京大学',
      type: '综合类',
      level: '985,211,双一流',
      province: '北京市',
      description: '北京大学创立于1898年，初名京师大学堂，是中国近代第一所国立综合性大学，以深厚的学术底蕴、顶尖的科研实力和卓越的人才培养享誉全球。',
      nature: '公办、全日制普通高等学校',
      education_level: '本科、硕士、博士',
      category: '综合类',
      address: '北京市海淀区',
      tags: '985、211、双一流、强基计划、部属院校',
      phone: '010-62751415'
    },
    {
      name: '清华大学',
      type: '综合类',
      level: '985,211,双一流',
      province: '北京市',
      description: '清华大学是中国著名高等学府，坐落于北京西北郊风景秀丽的清华园。清华大学始终坚持"自强不息，厚德载物"的校训和"行胜于言"的校风。',
      nature: '公办、全日制普通高等学校',
      education_level: '本科、硕士、博士',
      category: '综合类',
      address: '北京市海淀区',
      tags: '985、211、双一流、强基计划、部属院校',
      phone: '010-62782051'
    },
    {
      name: '复旦大学',
      type: '综合类',
      level: '985,211,双一流',
      province: '上海市',
      description: '复旦大学是国家教育部直属、中央直管副部级建制的全国重点大学。位列"211工程"、"985工程"，是一所世界知名、国内顶尖的综合性研究型大学。',
      nature: '公办、全日制普通高等学校',
      education_level: '本科、硕士、博士',
      category: '综合类',
      address: '上海市杨浦区',
      tags: '985、211、双一流、强基计划',
      phone: '021-65642222'
    },
    {
      name: '厦门大学',
      type: '综合类',
      level: '985,211,双一流',
      province: '福建省',
      description: '厦门大学是由著名爱国华侨领袖陈嘉庚先生于1921年创办的，是中国近代教育史上第一所由华侨创办的大学。',
      nature: '公办、全日制普通高等学校',
      education_level: '本科、硕士、博士',
      category: '综合类',
      address: '福建省厦门市',
      tags: '985、211、双一流',
      phone: '0592-2186111'
    },
    {
      name: '浙江大学',
      type: '综合类',
      level: '985,211,双一流',
      province: '浙江省',
      description: '浙江大学是一所历史悠久、声誉卓著的高等学府，坐落于中国历史文化名城、风景旅游胜地杭州。',
      nature: '公办、全日制普通高等学校',
      education_level: '本科、硕士、博士',
      category: '综合类',
      address: '浙江省杭州市',
      tags: '985、211、双一流、C9联盟',
      phone: '0571-87951006'
    }
  ];

  const insertSchool = db.prepare(`
    INSERT OR IGNORE INTO schools (name, type, level, province, description, nature, education_level, category, address, tags, phone)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  schools.forEach(school => {
    insertSchool.run(
      school.name,
      school.type,
      school.level,
      school.province,
      school.description,
      school.nature,
      school.education_level,
      school.category,
      school.address,
      school.tags,
      school.phone
    );
    console.log(`插入: ${school.name}`);
  });

  // 获取学校ID
  const schoolList = db.prepare('SELECT id, name FROM schools').all();
  console.log(`\n共插入 ${schoolList.length} 所学校`);

  // 插入本科历年分数数据
  console.log('\n插入本科历年分数数据...');
  
  const insertYearlyScore = db.prepare(`
    INSERT OR IGNORE INTO undergraduate_yearly_scores
    (school_id, year, province, batch, enrollment_type, professional_group, subject_requirement, min_score, min_rank, avg_score, provincial_control, data_source)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  schoolList.forEach(school => {
    const baseScore = 650 + Math.floor(Math.random() * 30);
    
    [2024, 2023, 2022, 2021].forEach(year => {
      const yearFactor = (2024 - year) * 3;
      insertYearlyScore.run(
        school.id, year, '河南省', '本科一批', '普通类', '(01)', '物理必选',
        baseScore - yearFactor - 15,
        1000 + Math.floor(Math.random() * 500),
        baseScore - yearFactor,
        521 + Math.floor(yearFactor / 2),
        'EOL教育在线'
      );
    });
  });
  console.log('插入本科历年分数完成');

  // 插入专业分数数据
  console.log('插入专业分数数据...');
  
  const insertMajorScore = db.prepare(`
    INSERT OR IGNORE INTO undergraduate_major_scores
    (school_id, year, province, major_name, batch, avg_score, min_score, min_rank, major_group, subject_requirement)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  const majors = ['计算机科学与技术', '电子信息工程', '自动化', '机械工程', '材料科学与工程'];

  schoolList.forEach(school => {
    majors.forEach((major, idx) => {
      const baseScore = 650 + idx * 5;
      insertMajorScore.run(
        school.id, 2023, '河南省', major, '本科一批',
        baseScore - 5,
        baseScore - 15,
        800 + idx * 100,
        '(01)', '物理必选'
      );
    });
  });
  console.log('插入专业分数完成');

  // 插入研究生信息
  console.log('插入研究生招生信息...');
  
  const insertPostgradInfo = db.prepare(`
    INSERT OR IGNORE INTO postgraduate_info
    (school_id, year, enrollment_plan, registration_start, registration_end, exam_date_start, exam_date_end, majors_offered, contact_phone, official_website, important_notes, brochure_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  schoolList.forEach(school => {
    insertPostgradInfo.run(
      school.id, 2024, '约5000人', '2023-10-08', '2023-10-25', '2023-12-23', '2023-12-25',
      '涵盖哲学、经济学、法学、教育学、文学、历史学、理学、工学、医学等学科门类',
      school.phone, `https://www.example.edu.cn`,
      '硕士研究生复试基本分数线划线工作坚持质量为先、宁缺毋滥的原则，按学科门类划定。',
      `https://www.example.edu.cn/zsjz/2024`
    );
  });
  console.log('插入研究生信息完成');

  // 插入研究生复试线
  console.log('插入研究生复试分数线...');
  
  const insertReplyLine = db.prepare(`
    INSERT OR IGNORE INTO postgraduate_reply_lines
    (school_id, year, line_type, category_name, category_code, politics, foreign_language, 专业课1, 专业课2, total_score, remarks)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  const categories = [
    { name: '哲学', code: '01', politics: 55, foreign: 55,专业课1: 90,专业课2: 90, total: 345 },
    { name: '经济学', code: '02', politics: 55, foreign: 55,专业课1: 90,专业课2: 90, total: 360 },
    { name: '法学', code: '03', politics: 55, foreign: 55,专业课1: 90,专业课2: 90, total: 340 },
    { name: '教育学', code: '04', politics: 55, foreign: 55,专业课1: 180,专业课2: null, total: 335 },
    { name: '文学', code: '05', politics: 55, foreign: 55,专业课1: 90,专业课2: 90, total: 355 },
    { name: '历史学', code: '06', politics: 55, foreign: 55,专业课1: 180,专业课2: null, total: 345 },
    { name: '工学', code: '08', politics: 55, foreign: 55,专业课1: 90,专业课2: 90, total: 320 },
    { name: '医学', code: '10', politics: 55, foreign: 55,专业课1: 180,专业课2: null, total: 310 }
  ];

  schoolList.forEach(school => {
    categories.forEach(cat => {
      insertReplyLine.run(
        school.id, 2024, '普通复试线', cat.name, `[${cat.code}]`,
        cat.politics, cat.foreign, cat.专业课1, cat.专业课2, cat.total,
        '招生院系自主确定复试要求'
      );
    });
  });
  console.log('插入研究生复试线完成');

  // 验证数据
  console.log('\n验证数据...');
  const counts = {
    schools: db.prepare('SELECT COUNT(*) as count FROM schools').get().count,
    yearlyScores: db.prepare('SELECT COUNT(*) as count FROM undergraduate_yearly_scores').get().count,
    majorScores: db.prepare('SELECT COUNT(*) as count FROM undergraduate_major_scores').get().count,
    postgradInfo: db.prepare('SELECT COUNT(*) as count FROM postgraduate_info').get().count,
    replyLines: db.prepare('SELECT COUNT(*) as count FROM postgraduate_reply_lines').get().count
  };

  console.log(`
📊 数据插入完成！
================================
学校数量: ${counts.schools}
本科历年分数: ${counts.yearlyScores}
专业分数: ${counts.majorScores}
研究生招生信息: ${counts.postgradInfo}
研究生复试线: ${counts.replyLines}
================================
  `);

  db.close();

} catch (error) {
  console.error('操作失败:', error.message);
}
