from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from werkzeug.utils import secure_filename
from news_crawler import get_news, get_cases, get_policies

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///supply_chain.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
app.jinja_env.cache = {}

# 文件上传配置
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    content = db.Column(db.Text, nullable=False)
    image_prompt = db.Column(db.String(200))
    link = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    group_id = db.Column(db.Integer, default=1)
    source = db.Column(db.String(100))

class FinanceCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_prompt = db.Column(db.String(200))
    link = db.Column(db.String(200))
    source = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)

class PlatformVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(300))  # 外部链接
    video_path = db.Column(db.String(300))  # 上传文件路径
    thumbnail_url = db.Column(db.String(300))
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200))
    source = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)

# 合作伙伴
class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(300))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# 特色服务
class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# 服务流程
class ProcessStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    step_number = db.Column(db.Integer, default=1)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# 常见问题
class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# 用户评价/成功案例
class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    role = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    avatar_url = db.Column(db.String(300))
    rating = db.Column(db.Integer, default=5)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# 统计数据
class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    suffix = db.Column(db.String(20))
    order = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)

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
    partners = Partner.query.order_by(Partner.order.asc()).limit(12).all()
    features = Feature.query.order_by(Feature.order.asc()).limit(6).all()
    process_steps = ProcessStep.query.order_by(ProcessStep.step_number.asc()).limit(6).all()
    faqs = FAQ.query.order_by(FAQ.order.asc()).limit(6).all()
    testimonials = Testimonial.query.order_by(Testimonial.date.desc()).limit(3).all()
    stats = Stat.query.order_by(Stat.order.asc()).limit(4).all()
    
    return render_template('index.html', 
        partners=partners,
        features=features,
        process_steps=process_steps,
        faqs=faqs,
        testimonials=testimonials,
        stats=stats
    )

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

# ========== 新闻管理 ==========
# 新闻列表
@app.route('/admin/news')
def admin_news():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    news_list = News.query.order_by(News.date.desc()).all()
    return render_template('admin_news.html', news_list=news_list)

# 添加新闻
@app.route('/admin/news/add', methods=['GET', 'POST'])
def admin_news_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        news = News(
            title=request.form['title'],
            content=request.form['content'],
            image_prompt=request.form.get('image_prompt'),
            link=request.form.get('link'),
            source=request.form.get('source'),
            group_id=request.form.get('group_id', 1)
        )
        db.session.add(news)
        db.session.commit()
        return redirect(url_for('admin_news'))
    return render_template('admin_news_form.html')

# 编辑新闻
@app.route('/admin/news/edit/<int:id>', methods=['GET', 'POST'])
def admin_news_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    news = News.query.get(id)
    if not news:
        return redirect(url_for('admin_news'))
    if request.method == 'POST':
        news.title = request.form['title']
        news.content = request.form['content']
        news.image_prompt = request.form.get('image_prompt')
        news.link = request.form.get('link')
        news.source = request.form.get('source')
        news.group_id = request.form.get('group_id', 1)
        db.session.commit()
        return redirect(url_for('admin_news'))
    return render_template('admin_news_form.html', news=news)

# 删除新闻
@app.route('/admin/news/delete/<int:id>')
def admin_news_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    news = News.query.get(id)
    if news:
        db.session.delete(news)
        db.session.commit()
    return redirect(url_for('admin_news'))

# ========== 金融案例管理 ==========
# 案例列表
@app.route('/admin/cases')
def admin_cases():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    cases = FinanceCase.query.order_by(FinanceCase.date.desc()).all()
    return render_template('admin_cases.html', cases=cases)

# 添加案例
@app.route('/admin/cases/add', methods=['GET', 'POST'])
def admin_cases_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        case = FinanceCase(
            title=request.form['title'],
            content=request.form['content'],
            image_prompt=request.form.get('image_prompt'),
            link=request.form.get('link'),
            source=request.form.get('source')
        )
        db.session.add(case)
        db.session.commit()
        return redirect(url_for('admin_cases'))
    return render_template('admin_cases_form.html')

