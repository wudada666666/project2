-- 在 cet6zx 数据库运行 (Navicat 中打开 cet6zx 数据库，新建查询，粘贴运行)
-- 如果已运行过，先删旧表: DROP TABLE IF EXISTS word_progress, study_sessions;

CREATE TABLE IF NOT EXISTS word_progress (
  id INT AUTO_INCREMENT PRIMARY KEY,
  word_id INT NOT NULL,
  status INT DEFAULT 0 COMMENT '0=未标记 1=认识 2=模糊 3=不认识',
  review_count INT DEFAULT 0,
  ease_factor FLOAT DEFAULT 2.5 COMMENT '记忆难度系数',
  review_interval INT DEFAULT 0 COMMENT '当前复习间隔(天)',
  last_review_at DATETIME,
  next_review_at DATETIME COMMENT '下次复习日期',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_word (word_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS study_sessions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  started_at DATETIME NOT NULL,
  ended_at DATETIME,
  words_total INT DEFAULT 0,
  words_correct INT DEFAULT 0,
  words_wrong INT DEFAULT 0,
  duration_sec INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
