from flask import render_template, Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        password = request.form.get('password')
        # if db.session.query(User.id).filter_by(nickname=nickname).scalar():

        user = User(nickname=nickname, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return request
    else:
        return render_template('signup.html')


if __name__ == '__main__':
    db.create_all()
    app.run(port=8080, host='127.0.0.1')
