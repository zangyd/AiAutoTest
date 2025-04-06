-- 初始化部门数据
INSERT INTO departments (id, name, description, parent_id, level, path, created_by) VALUES
(1, '总部', '公司总部', NULL, 1, '/1', 'system'),
(2, '研发部', '负责产品研发', 1, 2, '/1/2', 'system'),
(3, '测试部', '负责产品测试', 1, 2, '/1/3', 'system'),
(4, '运维部', '负责系统运维', 1, 2, '/1/4', 'system'),
(5, '产品部', '负责产品规划', 1, 2, '/1/5', 'system');

-- 初始化角色数据
INSERT INTO roles (id, name, description, is_system, created_by) VALUES
(1, '超级管理员', '系统超级管理员，拥有所有权限', TRUE, 'system'),
(2, '管理员', '系统管理员，管理系统配置', TRUE, 'system'),
(3, '测试经理', '测试团队负责人', TRUE, 'system'),
(4, '测试工程师', '执行测试任务', TRUE, 'system'),
(5, '开发人员', '开发人员角色', TRUE, 'system'),
(6, '访客', '只读权限', TRUE, 'system');

-- 初始化权限数据
INSERT INTO permissions (code, name, description, type, resource, action) VALUES
-- 用户管理权限
('user:view', '查看用户', '查看用户信息', 'menu', 'user', 'view'),
('user:create', '创建用户', '创建新用户', 'button', 'user', 'create'),
('user:edit', '编辑用户', '编辑用户信息', 'button', 'user', 'edit'),
('user:delete', '删除用户', '删除用户', 'button', 'user', 'delete'),
-- 角色管理权限
('role:view', '查看角色', '查看角色信息', 'menu', 'role', 'view'),
('role:create', '创建角色', '创建新角色', 'button', 'role', 'create'),
('role:edit', '编辑角色', '编辑角色信息', 'button', 'role', 'edit'),
('role:delete', '删除角色', '删除角色', 'button', 'role', 'delete'),
-- 权限管理权限
('permission:view', '查看权限', '查看权限信息', 'menu', 'permission', 'view'),
('permission:create', '创建权限', '创建新权限', 'button', 'permission', 'create'),
('permission:edit', '编辑权限', '编辑权限信息', 'button', 'permission', 'edit'),
('permission:delete', '删除权限', '删除权限', 'button', 'permission', 'delete'),
-- 部门管理权限
('department:view', '查看部门', '查看部门信息', 'menu', 'department', 'view'),
('department:create', '创建部门', '创建新部门', 'button', 'department', 'create'),
('department:edit', '编辑部门', '编辑部门信息', 'button', 'department', 'edit'),
('department:delete', '删除部门', '删除部门', 'button', 'department', 'delete'),
-- 日志管理权限
('log:view', '查看日志', '查看操作日志', 'menu', 'log', 'view'),
('log:export', '导出日志', '导出操作日志', 'button', 'log', 'export');

-- 初始化角色权限关联
-- 超级管理员角色权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, id FROM permissions;

-- 管理员角色权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 2, id FROM permissions 
WHERE code NOT IN ('permission:create', 'permission:edit', 'permission:delete');

-- 测试经理角色权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 3, id FROM permissions 
WHERE code IN ('user:view', 'department:view', 'log:view');

-- 测试工程师角色权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 4, id FROM permissions 
WHERE code IN ('user:view', 'department:view');

-- 开发人员角色权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 5, id FROM permissions 
WHERE code IN ('user:view', 'department:view');

-- 访客角色权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 6, id FROM permissions 
WHERE code IN ('user:view', 'department:view');

-- 初始化系统管理员用户
INSERT INTO users (
    username, 
    email,
    password_hash,
    real_name,
    position,
    is_active,
    is_superuser,
    created_by
) VALUES (
    'admin',
    'admin@example.com',
    -- 密码为: Admin@2024
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpwQLJkL5mJ.4K',
    '系统管理员',
    '系统管理员',
    TRUE,
    TRUE,
    'system'
);

-- 初始化测试经理用户
INSERT INTO users (
    username,
    email,
    password_hash,
    real_name,
    position,
    is_active,
    created_by
) VALUES (
    'test_manager',
    'test_manager@example.com',
    -- 密码为: Test@2024
    '$2b$12$QE3/KZKP8/9P1K6ML7.3.O1kFn0UmJ4q.4qHaGj.xYRAXUk4Qk9.q',
    '测试经理',
    '测试经理',
    TRUE,
    'system'
);

-- 关联用户和角色
INSERT INTO user_roles (user_id, role_id)
SELECT 
    (SELECT id FROM users WHERE username = 'admin'),
    (SELECT id FROM roles WHERE name = '超级管理员');

INSERT INTO user_roles (user_id, role_id)
SELECT 
    (SELECT id FROM users WHERE username = 'test_manager'),
    (SELECT id FROM roles WHERE name = '测试经理');

-- 关联用户和部门
INSERT INTO user_departments (user_id, department_id, is_leader)
SELECT 
    (SELECT id FROM users WHERE username = 'admin'),
    (SELECT id FROM departments WHERE name = '总部'),
    TRUE;

INSERT INTO user_departments (user_id, department_id, is_leader)
SELECT 
    (SELECT id FROM users WHERE username = 'test_manager'),
    (SELECT id FROM departments WHERE name = '测试部'),
    TRUE; 