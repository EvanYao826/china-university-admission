import Database from 'better-sqlite3';
import path from 'path';

interface University {
  id?: number;
  name: string;
  type?: string;
  level?: string;
  province?: string;
  city?: string;
  tags?: string;
  logo_url?: string;
  description?: string;
}

interface UndergraduateAdmission {
  id?: number;
  university_id: number;
  province: string;
  year: number;
  category?: string;
  batch?: string;
  enrollment_type?: string;
  major?: string;
  min_score?: number;
  min_rank?: number;
  avg_score?: number;
  provincial_control_line?: number;
  subject_requirements?: string;
  professional_group?: string;
  source_url?: string;
}

interface PostgraduateAdmission {
  id?: number;
  university_id: number;
  year: number;
  degree_type?: string;
  discipline_category?: string;
  admission_type?: string;
  political_score?: number;
  foreign_language_score?: number;
  subject1_score?: number;
  subject2_score?: number;
  total_score?: number;
  remarks?: string;
  adjustment_info?: string;
  source_url?: string;
}

export class SchoolRepository {
  private db: Database.Database;

  constructor() {
    const dbPath = path.join(__dirname, '../../../data/test.db');
    this.db = new Database(dbPath);
    this.db.pragma('foreign_keys = ON');
  }

  getAllSchools(filters: Partial<University> = {}): University[] {
    let query = 'SELECT * FROM universities WHERE 1=1';
    const params: any[] = [];

    if (filters.name) {
      query += ' AND name LIKE ?';
      params.push(`%${filters.name}%`);
    }
    if (filters.type) {
      query += ' AND type = ?';
      params.push(filters.type);
    }
    if (filters.level) {
      query += ' AND level LIKE ?';
      params.push(`%${filters.level}%`);
    }
    if (filters.province) {
      query += ' AND province = ?';
      params.push(filters.province);
    }

    query += ' ORDER BY id';

    const stmt = this.db.prepare(query);
    return stmt.all(...params) as University[];
  }

  getSchoolById(id: number): University | undefined {
    const stmt = this.db.prepare('SELECT * FROM universities WHERE id = ?');
    return stmt.get(id) as University | undefined;
  }



  getPostgraduateAdmissions(universityId: number, filters: Partial<PostgraduateAdmission> = {}): PostgraduateAdmission[] {
    let query = 'SELECT * FROM postgraduate_admissions WHERE university_id = ?';
    const params: any[] = [universityId];

    if (filters.year) {
      query += ' AND year = ?';
      params.push(filters.year);
    }
    if (filters.degree_type) {
      query += ' AND degree_type = ?';
      params.push(filters.degree_type);
    }
    if (filters.admission_type) {
      query += ' AND admission_type = ?';
      params.push(filters.admission_type);
    }

    query += ' ORDER BY year DESC';

    const stmt = this.db.prepare(query);
    return stmt.all(...params) as PostgraduateAdmission[];
  }

