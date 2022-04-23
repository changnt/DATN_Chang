CREATE DATABASE  IF NOT EXISTS `news_portal_mobio`;
USE `news_portal_mobio`;

-- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `sections`;
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
DROP TABLE IF EXISTS `subsections`;
CREATE TABLE `subsections`
(
  `id_subsection` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `id_section` int,
  PRIMARY KEY (`id_subsection`),
  FOREIGN KEY (`id_section`) REFERENCES `sections`(`id_section`)
) CHARACTER SET UTF8MB4;


LOCK TABLES `subsections` WRITE;
INSERT INTO `subsections` VALUES 
(1,1,'Tin tức'),(2,1,'Xây dựng Đảng - chính quyền'),(3,1,'Làm theo gương Bác'),
(4,3,'Công nghiệp'),(5,3,'Nông nghiệp - Nông thôn'),(6,3,'Thị trường'),(7,3,'Giao thông - Đô thị'),
(8,4,'Y tế - Sức khỏe'),(9,4,'Lao động - Việc làm'),(10,4,'Môi trường'),(11,4,'Việc tử tế'),
(12,5,'Giáo dục'),(13,5,'Khoa học - Công nghệ'),
(14,6,'Tin tức'),(15,6,'Hồ sơ phá án'),(16,6,'Tư vấn'),
(17,7,'Gia đình'),(18,7,'Làm đẹp'),(19,7,'Mua sắm'),(20,7,'Ẩm thực'),(21,7,'Mẹo vặt'),
(22,8,'Đời sống văn hóa'),(23,8,'Tác giả - Tác phẩm'),(24,8,'Xem - Nghe - Đọc'),(25,8,'Thời trang'),
(26,9,'Tin tức'),(27,9,'Bình luận'),(28,9,'Tư liệu'),
(29,10,'Tư liệu'),(30,10,'Trong nước'),(31,10,'Quốc tế'),
(32,11,'Phong tục - Lễ hội'),(33,11,'Di tích'),(34,11,'Di tích'),
(35,12,'Bạn đọc viết'),(36,12,'Bạn đọc viết');
UNLOCK TABLES;
-- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`
(
  `id_user` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `position` varchar(255) NOT NULL,
  `status` varchar(255) NOT NULL DEFAULT 'Biên tập',
  PRIMARY KEY (`id_user`),
  UNIQUE KEY `id_user_UNIQUE` (`id_user`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) CHARACTER SET UTF8MB4;


LOCK TABLES `users` WRITE;
INSERT INTO `users` VALUES 
(1,'hiep','admin123','Lê Văn Hiệp','Biên tập','Kích hoạt'),
(2,'chang','admin123','Nguyễn Chang','Biên tập','Kích hoạt'),
(3,'bientap1','12345678','Lê Thị Đào','Biên tập','Kích hoạt'),
(4,'bientap2','12345678','Lê Hồng Bưởi','Biên tập','Bất hoạt'),
(5,'nhavan1','12345678','Lê Hương Hoa','Biên soạn','Kích hoạt'),
(6,'nhavan2','12345678','Lê Lan Mai','Biên soạn','Bất hoạt');
UNLOCK TABLES;
-- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `articles`;
CREATE TABLE `articles`
(
  `id_article` int NOT NULL AUTO_INCREMENT,
  `uploaded_by` varchar(255),
  `headline` longtext,
  `byline` varchar(255),
  `body` longtext,
  `section` varchar(255),
  `photo_filename` longtext,
  `photographer` longtext,
  `photo_caption` longtext,
  `status` varchar(255),
  `last_edited` timestamp DEFAULT CURRENT_TIMESTAMP,
  `subsection` varchar(255),
  PRIMARY KEY (`id_article`)
) CHARACTER SET UTF8MB4;


LOCK TABLES `articles` WRITE;
INSERT INTO `articles` VALUES 
(1,'Nguyễn Chang','Bài báo 1','Nguyễn Chang','<p>Body</p>','Chính trị',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(2,'Nguyễn Chang','Bài báo 2','Nguyễn Chang','<p>Body</p>','Góc nhìn',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(3,'Nguyễn Chang','Bài báo 3','Nguyễn Chang','<p>Body</p>','Kinh tế',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(4,'Nguyễn Chang','Bài báo 4','Nguyễn Chang','<p>Body</p>','Xã hội',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(5,'Nguyễn Chang','Bài báo 5','Nguyễn Chang','<p>Body</p>','Khoa học - Giáo dục',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(6,'Nguyễn Chang','Bài báo 6','Nguyễn Chang','<p>Body</p>','Pháp luật',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(7,'Nguyễn Chang','Bài báo 7','Nguyễn Chang','<p>Body</p>','Đời sống',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(8,'Nguyễn Chang','Bài báo 8','Nguyễn Chang','<p>Body</p>','Văn hóa - Giải trí',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(9,'Nguyễn Chang','Bài báo 9','Nguyễn Chang','<p>Body</p>','Thế giới',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(10,'Nguyễn Chang','Bài báo 10','Nguyễn Chang','<p>Body</p>','Thể thao',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(11,'Nguyễn Chang','Bài báo 11','Nguyễn Chang','<p>Body</p>','Đất và người xứ Đông',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(12,'Nguyễn Chang','Bài báo 12','Nguyễn Chang','<p>Body</p>','Bạn đọc',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL),
(13,'Nguyễn Chang','Bài báo 13','Nguyễn Chang','<p>Body</p>','Chính trị',NULL,NULL,NULL,'Đã xuất bản',current_timestamp(),NULL);
UNLOCK TABLES;
-- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Show all tables
SELECT * FROM users;
SELECT * FROM sections;
SELECT * FROM subsections;
SELECT * FROM articles;