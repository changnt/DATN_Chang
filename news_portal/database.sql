CREATE DATABASE IF NOT EXISTS `news_portal_mobio`;
USE `news_portal_mobio`;
DROP TABLE IF EXISTS `subsections`;
DROP TABLE IF EXISTS `sections`;
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `articles`;
-- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
CREATE TABLE `sections`
(
  `id_section` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id_section`)
) CHARACTER SET UTF8MB4;


LOCK TABLES `sections` WRITE;
INSERT INTO `sections` VALUES 
(1,'Chính trị'),(2,'Góc nhìn'),(3,'Kinh tế'),(4,'Xã hội'),(5,'Khoa học - Giáo dục'),(6,'Pháp luật'),
(7,'Đời sống'),(8,'Văn hóa - Giải trí'),(9,'Thế giới'),(10,'Thể thao'),(11,'Đất và người xứ Đông'),(12,'Bạn đọc');
UNLOCK TABLES;
-- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- CREATE TABLE `subsections`
-- (
--   `id_subsection` int NOT NULL AUTO_INCREMENT,
--   `id_section` int,
--   `name` varchar(255),
--   PRIMARY KEY (`id_subsection`),
--   FOREIGN KEY (`id_section`) REFERENCES `sections`(`id_section`)
-- ) CHARACTER SET UTF8MB4;

-- LOCK TABLES `subsections` WRITE;
-- INSERT INTO `subsections` VALUES 
-- (1,1,'Tin tức'),(2,1,'Xây dựng Đảng - chính quyền'),(3,1,'Làm theo gương Bác'),
-- (4,3,'Công nghiệp'),(5,3,'Nông nghiệp - Nông thôn'),(6,3,'Thị trường'),(7,3,'Giao thông - Đô thị'),
-- (8,4,'Y tế - Sức khỏe'),(9,4,'Lao động - Việc làm'),(10,4,'Môi trường'),(11,4,'Việc tử tế'),
-- (12,5,'Giáo dục'),(13,5,'Khoa học - Công nghệ'),
-- (14,6,'Tin tức'),(15,6,'Hồ sơ phá án'),(16,6,'Tư vấn'),
-- (17,7,'Gia đình'),(18,7,'Làm đẹp'),(19,7,'Mua sắm'),(20,7,'Ẩm thực'),(21,7,'Mẹo vặt'),
-- (22,8,'Đời sống văn hóa'),(23,8,'Tác giả - Tác phẩm'),(24,8,'Xem - Nghe - Đọc'),(25,8,'Thời trang'),
-- (26,9,'Tin tức'),(27,9,'Bình luận'),(28,9,'Tư liệu'),
-- (29,10,'Tư liệu'),(30,10,'Trong nước'),(31,10,'Quốc tế'),
-- (32,11,'Phong tục - Lễ hội'),(33,11,'Di tích'),(34,11,'Di tích'),
-- (35,12,'Bạn đọc viết'),(36,12,'Bạn đọc viết');
-- UNLOCK TABLES;
-- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
CREATE TABLE `users`
(
  `id_user` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL UNIQUE,
  `password` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `position` varchar(255) NOT NULL,
  `status` varchar(255) NOT NULL,
  PRIMARY KEY (`id_user`)
) CHARACTER SET UTF8MB4;

LOCK TABLES `users` WRITE;
INSERT INTO `users` VALUES 
(1,'changnt','admin123','Nguyễn Chang','Quản trị','Kích hoạt');
UNLOCK TABLES;
-- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
CREATE TABLE `articles`
(
  `id_article` int NOT NULL AUTO_INCREMENT,
  `id_section` int,
  `id_poster` int,
  `byline` varchar(255),
  `headline` longtext,
  `body` longtext,
  `photo` varchar(255),
  `status` varchar(255),
  `last_edited` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_article`),
  FOREIGN KEY (`id_section`) REFERENCES `sections`(`id_section`),
  FOREIGN KEY (`id_poster`) REFERENCES `users`(`id_user`)
) CHARACTER SET UTF8MB4;

LOCK TABLES `articles` WRITE;
INSERT INTO `articles` VALUES 
( 1, 1, 1, 'Sưu tầm', 'Bài báo 1', '<p>Nội dung</p>','1.jpg','Xuất bản',current_timestamp()),
( 2, 2, 1, 'Sưu tầm', 'Bài báo 2', '<p>Nội dung</p>','1.jpg','Xuất bản',current_timestamp());
UNLOCK TABLES;
-- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Show all tables
SELECT * FROM users;
SELECT * FROM sections;
SELECT * FROM articles;