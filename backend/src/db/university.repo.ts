import DatabaseManager from './index';
import { University, SearchParams } from '../types';

export class UniversityRepository {
  private db = DatabaseManager.getInstance().getDatabase();

  // 获取所有高校（支持分页和筛选）
  getAll(params: SearchParams = {}): { data: University[]; total: number } {
    const {
      province,
      type,
      level,
      page = 1,
      limit = 20,
      sortBy = 'name',
      sortOrder = 'asc'
    } = params;

    const offset = (page - 1) * limit;

    // 构建 WHERE 子句
    const conditions: string[] = [];
    const values: any[] = [];

    if (province) {
      conditions.push('province = ?');
      values.push(province);
    }

    if (type) {
      conditions.push('type = ?');
      values.push(type);
    }

    if (level) {
      conditions.push('level = ?');
      values.push(level);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    // 获取总数
    const countStmt = this.db.prepare(`SELECT COUNT(*) as total FROM universities ${whereClause}`);
    const countResult = countStmt.get(...values) as { total: number };
    const total = countResult.total;

    // 获取数据
    const orderBy = sortBy === 'name' ? 'name COLLATE NOCASE' : sortBy;
    const query = `
      SELECT * FROM universities
      ${whereClause}
      ORDER BY ${orderBy} ${sortOrder.toUpperCase()}
      LIMIT ? OFFSET ?
    `;

    const stmt = this.db.prepare(query);
    const data = stmt.all(...values, limit, offset) as University[];

    return { data, total };
  }

  // 根据ID获取高校详情
  getById(id: number): University | null {
    const stmt = this.db.prepare('SELECT * FROM universities WHERE id = ?');
    return stmt.get(id) as University || null;
  }

  // 根据名称搜索高校
  searchByName(name: string, limit = 10): University[] {
    const stmt = this.db.prepare(`
      SELECT * FROM universities
      WHERE name LIKE ?
      ORDER BY name COLLATE NOCASE
      LIMIT ?
    `);
    return stmt.all(`%${name}%`, limit) as University[];
  }

  // 获取省份列表
  getProvinces(): string[] {
    const stmt = this.db.prepare('SELECT DISTINCT province FROM universities ORDER BY province');
    const result = stmt.all() as { province: string }[];
    return result.map(row => row.province);
  }

  // 获取高校类型列表
  getTypes(): string[] {
    const stmt = this.db.prepare('SELECT DISTINCT type FROM universities ORDER BY type');
    const result = stmt.all() as { type: string }[];
    return result.map(row => row.type);
  }

  // 获取高校层次列表
  getLevels(): string[] {
    const stmt = this.db.prepare('SELECT DISTINCT level FROM universities ORDER BY level');
    const result = stmt.all() as { level: string }[];
    return result.map(row => row.level);
  }

  // 获取高校统计信息
  getStatistics() {
    const totalStmt = this.db.prepare('SELECT COUNT(*) as total FROM universities');
    const provinceStmt = this.db.prepare(`
      SELECT province, COUNT(*) as count
      FROM universities
      GROUP BY province
      ORDER BY count DESC
    `);
    const typeStmt = this.db.prepare(`
      SELECT type, COUNT(*) as count
      FROM universities
      GROUP BY type
      ORDER BY count DESC
    `);
    const levelStmt = this.db.prepare(`
      SELECT level, COUNT(*) as count
      FROM universities
      GROUP BY level
      ORDER BY
        CASE level
          WHEN '985' THEN 1
          WHEN '211' THEN 2
          WHEN '双一流' THEN 3
          WHEN '普通本科' THEN 4
          WHEN '专科' THEN 5
          ELSE 6
        END
    `);

    const totalResult = totalStmt.get() as { total: number };
    return {
      total: totalResult.total,
      byProvince: provinceStmt.all(),
      byType: typeStmt.all(),
      byLevel: levelStmt.all()
    };
  }
}