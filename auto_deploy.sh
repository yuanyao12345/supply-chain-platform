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
