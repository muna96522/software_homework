# 成员3 - 学生模块详细设计说明文档

## 1. 模块功能描述

学生模块（Student Module）是学生管理系统中学生角色的功能模块，为学生提供查看个人信息、出勤、成绩、参与活动等功能。

### 1.1 核心功能

1. **出勤查看**
   - 查看个人出勤记录：按科目和日期范围查看出勤情况
   - 出勤统计：查看出勤率和各科目出勤统计

2. **成绩查看**
   - 查看个人成绩：查看各科目的平时成绩和考试成绩
   - 成绩统计：查看成绩分布和趋势

3. **请假管理**
   - 提交请假申请：向管理员提交请假申请
   - 查看请假状态：查看请假申请的审批状态

4. **反馈管理**
   - 提交反馈：向管理员提交反馈意见或建议
   - 查看回复：查看管理员对反馈的回复

5. **通知管理**
   - 查看通知：查看管理员发送的通知消息
   - 接收推送：接收Firebase推送通知

6. **活动管理**
   - 浏览活动：查看所有已通过审批的校园活动
   - 报名活动：报名参加感兴趣的校园活动
   - 我的活动：查看已报名的活动列表
   - 活动评价：对参与的活动进行评分和评价

7. **个人管理**
   - 查看个人资料：查看和编辑个人信息
   - 修改密码：更新登录密码

### 1.2 权限说明

学生可以：
- 查看个人的出勤和成绩信息
- 提交请假和反馈申请
- 浏览和报名校园活动
- 查看个人相关的通知和消息

学生不能：
- 访问管理员功能
- 访问教师功能
- 查看其他学生的信息

---

## 2. 模块的类设计

### 2.1 视图类（View Functions）

#### 2.1.1 主页面视图

**类名：** `student_home`

**功能：** 显示学生主页面，展示个人统计信息

**方法：**
- `student_home(request)` - 处理GET请求，返回学生主页数据

**主要逻辑：**
- 获取当前学生对象
- 统计所学科目总数
- 统计出勤记录总数和出勤率
- 准备各科目的出勤统计图表数据

---

#### 2.1.2 出勤查看视图类

**类名：** `AttendanceViewViews`（功能集合）

**包含方法：**

1. **`student_view_attendance(request)`**
   - **功能：** 查看个人出勤记录
   - **方法类型：** GET/POST
   - **主要逻辑：**
     - GET：显示出勤查询表单
     - POST：根据科目和日期范围筛选出勤记录
     - 返回出勤数据列表

---

#### 2.1.3 成绩查看视图类

**类名：** `ResultViewViews`（功能集合）

**包含方法：**

1. **`student_view_result(request)`**
   - **功能：** 查看个人成绩
   - **方法类型：** GET
   - **主要逻辑：**
     - 获取当前学生对象
     - 获取该学生的所有成绩记录
     - 按科目分组显示成绩

---

#### 2.1.4 请假管理视图类

**类名：** `LeaveManagementViews`（功能集合）

**包含方法：**

1. **`student_apply_leave(request)`**
   - **功能：** 提交请假申请
   - **方法类型：** POST/GET
   - **主要逻辑：**
     - GET：显示请假申请表单
     - POST：验证表单数据，创建LeaveReportStudent对象

---

#### 2.1.5 反馈管理视图类

**类名：** `FeedbackManagementViews`（功能集合）

**包含方法：**

1. **`student_feedback(request)`**
   - **功能：** 提交反馈
   - **方法类型：** POST/GET
   - **主要逻辑：**
     - GET：显示反馈表单
     - POST：验证表单数据，创建FeedbackStudent对象

---

#### 2.1.6 通知管理视图类

**类名：** `NotificationManagementViews`（功能集合）

**包含方法：**

1. **`student_view_notification(request)`**
   - **功能：** 查看通知列表
   - **方法类型：** GET
   - **主要逻辑：**
     - 获取当前学生对象
     - 获取该学生的所有通知（按时间倒序）

2. **`student_fcmtoken(request)`**
   - **功能：** 保存Firebase推送通知令牌
   - **方法类型：** POST
   - **主要逻辑：** 更新CustomUser对象的fcm_token字段

