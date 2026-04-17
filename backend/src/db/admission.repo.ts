import DatabaseManager from './index';
import { AdmissionRecord, GraduateAdmission, SearchParams } from '../types';

export class AdmissionRepository {
  private db = DatabaseManager.getInstance().getDatabase();

  // 获取高校的高考录取数据
  getGaokaoByUniversity(
    universityId: number,
    params: SearchParams = {}
  ): { data: AdmissionRecord[]; total: number } {
    const {
      year,
      province,
      category,
      batch,
      page = 1,
      limit = 50,
      sortBy = 'year',
      sortOrder = 'desc'
    } = params;

    const offset = (page - 1) * limit;

    // 构建 WHERE 子句
    const conditions: string[] = ['university_id = ?'];
    const values: any[] = [universityId];

    if (year) {
      conditions.push('year = ?');
      values.push(year);
    }

    if (province) {
      conditions.push('province = ?');
      values.push(province);
    }

    if (category) {
      conditions.push('category = ?');
      values.push(category);
    }

    if (batch) {
      conditions.push('batch = ?');
      values.push(batch);
    }

    const whereClause = `WHERE ${conditions.join(' AND ')}`;

    // 获取总数
    const countStmt = this.db.prepare(`SELECT COUNT(*) as total FROM gaokao_admissions ${whereClause}`);
    const countResult = countStmt.get(...values) as { total: number };
    const total = countResult.total;

    // 获取数据
    const query = `
      SELECT * FROM gaokao_admissions
      ${whereClause}
      ORDER BY ${sortBy} ${sortOrder.toUpperCase()}
      LIMIT ? OFFSET ?
    `;

    const stmt = this.db.prepare(query);
    const data = stmt.all(...values, limit, offset) as AdmissionRecord[];

    return { data, total };
  }

  // 获取高校的研究生录取数据
  getGraduateByUniversity(
    universityId: number,
    params: SearchParams = {}
  ): { data: GraduateAdmission[]; total: number } {
    const {
      year,
      major,
      degree_type,
      study_mode,
      page = 1,
      limit = 50,
      sortBy = 'year',
      sortOrder = 'desc'
    } = params;

    const offset = (page - 1) * limit;

    // 构建 WHERE 子句
    const conditions: string[] = ['university_id = ?'];
    const values: any[] = [universityId];

    if (year) {
      conditions.push('year = ?');
      values.push(year);
    }

    if (major) {
      conditions.push('major LIKE ?');
      values.push(`%${major}%`);
    }

    if (degree_type) {
      conditions.push('degree_type = ?');
      values.push(degree_type);
    }

    if (study_mode) {
      conditions.push('study_mode = ?');
      values.push(study_mode);
    }

    const whereClause = `WHERE ${conditions.join(' AND ')}`;

    // 获取总数
    const countStmt = this.db.prepare(`SELECT COUNT(*) as total FROM graduate_admissions ${whereClause}`);
    const countResult = countStmt.get(...values) as { total: number };
    const total = countResult.total;

    // 获取数据
    const query = `
      SELECT * FROM graduate_admissions
      ${whereClause}
      ORDER BY ${sortBy} ${sortOrder.toUpperCase()}
      LIMIT ? OFFSET ?
    `;

    const stmt = this.db.prepare(query);
    const data = stmt.all(...values, limit, offset) as GraduateAdmission[];

    return { data, total };
  }

  // 根据分数查询匹配的高校（高考）
  searchByScore(params: {
    province: string;
    year: number;
    category: string;
    batch: string;
    score: number;
    limit?: number;
  }): Array<AdmissionRecord & { university_name: string }> {
    const { province, year, category, batch, score, limit = 20 } = params;

    const query = `
      SELECT ga.*, u.name as university_name
      FROM gaokao_admissions ga
      JOIN universities u ON ga.university_id = u.id
      WHERE ga.province = ?
        AND ga.year = ?
        AND ga.category = ?
        AND ga.batch = ?
        AND ga.avg_score >= ?
      ORDER BY ga.avg_score ASC
      LIMIT ?
    `;

    const stmt = this.db.prepare(query);
    return stmt.all(province, year, category, batch, score, limit) as Array<AdmissionRecord & { university_name: string }>;
  }

