import os
import time
import subprocess

# 启动Flask服务器
print("Starting Flask server...")
process = subprocess.Popen(
    ["python", "app.py"],
    cwd=os.getcwd(),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 等待服务器启动
time.sleep(3)

# 检查服务器状态
if process.poll() is None:
    print("Server is running!")
    print("Access the platform at: http://127.0.0.1:5001")
    # 保持脚本运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
        process.terminate()
else:
    print("Server failed to start.")
    print("Stdout:", process.stdout.read())
    print("Stderr:", process.stderr.read())
