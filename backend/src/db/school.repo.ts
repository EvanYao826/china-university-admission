import Database from 'better-sqlite3';
import path from 'path';

interface School {
  id?: number;
  name: string;
  type?: string;
  level?: string;
  province?: string;
  description?: string;
  nature?: string;
  education_level?: string;
  category?: string;
  address?: string;
  tags?: string;
  phone?: string;
}

interface UndergraduateYearlyScore {
  id?: number;
  school_id: number;
  year: number;
  province: string;
  batch?: string;
  enrollment_type?: string;
  category?: string;
  professional_group?: string;
  subject_requirement?: string;
  min_score?: number;
  min_rank?: number;
  avg_score?: number;
  provincial_control?: number;
  data_source?: string;
}

interface UndergraduateMajorScore {
  id?: number;
  school_id: number;
  year: number;
  province: string;
  major_name: string;
  batch?: string;
  avg_score?: number;
  min_score?: number;
  min_rank?: number;
  major_group?: string;
  subject_requirement?: string;
}

interface PostgraduateInfo {
  id?: number;
  school_id: number;
  year: number;
  enrollment_plan?: string;
  registration_start?: string;
  registration_end?: string;
  exam_date_start?: string;
  exam_date_end?: string;
  majors_offered?: string;
  contact_phone?: string;
  official_website?: string;
  important_notes?: string;
  brochure_url?: string;
}

interface PostgraduateReplyLine {
  id?: number;
  school_id: number;
  year: number;
  line_type?: string;
  category_name: string;
  category_code?: string;
  politics?: number;
  foreign_language?: number;
  专业课1?: number;
  专业课2?: number;
  total_score?: number;
  remarks?: string;
}

export class SchoolRepository {
  private db: Database.Database;

  constructor() {
    const dbPath = path.join(__dirname, '../../../data/university.db');
    this.db = new Database(dbPath);
    this.db.pragma('foreign_keys = ON');
  }

  getAllSchools(filters: Partial<School> = {}): School[] {
    let query = 'SELECT * FROM schools WHERE 1=1';
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
      query += ' AND level = ?';
      params.push(filters.level);
    }
    if (filters.province) {
      query += ' AND province = ?';
      params.push(filters.province);
    }

    query += ' ORDER BY id';

    const stmt = this.db.prepare(query);
    return stmt.all(...params) as School[];
  }

  getSchoolById(id: number): School | undefined {
    const stmt = this.db.prepare('SELECT * FROM schools WHERE id = ?');
    return stmt.get(id) as School | undefined;
  }

  getUndergraduateYearlyScores(schoolId: number, filters: Partial<UndergraduateYearlyScore> = {}): UndergraduateYearlyScore[] {
    let query = 'SELECT * FROM undergraduate_yearly_scores WHERE school_id = ?';
    const params: any[] = [schoolId];

    if (filters.province) {
      query += ' AND province = ?';
      params.push(filters.province);
    }
    if (filters.year) {
      query += ' AND year = ?';
      params.push(filters.year);
    }
    if (filters.category) {
      query += ' AND category = ?';
      params.push(filters.category);
    }
    if (filters.batch) {
      query += ' AND batch = ?';
      params.push(filters.batch);
    }

    query += ' ORDER BY year DESC';

    const stmt = this.db.prepare(query);
    return stmt.all(...params) as UndergraduateYearlyScore[];
  }

  getUndergraduateMajorScores(schoolId: number, filters: Partial<UndergraduateMajorScore> = {}): UndergraduateMajorScore[] {
    let query = 'SELECT * FROM undergraduate_major_scores WHERE school_id = ?';
    const params: any[] = [schoolId];

    if (filters.province) {
      query += ' AND province = ?';
      params.push(filters.province);
    }
    if (filters.year) {
      query += ' AND year = ?';
      params.push(filters.year);
    }
    if (filters.province) {
      query += ' AND province = ?';
      params.push(filters.province);
    }

    query += ' ORDER BY year DESC, major_name';

    const stmt = this.db.prepare(query);
    return stmt.all(...params) as UndergraduateMajorScore[];
  }

  getPostgraduateInfo(schoolId: number, year: number): PostgraduateInfo | undefined {
    const stmt = this.db.prepare('SELECT * FROM postgraduate_info WHERE school_id = ? AND year = ?');
    return stmt.get(schoolId, year) as PostgraduateInfo | undefined;
  }

  getPostgraduateReplyLines(schoolId: number, year: number): PostgraduateReplyLine[] {
    const stmt = this.db.prepare('SELECT * FROM postgraduate_reply_lines WHERE school_id = ? AND year = ? ORDER BY category_code');
    return stmt.all(schoolId, year) as PostgraduateReplyLine[];
  }

  createSchool(school: School): number {
    const stmt = this.db.prepare(`
      INSERT INTO schools (name, type, level, province, description, nature, education_level, category, address, tags, phone)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      school.name,
      school.type,
      school.level,
      school.province,
      school.description,
      school.nature,
      school.education_level,
      school.category,
      school.address,
      school.tags,
      school.phone
    );
    return result.lastInsertRowid as number;
  }

  createUndergraduateYearlyScore(score: UndergraduateYearlyScore): number {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO undergraduate_yearly_scores
      (school_id, year, province, batch, enrollment_type, category, professional_group, subject_requirement, min_score, min_rank, avg_score, provincial_control, data_source)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      score.school_id,
      score.year,
      score.province,
      score.batch,
      score.enrollment_type,
      score.category,
      score.professional_group,
      score.subject_requirement,
      score.min_score,
      score.min_rank,
      score.avg_score,
      score.provincial_control,
      score.data_source
    );
    return result.lastInsertRowid as number;
  }

  createUndergraduateMajorScore(score: UndergraduateMajorScore): number {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO undergraduate_major_scores
      (school_id, year, province, major_name, batch, avg_score, min_score, min_rank, major_group, subject_requirement)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      score.school_id,
      score.year,
      score.province,
      score.major_name,
      score.batch,
      score.avg_score,
      score.min_score,
      score.min_rank,
      score.major_group,
      score.subject_requirement
    );
    return result.lastInsertRowid as number;
  }

  createPostgraduateInfo(info: PostgraduateInfo): number {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO postgraduate_info
      (school_id, year, enrollment_plan, registration_start, registration_end, exam_date_start, exam_date_end, majors_offered, contact_phone, official_website, important_notes, brochure_url)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      info.school_id,
      info.year,
      info.enrollment_plan,
      info.registration_start,
      info.registration_end,
      info.exam_date_start,
      info.exam_date_end,
      info.majors_offered,
      info.contact_phone,
      info.official_website,
      info.important_notes,
      info.brochure_url
    );
    return result.lastInsertRowid as number;
  }

  createPostgraduateReplyLine(line: PostgraduateReplyLine): number {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO postgraduate_reply_lines
      (school_id, year, line_type, category_name, category_code, politics, foreign_language, 专业课1, 专业课2, total_score, remarks)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      line.school_id,
      line.year,
      line.line_type,
      line.category_name,
      line.category_code,
      line.politics,
      line.foreign_language,
      line.专业课1,
      line.专业课2,
      line.total_score,
      line.remarks
    );
    return result.lastInsertRowid as number;
  }

  close(): void {
    this.db.close();
  }
}