---

#### 2.1.7 活动管理视图类

**类名：** `ActivityManagementViews`（功能集合）

**包含方法：**

1. **`student_view_activities(request)`**
   - **功能：** 浏览可报名的活动
   - **方法类型：** GET
   - **主要逻辑：**
     - 获取所有已通过审批的活动（status=1）
     - 检查每个活动是否已报名
     - 检查活动是否已满员

2. **`student_register_activity(request, activity_id)`**
   - **功能：** 报名参加活动
   - **参数：** `activity_id` - 活动ID
   - **方法类型：** POST
   - **主要逻辑：**
     - 验证活动是否可报名
     - 检查是否已报名
     - 检查活动是否已满员
     - 创建ActivityRegistration对象

3. **`student_my_activities(request)`**
   - **功能：** 查看我的活动列表
   - **方法类型：** GET
   - **主要逻辑：**
     - 获取当前学生对象
     - 获取该学生报名的所有活动
     - 获取每个活动的签到状态

4. **`student_feedback_activity(request, activity_id)`**
   - **功能：** 对活动进行评价
   - **参数：** `activity_id` - 活动ID
   - **方法类型：** POST/GET
   - **主要逻辑：**
     - GET：显示评价表单
     - POST：验证表单数据，创建ActivityFeedback对象
     - 检查是否已评价过

---

#### 2.1.8 个人管理视图类

**类名：** `ProfileManagementViews`（功能集合）

**包含方法：**

1. **`student_view_profile(request)`**
   - **功能：** 查看和编辑个人资料
   - **方法类型：** POST/GET
   - **主要逻辑：**
     - GET：显示当前学生信息
     - POST：更新学生信息（姓名、邮箱、电话、头像等）

---

### 2.2 表单类（Form Classes）

#### 2.2.1 LeaveReportStudentForm

**功能：** 学生请假申请表单

**属性：**
- `date`: DateField - 请假日期（DateInput类型）
- `message`: TextField - 请假原因

**方法：**
- `__init__(*args, **kwargs)`: 设置字段标签和帮助文本

---

#### 2.2.2 FeedbackStudentForm

**功能：** 学生反馈表单

**属性：**
- `feedback`: TextField - 反馈内容

**方法：**
- `__init__(*args, **kwargs)`: 设置字段标签和帮助文本

---

#### 2.2.3 ActivityFeedbackForm

**功能：** 活动评价表单

**属性：**
- `rating`: IntegerField - 评分（1-5星）
- `comment`: TextField - 评价内容（Textarea，5行）

**方法：**
- `__init__(*args, **kwargs)`: 设置字段标签和帮助文本

**验证：**
- 评分范围：1-5
- 评价内容不能为空

---

### 2.3 类间关系图

```
┌─────────────────────────────────────────────────────────────┐
│                     学生模块类关系图                          │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │ student_home │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼───────┐  ┌───────▼────────┐
│AttendanceView  │  │ResultView     │  │ActivityMgmt     │
│    Views       │  │    Views     │  │    Views        │
└────────────────┘  └──────────────┘  └───────┬────────┘
        │                                      │
┌───────▼────────┐  ┌──────────────┐  ┌──────▼────────┐
│LeaveReportStudent│ │FeedbackStudent│ │ActivityFeedback│
│     Form        │  │     Form      │  │     Form      │
└─────────────────┘  └──────────────┘  └───────────────┘
        │                  │
        └──────────┬───────┘
                   │
        ┌──────────▼──────────┐
        │      Models         │
        │  (数据模型层)       │
        └─────────────────────┘
```

---

## 3. 数据设计

### 3.1 数据表清单

学生模块涉及以下数据表：

1. `main_app_customuser` - 用户基础信息表
2. `main_app_student` - 学生信息表
3. `main_app_course` - 专业信息表
4. `main_app_subject` - 科目信息表
5. `main_app_session` - 学期信息表
6. `main_app_attendance` - 出勤记录表
7. `main_app_attendancereport` - 学生出勤报告表
8. `main_app_studentresult` - 学生成绩表
9. `main_app_leaverepotstudent` - 学生请假表
10. `main_app_feedbackstudent` - 学生反馈表
11. `main_app_notificationstudent` - 学生通知表
12. `main_app_activity` - 校园活动表
13. `main_app_activityregistration` - 活动报名表
14. `main_app_activityattendance` - 活动签到表
15. `main_app_activityfeedback` - 活动评价表

