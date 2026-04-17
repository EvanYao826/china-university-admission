const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

// 数据库文件路径
const dbPath = './data/university.db';
const sqlPath = './scripts/create-optimized-tables.sql';

console.log('🚀 开始初始化优化后的数据库...');

try {
  // 如果数据库文件已存在，备份
  if (fs.existsSync(dbPath)) {
    const backupPath = `${dbPath}.backup.${Date.now()}`;
    fs.copyFileSync(dbPath, backupPath);
    console.log(`📁 已备份原数据库: ${backupPath}`);
  }

  // 创建数据库连接
  console.log('🔗 连接数据库...');
  const db = new Database(dbPath);

  // 启用外键约束
  db.pragma('foreign_keys = ON');

  // 读取SQL文件
  console.log('📄 读取SQL文件...');
  const sql = fs.readFileSync(sqlPath, 'utf8');

  // 执行SQL语句
  console.log('⚡ 执行SQL语句...');
  const statements = sql.split(';').filter(stmt => stmt.trim());

  statements.forEach((stmt, index) => {
    if (stmt.trim()) {
      try {
        db.exec(stmt);
        console.log(`  ✓ 执行语句 ${index + 1}/${statements.length}`);
      } catch (error) {
        console.error(`  ✗ 语句 ${index + 1} 执行失败:`, error.message);
      }
    }
  });

  // 验证表创建
  console.log('\n🔍 验证数据库结构...');
  const tables = db.prepare(`
    SELECT name FROM sqlite_master
    WHERE type='table' AND name NOT LIKE 'sqlite_%'
    ORDER BY name
  `).all();

  console.log('📊 创建的表:');
  tables.forEach(table => {
    const count = db.prepare(`SELECT COUNT(*) as count FROM ${table.name}`).get();
    console.log(`  • ${table.name}: ${count.count} 条记录`);
  });

  // 查看示例数据
  console.log('\n👀 示例数据预览:');

  // 高校数据
  const universities = db.prepare('SELECT id, name, province, level FROM universities LIMIT 5').all();
  console.log('🏫 高校数据:');
  universities.forEach(uni => {
    console.log(`  ${uni.id}. ${uni.name} (${uni.province}, ${uni.level})`);
  });

  // 本科生数据
  const undergrad = db.prepare(`
    SELECT u.name, ua.year, ua.province, ua.category, ua.min_score, ua.min_rank
    FROM undergraduate_admissions ua
    JOIN universities u ON ua.university_id = u.id
    LIMIT 3
  `).all();

  console.log('\n🎓 本科生录取数据:');
  undergrad.forEach(item => {
    console.log(`  ${item.name} ${item.year}年 ${item.province} ${item.category}: ${item.min_score}分 (位次:${item.min_rank})`);
  });

  // 研究生数据
  const postgrad = db.prepare(`
    SELECT u.name, pa.year, pa.category_name, pa.total_score
    FROM postgraduate_admissions pa
    JOIN universities u ON pa.university_id = u.id
    WHERE pa.line_type = '普通复试线'
    LIMIT 3
  `).all();

  console.log('\n🎓 研究生复试线:');
  postgrad.forEach(item => {
    console.log(`  ${item.name} ${item.year}年 ${item.category_name}: ${item.total_score}分`);
  });

  db.close();
  console.log('\n✅ 数据库初始化完成!');
  console.log('📁 数据库文件:', path.resolve(dbPath));

} catch (error) {
  console.error('❌ 初始化失败:', error.message);
  process.exit(1);
}