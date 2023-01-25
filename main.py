from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    # salt the password
    hash_salted_pw = generate_password_hash(
        request.form.get('password'),
        method = 'pbkdf2:sha256',
        salt_length = 8
    )

    # create user values from HTML form
    if request.method == "POST":
        user = User()
        user.name = request.form['name']
        user.email = request.form['email']
        password = hash_salted_pw

        # Check if the email is already registered
        if User.query.filter_by(email=user.email).first():
            flash(f"User {user.email} already exists!", 'info')
            flash("Log in instead.")
            return render_template("login.html")

        try:
            # save user in database
            db.session.add(user)
            db.session.commit()
        except AttributeError:
            db.session.rollback()

        return redirect(url_for("secrets", name=user.name))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # Checking email and password
        all_post = db.session.query(User).all()
        for user in all_post:
            if email not in user.email or not check_password_hash(user.password, password):
                error = "Invalid credentials"
                return render_template("login.html", error=error)
            else:
                user = User.query.filter_by(email=email).first()
                login_user(user)
                return redirect(url_for('secrets'))

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    name = request.args.get('name')
    return render_template("secrets.html", name=name)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/download')
def download():
    return send_from_directory('static', filename="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