---

### 3.2 数据表详细设计

#### 3.2.1 main_app_student（学生信息表）

**表描述：** 存储学生信息，与用户表一对一关联，同时关联专业和学期。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 学生ID（主键） |
| admin_id | INTEGER | - | FOREIGN KEY, UNIQUE, NOT NULL | - | 关联的用户ID（外键，关联customuser.id） |
| course_id | INTEGER | - | FOREIGN KEY, NULL | NULL | 所属专业ID（外键，关联course.id） |
| session_id | INTEGER | - | FOREIGN KEY, NULL | NULL | 所属学期ID（外键，关联session.id） |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (admin_id) REFERENCES main_app_customuser(id)
- FOREIGN KEY (course_id) REFERENCES main_app_course(id)
- FOREIGN KEY (session_id) REFERENCES main_app_session(id)
- UNIQUE (admin_id)

---

#### 3.2.2 main_app_attendancereport（学生出勤报告表）

**表描述：** 存储每个学生在每次出勤记录中的出勤状态。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 出勤报告ID（主键） |
| student_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 学生ID（外键，关联student.id） |
| attendance_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 出勤记录ID（外键，关联attendance.id） |
| status | BOOLEAN | - | NOT NULL | False | 出勤状态（True-出席，False-缺席） |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (student_id) REFERENCES main_app_student(id)
- FOREIGN KEY (attendance_id) REFERENCES main_app_attendance(id)

---

#### 3.2.3 main_app_studentresult（学生成绩表）

**表描述：** 存储学生的成绩信息，包括平时成绩和考试成绩。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 成绩ID（主键） |
| student_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 学生ID（外键，关联student.id） |
| subject_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 科目ID（外键，关联subject.id） |
| test | FLOAT | - | NOT NULL | 0 | 平时成绩（0-100分） |
| exam | FLOAT | - | NOT NULL | 0 | 考试成绩（0-100分） |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (student_id) REFERENCES main_app_student(id)
- FOREIGN KEY (subject_id) REFERENCES main_app_subject(id)

---

#### 3.2.4 main_app_leaverepotstudent（学生请假表）

**表描述：** 存储学生的请假申请记录。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 请假记录ID（主键） |
| student_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 学生ID（外键，关联student.id） |
| date | VARCHAR | 60 | NOT NULL | - | 请假日期 |
| message | TEXT | - | NOT NULL | - | 请假原因 |
| status | SMALLINT | - | NOT NULL | 0 | 审批状态（0-待审批，1-已通过，2-已拒绝） |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (student_id) REFERENCES main_app_student(id)

---

#### 3.2.5 main_app_feedbackstudent（学生反馈表）

**表描述：** 存储学生的反馈信息和管理员回复。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 反馈ID（主键） |
| student_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 学生ID（外键，关联student.id） |
| feedback | TEXT | - | NOT NULL | - | 反馈内容 |
| reply | TEXT | - | NOT NULL | '' | 管理员回复 |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (student_id) REFERENCES main_app_student(id)

---

#### 3.2.6 main_app_notificationstudent（学生通知表）

**表描述：** 存储发送给学生的通知信息。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 通知ID（主键） |
| student_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 学生ID（外键，关联student.id） |
| message | TEXT | - | NOT NULL | - | 通知内容 |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (student_id) REFERENCES main_app_student(id)

---

#### 3.2.7 main_app_activity（校园活动表）

