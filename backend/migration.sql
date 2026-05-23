-- backend/migration.sql
-- 与项目根目录 migration.sql 内容一致，在 cet6zx 数据库运行

CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(32) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `user_favorites` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `word_id` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_user_fav` (`user_id`, `word_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `word_progress` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL DEFAULT 0,
  `word_id` INT NOT NULL,
  `status` INT DEFAULT 0 COMMENT '0=未标记 1=已掌握(斩) 2=待复习(认识) 3=不认识',
  `review_count` INT DEFAULT 0,
  `ease_factor` FLOAT DEFAULT 2.5,
  `review_interval` INT DEFAULT 0,
  `last_review_at` DATETIME,
  `next_review_at` DATETIME,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_user_word` (`user_id`, `word_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `study_sessions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL DEFAULT 0,
  `started_at` DATETIME NOT NULL,
  `ended_at` DATETIME,
  `words_total` INT DEFAULT 0,
  `words_correct` INT DEFAULT 0,
  `words_wrong` INT DEFAULT 0,
  `duration_sec` INT DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
