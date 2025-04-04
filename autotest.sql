/*
 Navicat Premium Data Transfer

 Source Server         : 本地Mysql8.0.41官方版
 Source Server Type    : MySQL
 Source Server Version : 50726
 Source Host           : localhost:3306
 Source Schema         : autotest

 Target Server Type    : MySQL
 Target Server Version : 50726
 File Encoding         : 65001

 Date: 04/04/2025 02:38:49
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version`  (
  `version_num` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO `alembic_version` VALUES ('a5aac0856f04');

-- ----------------------------
-- Table structure for login_history
-- ----------------------------
DROP TABLE IF EXISTS `login_history`;
CREATE TABLE `login_history`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NULL DEFAULT NULL,
  `login_time` datetime NULL DEFAULT NULL,
  `ip_address` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `user_agent` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `status` tinyint(1) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `ix_login_history_id`(`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of login_history
-- ----------------------------
INSERT INTO `login_history` VALUES (1, 1, '2025-03-31 23:39:42', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (2, 1, '2025-03-31 23:41:08', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (3, 1, '2025-03-31 23:43:28', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (4, 1, '2025-03-31 23:49:23', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (5, 1, '2025-03-31 23:53:42', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (6, 1, '2025-03-31 23:53:59', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (7, 1, '2025-04-01 00:13:16', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (8, 1, '2025-04-01 00:14:40', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (9, 1, '2025-04-01 00:14:53', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (10, 1, '2025-04-01 00:15:05', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (11, 1, '2025-04-01 00:22:39', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (12, 1, '2025-04-01 00:22:50', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);
INSERT INTO `login_history` VALUES (13, 1, '2025-04-01 00:22:56', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 1);

-- ----------------------------
-- Table structure for permissions
-- ----------------------------
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name`) USING BTREE,
  UNIQUE INDEX `code`(`code`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of permissions
-- ----------------------------
INSERT INTO `permissions` VALUES (1, '用户管理', 'system:user:list', '用户列表权限', 'menu', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (2, '用户创建', 'system:user:create', '创建用户权限', 'button', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (3, '用户编辑', 'system:user:edit', '编辑用户权限', 'button', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (4, '用户删除', 'system:user:delete', '删除用户权限', 'button', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (5, '角色管理', 'system:role:list', '角色列表权限', 'menu', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (6, '角色创建', 'system:role:create', '创建角色权限', 'button', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (7, '角色编辑', 'system:role:edit', '编辑角色权限', 'button', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (8, '角色删除', 'system:role:delete', '删除角色权限', 'button', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (9, '权限管理', 'system:permission:list', '权限列表权限', 'menu', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (10, '权限创建', 'system:permission:create', '创建权限权限', 'button', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `permissions` VALUES (11, '权限编辑', 'system:permission:edit', '编辑权限权限', 'button', '2025-04-01 21:38:50', '2025-04-01 21:38:50');

-- ----------------------------
-- Table structure for role_permission
-- ----------------------------
DROP TABLE IF EXISTS `role_permission`;
CREATE TABLE `role_permission`  (
  `role_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`, `permission_id`) USING BTREE,
  INDEX `permission_id`(`permission_id`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Fixed;

-- ----------------------------
-- Records of role_permission
-- ----------------------------
INSERT INTO `role_permission` VALUES (1, 1, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 2, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 3, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 4, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 5, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 6, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 7, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 8, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 9, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 10, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (1, 11, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (2, 1, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (2, 2, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (2, 3, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (2, 5, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (2, 9, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (3, 1, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (3, 5, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (3, 9, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (4, 1, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (4, 5, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (4, 9, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (5, 1, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (5, 5, '2025-04-01 21:38:50');
INSERT INTO `role_permission` VALUES (5, 9, '2025-04-01 21:38:50');

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name`) USING BTREE,
  UNIQUE INDEX `code`(`code`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of roles
-- ----------------------------
INSERT INTO `roles` VALUES (1, '超级管理员', 'admin', '系统最高权限管理员', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `roles` VALUES (2, '测试经理', 'test_manager', '测试团队管理者', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `roles` VALUES (3, '测试工程师', 'test_engineer', '执行测试的工程师', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `roles` VALUES (4, '开发人员', 'developer', '开发人员', '2025-04-01 21:38:50', '2025-04-01 21:38:50');
INSERT INTO `roles` VALUES (5, '观察者', 'observer', '只读权限用户', '2025-04-01 21:38:50', '2025-04-01 21:38:50');

-- ----------------------------
-- Table structure for user_role
-- ----------------------------
DROP TABLE IF EXISTS `user_role`;
CREATE TABLE `user_role`  (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE,
  INDEX `role_id`(`role_id`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Fixed;

-- ----------------------------
-- Records of user_role
-- ----------------------------
INSERT INTO `user_role` VALUES (1, 1, '2025-04-01 21:38:50');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `hashed_password` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `is_superuser` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE,
  UNIQUE INDEX `email`(`email`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'admin@example.com', NULL, NULL, NULL, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LcdYwKxDV6CipNFPu', 1, 1, '2025-04-01 21:38:50', '2025-04-02 12:27:19');

SET FOREIGN_KEY_CHECKS = 1;
