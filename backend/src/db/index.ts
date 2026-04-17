import Database from 'better-sqlite3';
import path from 'path';

class DatabaseManager {
  private static instance: DatabaseManager;
  private db: Database.Database;

  private constructor() {
    const dbPath = process.env.DB_PATH || path.join(__dirname, '../../../data/university.db');
    console.log(`Connecting to database: ${dbPath}`);

    this.db = new Database(dbPath, {
      verbose: process.env.NODE_ENV === 'development' ? console.log : undefined
    });

    // 启用外键约束
    this.db.pragma('foreign_keys = ON');

    // 创建表（如果不存在）
    this.initializeTables();
  }

  public static getInstance(): DatabaseManager {
    if (!DatabaseManager.instance) {
      DatabaseManager.instance = new DatabaseManager();
    }
    return DatabaseManager.instance;
  }

  public getDatabase(): Database.Database {
    return this.db;
  }

  private initializeTables(): void {
    // 创建高校表
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS universities (
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

    // 创建高考录取表
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS gaokao_admissions (
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

    // 创建研究生录取表
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS graduate_admissions (
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
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_universities_province ON universities(province);
      CREATE INDEX IF NOT EXISTS idx_universities_type ON universities(type);
      CREATE INDEX IF NOT EXISTS idx_universities_level ON universities(level);
      CREATE INDEX IF NOT EXISTS idx_gaokao_university_year ON gaokao_admissions(university_id, year);
      CREATE INDEX IF NOT EXISTS idx_gaokao_province_year ON gaokao_admissions(province, year);
      CREATE INDEX IF NOT EXISTS idx_graduate_university_year ON graduate_admissions(university_id, year);
    `);
  }

  public close(): void {
    this.db.close();
  }
}

export default DatabaseManager;