**表描述：** 存储校园活动信息，学生可以浏览和报名已通过审批的活动。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 活动ID（主键） |
| title | VARCHAR | 200 | NOT NULL | - | 活动标题 |
| description | TEXT | - | NOT NULL | - | 活动描述 |
| organizer_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 发起教师ID（外键，关联staff.id） |
| location | VARCHAR | 200 | NOT NULL | - | 活动地点 |
| start_time | DATETIME | - | NOT NULL | - | 活动开始时间 |
| end_time | DATETIME | - | NOT NULL | - | 活动结束时间 |
| max_participants | INTEGER | - | NOT NULL | 0 | 最大参与人数（0表示不限制） |
| status | SMALLINT | - | NOT NULL | 0 | 审批状态（0-待审批，1-已通过，2-已拒绝） |
| admin_reply | TEXT | - | NULL | NULL | 管理员回复 |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (organizer_id) REFERENCES main_app_staff(id)

---

#### 3.2.8 main_app_activityregistration（活动报名表）

**表描述：** 存储学生报名参加活动的记录。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 报名ID（主键） |
| activity_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 活动ID（外键，关联activity.id） |
| student_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 学生ID（外键，关联student.id） |
| registered_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 报名时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (activity_id) REFERENCES main_app_activity(id)
- FOREIGN KEY (student_id) REFERENCES main_app_student(id)
- UNIQUE (activity_id, student_id) - 每个学生只能报名一次

---

#### 3.2.9 main_app_activityattendance（活动签到表）

**表描述：** 存储学生在活动中的签到记录，由教师确认。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 签到ID（主键） |
| activity_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 活动ID（外键，关联activity.id） |
| student_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 学生ID（外键，关联student.id） |
| is_present | BOOLEAN | - | NOT NULL | False | 是否出席（True-出席，False-缺席） |
| checked_by_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 签到确认人ID（外键，关联staff.id） |
| checked_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 签到时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (activity_id) REFERENCES main_app_activity(id)
- FOREIGN KEY (student_id) REFERENCES main_app_student(id)
- FOREIGN KEY (checked_by_id) REFERENCES main_app_staff(id)
- UNIQUE (activity_id, student_id) - 每个学生只能签到一次

---

#### 3.2.10 main_app_activityfeedback（活动评价表）

**表描述：** 存储学生对活动的评价信息。

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| id | INTEGER | - | PRIMARY KEY, AUTO_INCREMENT | - | 评价ID（主键） |
| activity_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 活动ID（外键，关联activity.id） |
| student_id | INTEGER | - | FOREIGN KEY, NOT NULL | - | 学生ID（外键，关联student.id） |
| rating | INTEGER | - | NOT NULL | - | 评分（1-5星） |
| comment | TEXT | - | NOT NULL | - | 评价内容 |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 评价时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (activity_id) REFERENCES main_app_activity(id)
- FOREIGN KEY (student_id) REFERENCES main_app_student(id)
- UNIQUE (activity_id, student_id) - 每个学生只能评价一次

---

### 3.3 数据表关系图

```
┌─────────────────────────────────────────────────────────────┐
│                     数据表关系图                              │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │     student      │
                    │     (学生)       │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        │                    │                    │
┌───────▼──────┐    ┌───────▼──────┐    ┌───────▼──────┐
│attendancereport│  │studentresult │  │leaverepotstudent│
│ (出勤报告)    │  │  (成绩)      │  │  (请假)       │
└───────────────┘  └──────────────┘  └───────────────┘
        │
┌───────▼──────┐
│ attendance   │
│ (出勤记录)   │
└──────────────┘

                    ┌──────────────────┐
                    │    activity      │
                    │    (活动)        │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────────────┐  ┌──▼──────────────┐  ┌──▼──────────────┐
│activityregistration  │  │activityattendance│  │activityfeedback│
│   (活动报名)         │  │   (活动签到)    │  │   (活动评价)   │
└──────────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 4. 总结

学生模块是学生管理系统中学生角色的功能模块，为学生提供了完整的个人信息管理、学习数据查看、活动参与等功能。该模块通过完善的视图类、表单类和数据表设计，实现了出勤查看、成绩查看、请假管理、反馈管理、通知管理、活动管理等功能，为学生的学习生活提供了便利。

文档中详细描述了：
- 模块的功能和权限
- 所有视图类和表单类的设计
- 10个核心数据表的详细结构
- 类间关系和数据表关系

该设计文档可以作为系统开发和维护的重要参考。

