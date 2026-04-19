/*
 Navicat Premium Data Transfer

 Source Server         : studentSQLlite
 Source Server Type    : SQLite
 Source Server Version : 3035005 (3.35.5)
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3035005 (3.35.5)
 File Encoding         : 65001

 Date: 19/04/2026 10:43:34
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for postgraduate_admissions
-- ----------------------------
DROP TABLE IF EXISTS "postgraduate_admissions";
CREATE TABLE "postgraduate_admissions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "university_id" INTEGER NOT NULL,
  "year" INTEGER NOT NULL,
  "degree_type" TEXT,
  "discipline_category" TEXT,
  "admission_type" TEXT,
  "political_score" REAL,
  "foreign_language_score" REAL,
  "subject1_score" REAL,
  "subject2_score" REAL,
  "total_score" REAL,
  "remarks" TEXT,
  "adjustment_info" TEXT,
  "source_url" TEXT,
  "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
  "updated_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("university_id") REFERENCES "universities" ("id") ON DELETE CASCADE ON UPDATE NO ACTION,
  UNIQUE ("university_id" ASC, "year" ASC, "degree_type" ASC, "discipline_category" ASC, "admission_type" ASC)
);

-- ----------------------------
-- Table structure for sqlite_sequence
-- ----------------------------
DROP TABLE IF EXISTS "sqlite_sequence";
CREATE TABLE "sqlite_sequence" (
  "name",
  "seq"
);

-- ----------------------------
-- Table structure for undergraduate_admissions
-- ----------------------------
DROP TABLE IF EXISTS "undergraduate_admissions";
CREATE TABLE "undergraduate_admissions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "university_id" INTEGER NOT NULL,
  "province" TEXT NOT NULL,
  "year" INTEGER NOT NULL,
  "category" TEXT,
  "batch" TEXT,
  "enrollment_type" TEXT,
  "major" TEXT,
  "min_score" REAL,
  "min_rank" INTEGER,
  "avg_score" REAL,
  "provincial_control_line" REAL,
  "subject_requirements" TEXT,
  "professional_group" TEXT,
  "source_url" TEXT,
  "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
  "updated_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("university_id") REFERENCES "universities" ("id") ON DELETE CASCADE ON UPDATE NO ACTION,
  UNIQUE ("university_id" ASC, "province" ASC, "year" ASC, "category" ASC, "batch" ASC, "major" ASC, "enrollment_type" ASC)
);

-- ----------------------------
-- Table structure for universities
-- ----------------------------
DROP TABLE IF EXISTS "universities";
CREATE TABLE "universities" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "name" TEXT NOT NULL,
  "type" TEXT,
  "level" TEXT,
  "province" TEXT NOT NULL,
  "city" TEXT,
  "tags" TEXT,
  "logo_url" TEXT,
  "description" TEXT,
  "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
  "updated_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
  "website" TEXT,
  UNIQUE ("name" ASC)
);

-- ----------------------------
-- Auto increment value for postgraduate_admissions
-- ----------------------------
UPDATE "sqlite_sequence" SET seq = 13 WHERE name = 'postgraduate_admissions';

-- ----------------------------
-- Indexes structure for table postgraduate_admissions
-- ----------------------------
CREATE INDEX "idx_postgrad_univ_year"
ON "postgraduate_admissions" (
  "university_id" ASC,
  "year" ASC
);
CREATE INDEX "idx_postgrad_year"
ON "postgraduate_admissions" (
  "year" ASC
);

-- ----------------------------
-- Auto increment value for undergraduate_admissions
-- ----------------------------
UPDATE "sqlite_sequence" SET seq = 199 WHERE name = 'undergraduate_admissions';

-- ----------------------------
-- Indexes structure for table undergraduate_admissions
-- ----------------------------
CREATE INDEX "idx_undergrad_major"
ON "undergraduate_admissions" (
  "major" ASC
);
CREATE INDEX "idx_undergrad_order"
ON "undergraduate_admissions" (
  "university_id" ASC,
  "province" ASC,
  "year" DESC
);
CREATE INDEX "idx_undergrad_prov_year"
ON "undergraduate_admissions" (
  "province" ASC,
  "year" ASC
);
CREATE INDEX "idx_undergrad_univ_prov_year"
ON "undergraduate_admissions" (
  "university_id" ASC,
  "province" ASC,
  "year" ASC
);
CREATE INDEX "idx_undergrad_univ_year"
ON "undergraduate_admissions" (
  "university_id" ASC,
  "year" ASC
);

-- ----------------------------
-- Auto increment value for universities
-- ----------------------------
UPDATE "sqlite_sequence" SET seq = 20 WHERE name = 'universities';

PRAGMA foreign_keys = true;
