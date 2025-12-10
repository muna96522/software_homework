## 登録改造説明：単入口拆分為三入口

本文記錄如何將原本單一的登錄入口（統一表單，根據 `user_type` 跳轉）改造成三個獨立的登錄界面（管理員 / 教師 / 學生），並保留舊接口兼容性。

### 改造目標
- 為不同角色提供獨立的登錄頁與提交流程，減少誤登與權限錯誤提示。
- 登錄後按角色落到對應首頁（管理員 `admin_home`、教師 `staff_home`、學生 `student_home`）。
- 保留原有 `doLogin/` 路由，避免外部依賴立即失效。

### 主要改動模塊
1) **視圖層 `main_app/views.py`**
   - 新增角色選擇頁 `login_page`，已登錄用戶直接按角色重定向。
   - 為三類角色各新增展示頁 + 處理邏輯：
     - 展示頁：`login_admin`、`login_teacher`、`login_student`
     - 提交處理：`do_admin_login`、`do_teacher_login`、`do_student_login`
   - 保留舊的 `doLogin` 作為兼容入口（POST email/password，按 `user_type` 跳轉）。
   - 每個處理函數都在認證後**二次校驗 `user_type`**，否則提示"權限不符"並返回對應登錄頁。

2) **路由層 `main_app/urls.py`**
   - 新增角色選擇與分角色登錄路由：
     - `/` → `login_page`（角色選擇卡片）
     - `/login/admin/` → 管理員登錄頁，`/do-admin-login/` → 管理員登錄提交
     - `/login/teacher/` → 教師登錄頁，`/do-teacher-login/` → 教師登錄提交
     - `/login/student/` → 學生登錄頁，`/do-student-login/` → 學生登錄提交
   - 保留舊路由 `/doLogin/` 與登出路由 `/logout_user/`。

3) **模板層 `main_app/templates/main_app/`**
   - 新增/拆分 4 個頁面：
     - `login_role_select.html`：角色選擇卡片頁（管理員/教師/學生），未登錄時的入口；已登錄用戶會在視圖中被重定向。
     - `login_admin.html`：管理員登錄頁（粉色漸變主題）。
     - `login_teacher.html`：教師登錄頁（藍色漸變主題）。
     - `login_student.html`：學生登錄頁（綠色漸變主題）。
   - 每個登錄頁表單分別提交到對應的處理路由，並顯示 Django `messages` 的錯誤提示。
   - 舊版 `login.html` 保留，方便回滾或對比，但當前入口已切換到上面三個新頁面。

### 實現思路（步驟回顧）
1. **路由拆分**：在 `urls.py` 為三個角色各自添加展示路由和處理路由，保留舊路由兼容性。
2. **視圖拆分**：在 `views.py` 拆出三套登錄展示函數與處理函數，處理函數內增加 `user_type` 校驗，認證失敗或角色不符時用 `messages` 返回提示。
3. **頁面拆分與美化**：基於 AdminLTE/FontAwesome 複製原登錄頁結構，分別著色並替換提交 URL，加入"返回角色選擇"鏈接。
4. **角色選擇頁**：新增 `login_role_select.html`，提供三張卡片跳轉到各自登錄頁；若用戶已登錄，則視圖直接按角色重定向。
5. **回退與兼容**：保留舊 `doLogin/`，確保外部腳本或舊書籤仍可用；遇到權限不符時引導到正確入口。

### 使用方式（運行後體驗路徑）
1. 打開站點根路徑 `/`，先到角色選擇頁。
2. 按角色進入對應登錄頁：`/login/admin/`、`/login/teacher/`、`/login/student/`。
3. 登錄成功後自動跳轉到各自首頁：`admin_home` / `staff_home` / `student_home`。
4. 如仍使用舊接口，可向 `/doLogin/` POST `email`、`password`，行為與改造前一致。

### 關鍵文件索引
- 視圖：`main_app/views.py`（login_xxx 與 do_xxx_login 系列）
- 路由：`main_app/urls.py`（登錄相關路由分組位於頂部）
- 模板：`main_app/templates/main_app/login_role_select.html`
  `main_app/templates/main_app/login_admin.html`
  `main_app/templates/main_app/login_teacher.html`
  `main_app/templates/main_app/login_student.html`
  （`login.html` 為舊版保留模板）

如需回滾到單入口，只需：
- 在 `urls.py` 移除新登錄路由並將 `/` 指回舊模板。
- 在 `views.py` 使用 `doLogin` 統一處理登錄。
- 刪除或忽略分角色模板。
