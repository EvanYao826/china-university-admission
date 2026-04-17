#!/usr/bin/env ts-node
"""
TypeScript爬虫示例
用于抓取高校录取数据

注意：本代码仅供学习参考，实际使用时请遵守网站robots.txt和法律法规
"""

import axios from 'axios';
import cheerio from 'cheerio';
import fs from 'fs';
import path from 'path';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// 类型定义
interface GaokaoRecord {
  university_name: string;
  province: string;
  year: number;
  category: string;  // 文科/理科/综合改革
  batch: string;     // 本科一批/本科二批/专科批/提前批
  min_score?: number;
  avg_score?: number;
  max_score?: number;
  min_rank?: number;
  avg_rank?: number;
  max_rank?: number;
  admission_count?: number;
  major?: string;
  notes?: string;
}

interface GraduateRecord {
  university_name: string;
  year: number;
  major: string;
  degree_type: string;  // 硕士/博士
  study_mode: string;   // 全日制/非全日制
  admission_count: number;
  min_score?: number;
  avg_score?: number;
  max_score?: number;
  notes?: string;
}

class BaseCrawler {
  protected dbPath: string;
  protected headers: Record<string, string>;
  
  constructor(dbPath: string = '../data/university.db') {
    this.dbPath = dbPath;
    this.headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
    };
  }

  protected async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  protected async fetchHtml(url: string): Promise<string> {
    try {
      const response = await axios.get(url, {
        headers: this.headers,
        timeout: 30000,
      });
      return response.data;
    } catch (error) {
      console.error(`Fetching ${url} failed:`, error);
      throw error;
    }
  }

  protected async saveToDatabase(records: (GaokaoRecord | GraduateRecord)[]): Promise<void> {
    const db = await open({
      filename: this.dbPath,
      driver: sqlite3.Database
    });

    try {
      for (const record of records) {
        if ('batch' in record) {
          // 高考数据
          await this.saveGaokaoRecord(db, record);
        } else {
          // 研究生数据
          await this.saveGraduateRecord(db, record);
        }
      }
      console.log(`Saved ${records.length} records to database`);
    } finally {
      await db.close();
    }
  }

  private async saveGaokaoRecord(db: any, record: GaokaoRecord): Promise<void> {
    // 查找高校ID
    const university = await db.get(
      'SELECT id FROM universities WHERE name = ?',
      [record.university_name]
    );

    if (university) {
      await db.run(
        `INSERT OR REPLACE INTO gaokao_admissions
         (university_id, year, province, category, batch,
          min_score, avg_score, max_score, min_rank, avg_rank, max_rank,
          admission_count, major, notes)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          university.id, record.year, record.province, record.category, record.batch,
          record.min_score, record.avg_score, record.max_score,
          record.min_rank, record.avg_rank, record.max_rank,
          record.admission_count, record.major, record.notes
        ]
      );
    }
  }

  private async saveGraduateRecord(db: any, record: GraduateRecord): Promise<void> {
    // 查找高校ID
    const university = await db.get(
      'SELECT id FROM universities WHERE name LIKE ?',
      [`%${record.university_name}%`]
    );

    if (university) {
      await db.run(
        `INSERT OR REPLACE INTO graduate_admissions
         (university_id, year, major, degree_type, study_mode,
          admission_count, min_score, avg_score, max_score, notes)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          university.id, record.year, record.major, record.degree_type,
          record.study_mode, record.admission_count,
          record.min_score, record.avg_score, record.max_score,
          record.notes
        ]
      );
    }
  }
}

class GaokaoCrawler extends BaseCrawler {
  async fetchProvinceData(province: string, year: number): Promise<GaokaoRecord[]> {
    // 实际项目中需要实现具体的抓取逻辑
    // 这里返回模拟数据
    const universities = [
      '清华大学', '北京大学', '浙江大学', '复旦大学', '上海交通大学',
      '南京大学', '武汉大学', '华中科技大学', '中山大学', '西安交通大学'
    ];

    const records: GaokaoRecord[] = [];
    for (let i = 0; i < universities.length; i++) {
      const baseScore = 650 + i * 5;
      const baseRank = 1000 + i * 100;

      records.push({
        university_name: universities[i],
        province,
        year,
        category: '理科',
        batch: '本科一批',
        min_score: baseScore - 10,
        avg_score: baseScore,
        max_score: baseScore + 10,
        min_rank: baseRank + 200,
        avg_rank: baseRank,
        max_rank: baseRank - 200,
        admission_count: 100 + i * 10,
        notes: `模拟数据 - ${province} ${year}年`
      });
    }

    return records;
  }

  async run(provinces: string[], years: number[]): Promise<GaokaoRecord[]> {
    const allRecords: GaokaoRecord[] = [];

    for (const province of provinces) {
      for (const year of years) {
        console.log(`Fetching ${province} ${year} year gaokao data...`);
        try {
          const records = await this.fetchProvinceData(province, year);
          allRecords.push(...records);
          console.log(`Fetched ${records.length} records`);
          await this.delay(2000); // 礼貌延迟
        } catch (error) {
          console.error(`Failed to fetch ${province} ${year} data:`, error);
        }
      }
    }

    if (allRecords.length > 0) {
      await this.saveToDatabase(allRecords);
    }

    return allRecords;
  }
}

