from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///supply_chain.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# 创建数据库
with app.app_context():
    db.create_all()
    # 创建默认管理员账户
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', password='admin123')
        db.session.add(admin)
        db.session.commit()

# 首页
@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)