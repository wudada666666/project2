# CET-6 六级词汇学习平台

一个用于英语六级词汇学习的 Web 应用，支持单词浏览、搜索、随机抽词、拼写检测、AI 助手等功能。

## 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8.0+

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/wudada666666/project2.git
cd project2
```

### 2. 安装 MySQL 并导入数据库

确保 MySQL 服务已启动，然后登录 MySQL：

```bash
mysql -u root -p
```

创建数据库并导入数据：

```sql
CREATE DATABASE cet6zx CHARACTER SET utf8mb3;
USE cet6zx;
SOURCE backend/cet6zx.sql;
```

### 3. 修改数据库配置

编辑 `backend/database.py`，将密码改为你自己的 MySQL 密码：

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "你的MySQL密码",   # 改这里
    "database": "cet6zx",
    "charset": "utf8",
    "cursorclass": pymysql.cursors.DictCursor,
}
```

### 4. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 5. 安装前端依赖

```bash
cd backend/frontend
npm install
```

## 启动项目

### 方式一：双击运行 start.bat（Windows）

直接双击项目根目录下的 `start.bat`，会自动启动后端和前端。

### 方式二：手动启动

启动后端（在一个终端窗口）：

```bash
cd backend
python main.py
```

启动前端（在另一个终端窗口）：

```bash
cd backend/frontend
npm run dev
```

## 访问地址

启动成功后，在浏览器地址栏输入：

- **前端页面：** http://localhost:5173
- **后端 API：** http://localhost:8000

## 技术栈

- 后端：Python + FastAPI + pymysql
- 前端：Vue 3 + Vite + Vue Router + Axios
- 数据库：MySQL 8.0
