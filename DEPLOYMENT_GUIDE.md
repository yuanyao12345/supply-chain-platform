# 花湖国际机场供应链金融平台 - PaaS部署指南

## 方案一：PythonAnywhere（推荐新手）

### 1. 注册账号
- 访问 https://www.pythonanywhere.com/
- 点击"Create a free account"
- 填写用户名、邮箱和密码
- 验证邮箱

### 2. 创建Web应用
1. 登录PythonAnywhere
2. 点击"Web"标签
3. 点击"Add a new web app"
4. 选择"Flask"框架
5. 选择Python 3.9版本
6. 输入应用名称（如：supplychain）

### 3. 上传代码
#### 方法A：使用Git（推荐）
```bash
# 在本地初始化Git仓库
git init
git add .
git commit -m "Initial commit"

# 在PythonAnywhere创建仓库
# 1. 进入"Consoles" -> "Bash"
# 2. 运行：git clone https://github.com/yourusername/supplychain.git
```

#### 方法B：直接上传文件
1. 在PythonAnywhere进入"Files"
2. 进入你的用户目录
3. 点击"Upload a file"
4. 上传所有项目文件

### 4. 配置Web应用
1. 在"Web"页面找到"Code"部分
2. 设置"Working directory"为：`/home/yourusername/supplychain`
3. 设置"WSGI configuration file"为：`/home/yourusername/supplychain/supplychain_wsgi.py`

### 5. 创建WSGI配置文件
在PythonAnywhere的"Files"中创建`supplychain_wsgi.py`：
```python
import sys
path = '/home/yourusername/supplychain'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### 6. 安装依赖
1. 进入"Consoles" -> "Bash"
2. 运行：
```bash
cd supplychain
pip install -r requirements.txt
```

### 7. 配置环境变量
1. 在"Web"页面找到"Environment variables"
2. 添加：
   - `SECRET_KEY`: `your-secret-key-here`
   - `FLASK_ENV`: `production`

### 8. 重载Web应用
1. 在"Web"页面点击"Reload"按钮
2. 等待几秒钟
3. 访问你的应用：`https://yourusername.pythonanywhere.com`

### 9. 设置自定义域名（可选）
1. 在"Web"页面找到"Domains"
2. 点击"Add a new domain"
3. 输入你的域名（如：supplychain.yourdomain.com）
4. 按照提示配置DNS

---

## 方案二：Heroku

### 1. 注册账号
- 访问 https://www.heroku.com/
- 点击"Sign up"
- 填写信息并验证邮箱

### 2. 安装Heroku CLI
```bash
# Windows
# 下载并安装：https://devcenter.heroku.com/articles/heroku-cli

# 验证安装
heroku --version
```

### 3. 登录Heroku
```bash
heroku login
```

### 4. 初始化Git仓库
```bash
cd Supply-Chain-Plat
git init
git add .
git commit -m "Initial commit"
```

### 5. 创建Heroku应用
```bash
heroku create supplychain-platform
```

### 6. 配置环境变量
```bash
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set FLASK_ENV=production
```

### 7. 部署到Heroku
```bash
git push heroku master
```

### 8. 查看应用状态
```bash
heroku ps
heroku logs --tail
```

### 9. 访问应用
```bash
heroku open
```

### 10. 配置PostgreSQL数据库（推荐）
```bash
# 添加PostgreSQL插件
heroku addons:create heroku-postgresql:mini

# 获取数据库URL
heroku config:get DATABASE_URL
```

---

## 方案三：Render（简单易用）

### 1. 注册账号
- 访问 https://render.com/
- 点击"Sign up"
- 使用GitHub账号登录

### 2. 连接GitHub仓库
1. 点击"New +"
2. 选择"Web Service"
3. 连接你的GitHub仓库

### 3. 配置构建设置
- **Name**: supplychain-platform
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 4. 配置环境变量
- `SECRET_KEY`: `your-secret-key-here`
- `FLASK_ENV`: `production`

### 5. 部署
点击"Create Web Service"，等待部署完成

---

## 常见问题解决

### 1. 数据库迁移问题
如果使用PostgreSQL，需要修改数据库连接：
```python
# 在app.py中
import os
import psycopg2

# Heroku会自动设置DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
```

### 2. 静态文件问题
确保静态文件在正确的位置：
```
Supply-Chain-Plat/
├── app.py
├── requirements.txt
├── static/
│   └── css/
│   └── js/
└── templates/
    └── index.html
```

### 3. 端口问题
PaaS平台会自动分配端口，确保代码中正确读取环境变量：
```python
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

### 4. 内存限制
免费账户通常有内存限制，如果遇到内存不足：
- 优化数据库查询
- 减少同时处理的请求数
- 考虑升级到付费计划

---

## 安全建议

1. **使用HTTPS**：所有PaaS平台都支持免费SSL证书
2. **保护敏感信息**：不要在代码中硬编码密码和密钥
3. **定期备份**：定期备份数据库
4. **监控日志**：定期检查应用日志
5. **更新依赖**：定期更新Python包以修复安全漏洞

---

## 成本对比

| 平台 | 免费额度 | 付费计划 | 推荐场景 |
|------|---------|---------|---------|
| PythonAnywhere | 每天24小时 | $5/月起 | 新手、小流量 |
| Heroku | 有限制 | $5/月起 | 专业开发 |
| Render | 有限制 | $7/月起 | 现代部署 |

---

## 推荐选择

- **新手**：PythonAnywhere（配置简单，文档丰富）
- **专业开发**：Heroku（功能强大，生态完善）
- **快速部署**：Render（界面友好，自动部署）

选择最适合您需求的平台开始部署吧！
