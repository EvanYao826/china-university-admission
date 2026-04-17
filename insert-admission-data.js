const Database = require('better-sqlite3');

// 数据库文件路径
const dbPath = './data/university.db';

try {
  console.log('连接数据库...');
  const db = new Database(dbPath);

  console.log('获取高校ID...');
  // 获取所有高校
  const universities = db.prepare('SELECT id, name FROM universities').all();
  console.log(`找到 ${universities.length} 所高校`);

  // 山河四省
  const provinces = ['山东', '山西', '河南', '河北'];
  // 近三年
  const years = [2023, 2022, 2021];
  // 科类
  const categories = ['理科', '文科'];
  // 批次
  const batches = ['本科一批'];

  console.log('插入高考录取数据...');
  const insertGaokao = db.prepare(`
    INSERT OR IGNORE INTO gaokao_admissions
    (university_id, year, province, category, batch, min_score, avg_score, max_score, min_rank, avg_rank, max_rank, admission_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  let gaokaoCount = 0;
  universities.forEach((uni, uniIndex) => {
    provinces.forEach(province => {
      years.forEach(year => {
        categories.forEach(category => {
          batches.forEach(batch => {
            // 生成合理的分数和排名数据
            const baseScore = 650 + uniIndex * 10;
            const yearFactor = (2023 - year) * 5; // 每年分数略有下降
            const provinceFactor = provinces.indexOf(province) * 2; // 不同省份分数略有差异
            
            const minScore = baseScore - 15 - yearFactor + provinceFactor;
            const avgScore = baseScore - 5 - yearFactor + provinceFactor;
            const maxScore = baseScore + 5 - yearFactor + provinceFactor;
            
            const minRank = 1500 + uniIndex * 200 + years.indexOf(year) * 100;
            const avgRank = 1200 + uniIndex * 150 + years.indexOf(year) * 80;
            const maxRank = 900 + uniIndex * 100 + years.indexOf(year) * 60;
            
            const admissionCount = 80 + uniIndex * 10 + provinces.indexOf(province) * 5;

            const result = insertGaokao.run(
              uni.id,
              year,
              province,
              category,
              batch,
              minScore,
              avgScore,
              maxScore,
              minRank,
              avgRank,
              maxRank,
              admissionCount
            );
            
            if (result.changes > 0) {
              gaokaoCount++;
            }
          });
        });
      });
    });
  });

  console.log(`插入了 ${gaokaoCount} 条高考录取数据`);

  console.log('插入研究生录取数据...');
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

  let graduateCount = 0;
  universities.forEach((uni, uniIndex) => {
    years.forEach(year => {
      majors.forEach((major, majorIndex) => {
        // 生成合理的分数数据
        const baseScore = 380 + uniIndex * 5 + majorIndex * 2;
        const yearFactor = (2023 - year) * 3;
        
        const minScore = baseScore - 10 - yearFactor;
        const avgScore = baseScore - yearFactor;
        const maxScore = baseScore + 10 - yearFactor;
        
        const admissionCount = 15 + uniIndex * 3 + majorIndex;

        // 硕士
        const result1 = insertGraduate.run(
          uni.id,
          year,
          major,
          '硕士',
          '全日制',
          admissionCount,
          minScore,
          avgScore,
          maxScore
        );
        
        if (result1.changes > 0) {
          graduateCount++;
        }

        // 博士
        if (uniIndex % 2 === 0) {
          const result2 = insertGraduate.run(
            uni.id,
            year,
            major,
            '博士',
            '全日制',
            Math.floor(admissionCount / 3),
            minScore + 5,
            avgScore + 5,
            maxScore + 5
          );
          
          if (result2.changes > 0) {
            graduateCount++;
          }
        }
      });
    });
  });

  console.log(`插入了 ${graduateCount} 条研究生录取数据`);

  // 验证数据
  console.log('\n验证数据:');
  const totalGaokao = db.prepare('SELECT COUNT(*) as count FROM gaokao_admissions').get();
  const totalGraduate = db.prepare('SELECT COUNT(*) as count FROM graduate_admissions').get();
  
  console.log(`高考录取数据: ${totalGaokao.count} 条`);
  console.log(`研究生录取数据: ${totalGraduate.count} 条`);

  // 查看部分数据
  console.log('\n部分高考数据:');
  const sampleGaokao = db.prepare('SELECT university_id, year, province, category, avg_score FROM gaokao_admissions LIMIT 10').all();
  sampleGaokao.forEach(item => {
    const uni = universities.find(u => u.id === item.university_id);
    console.log(`${uni?.name} - ${item.year}年 ${item.province} ${item.category} - 平均分: ${item.avg_score}`);
  });

  console.log('\n部分研究生数据:');
  const sampleGraduate = db.prepare('SELECT university_id, year, major, degree_type, avg_score FROM graduate_admissions LIMIT 10').all();
  sampleGraduate.forEach(item => {
    const uni = universities.find(u => u.id === item.university_id);
    console.log(`${uni?.name} - ${item.year}年 ${item.major} ${item.degree_type} - 平均分: ${item.avg_score}`);
  });

  db.close();
  console.log('\n数据插入完成');
} catch (error) {
  console.error('操作失败:', error.message);
}