  createUniversity(university: University): number {
    const stmt = this.db.prepare(`
      INSERT INTO universities (name, type, level, province, city, tags, logo_url, description)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      university.name,
      university.type,
      university.level,
      university.province,
      university.city,
      university.tags,
      university.logo_url,
      university.description
    );
    return result.lastInsertRowid as number;
  }

  createUndergraduateAdmission(admission: UndergraduateAdmission): number {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO undergraduate_admissions
      (university_id, province, year, category, batch, enrollment_type, major, min_score, min_rank, avg_score, provincial_control_line, subject_requirements, professional_group, source_url)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      admission.university_id,
      admission.province,
      admission.year,
      admission.category,
      admission.batch,
      admission.enrollment_type,
      admission.major,
      admission.min_score,
      admission.min_rank,
      admission.avg_score,
      admission.provincial_control_line,
      admission.subject_requirements,
      admission.professional_group,
      admission.source_url
    );
    return result.lastInsertRowid as number;
  }

  createPostgraduateAdmission(admission: PostgraduateAdmission): number {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO postgraduate_admissions
      (university_id, year, degree_type, discipline_category, admission_type, political_score, foreign_language_score, subject1_score, subject2_score, total_score, remarks, adjustment_info, source_url)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      admission.university_id,
      admission.year,
      admission.degree_type,
      admission.discipline_category,
      admission.admission_type,
      admission.political_score,
      admission.foreign_language_score,
      admission.subject1_score,
      admission.subject2_score,
      admission.total_score,
      admission.remarks,
      admission.admission_type === '调剂信息' ? admission.adjustment_info : null,
      admission.source_url
    );
    return result.lastInsertRowid as number;
  }

  // 对类别进行归类
  private categorizeCategory(category: string): string {
    if (category.includes('文科') || category.includes('历史')) {
      return '文科/历史类';
    } else if (category.includes('理科') || category.includes('物理')) {
      return '理科/物理类';
    } else if (category.includes('不限')) {
      return '不限组';
    } else if (category.includes('物化')) {
      return '物化组';
    } else {
      return category;
    }
  }

  // 获取省份可用的类别列表（已归类）
  getCategoriesByProvince(province: string): string[] {
    const stmt = this.db.prepare(`
      SELECT DISTINCT category 
      FROM undergraduate_admissions 
      WHERE province = ? 
      ORDER BY category
    `);
    const result = stmt.all(province) as { category: string }[];
    const categories = result.map(row => row.category).filter(Boolean);
    
    // 对类别进行归类并去重
    const categorized = categories.map(this.categorizeCategory);
    const uniqueCategories = [...new Set(categorized)];
    
    return uniqueCategories;
  }

  // 获取省份可用的批次列表
  getBatchesByProvinceAndCategory(province: string, category: string, universityId?: number): string[] {
    let query = `
      SELECT DISTINCT batch 
      FROM undergraduate_admissions 
      WHERE province = ? AND (
        category = ? OR 
        (category LIKE '%文科%' AND ? LIKE '%文科%') OR 
        (category LIKE '%理科%' AND ? LIKE '%理科%') OR 
        (category LIKE '%历史%' AND ? LIKE '%历史%') OR 
        (category LIKE '%物理%' AND ? LIKE '%物理%') OR 
        (category LIKE '%不限%' AND ? LIKE '%不限%') OR 
        (category LIKE '%物化%' AND ? LIKE '%物化%')
      ) 
    `;
    const params: any[] = [province, category, category, category, category, category, category, category];

    if (universityId) {
      query += ' AND university_id = ? ';
      params.push(universityId);
    }

    query += ' ORDER BY batch';

    const stmt = this.db.prepare(query);
    const result = stmt.all(...params) as { batch: string }[];
    return result.map(row => row.batch).filter(Boolean);
  }

  // 获取本科录取数据（支持归类后的类别）
  getUndergraduateAdmissions(universityId: number, filters: Partial<UndergraduateAdmission> = {}): UndergraduateAdmission[] {
    let query = 'SELECT * FROM undergraduate_admissions WHERE university_id = ?';
    const params: any[] = [universityId];

    if (filters.province) {
      query += ' AND province = ?';
      params.push(filters.province);
    }
    // 不添加年份过滤，这样会返回所有年份的数据
    // if (filters.year) {
    //   query += ' AND year = ?';
    //   params.push(filters.year);
    // }
    if (filters.category) {
      query += ' AND (';
      query += 'category = ? OR ';
      query += '(category LIKE \'%文科%\' AND ? LIKE \'%文科%\') OR ';
      query += '(category LIKE \'%理科%\' AND ? LIKE \'%理科%\') OR ';
      query += '(category LIKE \'%历史%\' AND ? LIKE \'%历史%\') OR ';
      query += '(category LIKE \'%物理%\' AND ? LIKE \'%物理%\') OR ';
      query += '(category LIKE \'%不限%\' AND ? LIKE \'%不限%\') OR ';
      query += '(category LIKE \'%物化%\' AND ? LIKE \'%物化%\')';
      query += ')';
      params.push(filters.category, filters.category, filters.category, filters.category, filters.category, filters.category, filters.category);
    }
    if (filters.batch) {
      query += ' AND batch = ?';
      params.push(filters.batch);
    }

    query += ' ORDER BY year DESC';

    const stmt = this.db.prepare(query);
    return stmt.all(...params) as UndergraduateAdmission[];
  }

  close(): void {
    this.db.close();
  }
}
