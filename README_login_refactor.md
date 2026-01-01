## 登录改造说明：单入口拆分为三入口

本文记录如何将原本单一的登录入口（统一表单，根据 `user_type` 跳转）改造成三个独立的登录界面（管理员 / 教师 / 学生），并保留旧接口兼容性。

### 改造目标
- 为不同角色提供独立的登录页与提交流程，减少误登与权限错误提示。
- 登录后按角色落到对应首页（管理员 `admin_home`、教师 `staff_home`、学生 `student_home`）。
- 保留原有 `doLogin/` 路由，避免外部依赖立即失效。

### 主要改动模块
1) **视图层 `main_app/views.py`**
   - 新增角色选择页 `login_page`，已登录用户直接按角色重定向。
   - 为三类角色各新增展示页 + 处理逻辑：
     - 展示页：`login_admin`、`login_teacher`、`login_student`
     - 提交处理：`do_admin_login`、`do_teacher_login`、`do_student_login`
   - 保留旧的 `doLogin` 作为兼容入口（POST email/password，按 `user_type` 跳转）。
   - 每个处理函数都在认证后**二次校验 `user_type`**，否则提示"权限不符"并返回对应登录页。

2) **路由层 `main_app/urls.py`**
   - 新增角色选择与分角色登录路由：
     - `/` → `login_page`（角色选择卡片）
     - `/login/admin/` → 管理员登录页，`/do-admin-login/` → 管理员登录提交
     - `/login/teacher/` → 教师登录页，`/do-teacher-login/` → 教师登录提交
     - `/login/student/` → 学生登录页，`/do-student-login/` → 学生登录提交
   - 保留旧路由 `/doLogin/` 与登出路由 `/logout_user/`。

3) **模板层 `main_app/templates/main_app/`**
   - 新增/拆分 4 个页面：
     - `login_role_select.html`：角色选择卡片页（管理员/教师/学生），未登录时的入口；已登录用户会在视图中被重定向。
     - `login_admin.html`：管理员登录页（粉色渐变主题）。
     - `login_teacher.html`：教师登录页（蓝色渐变主题）。
     - `login_student.html`：学生登录页（绿色渐变主题）。
   - 每个登录页表单分别提交到对应的处理路由，并显示 Django `messages` 的错误提示。
   - 旧版 `login.html` 保留，方便回滚或对比，但当前入口已切换到上面三个新页面。

### 实现思路（步骤回顾）
1. **路由拆分**：在 `urls.py` 为三个角色各自添加展示路由和处理路由，保留旧路由兼容性。
2. **视图拆分**：在 `views.py` 拆出三套登录展示函数与处理函数，处理函数内增加 `user_type` 校验，认证失败或角色不符时用 `messages` 返回提示。
3. **页面拆分与美化**：基于 AdminLTE/FontAwesome 复制原登录页结构，分别着色并替换提交 URL，加入"返回角色选择"链接。
4. **角色选择页**：新增 `login_role_select.html`，提供三张卡片跳转到各自登录页；若用户已登录，则视图直接按角色重定向。
5. **回退与兼容**：保留旧 `doLogin/`，确保外部脚本或旧书签仍可用；遇到权限不符时引导到正确入口。

### 使用方式（运行后体验路径）
1. 打开站点根路径 `/`，先到角色选择页。
2. 按角色进入对应登录页：`/login/admin/`、`/login/teacher/`、`/login/student/`。
3. 登录成功后自动跳转到各自首页：`admin_home` / `staff_home` / `student_home`。
4. 如仍使用旧接口，可向 `/doLogin/` POST `email`、`password`，行为与改造前一致。

### 关键文件索引
- 视图：`main_app/views.py`（login_xxx 与 do_xxx_login 系列）
- 路由：`main_app/urls.py`（登录相关路由分组位于顶部）
- 模板：`main_app/templates/main_app/login_role_select.html`
  `main_app/templates/main_app/login_admin.html`
  `main_app/templates/main_app/login_teacher.html`
  `main_app/templates/main_app/login_student.html`
  （`login.html` 为旧版保留模板）

如需回滚到单入口，只需：
- 在 `urls.py` 移除新登录路由并将 `/` 指回旧模板。
- 在 `views.py` 使用 `doLogin` 统一处理登录。
- 删除或忽略分角色模板。
