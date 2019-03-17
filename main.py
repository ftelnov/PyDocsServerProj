from flask import render_template, Flask, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(120), unique=True, nullable=False)
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


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
