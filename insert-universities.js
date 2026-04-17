const Database = require('better-sqlite3');

// 数据库文件路径
const dbPath = './data/university.db';

try {
  console.log('连接数据库...');
  const db = new Database(dbPath);

  console.log('插入高校数据...');
  
  // 插入5所高校数据
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

  const insertUniversity = db.prepare(`
    INSERT OR IGNORE INTO universities (name, province, city, type, level, website, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  universities.forEach(uni => {
    const result = insertUniversity.run(
      uni.name,
      uni.province,
      uni.city,
      uni.type,
      uni.level,
      uni.website,
      uni.description
    );
    console.log(`插入 ${uni.name}: ${result.changes > 0 ? '成功' : '已存在'}`);
  });

  // 验证插入结果
  const count = db.prepare('SELECT COUNT(*) as count FROM universities').get();
  console.log(`\n高校数据插入完成，共 ${count.count} 所高校`);

  // 查看所有高校
  const allUniversities = db.prepare('SELECT id, name, province, level FROM universities').all();
  console.log('\n所有高校:');
  allUniversities.forEach(uni => {
    console.log(`${uni.id}. ${uni.name} (${uni.province}, ${uni.level})`);
  });

  db.close();
  console.log('\n操作完成');
} catch (error) {
  console.error('操作失败:', error.message);
}
