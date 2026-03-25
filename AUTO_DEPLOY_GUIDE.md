# 自动化部署指南

## 📋 前提条件

1. ✅ 您已注册PythonAnywhere账户
2. ✅ 您已创建Web应用
3. ✅ 您的GitHub仓库地址：https://github.com/yuanyao12345/supply-chain-platform.git
4. ✅ 本地代码已推送到GitHub

## 🚀 自动化部署步骤

### 第一步：上传部署脚本

1. **打开PythonAnywhere的Bash控制台**
   - 登录PythonAnywhere
   - 点击 "Consoles" -> "Bash"

2. **创建部署脚本**
   - 在Bash中运行以下命令创建脚本文件：
     ```bash
     cd ~
     nano auto_deploy.sh
     ```

3. **复制脚本内容**
   - 复制下面的完整脚本内容：
     ```bash
     #!/bin/bash

     echo "========================================"
     echo "花湖国际机场供应链金融平台 - 自动部署"
     echo "========================================"
     echo ""

     # 检查是否在正确的目录
     if [ "$PWD" != "/home/yuanyao" ]; then
         echo "请先切换到home目录: cd ~"
         exit 1
     fi

     # 步骤1：删除旧目录（如果存在）
     echo "[1/7] 清理旧目录..."
     if [ -d "supplychain" ]; then
         rm -rf supplychain
         echo "✓ 已删除旧目录"
     else
         echo "✓ 无需清理"
     fi

     # 步骤2：克隆GitHub仓库
     echo ""
     echo "[2/7] 克隆GitHub仓库..."
     git clone https://github.com/yuanyao12345/supply-chain-platform.git supplychain
     if [ $? -eq 0 ]; then
         echo "✓ 仓库克隆成功"
     else
         echo "✗ 仓库克隆失败"
         exit 1
     fi

     # 步骤3：进入项目目录
     echo ""
     echo "[3/7] 进入项目目录..."
     cd supplychain
     if [ $? -eq 0 ]; then
         echo "✓ 已进入项目目录"
     else
         echo "✗ 进入项目目录失败"
         exit 1
     fi

     # 步骤4：安装Python依赖
     echo ""
     echo "[4/7] 安装Python依赖..."
     pip install -r requirements.txt
     if [ $? -eq 0 ]; then
         echo "✓ 依赖安装成功"
     else
         echo "✗ 依赖安装失败"
         exit 1
     fi

     # 步骤5：创建数据库
     echo ""
     echo "[5/7] 创建数据库..."
     python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created successfully!')"
     if [ $? -eq 0 ]; then
         echo "✓ 数据库创建成功"
     else
         echo "✗ 数据库创建失败"
         exit 1
     fi

     # 步骤6：创建管理员账户
     echo ""
     echo "[6/7] 创建管理员账户..."
     python -c "from app import app, db, Admin; app.app_context().push(); admin = Admin(username='admin', password='admin123'); db.session.add(admin); db.session.commit(); print('Admin account created!')"
     if [ $? -eq 0 ]; then
         echo "✓ 管理员账户创建成功"
     else
         echo "✗ 管理员账户创建失败"
         exit 1
     fi

     # 步骤7：完成部署
     echo ""
     echo "========================================"
     echo "部署完成！"
     echo "========================================"
     echo ""
     echo "下一步操作："
     echo "1. 进入PythonAnywhere的Web配置页面"
     echo "2. 设置Working directory为: /home/yuanyao/supplychain"
     echo "3. 创建WSGI配置文件（见下方）"
     echo "4. 点击Reload按钮"
     echo "5. 访问: https://yuanyao.pythonanywhere.com"
     echo ""
     echo "WSGI配置文件内容："
     echo "----------------------------------------"
     cat << 'EOF'
     import sys
     import os

     # 添加项目路径
     path = '/home/yuanyao/supplychain'
     if path not in sys.path:
         sys.path.append(path)

     # 设置环境变量
     os.environ.setdefault('FLASK_ENV', 'production')
     os.environ.setdefault('SECRET_KEY', 'your-secret-key-change-this')

     # 导入应用
     from app import app as application
     EOF
     echo "----------------------------------------"
     echo ""
     echo "默认管理员账户："
     echo "用户名: admin"
     echo "密码: admin123"
     echo ""
     ```