# 编辑案例
@app.route('/admin/cases/edit/<int:id>', methods=['GET', 'POST'])
def admin_cases_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    case = FinanceCase.query.get(id)
    if not case:
        return redirect(url_for('admin_cases'))
    if request.method == 'POST':
        case.title = request.form['title']
        case.content = request.form['content']
        case.image_prompt = request.form.get('image_prompt')
        case.link = request.form.get('link')
        case.source = request.form.get('source')
        db.session.commit()
        return redirect(url_for('admin_cases'))
    return render_template('admin_cases_form.html', case=case)

# 删除案例
@app.route('/admin/cases/delete/<int:id>')
def admin_cases_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    case = FinanceCase.query.get(id)
    if case:
        db.session.delete(case)
        db.session.commit()
    return redirect(url_for('admin_cases'))

# ========== 平台视频管理 ==========
# 视频列表
@app.route('/admin/videos')
def admin_videos():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    videos = PlatformVideo.query.order_by(PlatformVideo.date.desc()).all()
    return render_template('admin_videos.html', videos=videos)

# 添加视频
@app.route('/admin/videos/add', methods=['GET', 'POST'])
def admin_videos_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        video_path = None
        
        # 处理文件上传
        if 'video_file' in request.files:
            file = request.files['video_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 生成唯一文件名
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                video_path = filename
        
        video = PlatformVideo(
            title=request.form['title'],
            description=request.form['description'],
            video_url=video_url,
            video_path=video_path,
            thumbnail_url=request.form.get('thumbnail_url')
        )
        db.session.add(video)
        db.session.commit()
        return redirect(url_for('admin_videos'))
    return render_template('admin_videos_form.html')

# 编辑视频
@app.route('/admin/videos/edit/<int:id>', methods=['GET', 'POST'])
def admin_videos_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    video = PlatformVideo.query.get(id)
    if not video:
        return redirect(url_for('admin_videos'))
    if request.method == 'POST':
        video.title = request.form['title']
        video.description = request.form['description']
        video.video_url = request.form.get('video_url')
        video.thumbnail_url = request.form.get('thumbnail_url')
        
        # 处理文件上传
        if 'video_file' in request.files:
            file = request.files['video_file']
            if file and allowed_file(file.filename):
                # 删除旧文件
                if video.video_path:
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], video.video_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # 保存新文件
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                video.video_path = filename
        
        db.session.commit()
        return redirect(url_for('admin_videos'))
    return render_template('admin_videos_form.html', video=video)

# 删除视频
@app.route('/admin/videos/delete/<int:id>')
def admin_videos_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    video = PlatformVideo.query.get(id)
    if video:
        # 删除关联的视频文件
        if video.video_path:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], video.video_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(video)
        db.session.commit()
    return redirect(url_for('admin_videos'))

# ========== 政策资讯管理 ==========
# 政策列表
@app.route('/admin/policies')
def admin_policies():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    policies = Policy.query.order_by(Policy.date.desc()).all()
    return render_template('admin_policies.html', policies=policies)

# 添加政策
@app.route('/admin/policies/add', methods=['GET', 'POST'])
def admin_policies_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        policy = Policy(
            title=request.form['title'],
            content=request.form['content'],
            link=request.form.get('link'),
            source=request.form.get('source')
        )
        db.session.add(policy)
        db.session.commit()
        return redirect(url_for('admin_policies'))
    return render_template('admin_policies_form.html')

# 编辑政策
@app.route('/admin/policies/edit/<int:id>', methods=['GET', 'POST'])
def admin_policies_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    policy = Policy.query.get(id)
    if not policy:
        return redirect(url_for('admin_policies'))
    if request.method == 'POST':
        policy.title = request.form['title']
        policy.content = request.form['content']
        policy.link = request.form.get('link')
        policy.source = request.form.get('source')
        db.session.commit()
        return redirect(url_for('admin_policies'))
    return render_template('admin_policies_form.html', policy=policy)

# 删除政策
@app.route('/admin/policies/delete/<int:id>')
def admin_policies_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    policy = Policy.query.get(id)
    if policy:
        db.session.delete(policy)
        db.session.commit()
    return redirect(url_for('admin_policies'))

# ========== 合作伙伴管理 ==========
@app.route('/admin/partners')
def admin_partners():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    partners = Partner.query.order_by(Partner.order.asc(), Partner.date.desc()).all()
    return render_template('admin_partners.html', partners=partners)

