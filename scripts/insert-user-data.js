#!/usr/bin/env node

const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '../data/university.db');

try {
  console.log('连接数据库...');
  const db = new Database(dbPath);
  db.pragma('foreign_keys = ON');

  console.log('执行SQL语句...');

  // 插入学校数据
  const schoolSql = `
    INSERT OR REPLACE INTO schools (id, name, type, level, province, description, nature, education_level, category, address, tags, phone) VALUES
    (1, '北京大学', '综合类', '985 211 双一流', '北京', '北京大学创立于1898年，初名京师大学堂，是中国近代第一所国立综合性大学。', '公办', '本科 硕士 博士', '综合类', '北京市海淀区颐和园路5号', '985,211,双一流,强基计划', '010-62751415'),
    (2, '清华大学', '理工类', '985 211 双一流', '北京', '清华大学始建于1911年，是中国著名高等学府，被誉为“红色工程师的摇篮”。', '公办', '本科 硕士 博士', '理工类', '北京市海淀区清华园1号', '985,211,双一流,强基计划', '010-62793001');
  `;
  db.exec(schoolSql);
  console.log('插入学校数据完成');

  // 插入北京大学本科历年分数线
  const pkuUndergraduateSql = `
    INSERT OR REPLACE INTO undergraduate_yearly_scores (school_id, year, province, batch, enrollment_type, professional_group, subject_requirement, min_score, min_rank, avg_score, provincial_control, data_source) VALUES
    (1, 2021, '北京', '本科批', '普通类', '(01)', '不限', 678, 461, NULL, 400, 'EOL教育在线'),
    (1, 2021, '北京', '本科批', '普通类', '(02)', '不限', 683, 304, NULL, 400, 'EOL教育在线'),
    (1, 2021, '北京', '本科批', '普通类', '(03)', '物理必选', 681, 350, NULL, 400, 'EOL教育在线'),
    (1, 2021, '北京', '本科批', '普通类', '(04)', '物理/化学(2选1)', 679, 427, NULL, 400, 'EOL教育在线'),
    (1, 2022, '北京', '本科批', '普通类', '(01)', '不限', 687, 416, NULL, 425, 'EOL教育在线'),
    (1, 2022, '北京', '本科批', '普通类', '(02)', '不限', 695, 194, NULL, 425, 'EOL教育在线'),
    (1, 2022, '北京', '本科批', '普通类', '(03)', '物理必选', 688, 390, NULL, 425, 'EOL教育在线');
  `;
  db.exec(pkuUndergraduateSql);
  console.log('插入北京大学本科历年分数线完成');

  // 插入清华大学本科历年分数线
  const tsinghuaUndergraduateSql = `
    INSERT OR REPLACE INTO undergraduate_yearly_scores (school_id, year, province, batch, enrollment_type, professional_group, subject_requirement, min_score, min_rank, avg_score, provincial_control, data_source) VALUES
    (2, 2021, '北京', '本科批', '普通类', '(01)', '不限', 681, 380, NULL, 400, 'EOL教育在线'),
    (2, 2021, '北京', '本科批', '普通类', '(02)', '物理必选', 682, 360, NULL, 400, 'EOL教育在线'),
    (2, 2022, '北京', '本科批', '普通类', '(01)', '不限', 688, 350, NULL, 425, 'EOL教育在线'),
    (2, 2022, '北京', '本科批', '普通类', '(02)', '物理必选', 690, 300, NULL, 425, 'EOL教育在线');
  `;
  db.exec(tsinghuaUndergraduateSql);
  console.log('插入清华大学本科历年分数线完成');

  // 插入北京大学本科专业分数线
  const pkuMajorSql = `
    INSERT OR REPLACE INTO undergraduate_major_scores (school_id, year, province, major_name, batch, avg_score, min_score, min_rank, major_group, subject_requirement) VALUES
    (1, 2021, '北京', '历史学类（含历史学、世界史、外国语言与外国历史）', '本科批', NULL, 661, 54, '(01)', '不限'),
    (1, 2021, '北京', '考古学', '本科批', NULL, 661, 54, '(01)', '不限'),
    (1, 2021, '北京', '计算机类', '本科批', NULL, 690, 120, '(03)', '物理必选');
  `;
  db.exec(pkuMajorSql);
  console.log('插入北京大学本科专业分数线完成');

  // 插入清华大学本科专业分数线
  const tsinghuaMajorSql = `
    INSERT OR REPLACE INTO undergraduate_major_scores (school_id, year, province, major_name, batch, avg_score, min_score, min_rank, major_group, subject_requirement) VALUES
    (2, 2021, '北京', '计算机科学与技术', '本科批', NULL, 693, 100, '(02)', '物理必选'),
    (2, 2021, '北京', '电子信息类', '本科批', NULL, 688, 150, '(02)', '物理必选');
  `;
  db.exec(tsinghuaMajorSql);
  console.log('插入清华大学本科专业分数线完成');

  // 插入北京大学研究生信息
  const pkuPostgradSql = `
    INSERT OR REPLACE INTO postgraduate_info (school_id, year, enrollment_plan, registration_start, registration_end, exam_date_start, exam_date_end, majors_offered, contact_phone, official_website, important_notes, brochure_url) VALUES
    (1, 2025, '约5000人', '2024-10-08', '2024-10-25', '2024-12-21', '2024-12-22', '哲学、经济学、法学、教育学、文学、历史学、理学、工学、管理学、艺术学等', '010-62751351', 'https://grs.pku.edu.cn', '1. 考生需满足本科及以上学历；2. 部分专业要求相关工作经验；3. 复试含笔试、面试、综合能力考核。', 'https://grs.pku.edu.cn/docs/2025_guide.pdf');
  `;
  db.exec(pkuPostgradSql);
  console.log('插入北京大学研究生信息完成');

  // 插入清华大学研究生信息
  const tsinghuaPostgradSql = `
    INSERT OR REPLACE INTO postgraduate_info (school_id, year, enrollment_plan, registration_start, registration_end, exam_date_start, exam_date_end, majors_offered, contact_phone, official_website, important_notes, brochure_url) VALUES
    (2, 2025, '约6000人', '2024-10-08', '2024-10-25', '2024-12-21', '2024-12-22', '工学、理学、经济学、法学、文学、医学、管理学、艺术学等', '010-62782192', 'https://yz.tsinghua.edu.cn', '详见招生简章。', 'https://yz.tsinghua.edu.cn/sszs2025.pdf');
  `;
  db.exec(tsinghuaPostgradSql);
  console.log('插入清华大学研究生信息完成');

  // 插入北京大学研究生复试线
  const pkuReplyLinesSql = `
    INSERT OR REPLACE INTO postgraduate_reply_lines (school_id, year, line_type, category_name, category_code, politics, foreign_language, 专业课1, 专业课2, total_score, remarks) VALUES
    (1, 2026, '普通复试线', '哲学', '01', 55, 55, 90, 90, 345, NULL),
    (1, 2026, '普通复试线', '经济学', '02', 55, 55, 90, 90, 375, NULL),
    (1, 2026, '普通复试线', '法学', '03', 55, 55, 90, 90, 345, NULL),
    (1, 2026, '普通复试线', '教育学', '04', 55, 55, 180, NULL, 350, '专业课为311教育学专业基础综合'),
    (1, 2026, '普通复试线', '文学', '05', 55, 55, 90, 90, 355, NULL),
    (1, 2026, '普通复试线', '历史学', '06', 55, 55, 180, NULL, 355, NULL);
  `;
  db.exec(pkuReplyLinesSql);
  console.log('插入北京大学研究生复试线完成');

  // 插入清华大学研究生复试线
  const tsinghuaReplyLinesSql = `
    INSERT OR REPLACE INTO postgraduate_reply_lines (school_id, year, line_type, category_name, category_code, politics, foreign_language, 专业课1, 专业课2, total_score, remarks) VALUES
    (2, 2026, '普通复试线', '工学', '08', 50, 50, 80, 80, 320, NULL),
    (2, 2026, '普通复试线', '理学', '07', 50, 50, 80, 80, 310, NULL),
    (2, 2026, '普通复试线', '经济学', '02', 50, 50, 90, 90, 350, NULL);
  `;
  db.exec(tsinghuaReplyLinesSql);
  console.log('插入清华大学研究生复试线完成');

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
  console.error('错误堆栈:', error.stack);
}
