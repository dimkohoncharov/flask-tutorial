"""Flask Application for Paws Rescue Center."""
from flask import Flask, render_template, abort, request, flash
from forms import LoginForm, SignupForm
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///example.db"
db = SQLAlchemy(app) 

"""Model for Pets."""
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    age = db.Column(db.String)
    bio = db.Column(db.String)

"""Model for Users."""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)

with app.app_context():
    db.create_all()

"""Information regarding the Pets in the System."""
pets = [
            {"id": 1, "name": "Nelly", "age": "5 weeks", "bio": "I am a tiny kitten rescued by the good people at Paws Rescue Center. I love squeaky toys and cuddles."},
            {"id": 2, "name": "Yuki", "age": "8 months", "bio": "I am a handsome gentle-cat. I like to dress up in bow ties."},
            {"id": 3, "name": "Basker", "age": "1 year", "bio": "I love barking. But, I love my friends more."},
            {"id": 4, "name": "Mr. Furrkins", "age": "5 years", "bio": "Probably napping."}, 
        ]

"""Information regarding the Users in the System"""
users = [
            {"id": 1, "full_name": "Pet Rescue Team", "email": "team@pawsrescue.co", "password": "adminpass"},
        ]
@app.route("/")
def homepage():
    """View function for Home Page."""
    return render_template("home.html", pets = pets)


@app.route("/about")
def about():
    """View function for About Page."""
    return render_template("about.html")

@app.route("/details/<int:pet_id>")
def pet_details(pet_id):
    """View function for Showing Details of Each Pet.""" 
    pet = next((pet for pet in pets if pet["id"] == pet_id), None) 
    if pet is None: 
        abort(404, description="No Pet was Found with the given ID")
    return render_template("details.html", pet = pet)

@app.route("/simplelogin", methods=["GET", "POST"])
def simplelogin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email in users and users[email] == password:
            return render_template("simplelogin.html", message="Successfully logged in!")
        else:
            return render_template("simplelogin.html", message="Incorrect Email or Password!")
    return render_template("simplelogin.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = next((user for user in users if user["email"] == form.email.data and user["password"] == form.password.data), None)
        if user is None:
            return render_template("login.html", form = form, message = "Wrong Credentials. Please Try Again.")
        else:
            session['user'] = user
            flash("Successfully Logged In!")
            return redirect(url_for("homepage", _scheme="http", _external=True, message="Successfully Logged In!"))
            # return render_template("login.html", message = "Successfully Logged In!")

    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET"])
def logout():
    if 'user' in session:
        session.pop("user")
    return redirect(url_for("homepage", _scheme="http", _external=True))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = {"id": len(users)+1, "email": form.email.data, "password": form.password.data}
        users.append(new_user)
        session['user'] = new_user
        flash("Successfully signed in!")
        return redirect(url_for("homepage", _scheme="http", _external=True))
    return render_template("signup.html", form=form)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
