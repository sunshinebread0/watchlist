from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie


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
            flash("Invalid input.")  # 显示错误提示
            return redirect((url_for('index')))  # 重定向页面
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加数据到会话
        db.session.commit()  # 提交数据会话
        flash("Item Created.")  # 显示成功创建的的提示
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


@app.route("/movie/delete/<int:movie_id>", methods=['POST'])  # 只接受post请求
@login_required  # 登陆保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取数据
    db.session.delete(movie)  # 删除数据
    db.session.commit()  # 交付
    flash("Item deleted.")  # 提示
    return redirect(url_for('index'))  # 重定向回主页


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash("Invalid input.")
            return redirect(url_for('settings'))

        # current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
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
