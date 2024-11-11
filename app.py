from flask import Flask,render_template
from flask import url_for
from markupsafe import escape

app = Flask(__name__)
#
# @app.route('/user/<name>')#app.route()来绑定URL，当用户访问这个网址的时候就会执行下面的函数
# def user_page(name):
#     return f"User : {escape(name)}"
#
# @app.route('/index')#app.route()来绑定URL，当用户访问这个网址的时候就会执行下面的函数
# def hello1():
#     return "你好"
#
# @app.route('/')
# def say_hello():
#     return "<center><h1>Hello Emanon</h1><img src='http://helloflask.com/totoro.gif'></center>"
# @app.route('/get_url')
# def get_hello1_url():
#     url = url_for("hello1")#查询地址url_for(函数名)
#     return f"查到的地址为{url}"
# @app.route('/test')
# def test_url_for():
#     print(url_for('hello1'))
#     print(url_for("user_page",name = 'hmx'))
#     print(url_for("user_page",name = 'emanon'))
#     print(test_url_for)
#     print(test_url_for)
#     return 'Test page'


name = 'Grey Li'
movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]
@app.route("/")
def index():
    return render_template("index.html",name=name,movies=movies)
if __name__ =="__main__" :
    app.run(port=8000)