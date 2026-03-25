# PythonAnywhere 部署详细指南

## 📋 准备工作

### 1. 确保项目文件完整
在部署前，确保您的项目包含以下文件：
```
Supply-Chain-Plat/
├── app.py                    # 主应用文件
├── requirements.txt          # Python依赖包
├── Procfile                  # 进程配置（Heroku用）
├── runtime.txt               # Python版本
├── .gitignore               # Git忽略文件
├── templates/               # HTML模板
│   ├── index.html
│   ├── register_company.html
│   ├── register_bank.html
│   ├── loan_application.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── bank_login.html
│   └── bank_dashboard.html
└── instance/                # 数据库文件（会被忽略）
    └── supply_chain.db
```

### 2. 检查requirements.txt
确保您的requirements.txt包含以下内容：
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

---

## 🚀 PythonAnywhere 部署步骤

### 第一步：注册账号

1. **访问官网**
   - 打开浏览器，访问：https://www.pythonanywhere.com/

2. **创建账户**
   - 点击右上角的"Create a free account"
   - 填写以下信息：
     - **Username**：选择一个用户名（这将作为您的子域名）
     - **Email**：输入您的邮箱地址
     - **Password**：设置密码
   - 点击"Register"

3. **验证邮箱**
   - 检查您的邮箱
   - 点击验证链接
   - 返回PythonAnywhere登录

---

### 第二步：创建Web应用

1. **进入Web应用页面**
   - 登录后，点击顶部菜单的"Web"
   - 点击"Add a new web app"

2. **选择配置**
   - 点击"Next"
   - 选择"Flask"框架
   - 点击"Next"

3. **选择Python版本**
   - 选择"Python 3.9"
   - 点击"Next"

4. **输入应用名称**
   - 输入应用名称（如：`supplychain`）
   - 这将作为您的应用路径：`/home/yourusername/supplychain`
   - 点击"Next"

5. **完成创建**
   - 系统会自动创建基础配置
   - 点击"Finish"完成

---

### 第三步：上传代码

#### 方法A：使用Git上传（推荐）

1. **在本地初始化Git仓库**
   ```bash
   cd C:\Users\yuany\Documents\trae_projects\Supply-Chain-Plat
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **创建GitHub仓库**
   - 访问 https://github.com/new
   - 创建新仓库：`supplychain-platform`
   - 不要初始化README、.gitignore或license

3. **推送代码到GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/supplychain-platform.git
   git branch -M main
   git push -u origin main
   ```

4. **在PythonAnywhere克隆仓库**
   - 进入PythonAnywhere的"Consoles" -> "Bash"
   - 运行：
     ```bash
     cd ~
     git clone https://github.com/yourusername/supplychain-platform.git supplychain
     ```

#### 方法B：直接上传文件

1. **进入Files页面**
   - 在PythonAnywhere点击"Files"
   - 进入您的用户目录（`/home/yourusername`）

2. **创建项目目录**
   - 点击"New directory"
   - 输入目录名：`supplychain`

3. **上传文件**
   - 进入`supplychain`目录
   - 点击"Upload a file"
   - 依次上传以下文件：
     - `app.py`
     - `requirements.txt`
     - `.gitignore`

4. **创建templates目录**
   - 点击"New directory"
   - 输入目录名：`templates`
   - 进入`templates`目录
   - 上传所有HTML模板文件

---

### 第四步：配置Web应用

1. **进入Web配置页面**
   - 点击"Web"标签
   - 找到您刚创建的应用
   - 点击应用名称进入配置页面

2. **配置代码路径**
   - 找到"Code"部分
   - 设置"Working directory"为：
     ```
     /home/yourusername/supplychain
     ```
   - 设置"WSGI configuration file"为：
     ```
     /home/yourusername/supplychain/supplychain_wsgi.py
     ```

3. **创建WSGI配置文件**
   - 点击"WSGI configuration file"的链接
   - 删除默认内容，粘贴以下代码：
     ```python
     import sys
     import os

     # 添加项目路径到Python路径
     path = '/home/yourusername/supplychain'
     if path not in sys.path:
         sys.path.append(path)

     # 设置环境变量
     os.environ.setdefault('FLASK_ENV', 'production')
     os.environ.setdefault('SECRET_KEY', 'your-secret-key-change-this')

     # 导入Flask应用
     from app import app as application
     ```

4. **保存配置文件**
   - 点击"Save"
   - 返回Web配置页面

---

### 第五步：安装依赖包

1. **打开Bash控制台**
   - 进入"Consoles" -> "Bash"
   - 如果没有Bash控制台，点击"Open a bash console"

2. **进入项目目录**
   ```bash
   cd ~/supplychain
   ```

3. **创建虚拟环境（可选但推荐）**
   ```bash
   virtualenv venv
   source venv/bin/activate
   ```

4. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

5. **验证安装**
   ```bash
   python -c "import flask; print(flask.__version__)"
   ```

---

### 第六步：配置环境变量

1. **进入Web配置页面**
   - 点击"Web"标签
   - 找到"Environment variables"部分

2. **添加环境变量**
   - 点击"Add a new variable"
   - 添加以下变量：
     - **Key**: `SECRET_KEY`
     - **Value**: `your-secret-key-here-change-to-random-string`
   - 点击"OK"

   - 再次点击"Add a new variable"
   - 添加：
     - **Key**: `FLASK_ENV`
     - **Value**: `production`
   - 点击"OK"

3. **保存配置**
   - 点击页面底部的"Save"按钮

---

### 第七步：创建数据库

1. **打开Bash控制台**
   - 进入"Consoles" -> "Bash"

2. **进入项目目录**
   ```bash
   cd ~/supplychain
   ```

