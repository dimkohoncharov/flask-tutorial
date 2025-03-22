"""Flask Application for Paws Rescue Center."""
from flask import Flask, render_template, abort, request, flash
from forms import LoginForm, SignupForm, EditPetForm
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

"""Information regarding the Pets in the System."""
pets = [
    {"id": 1, "name": "Nelly", "age": "5 weeks", "bio": "I am a tiny kitten rescued by the good people at Paws Rescue Center. I love squeaky toys and cuddles.", "user_id": 1},
    {"id": 2, "name": "Yuki", "age": "8 months", "bio": "I am a handsome gentle-cat. I like to dress up in bow ties.", "user_id": 1},
    {"id": 3, "name": "Basker", "age": "1 year", "bio": "I love barking. But, I love my friends more.", "user_id": 1},
    {"id": 4, "name": "Mr. Furrkins", "age": "5 years", "bio": "Probably napping.", "user_id": 1},
]

"""Information regarding the Users in the System"""
users = [
    {"id": 1, "full_name": "Pet Rescue Team", "email": "team@pawsrescue.co", "password": "adminpass"},
]


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
    posted_by = db.Column(db.Integer, db.ForeignKey("user.id"))

"""Model for Users."""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    pets = db.relationship("Pet", backref="user")
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

with app.app_context():
    db.create_all()
    team = User(full_name = "Pet Rescue Team", email = "team@petrescue.co", password = "adminpass")
    db.session.add(team)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

    for pet in pets:
        db.session.add(
            Pet(name=pet["name"], age=pet["age"], bio=pet["bio"], posted_by=pet["user_id"])
        )
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()


@app.route("/")
def homepage():
    """View function for Home Page."""
    pets = Pet.query.all()
    return render_template("home.html", pets = pets)


@app.route("/about")
def about():
    """View function for About Page."""
    return render_template("about.html")

@app.route("/details/<int:pet_id>")
def pet_details(pet_id):
    """View function for Showing Details of Each Pet.""" 
    pet = Pet.query.get(pet_id)
    if pet is None:
        abort(404, description="No Pet was Found with the given ID")
    return render_template("details.html", pet = pet)

@app.route("/details/<int:pet_id>/edit", methods=["GET", "POST"])
def pet_details_edit(pet_id):
    """Edit function for Pet"""
    pet = Pet.query.get(pet_id)
    form = EditPetForm()
    if pet is None:
        abort(404, description="No Pet was Found with the given ID")
    if form.validate_on_submit():
        pet.name = form.name.data
        pet.age = form.age.data
        pet.bio = form.bio.data
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return render_template(
                "details_edit.html", pet = pet, form = form, 
                message = "A Pet with this name already exists!"
                )
    return render_template("details_edit.html", pet=pet, form=form)

@app.route("/details/<int:pet_id>/delete")
def pet_details_delete(pet_id):
    pet = Pet.query.get(pet_id)
    if pet is None:
        abort(404, description="No Pet was Found with the given ID")
    db.session.delete(pet)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(url_for('homepage', _scheme='http', _external=True))

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
        user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
        if user is None:
            return render_template(
                "login.html", 
                form = form, 
                message = "Wrong Credentials. Please Try Again.")
        else:
            session['user'] = user.id
            flash("Successfully Logged In!")
            return redirect(
                url_for("homepage",
                        _scheme="http",
                        _external=True,
                        message="Successfully Logged In!"
                        ))
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
        new_user = User(full_name = form.full_name.data, 
                        email = form.email.data, password = form.password.data)
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return render_template(
                "signup.html",
                form = form,
                message = "This Email already exists in the system! Please Log in instead.")
        finally:
            db.session.close()
        session['user'] = new_user.id
        flash("Successfully signed in!")
        return redirect(url_for("homepage", _scheme="http", _external=True))
    return render_template("signup.html", form=form)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