@app.route('/admin/partners/add', methods=['GET', 'POST'])
def admin_partners_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        partner = Partner(
            name=request.form['name'],
            logo_url=request.form.get('logo_url'),
            website=request.form.get('website'),
            description=request.form.get('description'),
            order=request.form.get('order', type=int, default=0)
        )
        db.session.add(partner)
        db.session.commit()
        return redirect(url_for('admin_partners'))
    return render_template('admin_partners_form.html')

@app.route('/admin/partners/edit/<int:id>', methods=['GET', 'POST'])
def admin_partners_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    partner = Partner.query.get(id)
    if not partner:
        return redirect(url_for('admin_partners'))
    if request.method == 'POST':
        partner.name = request.form['name']
        partner.logo_url = request.form.get('logo_url')
        partner.website = request.form.get('website')
        partner.description = request.form.get('description')
        partner.order = request.form.get('order', type=int, default=0)
        db.session.commit()
        return redirect(url_for('admin_partners'))
    return render_template('admin_partners_form.html', partner=partner)

@app.route('/admin/partners/delete/<int:id>')
def admin_partners_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    partner = Partner.query.get(id)
    if partner:
        db.session.delete(partner)
        db.session.commit()
    return redirect(url_for('admin_partners'))

# ========== 特色服务管理 ==========
@app.route('/admin/features')
def admin_features():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    features = Feature.query.order_by(Feature.order.asc(), Feature.date.desc()).all()
    return render_template('admin_features.html', features=features)

@app.route('/admin/features/add', methods=['GET', 'POST'])
def admin_features_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        feature = Feature(
            title=request.form['title'],
            description=request.form.get('description'),
            icon=request.form.get('icon'),
            order=request.form.get('order', type=int, default=0)
        )
        db.session.add(feature)
        db.session.commit()
        return redirect(url_for('admin_features'))
    return render_template('admin_features_form.html')

@app.route('/admin/features/edit/<int:id>', methods=['GET', 'POST'])
def admin_features_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    feature = Feature.query.get(id)
    if not feature:
        return redirect(url_for('admin_features'))
    if request.method == 'POST':
        feature.title = request.form['title']
        feature.description = request.form.get('description')
        feature.icon = request.form.get('icon')
        feature.order = request.form.get('order', type=int, default=0)
        db.session.commit()
        return redirect(url_for('admin_features'))
    return render_template('admin_features_form.html', feature=feature)

@app.route('/admin/features/delete/<int:id>')
def admin_features_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    feature = Feature.query.get(id)
    if feature:
        db.session.delete(feature)
        db.session.commit()
    return redirect(url_for('admin_features'))

# ========== 服务流程管理 ==========
@app.route('/admin/process')
def admin_process():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    steps = ProcessStep.query.order_by(ProcessStep.step_number.asc(), ProcessStep.date.desc()).all()
    return render_template('admin_process.html', steps=steps)

@app.route('/admin/process/add', methods=['GET', 'POST'])
def admin_process_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        step = ProcessStep(
            title=request.form['title'],
            description=request.form.get('description'),
            icon=request.form.get('icon'),
            step_number=request.form.get('step_number', type=int, default=1)
        )
        db.session.add(step)
        db.session.commit()
        return redirect(url_for('admin_process'))
    return render_template('admin_process_form.html')

@app.route('/admin/process/edit/<int:id>', methods=['GET', 'POST'])
def admin_process_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    step = ProcessStep.query.get(id)
    if not step:
        return redirect(url_for('admin_process'))
    if request.method == 'POST':
        step.title = request.form['title']
        step.description = request.form.get('description')
        step.icon = request.form.get('icon')
        step.step_number = request.form.get('step_number', type=int, default=1)
        db.session.commit()
        return redirect(url_for('admin_process'))
    return render_template('admin_process_form.html', step=step)

@app.route('/admin/process/delete/<int:id>')
def admin_process_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    step = ProcessStep.query.get(id)
    if step:
        db.session.delete(step)
        db.session.commit()
    return redirect(url_for('admin_process'))

# ========== 常见问题管理 ==========
@app.route('/admin/faqs')
def admin_faqs():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    faqs = FAQ.query.order_by(FAQ.order.asc(), FAQ.date.desc()).all()
    return render_template('admin_faqs.html', faqs=faqs)

