from flask import render_template, Flask, redirect, request, make_response, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'anthrone'
app.config['SESSION_TYPE'] = 'filesystem'
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


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':
        if session.get('signin'):
            # получили пользователя, отфильтровав базу данных
            user = db.session.query(User.id, User.experience, User.nickname, User.level, User.email).filter_by(
                nickname=session.get('nickname')).first()
            identification = user[0]
            exp = user[1]
            nickname = user[2]
            level = user[3]
            email = user[4]
            return render_template('profile.html', nickname=nickname, exp=exp, level=level, id=identification)
        else:
            return redirect('/signin')

    elif request.method == 'POST':
        session['signin'] = 0
        session['nickname'] = None
        return redirect('/signin')


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        if db.session.query(User.id).filter_by(nickname=nickname, password=password).scalar():
            session['signin'] = 1
            session['nickname'] = nickname
            return redirect('/profile')
        else:
            alert = '''<div class="alert alert-danger text-left mt-md-2 pd-1" role="alert">
                    This user does not exist!
                    </div>'''
            return render_template('signin.html', response=alert)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        # получили все поля, в которые пользователь ввел какие-либо данные
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        password = request.form.get('password')
        password_submit = request.form.get('password_submit')

        # прописал все условия в разных строчках, чтобы не загромождать код
        conditional_1 = db.session.query(User.id).filter_by(nickname=nickname).scalar()
        conditional_2 = password != password_submit
        conditional_3 = db.session.query(User.id).filter_by(email=email).scalar()

        conditionals = []  # записываем все условия в массив строк
        if conditional_1:
            conditionals.append('<li> User with that nickname already exist! </li>')
        if conditional_2:
            conditionals.append('<li> Passwords do not match! </li>')
        if conditional_3:
            conditionals.append('<li> User with that email already exist! </li>')

        # если что-либо пошло не так, возвращаемся на туже страничку, но уже с вписанной ошибкой
        response = '''
        <div class="alert alert-danger text-left mt-md-5 pd-1" role="alert">
                <ul>
                     {conditionals}
                </ul>
        </div>'''.format(conditionals=' '.join(conditionals))
        if conditionals:
            return render_template('signup.html', response=response)

        user = User(nickname=nickname, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        session['nickname'] = nickname
        session['signin'] = 1

        return redirect('/profile')
    elif request.method == 'GET':
        return render_template('signup.html')


if __name__ == '__main__':
    db.create_all()
    app.run(port=8080, host='127.0.0.1')