class GraduateCrawler extends BaseCrawler {
  async fetchUniversityData(universityName: string, year: number): Promise<GraduateRecord[]> {
    // 实际项目中需要实现具体的抓取逻辑
    // 这里返回模拟数据
    const majors = [
      '计算机科学与技术', '软件工程', '电子信息工程',
      '机械工程', '材料科学与工程', '电气工程',
      '经济学', '金融学', '工商管理',
      '法学', '临床医学', '药学',
      '数学', '物理学', '化学',
      '外国语言文学', '新闻传播学', '教育学'
    ];

    const records: GraduateRecord[] = [];
    for (let i = 0; i < 10; i++) {
      const baseCount = 20 + i * 3;
      const baseScore = 350 + i * 5;

      // 硕士
      records.push({
        university_name: universityName,
        year,
        major: majors[i],
        degree_type: '硕士',
        study_mode: '全日制',
        admission_count: baseCount,
        min_score: baseScore - 10,
        avg_score: baseScore,
        max_score: baseScore + 10,
        notes: `模拟数据 - ${universityName} ${year}年`
      });

      // 部分专业有博士
      if (i % 3 === 0) {
        records.push({
          university_name: universityName,
          year,
          major: majors[i],
          degree_type: '博士',
          study_mode: '全日制',
          admission_count: Math.max(5, Math.floor(baseCount / 4)),
          min_score: baseScore + 5,
          avg_score: baseScore + 15,
          max_score: baseScore + 25,
          notes: `模拟数据 - ${universityName} ${year}年`
        });
      }

      // 部分专业有非全日制硕士
      if (i % 4 === 0) {
        records.push({
          university_name: universityName,
          year,
          major: majors[i],
          degree_type: '硕士',
          study_mode: '非全日制',
          admission_count: Math.max(10, Math.floor(baseCount / 2)),
          min_score: baseScore - 20,
          avg_score: baseScore - 10,
          max_score: baseScore,
          notes: `模拟数据 - ${universityName} ${year}年（非全日制）`
        });
      }
    }

    return records;
  }

  async run(universities: string[], years: number[]): Promise<GraduateRecord[]> {
    const allRecords: GraduateRecord[] = [];

    for (const university of universities) {
      for (const year of years) {
        console.log(`Fetching ${university} ${year} year graduate data...`);
        try {
          const records = await this.fetchUniversityData(university, year);
          allRecords.push(...records);
          console.log(`Fetched ${records.length} records`);
          await this.delay(3000); // 礼貌延迟
        } catch (error) {
          console.error(`Failed to fetch ${university} ${year} data:`, error);
        }
      }
    }

    if (allRecords.length > 0) {
      await this.saveToDatabase(allRecords);
    }

    return allRecords;
  }
}

// 主函数
async function main() {
  console.log('='.repeat(60));
  console.log('TypeScript 爬虫示例');
  console.log('='.repeat(60));
  console.log('注意：本代码仅供学习参考');
  console.log('实际使用时请遵守网站规定和法律法规');
  console.log('='.repeat(60));

  // 测试高考爬虫
  console.log('\n测试高考爬虫...');
  const gaokaoCrawler = new GaokaoCrawler();
  const gaokaoProvinces = ['北京', '上海', '浙江'];
  const gaokaoYears = [2023, 2022];
  
  try {
    const gaokaoRecords = await gaokaoCrawler.run(gaokaoProvinces, gaokaoYears);
    console.log(`\n✅ 高考数据抓取完成！共获取 ${gaokaoRecords.length} 条记录`);
    
    // 显示前3条记录
    if (gaokaoRecords.length > 0) {
      console.log('\n📋 示例数据:');
      for (let i = 0; i < Math.min(3, gaokaoRecords.length); i++) {
        const record = gaokaoRecords[i];
        console.log(`${i + 1}. ${record.university_name} - ${record.province} ${record.year}年`);
        console.log(`   批次: ${record.batch}, 类别: ${record.category}`);
        console.log(`   平均分: ${record.avg_score}, 平均位次: ${record.avg_rank}`);
        console.log(`   招生人数: ${record.admission_count}`);
        console.log('');
      }
    }
  } catch (error) {
    console.error('❌ 高考数据抓取失败:', error);
  }

  // 测试研究生爬虫
  console.log('\n测试研究生爬虫...');
  const graduateCrawler = new GraduateCrawler();
  const graduateUniversities = ['清华大学', '北京大学', '浙江大学'];
  const graduateYears = [2023, 2022];
  
  try {
    const graduateRecords = await graduateCrawler.run(graduateUniversities, graduateYears);
    console.log(`\n✅ 研究生数据抓取完成！共获取 ${graduateRecords.length} 条记录`);
    
    // 显示前3条记录
    if (graduateRecords.length > 0) {
      console.log('\n📋 示例数据:');
      for (let i = 0; i < Math.min(3, graduateRecords.length); i++) {
        const record = graduateRecords[i];
        console.log(`${i + 1}. ${record.university_name} - ${record.major}`);
        console.log(`   类型: ${record.degree_type}${record.study_mode}`);
        console.log(`   招生人数: ${record.admission_count}`);
        if (record.avg_score) {
          console.log(`   平均分: ${record.avg_score}`);
        }
        console.log('');
      }
    }
  } catch (error) {
    console.error('❌ 研究生数据抓取失败:', error);
  }

  console.log('='.repeat(60));
  console.log('使用说明:');
  console.log('1. 实现具体的网站抓取逻辑');
  console.log('2. 处理反爬机制（验证码、IP限制等）');
  console.log('3. 调整请求头、延迟等参数避免被封');
  console.log('4. 定期更新数据');
  console.log('='.repeat(60));
}

// 运行主函数
if (require.main === module) {
  main().catch(console.error);
}

// 导出模块
export { GaokaoCrawler, GraduateCrawler, GaokaoRecord, GraduateRecord };
