from app import app

# 打印所有注册的路由
print('All registered routes:')
for rule in app.url_map.iter_rules():
    print(f'{rule.rule} -> {rule.endpoint}')
