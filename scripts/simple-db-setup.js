// 简单数据库设置脚本
const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

console.log('🔧 开始设置数据库...');

const dbPath = './data/university.db';
const sqlPath = './scripts/create-final-tables.sql';

try {
  // 1. 检查并备份
  if (fs.existsSync(dbPath)) {
    const backup = `${dbPath}.backup.${Date.now()}`;
    fs.copyFileSync(dbPath, backup);
    console.log(`📁 备份创建: ${backup}`);
  }

  // 2. 创建数据库
  console.log('🔗 连接数据库...');
  const db = new Database(dbPath);
  db.pragma('foreign_keys = ON');

  // 3. 读取SQL
  console.log('📄 读取SQL文件...');
  const sql = fs.readFileSync(sqlPath, 'utf8');

  // 4. 分割并执行（简单方法）
  const lines = sql.split('\n');
  let currentStmt = '';
  let inStatement = false;

  for (const line of lines) {
    const trimmed = line.trim();

    // 跳过注释
    if (trimmed.startsWith('--') || trimmed.startsWith('/*')) {
      continue;
    }

    currentStmt += line + '\n';

    // 如果行以分号结束，执行语句
    if (line.trim().endsWith(';')) {
      try {
        db.exec(currentStmt);
        console.log(`  ✓ 执行语句`);
      } catch (err) {
        console.log(`  ⚠️ 跳过: ${err.message.substring(0, 60)}`);
      }
      currentStmt = '';
    }
  }

  // 5. 验证结果
  console.log('\n🔍 验证结果:');

  const tables = ['schools', 'undergraduate_yearly_scores', 'undergraduate_major_scores',
                  'postgraduate_info', 'postgraduate_reply_lines'];

  tables.forEach(tableName => {
    try {
      const count = db.prepare(`SELECT COUNT(*) as cnt FROM ${tableName}`).get();
      console.log(`  ${tableName}: ${count.cnt} 条记录`);
    } catch (err) {
      console.log(`  ${tableName}: 表不存在或错误`);
    }
  });

  // 6. 数据预览
  console.log('\n👀 数据预览:');

  const schools = db.prepare('SELECT id, name, province, level FROM schools LIMIT 3').all();
  console.log('高校:');
  schools.forEach(s => {
    console.log(`  ${s.id}. ${s.name} (${s.province}, ${s.level})`);
  });

  const scores = db.prepare(`
    SELECT s.name, u.year, u.province, u.min_score
    FROM undergraduate_yearly_scores u
    JOIN schools s ON u.school_id = s.id
    LIMIT 2
  `).all();

  console.log('\n录取分数:');
  scores.forEach(r => {
    console.log(`  ${r.name} ${r.year}年 ${r.province}: ${r.min_score}分`);
  });

  db.close();
  console.log('\n✅ 数据库设置完成!');
  console.log(`📁 数据库文件: ${path.resolve(dbPath)}`);

} catch (error) {
  console.error('❌ 错误:', error.message);
  process.exit(1);
}