  // 获取录取数据统计
  getAdmissionStatistics(universityId: number) {
    // 高考数据统计
    const gaokaoYearStats = this.db.prepare(`
      SELECT year, COUNT(*) as record_count,
             AVG(avg_score) as avg_score,
             SUM(admission_count) as total_admissions
      FROM gaokao_admissions
      WHERE university_id = ?
      GROUP BY year
      ORDER BY year DESC
    `).all(universityId) as Array<{ year: number; record_count: number; avg_score: number; total_admissions: number }>;

    const gaokaoProvinceStats = this.db.prepare(`
      SELECT province, COUNT(*) as record_count,
             SUM(admission_count) as total_admissions
      FROM gaokao_admissions
      WHERE university_id = ?
      GROUP BY province
      ORDER BY total_admissions DESC
    `).all(universityId);

    // 研究生数据统计
    const graduateYearStats = this.db.prepare(`
      SELECT year, COUNT(*) as record_count,
             SUM(admission_count) as total_admissions
      FROM graduate_admissions
      WHERE university_id = ?
      GROUP BY year
      ORDER BY year DESC
    `).all(universityId) as Array<{ year: number; record_count: number; total_admissions: number }>;

    const graduateMajorStats = this.db.prepare(`
      SELECT major, COUNT(*) as record_count,
             SUM(admission_count) as total_admissions
      FROM graduate_admissions
      WHERE university_id = ?
      GROUP BY major
      ORDER BY total_admissions DESC
      LIMIT 10
    `).all(universityId);

    return {
      gaokao: {
        byYear: gaokaoYearStats,
        byProvince: gaokaoProvinceStats,
        totalRecords: gaokaoYearStats.reduce((sum, item) => sum + item.record_count, 0),
        totalAdmissions: gaokaoYearStats.reduce((sum, item) => sum + (item.total_admissions || 0), 0)
      },
      graduate: {
        byYear: graduateYearStats,
        byMajor: graduateMajorStats,
        totalRecords: graduateYearStats.reduce((sum, item) => sum + item.record_count, 0),
        totalAdmissions: graduateYearStats.reduce((sum, item) => sum + (item.total_admissions || 0), 0)
      }
    };
  }

  // 获取省份的录取数据
  getProvinceAdmissions(province: string, year: number, category: string, batch: string) {
    const query = `
      SELECT ga.*, u.name as university_name, u.level, u.type
      FROM gaokao_admissions ga
      JOIN universities u ON ga.university_id = u.id
      WHERE ga.province = ?
        AND ga.year = ?
        AND ga.category = ?
        AND ga.batch = ?
      ORDER BY ga.avg_score DESC
    `;

    const stmt = this.db.prepare(query);
    return stmt.all(province, year, category, batch);
  }

  // 获取录取趋势数据（按年份）
  getAdmissionTrends(universityId: number, province?: string, category?: string) {
    const conditions: string[] = ['university_id = ?'];
    const values: any[] = [universityId];

    if (province) {
      conditions.push('province = ?');
      values.push(province);
    }

    if (category) {
      conditions.push('category = ?');
      values.push(category);
    }

    const whereClause = `WHERE ${conditions.join(' AND ')}`;

    const query = `
      SELECT year, province, category,
             AVG(avg_score) as avg_score,
             AVG(avg_rank) as avg_rank,
             SUM(admission_count) as total_admissions,
             COUNT(*) as record_count
      FROM gaokao_admissions
      ${whereClause}
      GROUP BY year, province, category
      ORDER BY year, province, category
    `;

    const stmt = this.db.prepare(query);
    return stmt.all(...values);
  }
}