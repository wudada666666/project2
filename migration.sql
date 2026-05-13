-- migration.sql
-- 更新 word_progress 表 status 注释，反映新语义
ALTER TABLE `word_progress`
MODIFY COLUMN `status` int DEFAULT 0 COMMENT '0=未标记 1=已掌握(斩) 2=待复习(认识) 3=不认识';
