@echo off
echo ========================================
echo PythonAnywhere 部署准备脚本
echo ========================================
echo.

echo [1/5] 检查项目文件...
if exist app.py (
    echo ✓ app.py 存在
) else (
    echo ✗ app.py 不存在
    pause
    exit /b 1
)

if exist requirements.txt (
    echo ✓ requirements.txt 存在
) else (
    echo ✗ requirements.txt 不存在
    pause
    exit /b 1
)

if exist templates\index.html (
    echo ✓ templates 目录存在
) else (
    echo ✗ templates 目录不存在
    pause
    exit /b 1
)

echo.
echo [2/5] 初始化 Git 仓库...
git init
if %errorlevel% neq 0 (
    echo ✗ Git 初始化失败
    pause
    exit /b 1
)
echo ✓ Git 仓库初始化成功

echo.
echo [3/5] 添加文件到 Git...
git add .
if %errorlevel% neq 0 (
    echo ✗ Git add 失败
    pause
    exit /b 1
)
echo ✓ 文件添加成功

echo.
echo [4/5] 提交文件...
git commit -m "Initial commit for PythonAnywhere deployment"
if %errorlevel% neq 0 (
    echo ✗ Git commit 失败
    pause
    exit /b 1
)
echo ✓ 文件提交成功

echo.
echo [5/5] 准备完成！
echo.
echo ========================================
echo 下一步操作：
echo ========================================
echo.
echo 1. 访问 https://github.com/new 创建新仓库
echo 2. 仓库名称建议：supplychain-platform
echo 3. 不要初始化 README、.gitignore 或 license
echo 4. 创建后，运行以下命令：
echo.
echo    git remote add origin https://github.com/yourusername/supplychain-platform.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 5. 然后按照 PYTHONANYWHERE_GUIDE.md 中的步骤部署
echo.
echo ========================================
echo.
pause
