const Database = require('better-sqlite3');

// 数据库文件路径
const dbPath = './data/university.db';

try {
  console.log('连接数据库...');
  const db = new Database(dbPath);

  console.log('检查表结构...');
  
  // 检查表是否存在
  const tables = db.prepare(`
    SELECT name FROM sqlite_master WHERE type='table'
  `).all();
  
  console.log('存在的表:', tables.map(t => t.name));
  
  // 检查 universities 表
  if (tables.some(t => t.name === 'universities')) {
    const count = db.prepare('SELECT COUNT(*) as count FROM universities').get();
    console.log('universities 表数据量:', count.count);
    
    // 查看前5条数据
    const universities = db.prepare('SELECT * FROM universities LIMIT 5').all();
    console.log('前5条高校数据:', universities);
  }
  
  // 检查 gaokao_admissions 表
  if (tables.some(t => t.name === 'gaokao_admissions')) {
    const count = db.prepare('SELECT COUNT(*) as count FROM gaokao_admissions').get();
    console.log('gaokao_admissions 表数据量:', count.count);
  }
  
  // 检查 graduate_admissions 表
  if (tables.some(t => t.name === 'graduate_admissions')) {
    const count = db.prepare('SELECT COUNT(*) as count FROM graduate_admissions').get();
    console.log('graduate_admissions 表数据量:', count.count);
  }
  
  db.close();
  console.log('数据库测试完成');
} catch (error) {
  console.error('数据库测试失败:', error.message);
}
