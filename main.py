from flask import Flask, render_template, redirect, jsonify, request, url_for, g
import requests
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from apis import get_books_by_genre, get_book_by_id
from data import db_session
from data.users import User
from data.favorites import Favorite
from form.register import RegisterForm
from form.login import LoginForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
last_location = {"lat": None, "lon": None}
weather_key = "6df0831671dd861b4d734b18cf1831d9"
books_key = 'AIzaSyCAbAWA_ksxmrana6fb26m8-ugT6QTcvyI'
mood_books = {("sadness", "Clouds"): "drama",
              ("joy", "Clouds"): "comedy",
              ("love", "Clouds"): "Romance",
              ("adventure", "Clouds"): "Adventure",
              ("sadness", "Clear"): "Crime",
              ("joy", "Clear"): "Satire",
              ("love", "Clear"): "Fantasy romance",
              ("adventure", "Clear"): "happy adventure",
              }


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/save_location", methods=["POST"])
def save_location():
    data = request.get_json()
    last_location["lat"] = data.get("lat")
    last_location["lon"] = data.get("lon")
    print(last_location)
    choice_of_mood()
    return jsonify({"status": "success", "data": last_location})


@app.route('/', methods=["GET", "POST"])
def choice_of_mood():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={last_location['lat']}&lon={last_location['lon']}&appid={weather_key}")
    if response.status_code == 200:
        json_response = response.json()
        weather = json_response["weather"][0]['main']
    if request.method == 'POST':
        selected_mood = request.form.get('mood')
        if selected_mood:
            return redirect(url_for('show_books', mood=selected_mood, weather=weather))
    return render_template('main.html', title='KinoMOOD')


@app.route('/books/<mood>/<weather>')
def show_books(mood, weather):
    params = []
    genre = mood_books[(mood, weather)]
    params = get_books_by_genre(genre, amount=3)
    return render_template('show_books.html', title="Найденные книги", params=params, genre=genre)


# Начал Можно ввести оценку книги, отзывы, где купить(ссылка на магазины)
@app.route('/book/<book_id>')
def book_detail(book_id):
    print(book_id)
    book = get_book_by_id(book_id)
    print(book)
    return render_template('book_detail.html', book=book)


@app.route('/book/addToFavorite/<book_id>')
def book_add_fav(book_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    g.user = current_user.get_id()
    print(current_user.get_id())
    book = get_book_by_id(book_id)
    print(book)
    favorite = Favorite(movie_id=book_id, title=book['title'], poster_url=book['image'], user_id=current_user.get_id(),
                        overview=10)
    db_sess.add(favorite)
    db_sess.commit()
    return render_template('book_detail.html', book=book)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким email уже есть")
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким логином уже есть")

        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', form=form)


def main():
    db_session.global_init("db/kino_mood.db")
    # app.register_blueprint(jobs_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
