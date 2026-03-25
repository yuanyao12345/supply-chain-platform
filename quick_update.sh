#!/bin/bash

echo "========================================"
echo "快速更新脚本"
echo "========================================"
echo ""

# 进入项目目录
cd ~/supplychain

# 拉取最新代码
echo "[1/3] 拉取最新代码..."
git pull origin main

# 检查是否有更新
if [ $? -eq 0 ]; then
    echo "✓ 代码更新成功"
else
    echo "✗ 代码更新失败"
    exit 1
fi

# 安装新依赖（如果有）
echo ""
echo "[2/3] 检查依赖..."
pip install -r requirements.txt

# 提示重启
echo ""
echo "[3/3] 准备完成"
echo "========================================"
echo "更新完成！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 访问PythonAnywhere的Web页面"
echo "2. 点击 'Reload' 按钮重启应用"
echo "3. 访问 https://yuanyao.pythonanywhere.com 查看更新"
echo ""
