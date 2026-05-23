-- migration.sql
-- CET-6 词汇平台数据库升级脚本
-- 请在 cet6zx 数据库中运行（Navicat / mysql 客户端均可）
-- 更新日期: 2026-05

-- =============================================
-- 一、新表：用户 & 收藏
-- =============================================

CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(32) NOT NULL COMMENT '登录用户名',
  `password_hash` VARCHAR(255) NOT NULL COMMENT 'bcrypt 密码哈希',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户账户';

CREATE TABLE IF NOT EXISTS `user_favorites` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `word_id` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_user_fav` (`user_id`, `word_id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏';

-- =============================================
-- 二、学习进度表（新部署可直接创建）
-- =============================================

CREATE TABLE IF NOT EXISTS `word_progress` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL DEFAULT 0 COMMENT '用户ID',
  `word_id` INT NOT NULL,
  `status` INT DEFAULT 0 COMMENT '0=未标记 1=已掌握(斩) 2=待复习(认识) 3=不认识',
  `review_count` INT DEFAULT 0,
  `ease_factor` FLOAT DEFAULT 2.5 COMMENT '记忆难度系数',
  `review_interval` INT DEFAULT 0 COMMENT '当前复习间隔(天)',
  `last_review_at` DATETIME,
  `next_review_at` DATETIME COMMENT '下次复习日期',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_user_word` (`user_id`, `word_id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户单词学习进度';

CREATE TABLE IF NOT EXISTS `study_sessions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL DEFAULT 0 COMMENT '用户ID',
  `started_at` DATETIME NOT NULL,
  `ended_at` DATETIME,
  `words_total` INT DEFAULT 0,
  `words_correct` INT DEFAULT 0,
  `words_wrong` INT DEFAULT 0,
  `duration_sec` INT DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习会话记录';

-- =============================================
-- 三、从旧版升级（若已有 word_progress 但无 user_id）
-- 若报错 Duplicate column / 索引不存在，说明已升级，可跳过对应语句
-- =============================================

-- ALTER TABLE `word_progress` ADD COLUMN `user_id` INT NOT NULL DEFAULT 0 COMMENT '用户ID' AFTER `id`;
-- ALTER TABLE `word_progress` DROP INDEX `uk_word`;
-- ALTER TABLE `word_progress` ADD UNIQUE KEY `uk_user_word` (`user_id`, `word_id`);
-- ALTER TABLE `study_sessions` ADD COLUMN `user_id` INT NOT NULL DEFAULT 0 COMMENT '用户ID' AFTER `id`;

-- 更新 status 注释
ALTER TABLE `word_progress`
MODIFY COLUMN `status` INT DEFAULT 0 COMMENT '0=未标记 1=已掌握(斩) 2=待复习(认识) 3=不认识';