@app.route('/admin/faqs/add', methods=['GET', 'POST'])
def admin_faqs_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        faq = FAQ(
            question=request.form['question'],
            answer=request.form['answer'],
            order=request.form.get('order', type=int, default=0)
        )
        db.session.add(faq)
        db.session.commit()
        return redirect(url_for('admin_faqs'))
    return render_template('admin_faqs_form.html')

@app.route('/admin/faqs/edit/<int:id>', methods=['GET', 'POST'])
def admin_faqs_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    faq = FAQ.query.get(id)
    if not faq:
        return redirect(url_for('admin_faqs'))
    if request.method == 'POST':
        faq.question = request.form['question']
        faq.answer = request.form['answer']
        faq.order = request.form.get('order', type=int, default=0)
        db.session.commit()
        return redirect(url_for('admin_faqs'))
    return render_template('admin_faqs_form.html', faq=faq)

@app.route('/admin/faqs/delete/<int:id>')
def admin_faqs_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    faq = FAQ.query.get(id)
    if faq:
        db.session.delete(faq)
        db.session.commit()
    return redirect(url_for('admin_faqs'))

# ========== 用户评价管理 ==========
@app.route('/admin/testimonials')
def admin_testimonials():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    testimonials = Testimonial.query.order_by(Testimonial.date.desc()).all()
    return render_template('admin_testimonials.html', testimonials=testimonials)

@app.route('/admin/testimonials/add', methods=['GET', 'POST'])
def admin_testimonials_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        testimonial = Testimonial(
            name=request.form['name'],
            company=request.form.get('company'),
            role=request.form.get('role'),
            content=request.form['content'],
            avatar_url=request.form.get('avatar_url'),
            rating=request.form.get('rating', type=int, default=5)
        )
        db.session.add(testimonial)
        db.session.commit()
        return redirect(url_for('admin_testimonials'))
    return render_template('admin_testimonials_form.html')

@app.route('/admin/testimonials/edit/<int:id>', methods=['GET', 'POST'])
def admin_testimonials_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    testimonial = Testimonial.query.get(id)
    if not testimonial:
        return redirect(url_for('admin_testimonials'))
    if request.method == 'POST':
        testimonial.name = request.form['name']
        testimonial.company = request.form.get('company')
        testimonial.role = request.form.get('role')
        testimonial.content = request.form['content']
        testimonial.avatar_url = request.form.get('avatar_url')
        testimonial.rating = request.form.get('rating', type=int, default=5)
        db.session.commit()
        return redirect(url_for('admin_testimonials'))
    return render_template('admin_testimonials_form.html', testimonial=testimonial)

@app.route('/admin/testimonials/delete/<int:id>')
def admin_testimonials_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    testimonial = Testimonial.query.get(id)
    if testimonial:
        db.session.delete(testimonial)
        db.session.commit()
    return redirect(url_for('admin_testimonials'))

# ========== 统计数据管理 ==========
@app.route('/admin/stats')
def admin_stats():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    stats = Stat.query.order_by(Stat.order.asc(), Stat.date.desc()).all()
    return render_template('admin_stats.html', stats=stats)

@app.route('/admin/stats/add', methods=['GET', 'POST'])
def admin_stats_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        stat = Stat(
            label=request.form['label'],
            value=request.form['value'],
            suffix=request.form.get('suffix'),
            order=request.form.get('order', type=int, default=0)
        )
        db.session.add(stat)
        db.session.commit()
        return redirect(url_for('admin_stats'))
    return render_template('admin_stats_form.html')

@app.route('/admin/stats/edit/<int:id>', methods=['GET', 'POST'])
def admin_stats_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    stat = Stat.query.get(id)
    if not stat:
        return redirect(url_for('admin_stats'))
    if request.method == 'POST':
        stat.label = request.form['label']
        stat.value = request.form['value']
        stat.suffix = request.form.get('suffix')
        stat.order = request.form.get('order', type=int, default=0)
        db.session.commit()
        return redirect(url_for('admin_stats'))
    return render_template('admin_stats_form.html', stat=stat)

