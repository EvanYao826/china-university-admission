const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

// 配置
const DB_PATH = './data/university.db';
const SQL_FILE = './scripts/create-final-tables.sql';
const BACKUP_DIR = './data/backups';

console.log('🚀 开始执行数据库优化...');
console.log('📁 数据库路径:', path.resolve(DB_PATH));
console.log('📄 SQL文件:', path.resolve(SQL_FILE));

// 创建备份目录
if (!fs.existsSync(BACKUP_DIR)) {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
}

try {
    // 1. 备份现有数据库
    let backupPath = null;
    if (fs.existsSync(DB_PATH)) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        backupPath = path.join(BACKUP_DIR, `university.db.backup.${timestamp}`);
        fs.copyFileSync(DB_PATH, backupPath);
        console.log(`✅ 数据库已备份: ${backupPath}`);

        // 检查现有表结构
        const oldDb = new Database(DB_PATH, { readonly: true });
        const oldTables = oldDb.prepare(`
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        `).all();
        oldDb.close();

        console.log(`📊 现有表数量: ${oldTables.length}`);
        if (oldTables.length > 0) {
            console.log('📋 现有表:');
            oldTables.forEach((table, i) => {
                console.log(`  ${i + 1}. ${table.name}`);
            });
        }
    } else {
        console.log('📝 数据库文件不存在，将创建新数据库');
    }

    // 2. 创建新数据库连接
    console.log('\n🔗 创建数据库连接...');
    const db = new Database(DB_PATH);

    // 启用外键和性能优化
    db.pragma('foreign_keys = ON');
    db.pragma('journal_mode = WAL');
    db.pragma('synchronous = NORMAL');

    // 3. 读取并执行SQL
    console.log('📖 读取SQL文件...');
    const sqlContent = fs.readFileSync(SQL_FILE, 'utf8');

    // 分割SQL语句（按分号分割，但排除视图和触发器中的分号）
    const statements = [];
    let currentStatement = '';
    let inView = false;
    let inTrigger = false;

    const lines = sqlContent.split('\n');
    for (const line of lines) {
        const trimmedLine = line.trim();

        // 检测视图开始/结束
        if (trimmedLine.toUpperCase().startsWith('CREATE VIEW')) {
            inView = true;
        }
        if (inView && trimmedLine.toUpperCase().startsWith('CREATE TRIGGER')) {
            inView = false;
        }

        // 检测触发器开始/结束
        if (trimmedLine.toUpperCase().startsWith('CREATE TRIGGER')) {
            inTrigger = true;
        }
        if (inTrigger && trimmedLine.toUpperCase().startsWith('INSERT OR IGNORE')) {
            inTrigger = false;
        }

        currentStatement += line + '\n';

        // 如果不是在视图或触发器中，并且遇到分号，则结束当前语句
        if (!inView && !inTrigger && line.includes(';')) {
            statements.push(currentStatement.trim());
            currentStatement = '';
        }
    }

    // 添加最后一个语句（如果有）
    if (currentStatement.trim()) {
        statements.push(currentStatement.trim());
    }

    console.log(`📝 共识别出 ${statements.length} 条SQL语句`);

    // 4. 执行SQL语句
    console.log('\n⚡ 开始执行SQL语句...');
    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < statements.length; i++) {
        const stmt = statements[i];
        if (!stmt) continue;

        try {
            // 跳过注释和空行
            if (stmt.startsWith('--') || stmt.startsWith('/*')) {
                console.log(`  📝 [${i + 1}/${statements.length}] 注释: ${stmt.substring(0, 50)}...`);
                continue;
            }

            console.log(`  🔧 [${i + 1}/${statements.length}] 执行语句...`);

            // 特殊处理SELECT验证语句
            if (stmt.toUpperCase().startsWith('SELECT')) {
                const result = db.prepare(stmt).all();
                if (result && result.length > 0) {
                    console.log(`    ✅ 验证结果:`);
                    result.forEach(row => {
                        if (row.check_item) {
                            console.log(`      ${row.check_item}`);
                        } else if (row.item && row.count !== undefined) {
                            console.log(`      ${row.item} ${row.count}`);
                        } else if (row.name) {
                            console.log(`      ${row.name}`);
                        }
                    });
                }
            } else {
                db.exec(stmt);
            }

            successCount++;
        } catch (error) {
            errorCount++;
            console.error(`    ❌ 语句执行失败 [${i + 1}]:`, error.message);
            console.error(`       SQL: ${stmt.substring(0, 100)}...`);
        }
    }

    // 5. 验证优化结果
    console.log('\n🔍 验证优化结果...');

    // 检查所有表
    const tables = db.prepare(`
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    `).all();

    console.log(`📊 创建的表 (${tables.length}个):`);
    tables.forEach(table => {
        const count = db.prepare(`SELECT COUNT(*) as count FROM ${table.name}`).get();
        console.log(`  • ${table.name}: ${count.count} 条记录`);
    });

    // 检查索引
    const indexes = db.prepare(`
        SELECT name FROM sqlite_master
        WHERE type='index' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    `).all();

    console.log(`📈 创建的索引 (${indexes.length}个):`);
    indexes.forEach((index, i) => {
        if (i < 10) { // 只显示前10个
            console.log(`  • ${index.name}`);
        }
    });
    if (indexes.length > 10) {
        console.log(`  ... 还有 ${indexes.length - 10} 个索引`);
    }

    // 检查视图
    const views = db.prepare(`
        SELECT name FROM sqlite_master
        WHERE type='view'
        ORDER BY name
    `).all();

    if (views.length > 0) {
        console.log(`👁️ 创建的视图 (${views.length}个):`);
        views.forEach(view => {
            console.log(`  • ${view.name}`);
        });
    }

    // 6. 数据预览
    console.log('\n👀 数据预览:');

    // 高校数据
    const schools = db.prepare(`
        SELECT id, name, province, level, type
        FROM schools
        ORDER BY id LIMIT 5
    `).all();

    console.log('🏫 高校数据 (前5所):');
    schools.forEach(school => {
        console.log(`  ${school.id}. ${school.name} (${school.province}, ${school.level}, ${school.type})`);
    });

    // 本科生数据
    const undergrad = db.prepare(`
        SELECT s.name, u.year, u.province, u.batch, u.subject_category, u.min_score
        FROM undergraduate_yearly_scores u
        JOIN schools s ON u.school_id = s.id
        ORDER BY u.year DESC, u.min_score DESC
        LIMIT 3
    `).all();

    console.log('\n🎓 本科生录取数据 (最新3条):');
    undergrad.forEach(item => {
        console.log(`  ${item.name} ${item.year}年 ${item.province} ${item.batch} ${item.subject_category}: ${item.min_score}分`);
    });

    // 研究生数据
    const postgrad = db.prepare(`
        SELECT s.name, p.year, p.line_type, p.category_name, p.total_score
        FROM postgraduate_reply_lines p
        JOIN schools s ON p.school_id = s.id
        ORDER BY p.year DESC, p.total_score DESC
        LIMIT 3
    `).all();

    console.log('\n🎓 研究生复试线 (最新3条):');
    postgrad.forEach(item => {
        console.log(`  ${item.name} ${item.year}年 ${item.line_type} ${item.category_name}: ${item.total_score}分`);
    });

    // 7. 性能检查
    console.log('\n⚡ 性能检查:');
    const pageSize = db.pragma('page_size', { simple: true });
    const pageCount = db.pragma('page_count', { simple: true });
    const dbSize = (pageSize * pageCount) / 1024 / 1024; // MB

    console.log(`  • 数据库大小: ${dbSize.toFixed(2)} MB`);
    console.log(`  • 页大小: ${pageSize} bytes`);
    console.log(`  • 总页数: ${pageCount}`);

    // 关闭数据库
    db.close();

    // 8. 总结
    console.log('\n' + '='.repeat(50));
    console.log('📋 优化执行总结:');
    console.log('='.repeat(50));
    console.log(`✅ 成功执行: ${successCount} 条语句`);
    console.log(`❌ 执行失败: ${errorCount} 条语句`);
    console.log(`📊 创建表: ${tables.length} 个`);
    console.log(`📈 创建索引: ${indexes.length} 个`);
    console.log(`👁️ 创建视图: ${views.length} 个`);

    if (backupPath) {
        console.log(`💾 备份文件: ${backupPath}`);
    }

    console.log(`📁 数据库文件: ${path.resolve(DB_PATH)}`);

    if (errorCount === 0) {
        console.log('\n🎉 数据库优化完成！所有语句执行成功。');
    } else {
        console.log(`\n⚠️ 数据库优化完成，但有 ${errorCount} 个错误，请检查。`);
    }

} catch (error) {
    console.error('\n💥 严重错误:', error.message);
    console.error(error.stack);
    process.exit(1);
}