4. **保存脚本**
   - 按 `Ctrl+O` 保存
   - 按 `Enter` 确认
   - 按 `Ctrl+X` 退出

5. **设置执行权限**
   ```bash
   chmod +x auto_deploy.sh
   ```

### 第二步：运行自动化脚本

1. **执行部署脚本**
   ```bash
   cd ~
   ./auto_deploy.sh
   ```

2. **等待脚本完成**
   - 脚本会自动完成所有步骤
   - 每个步骤都有进度提示
   - 如果出现错误，脚本会停止并显示错误信息

### 第三步：配置Web应用

1. **进入Web配置页面**
   - 点击顶部菜单的 "Web"
   - 点击您的应用：`yuanyao.pythonanywhere.com`

2. **设置代码路径**
   - 找到 "Code" 部分
   - **Source code**：设置为 `/home/yuanyao/supplychain`
   - **Working directory**：设置为 `/home/yuanyao/supplychain`

3. **配置WSGI文件**
   - 找到 "WSGI configuration file" 链接并点击
   - 删除默认内容，粘贴以下代码：
     ```python
     import sys
     import os

     # 添加项目路径
     path = '/home/yuanyao/supplychain'
     if path not in sys.path:
         sys.path.append(path)

     # 设置环境变量
     os.environ.setdefault('FLASK_ENV', 'production')
     os.environ.setdefault('SECRET_KEY', 'your-secret-key-change-this')

     # 导入应用
     from app import app as application
     ```
   - 点击 "Save"

4. **重启应用**
   - 点击 "重载" 或 "Reload" 按钮
   - 等待几秒钟

### 第四步：访问应用

1. **打开浏览器**
   - 访问：`https://yuanyao.pythonanywhere.com`

2. **测试功能**
   - 测试企业注册
   - 测试银行注册
   - 测试融资申请
   - 测试后台管理（用户名：admin，密码：admin123）
   - 测试银行审批

## 📝 复制粘贴快速版本

如果您不想创建脚本文件，可以直接在Bash中运行以下命令：

```bash
# 1. 清理旧目录
cd ~
rm -rf supplychain

# 2. 克隆仓库
git clone https://github.com/yuanyao12345/supply-chain-platform.git supplychain

# 3. 进入项目目录
cd supplychain

# 4. 安装依赖
pip install -r requirements.txt

# 5. 创建数据库
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created!')"

# 6. 创建管理员账户（如果不存在）
python -c 'from app import app, db, Admin; app.app_context().push(); admin = Admin.query.filter_by(username="admin").first(); if not admin: admin = Admin(username="admin", password="admin123"); db.session.add(admin); db.session.commit(); print("Admin account created!"); else: print("Admin account already exists, skipping...")'

# 7. 完成
echo "部署完成！现在去Web配置页面设置WSGI文件"
```

## 🔧 故障排除

### 问题1：脚本无法执行
**解决方案**：
```bash
chmod +x auto_deploy.sh
./auto_deploy.sh
```

### 问题2：Git克隆失败
**解决方案**：
- 检查GitHub仓库地址是否正确
- 检查网络连接
- 确认仓库是公开的

### 问题3：依赖安装失败
**解决方案**：
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 问题4：数据库创建失败
**解决方案**：
```bash
cd ~/supplychain
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Success')"
```

### 问题5：应用无法启动
**解决方案**：
- 检查错误日志
- 确认WSGI配置正确
- 确认所有依赖已安装

## 📊 部署检查清单

- [ ] GitHub仓库已创建
- [ ] 代码已推送到GitHub
- [ ] PythonAnywhere账户已注册
- [ ] Web应用已创建
- [ ] 部署脚本已执行
- [ ] 依赖已安装
- [ ] 数据库已创建
- [ ] 管理员账户已创建
- [ ] WSGI配置已设置
- [ ] 应用已重启
- [ ] 应用可访问
- [ ] 所有功能测试通过

## 🎉 部署成功后

您的应用现在可以通过以下地址访问：
- **主地址**：https://yuanyao.pythonanywhere.com
- **后台管理**：https://yuanyao.pythonanywhere.com/admin/login
- **银行登录**：https://yuanyao.pythonanywhere.com/bank/login

## 📞 需要帮助？

如果在部署过程中遇到问题，请提供：
1. 错误信息
2. 执行的命令
3. 错误日志内容

我会帮您解决问题！