3. **激活虚拟环境（如果使用了）**
   ```bash
   source venv/bin/activate
   ```

4. **创建数据库和表**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created successfully!')"
   ```

5. **创建默认管理员账户**
   ```bash
   python -c "from app import app, db, Admin; app.app_context().push(); admin = Admin(username='admin', password='admin123'); db.session.add(admin); db.session.commit(); print('Admin account created!')"
   ```

---

### 第八步：重载Web应用

1. **重载应用**
   - 在Web配置页面
   - 点击"Reload"按钮
   - 等待几秒钟

2. **检查日志**
   - 如果出现错误，点击"Log files"
   - 查看"Error log"和"Server log"
   - 根据错误信息进行调试

---

### 第九步：访问应用

1. **获取应用URL**
   - 在Web配置页面
   - 找到"Configuration"部分
   - 您的应用URL类似于：
     ```
     https://yourusername.pythonanywhere.com
     ```

2. **访问应用**
   - 在浏览器中打开上述URL
   - 您应该能看到花湖国际机场供应链金融平台的首页

3. **测试功能**
   - 测试企业注册功能
   - 测试银行注册功能
   - 测试融资申请功能
   - 测试后台管理功能
   - 测试银行审批功能

---

## 🔧 高级配置

### 配置自定义域名

1. **购买域名**
   - 在域名注册商处购买域名（如：supplychain.com）

2. **在PythonAnywhere添加域名**
   - 进入Web配置页面
   - 找到"Domains"部分
   - 点击"Add a new domain"
   - 输入您的域名
   - 点击"OK"

3. **配置DNS**
   - 登录您的域名管理面板
   - 添加A记录：
     - **主机记录**: `@` 或 `www`
     - **记录值**: PythonAnywhere提供的IP地址
   - 保存DNS设置

4. **等待DNS生效**
   - DNS生效通常需要24-48小时
   - 可以使用`nslookup`命令检查

### 配置HTTPS（SSL证书）

1. **启用HTTPS**
   - 进入Web配置页面
   - 找到"Security"部分
   - 点击"Enable HTTPS"
   - 选择"Let's Encrypt"（免费）
   - 点击"OK"

2. **自动续期**
   - PythonAnywhere会自动续期证书
   - 无需手动操作

### 配置PostgreSQL数据库（推荐）

1. **添加PostgreSQL服务**
   - 进入"Accounts" -> "API tokens"
   - 购买PostgreSQL服务（$9.99/月）

2. **创建数据库**
   - 进入"Databases"标签
   - 创建新数据库：`supplychain`

3. **修改数据库配置**
   - 在Web配置页面的"Environment variables"中添加：
     - **Key**: `DATABASE_URL`
     - **Value**: `postgresql://username:password@host/supplychain`

4. **迁移数据**
   - 使用`pg_dump`和`psql`命令迁移SQLite数据到PostgreSQL

---

## 🐛 常见问题解决

### 问题1：应用无法启动

**症状**：访问URL时显示"Internal Server Error"

**解决方案**：
1. 检查错误日志
2. 确认所有依赖包已安装
3. 检查WSGI配置文件路径是否正确
4. 确认Python版本兼容性

### 问题2：数据库连接错误

**症状**：显示"OperationalError: no such table"

**解决方案**：
1. 确认数据库已创建
2. 运行数据库创建命令
3. 检查数据库文件权限

### 问题3：静态文件无法加载

**症状**：页面样式丢失，图片不显示

**解决方案**：
1. 确认静态文件目录结构正确
2. 检查静态文件路径配置
3. 清除浏览器缓存

### 问题4：内存不足

**症状**：应用经常崩溃或响应缓慢

**解决方案**：
1. 优化数据库查询
2. 减少同时处理的请求数
3. 考虑升级到付费计划

### 问题5：端口被占用

**症状**：显示"Address already in use"

**解决方案**：
1. PythonAnywhere会自动分配端口
2. 检查是否有多个应用在运行
3. 联系PythonAnywhere支持

---

## 📊 监控和维护

### 查看应用日志

1. **访问日志**
   - 进入Web配置页面
   - 点击"Log files"
   - 查看"Error log"、"Server log"和"Access log"

2. **实时监控**
   ```bash
   tail -f /var/www/yourusername_pythonanywhere_com_supervisor.log
   ```

### 定期备份

1. **备份数据库**
   ```bash
   cp ~/supplychain/instance/supply_chain.db ~/supplychain/instance/backup_$(date +%Y%m%d).db
   ```

2. **备份代码**
   - 使用Git定期提交代码
   - 或使用`tar`命令打包备份

### 更新应用

1. **更新代码**
   ```bash
   cd ~/supplychain
   git pull origin main
   ```

2. **更新依赖**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **重载应用**
   - 在Web配置页面点击"Reload"

---

## 💡 最佳实践

1. **使用版本控制**
   - 始终使用Git管理代码
   - 定期提交和推送代码

2. **环境变量管理**
   - 不要在代码中硬编码敏感信息
   - 使用环境变量存储密钥

3. **定期更新**
   - 定期更新Python包
   - 关注安全公告

4. **监控性能**
   - 定期查看日志
   - 监控应用响应时间

5. **备份策略**
   - 定期备份数据库
   - 保留多个备份版本

---

## 📞 获取帮助

如果遇到问题，可以：

1. **查看PythonAnywhere文档**
   - https://help.pythonanywhere.com/

2. **查看Flask文档**
   - https://flask.palletsprojects.com/

3. **联系PythonAnywhere支持**
   - 发送邮件至support@pythonanywhere.com

4. **搜索相关问题**
   - Stack Overflow
   - PythonAnywhere论坛

---

恭喜！您已经成功将花湖国际机场供应链金融平台部署到PythonAnywhere！🎉
