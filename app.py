import os
import sys
import click

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, \
    logout_user, current_user

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = "dev"
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,
                                                              'data.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)
login_manager = LoginManager(app)  # 实例化扩展类


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户ID作为参数
    user = User.query.get(int(user_id))  # 用ID作为User模型的主键查询的对应用户
    return user  # 返回用户对象


login_manager.login_view = 'login'


@app.context_processor  # 模板上下文处理函数
def inject_user():
    user = User.query.first()
    return dict(user=user)  # 返回字典，等同于return{'user' : user}这个函数返回的变量
    # （以字典键值对的形式）将会统一注入到每一个模板的上下文环境中，因此可以直接在模板中使用。


class User(db.Model, UserMixin):  # 表名user(自动生成，小写)
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 生成密码散列值
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):  # 验证密码
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):  # 表名movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份


@app.cli.command()  # 用户登录命令
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user"""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo("Updating user...")
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo("Creating user...")
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done')


#  初始化flask-login

# 支持设置用户名字


# 用户登出

@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database"""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo("Initialize the database")  # 提示输出信息


# app = Flask(__name__)
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    # 全局的两个变量移动到这个函数内
    name = 'Emanon'
    movies = [
        {'title': '重庆森林', 'year': '1994'},
        {'title': '霸王别姬', 'year': '1993'},
        {'title': '搏击俱乐部', 'year': '1999'},
        {'title': '为奴十二年', 'year': '2013'},
        {'title': '孤注一掷', 'year': '2023'},
        {'title': '周处除三害', 'year': '2023'},
        {'title': '甲方乙方', 'year': '1997'},
        {'title': '不见不散', 'year': '1998'},
        {'title': '飞驰人生2', 'year': '2024'},
        {'title': '九龙城寨之围城', 'year': '2024'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m["title"], year=m["year"])
        db.session.add(movie)

    db.session.commit()
    click.echo("Done.")


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码


# 添加电影
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # 判断是否为POST请求
        if not current_user.is_authenticated:  # 如果當前用戶為認證
            return redirect(url_for('index'))  # 重定向到主頁
        # 获取表单数据
        title = request.form.get("title")  # 获取表单中name值
        year = request.form.get("year")
        # 验证数据
        if not title or not year or len(year) != 4 or len(title) > 60:
            flash("Invalid input")  # 显示错误提示
            return redirect((url_for('index')))  # 重定向页面
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加数据到会话
        db.session.commit()  # 提交数据会话
        flash("Item Created")  # 显示成功创建的的提示
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


# 编辑页面模板
@app.route("/movie/edit/<int:movie_id>", methods=['GET', 'POST'])
@login_required  # 登陆保护
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash("Invalid input.")
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回编辑页面

        movie.title = title  # 更新数据
        movie.year = year
        db.session.commit()
        flash("Item updated.")
        return redirect(url_for('index'))  # 返回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录


# 删除电影条目
@app.route("/movie/delete/<int:movie_id>", methods=['POST'])  # 只接受post请求
@login_required  # 登陆保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取数据
    db.session.delete(movie)  # 删除数据
    db.session.commit()  # 交付
    flash("Item Deleted")  # 提示
    return redirect(url_for('index'))  # 重定向回主页


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash("Invalidate input")
            return redirect(url_for('settings'))

        # current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings update.')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/login', methods=['GET', 'POST'])  # 用户登录
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("Invalid input.")
            return redirect(url_for('login'))
        # 验证用户名和密码是否一致
        user = User.query.first()

        if username == user.username and user.validate_password(password):

            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash("Invalid username or password.")
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required  # 用于试图保护
def logout():
    logout_user()  # 登出用户
    flash("Goodbye.")
    return redirect(url_for('index'))  # 重定向回首页


if __name__ == "__main__":
    app.run(port=8000)