@app.route('/admin/stats/delete/<int:id>')
def admin_stats_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    stat = Stat.query.get(id)
    if stat:
        db.session.delete(stat)
        db.session.commit()
    return redirect(url_for('admin_stats'))

# 获取供应链金融案例API
@app.route('/api/cases')
def api_get_cases():
    # 使用get_cases函数获取案例数据（会从文件中读取或抓取）
    crawler_cases = get_cases()
    
    # 获取数据库中的案例
    db_cases = FinanceCase.query.order_by(FinanceCase.date.desc()).limit(10).all()
    db_cases_list = []
    for case in db_cases:
        db_cases_list.append({
            'id': case.id,
            'title': case.title,
            'content': case.content,
            'link': case.link,
            'date': case.date.strftime('%Y-%m-%d %H:%M'),
            'source': case.source,
            'image_prompt': case.image_prompt
        })
    
    # 合并爬虫案例和数据库案例，数据库案例优先
    all_cases = db_cases_list + crawler_cases
    
    # 去重：以title为基准
    seen_titles = set()
    unique_cases = []
    for case in all_cases:
        if case['title'] not in seen_titles:
            seen_titles.add(case['title'])
            unique_cases.append(case)
    
    return jsonify(unique_cases[:6])

# 获取政策资讯API
@app.route('/api/policies')
def api_get_policies():
    # 使用get_policies函数获取政策数据（会从文件中读取或抓取）
    crawler_policies = get_policies()
    
    # 获取数据库中的政策
    db_policies = Policy.query.order_by(Policy.date.desc()).limit(10).all()
    db_policies_list = []
    for policy in db_policies:
        db_policies_list.append({
            'id': policy.id,
            'title': policy.title,
            'content': policy.content,
            'link': policy.link,
            'date': policy.date.strftime('%Y-%m-%d %H:%M'),
            'source': policy.source
        })
    
    # 合并爬虫政策和数据库政策，数据库政策优先
    all_policies = db_policies_list + crawler_policies
    
    # 去重：以title为基准
    seen_titles = set()
    unique_policies = []
    for policy in all_policies:
        if policy['title'] not in seen_titles:
            seen_titles.add(policy['title'])
            unique_policies.append(policy)
    
    return jsonify(unique_policies[:6])

# 获取平台视频API
@app.route('/api/videos')
def api_get_videos():
    # 获取数据库中的视频
    db_videos = PlatformVideo.query.order_by(PlatformVideo.date.desc()).limit(10).all()
    videos_list = []
    for video in db_videos:
        # 优先使用上传的视频文件
        video_src = video.video_url
        if video.video_path:
            video_src = url_for('uploaded_file', filename=video.video_path)
        
        videos_list.append({
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'video_url': video_src,
            'thumbnail_url': video.thumbnail_url,
            'date': video.date.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify(videos_list)

# 访问上传的视频文件
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 测试路由
@app.route('/api/test')
def api_test():
    return jsonify({'message': 'Test route works!'})

# 获取新闻API
@app.route('/api/news')
def api_news_list():
    news_list = News.query.order_by(News.date.desc()).limit(10).all()
    result = []
    for news in news_list:
        result.append({
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'link': news.link,
            'date': news.date.strftime('%Y-%m-%d %H:%M'),
            'source': news.source,
            'image_prompt': news.image_prompt
        })
    return jsonify(result)

@app.route('/api/news/<int:group_id>')
def api_get_news(group_id):
    # 使用get_news函数获取新闻数据（会从文件中读取或抓取）
    crawler_news = get_news()
    
    # 获取数据库中的新闻
    db_news = News.query.filter_by(group_id=group_id).order_by(News.date.desc()).limit(10).all()
    db_news_list = []
    for news in db_news:
        db_news_list.append({
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'link': news.link,
            'date': news.date.strftime('%Y-%m-%d %H:%M'),
            'source': news.source,
            'image_prompt': news.image_prompt
        })
    
    # 合并爬虫新闻和数据库新闻，数据库新闻优先
    all_news = db_news_list + crawler_news
    
    # 去重：以title为基准
    seen_titles = set()
    unique_news = []
    for news in all_news:
        if news['title'] not in seen_titles:
            seen_titles.add(news['title'])
            unique_news.append(news)
    
    return jsonify(unique_news[:10])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run()
