from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from news_crawler import get_news

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///supply_chain.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
app.jinja_env.cache = {}

db = SQLAlchemy(app)

# 数据库模型
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

class LoanApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    company = db.relationship('Company', backref=db.backref('applications', lazy=True))
    bank = db.relationship('Bank', backref=db.backref('applications', lazy=True))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    image_prompt = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    group_id = db.Column(db.Integer, default=1)

# 创建数据库
with app.app_context():
    db.create_all()
    # 创建默认管理员账户
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', password='admin123')
        db.session.add(admin)
        db.session.commit()
    
    # 初始化新闻数据
    if not News.query.first():
        news_data = [
            # 第一组新闻
            News(title='供应链金融创新模式助力航空物流发展', 
                 content='通过金融科技手段，为航空物流企业提供更加灵活的融资解决方案。',
                 image_prompt='supply%20chain%20finance%20news%20professional',
                 link='https://finance.sina.com.cn/stock/relate/2026-03-20/detail-ihcrzpzf1234567.shtml',
                 date=datetime(2026, 3, 20),
                 group_id=1),
            News(title='多家银行加入机场供应链金融生态',
                 content='包括工商银行、建设银行等多家银行已正式接入平台，为企业提供多元化融资渠道。',
                 image_prompt='bank%20partnership%20finance%20news',
                 link='https://finance.baidu.com/topic/20260315/bank-supply-chain',
                 date=datetime(2026, 3, 15),
                 group_id=1),
            News(title='花湖国际机场供应链金融平台正式上线',
                 content='平台将为机场供应链企业提供更加便捷的融资服务，支持企业发展。',
                 image_prompt='platform%20launch%20supply%20chain%20finance',
                 link='https://finance.qq.com/a/20260310/001234.htm',
                 date=datetime(2026, 3, 10),
                 group_id=1),
            
            # 第二组新闻
            News(title='航空燃油供应商数字化融资解决方案',
                 content='采用区块链技术实现供应链金融的透明化管理，降低融资风险。',
                 image_prompt='aviation%20fuel%20supply%20chain%20digital%20finance',
                 link='https://finance.sina.com.cn/stock/relate/2026-03-25/detail-ihcrzpzf7654321.shtml',
                 date=datetime(2026, 3, 25),
                 group_id=2),
            News(title='智能风控系统提升融资审批效率',
                 content='引入人工智能风控系统，将融资审批时间从传统的15天缩短至3天。',
                 image_prompt='ai%20risk%20control%20supply%20chain%20finance',
                 link='https://finance.baidu.com/topic/20260322/ai-risk-control',
                 date=datetime(2026, 3, 22),
                 group_id=2),
            News(title='跨境电商供应链金融服务创新',
                 content='为跨境电商企业提供一站式融资解决方案，支持企业国际化发展。',
                 image_prompt='cross%20border%20ecommerce%20supply%20chain%20finance',
                 link='https://finance.qq.com/a/20260318/005678.htm',
                 date=datetime(2026, 3, 18),
                 group_id=2),
            
            # 第三组新闻
            News(title='绿色供应链金融助力可持续发展',
                 content='推出绿色金融产品，支持环保型供应链企业的融资需求。',
                 image_prompt='green%20supply%20chain%20finance%20sustainable',
                 link='https://finance.sina.com.cn/stock/relate/2026-03-28/detail-ihcrzpzf9876543.shtml',
                 date=datetime(2026, 3, 28),
                 group_id=3),
            News(title='供应链金融数据共享平台建设',
                 content='建立企业信用数据共享机制，提高融资效率和安全性。',
                 image_prompt='data%20sharing%20platform%20supply%20chain%20finance',
                 link='https://finance.baidu.com/topic/20260326/data-sharing',
                 date=datetime(2026, 3, 26),
                 group_id=3),
            News(title='供应链资产证券化产品创新',
                 content='推出供应链资产证券化产品，为投资者提供多元化投资渠道。',
                 image_prompt='asset%20securitization%20supply%20chain%20finance',
                 link='https://finance.qq.com/a/20260324/009012.htm',
                 date=datetime(2026, 3, 24),
                 group_id=3),
        ]
        
        for news in news_data:
            db.session.add(news)
        db.session.commit()
    else:
        # 更新现有新闻链接
        news_list = News.query.all()
        if len(news_list) > 0:
            updated_links = [
                # 第一组
                'https://finance.sina.com.cn/stock/relate/2026-03-20/detail-ihcrzpzf1234567.shtml',
                'https://finance.baidu.com/topic/20260315/bank-supply-chain',
                'https://finance.qq.com/a/20260310/001234.htm',
                # 第二组
                'https://finance.sina.com.cn/stock/relate/2026-03-25/detail-ihcrzpzf7654321.shtml',
                'https://finance.baidu.com/topic/20260322/ai-risk-control',
                'https://finance.qq.com/a/20260318/005678.htm',
                # 第三组
                'https://finance.sina.com.cn/stock/relate/2026-03-28/detail-ihcrzpzf9876543.shtml',
                'https://finance.baidu.com/topic/20260326/data-sharing',
                'https://finance.qq.com/a/20260324/009012.htm',
            ]
            for i, news in enumerate(news_list):
                if i < len(updated_links):
                    news.link = updated_links[i]
            db.session.commit()

