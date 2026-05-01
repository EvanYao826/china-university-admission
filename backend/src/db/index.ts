import Database from 'better-sqlite3';
import path from 'path';

class DatabaseManager {
  private static instance: DatabaseManager;
  private db: Database.Database;
  private initialized = false;

  private constructor() {
    const dbPath = process.env.DB_PATH || path.join(__dirname, '../../../data/test.db');
    console.log(`Connecting to database: ${dbPath}`);

    this.db = new Database(dbPath);

    this.db.pragma('foreign_keys = ON');

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
    if (this.initialized) {
      return;
    }

    const tableDefinitions = [
      {
        name: 'universities',
        sql: `
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
        `
      },
      {
        name: 'undergraduate_admissions',
        sql: `
          CREATE TABLE IF NOT EXISTS undergraduate_admissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            university_id INTEGER NOT NULL,
            province TEXT NOT NULL,
            year INTEGER NOT NULL,
            category TEXT,
            batch TEXT,
            enrollment_type TEXT,
            major TEXT,
            min_score REAL,
            min_rank INTEGER,
            avg_score REAL,
            provincial_control_line REAL,
            subject_requirements TEXT,
            professional_group TEXT,
            source_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE
          )
        `
      },
      {
        name: 'graduate_admissions',
        sql: `
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
            FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE
          )
        `
      }
    ];

    const indexDefinitions = [
      'CREATE INDEX IF NOT EXISTS idx_universities_province ON universities(province)',
      'CREATE INDEX IF NOT EXISTS idx_universities_type ON universities(type)',
      'CREATE INDEX IF NOT EXISTS idx_universities_level ON universities(level)',
      'CREATE INDEX IF NOT EXISTS idx_undergraduate_university_year ON undergraduate_admissions(university_id, year)',
      'CREATE INDEX IF NOT EXISTS idx_undergraduate_province_year ON undergraduate_admissions(province, year)',
      'CREATE INDEX IF NOT EXISTS idx_graduate_university_year ON graduate_admissions(university_id, year)'
    ];

    let tablesCreated = 0;
    let indexesCreated = 0;

    for (const table of tableDefinitions) {
      const exists = this.db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?").get(table.name);

      if (!exists) {
        this.db.exec(table.sql);
        tablesCreated++;
        console.log(`  Created table: ${table.name}`);
      }
    }

    for (const indexSql of indexDefinitions) {
      const match = indexSql.match(/IF NOT EXISTS\s+(\w+)/);
      if (match) {
        const indexName = match[1];
        const exists = this.db.prepare("SELECT name FROM sqlite_master WHERE type='index' AND name=?").get(indexName);

        if (!exists) {
          this.db.exec(indexSql);
          indexesCreated++;
          console.log(`  Created index: ${indexName}`);
        }
      }
    }

    if (tablesCreated === 0 && indexesCreated === 0) {
      console.log('  Database tables already exist, skipping creation.');
    } else {
      console.log(`  Created ${tablesCreated} table(s) and ${indexesCreated} index(es).`);
    }

    this.initialized = true;
  }

  public close(): void {
    if (this.db) {
      this.db.close();
    }
  }
}

export default DatabaseManager;