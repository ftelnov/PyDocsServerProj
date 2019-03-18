from flask import render_template, Flask, redirect, request, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# класс пользователя в базе данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    level = db.Column(db.String(120), default='NewBie')
    experience = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<User id={} nickname={} email={} level={} exp={}>'.format(
            self.id, self.nickname, self.email, self.level, self.experience)


@app.route('/start', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['GET'])
def default():
    return redirect('/start')


@app.errorhandler(404)
def error_404(error):
    return render_template('not-found.html')


@app.route('/profile', methods=['GET'])
def profile():
    print(request.cookies.get('signin'))
    if request.cookies.get('signin'):
        return redirect('/start')
    else:
        return redirect('/signin')


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        if db.session.query(User.id).filter_by(nickname=nickname, password=password).scalar():
            resp = make_response('/start')
            resp.set_cookie('signin', '1',
                                expires=datetime.now() + timedelta(days=30))
            resp.set_cookie('nickname', nickname,
                            expires=datetime.now() + timedelta(days=30))
            resp.set_cookie('nickname', nickname)
            return redirect('/start')
        else:
            return redirect('/404')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        password = request.form.get('password')
        password_submit = request.form.get('password_submit')
        conditional_1 = db.session.query(User.id).filter_by(nickname=nickname).scalar()
        conditional_2 = password != password_submit
        if conditional_1 or conditional_2:
            print('err')
            return render_template('signup.html')

        user = User(nickname=nickname, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/start')
    elif request.method == 'GET':
        return render_template('signup.html')


if __name__ == '__main__':
    db.create_all()
    app.run(port=8080, host='127.0.0.1')