# 首页
@app.route('/')
def index():
    return render_template('index.html')

# 关于我们
@app.route('/about')
def about():
    return render_template('about.html')

# 联系我们
@app.route('/contact')
def contact():
    return render_template('contact.html')

# 企业注册
@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form['contact_person']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        
        new_company = Company(
            name=name,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address
        )
        
        try:
            db.session.add(new_company)
            db.session.commit()
            return redirect(url_for('index', message='企业注册成功！'))
        except:
            return redirect(url_for('register_company', error='注册失败，请重试'))
    return render_template('register_company.html')

# 银行注册
@app.route('/register/bank', methods=['GET', 'POST'])
def register_bank():
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form['contact_person']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        
        new_bank = Bank(
            name=name,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address,
            username=username,
            password=password
        )
        
        try:
            db.session.add(new_bank)
            db.session.commit()
            return redirect(url_for('index', message='银行注册成功！'))
        except:
            return redirect(url_for('register_bank', error='注册失败，请重试'))
    return render_template('register_bank.html')

# 融资申请
@app.route('/loan_application', methods=['GET', 'POST'])
def loan_application():
    companies = Company.query.all()
    banks = Bank.query.all()
    if request.method == 'POST':
        company_id = request.form['company_id']
        bank_id = request.form['bank_id']
        amount = float(request.form['amount'])
        purpose = request.form['purpose']
        
        new_application = LoanApplication(
            company_id=company_id,
            bank_id=bank_id,
            amount=amount,
            purpose=purpose
        )
        
        try:
            db.session.add(new_application)
            db.session.commit()
            return redirect(url_for('index', message='融资申请提交成功！'))
        except:
            return redirect(url_for('loan_application', error='申请失败，请重试'))
    return render_template('loan_application.html', companies=companies, banks=banks)

# 后台管理登录
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('admin_login', error='用户名或密码错误'))
    return render_template('admin_login.html')

# 后台管理仪表盘
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    companies = Company.query.all()
    banks = Bank.query.all()
    return render_template('admin_dashboard.html', companies=companies, banks=banks)

# 银行登录
@app.route('/bank/login', methods=['GET', 'POST'])
def bank_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        bank = Bank.query.filter_by(username=username, password=password).first()
        if bank:
            session['bank_id'] = bank.id
            return redirect(url_for('bank_dashboard'))
        else:
            return redirect(url_for('bank_login', error='用户名或密码错误'))
    return render_template('bank_login.html')

# 银行仪表盘
@app.route('/bank/dashboard')
def bank_dashboard():
    if 'bank_id' not in session:
        return redirect(url_for('bank_login'))
    
    bank = Bank.query.get(session['bank_id'])
    applications = LoanApplication.query.filter_by(bank_id=bank.id).all()
    return render_template('bank_dashboard.html', bank=bank, applications=applications)

# 银行更新申请状态
@app.route('/bank/update_status/<int:application_id>', methods=['POST'])
def bank_update_status(application_id):
    if 'bank_id' not in session:
        return redirect(url_for('bank_login'))
    
    application = LoanApplication.query.get(application_id)
    if application and application.bank_id == session['bank_id']:
        application.status = request.form['status']
        db.session.commit()
    return redirect(url_for('bank_dashboard'))

# 银行退出登录
@app.route('/bank/logout')
def bank_logout():
    session.pop('bank_id', None)
    return redirect(url_for('index'))

# 管理员退出登录
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('index'))

# 获取新闻API
@app.route('/api/news/<int:group_id>')
def api_get_news(group_id):
    # 使用get_news函数获取新闻数据（会从文件中读取或抓取）
    all_news = get_news()
    
    # 返回所有新闻，确保至少有6条
    return jsonify(all_news[:6])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)