import click

from watchlist import app, db
from watchlist.models import User, Movie


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
    click.echo("Initialized database.")  # 提示输出信息


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
    click.echo('Done.')
