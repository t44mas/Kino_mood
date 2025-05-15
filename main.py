import os

from flask import Flask, render_template, redirect, jsonify, request, url_for, g
import requests
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from bs4 import BeautifulSoup
from pyexpat.errors import messages
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from apis import get_books_by_genre, get_book_by_id, get_books_by_title
from data import db_session
from data.users import User
from data.overviews import Overview
from data.favorites import Favorite
from data.comments import Comment
from form.register import RegisterForm
from form.login import LoginForm
from apis import get_overview

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
last_location = {"lat": None, "lon": None}
weather_key = "6df0831671dd861b4d734b18cf1831d9"
books_key = 'AIzaSyCAbAWA_ksxmrana6fb26m8-ugT6QTcvyI'
mood_books = {
    # Радость
    ("joy", "Clear"): "Satire",
    ("joy", "Clouds"): "Comedy",
    ("joy", "Rain"): "Feel-good",
    ("joy", "Thunderstorm"): "Adventure",
    ("joy", "Fog"): "Magical realism",

    # Грусть
    ("sadness", "Clear"): "Crime",
    ("sadness", "Clouds"): "Drama",
    ("sadness", "Rain"): "Tragedy",
    ("sadness", "Thunderstorm"): "Psychological drama",
    ("sadness", "Fog"): "Melodrama",

    # Спокойствие
    ("calm", "Clear"): "Philosophy",
    ("calm", "Clouds"): "Classics",
    ("calm", "Rain"): "Poetry",
    ("calm", "Thunderstorm"): "Essays",
    ("calm", "Fog"): "Spirituality",

    # Страх
    ("fear", "Clear"): "Mystery",
    ("fear", "Clouds"): "Detective",
    ("fear", "Rain"): "Psychological thriller",
    ("fear", "Thunderstorm"): "Thriller",
    ("fear", "Fog"): "Noir",

    # Гнев
    ("anger", "Clear"): "Politics",
    ("anger", "Clouds"): "Dystopian",
    ("anger", "Rain"): "Dark fantasy",
    ("anger", "Thunderstorm"): "Horror",
    ("anger", "Fog"): "Revenge drama",
}
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DEF_PHOTO = os.path.join(app.config['UPLOAD_FOLDER'], 'def_image.jpg')


@login_manager.user_loader
def load_user(user_id):
    with db_session.create_session() as db_sess:
        return db_sess.query(User).get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


last_location = {"lat": 0.0, "lon": 0.0}
weather_key = '1c6e8a61e174ce1136affdebb97de726'


@app.route("/save_location", methods=["POST"])
def save_location():
    global last_location
    data = request.get_json()
    last_location = {'lat': data['lat'], 'lon': data['lon']}
    return jsonify({"success": True})


@app.route('/', methods=["GET", "POST"])
def choice_of_mood():
    try:
        req = f"https://api.openweathermap.org/data/2.5/weather?lat={last_location['lat']}&lon={last_location['lon']}&appid={weather_key}&lang=ru"
        print(req)
        response = requests.get(req)
        if response.status_code == 200:
            json_response = response.json()
            weather_main = json_response["weather"][0]['main']
        else:
            weather_main = "default"
    except Exception as e:
        print("Ошибка получения погоды:", e)
        weather_main = "default"

    if request.method == 'POST':
        selected_mood = request.form.get('mood')
        if selected_mood:
            print((selected_mood, weather_main))
            genre = mood_books.get((selected_mood, weather_main), mood_books.get((selected_mood, "default"), "Drama"))
            return redirect(url_for('show_books', genre=genre))
        else:
            return render_template('main.html', title='KinoMOOD', message='Выберете книгу')
    return render_template('main.html', title='KinoMOOD')


@app.route('/books/<genre>', methods=["GET", "POST"])
def show_books(genre):
    params = get_books_by_genre(genre, amount=3)
    if request.method == 'POST':
        if request.form.get('book_id'):
            with db_session.create_session() as db_sess:
                book_id = request.form.get('book_id')
                book = get_book_by_id(book_id)
                user_id = current_user.get_id()
                book_ids = [book_id for (book_id,) in
                            db_sess.query(Favorite.book_id).filter(Favorite.user_id == user_id).all()]
                if book_id not in book_ids:
                    overview = get_overview(book_id)
                    short_desc = book['description'][:150] if len(book['description']) > 150 else book['description']
                    favorite = Favorite(book_id=book_id, title=book['title'], poster_url=book['image'],
                                        user_id=current_user.get_id(),
                                        overview=overview, short_description=short_desc,
                                        author=book['authors'])
                    db_sess.add(favorite)
                    db_sess.commit()
                    return render_template('show_books.html', title="Найденные книги", params=params, genre=genre,
                                           message='Книга успешно добавлена')
                else:
                    return render_template('show_books.html', title="Найденные книги", params=params, genre=genre,
                                           message='Книга уже в Избранном')
        else:
            with db_session.create_session() as db_sess:
                user_id = int(current_user.get_id())
                data = request.get_json()
                book_id = data.get('book_ID')
                rating = data.get('rating')
                if not book_id or not rating:
                    return jsonify({'success': False, 'error': 'Missing book_ID or rating'}), 400
                overview = Overview(rate=rating, user_id=user_id, book_id=book_id)
                db_sess.add(overview)
                db_sess.commit()
                return jsonify({'success': True})
    return render_template('show_books.html', title="Найденные книги", params=params, genre=genre)


# Начал Можно ввести оценку книги, отзывы, где купить(ссылка на магазины)
@app.route('/book/<book_id>', methods=["GET", "POST"])
def book_detail(book_id):
    book = get_book_by_id(book_id)
    with db_session.create_session() as db_sess:
        comments = db_sess.query(Comment).options(joinedload(Comment.user)).filter(Comment.book_id == book_id).all()

        if request.method == 'POST':
            if request.form.get('book_fav'):
                book_id = request.form.get('book_fav')
                book = get_book_by_id(book_id)
                user_id = current_user.get_id()
                book_ids = [book_id for (book_id,) in
                            db_sess.query(Favorite.book_id).filter(Favorite.user_id == user_id).all()]
                if book_id not in book_ids:
                    overview = get_overview(book_id)
                    short_desc = book['description'][:150] if len(book['description']) > 150 else book['description']
                    favorite = Favorite(book_id=book_id, title=book['title'], poster_url=book['image'],
                                        user_id=current_user.get_id(),
                                        overview=overview, short_description=short_desc,
                                        author=book['authors'])
                    db_sess.add(favorite)
                    db_sess.commit()
                return render_template('book_detail.html', book=book, book_id=book_id, comments=comments)
            elif request.form.get('comment_text'):
                new_comment = Comment(text=request.form.get('comment_text'), user_id=current_user.id, book_id=book_id)
                db_sess.add(new_comment)
                db_sess.commit()
                return redirect(url_for('book_detail', book_id=book_id))
            else:
                user_id = int(current_user.get_id())
                data = request.get_json()
                book_id = data.get('book_ID')
                rating = data.get('rating')
                if not book_id or not rating:
                    return jsonify({'success': False, 'error': 'Missing book_ID or rating'}), 400
                overview = Overview(rate=rating, user_id=user_id, book_id=book_id)
                db_sess.add(overview)
                db_sess.commit()
                return jsonify({'success': True})
    return render_template('book_detail.html', book=book, book_id=book_id, comments=comments)


@app.route('/favourites_books', methods=["GET", "POST"])
@login_required
def favourites_books():
    with db_session.create_session() as db_sess:
        if request.method == 'POST':
            book_id = request.form.get('book_id')
            fav = db_sess.query(Favorite).filter(Favorite.book_id == book_id,
                                                 Favorite.user_id == current_user.id).first()
            if fav:
                db_sess.delete(fav)
                db_sess.commit()
            return redirect(url_for('favourites_books'))

        sort_by = request.args.get('sort_by', 'title')
        user_id = current_user.get_id()
        query = db_sess.query(Favorite).filter(Favorite.user_id == user_id)
        if sort_by == 'title':
            query = query.order_by(Favorite.title)
        elif sort_by == 'author':
            query = query.order_by(Favorite.author)
        elif sort_by == 'overview':
            query = query.order_by(Favorite.overview)
        list1 = query.all()
        books = [{
            'book_id': item.book_id,
            'title': item.title,
            'short_description': item.short_description,
            'author': item.author,
            'poster_url': item.poster_url,
            'overview': round(item.overview, 2)
        } for item in list1]

    return render_template('favourites_books.html', books=books)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with db_session.create_session() as db_sess:
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
        with db_session.create_session() as db_sess:
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
                profile_photo=DEF_PHOTO,
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    photo_path = None

    with db_session.create_session() as db_sess:
        user = db_sess.query(User).get(current_user.id)
        favorite_count = db_sess.query(Favorite).filter(Favorite.user_id == user.id).count()

        if request.method == 'POST':
            file = request.files.get('profile_photo')
            allowed_file = '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            if file and allowed_file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                user.profile_photo = filepath
                db_sess.commit()
                photo_path = filepath

        username = user.username
        photo_path = photo_path or user.profile_photo

    return render_template('profile.html', user=user, favorite_count=favorite_count, photo_path=photo_path)


@app.route('/search_by_title', methods=['GET', 'POST'])
def search_by_title():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('search_by_title.html', books=[], query=query, message="Введите запрос")

    books = get_books_by_title(query, amount=3)
    if request.method == 'POST':
        with db_session.create_session() as db_sess:
            book_id = request.form.get('book_id')
            book = get_book_by_id(book_id)
            user_id = current_user.get_id()
            book_ids = [book_id for (book_id,) in
                        db_sess.query(Favorite.book_id).filter(Favorite.user_id == user_id).all()]
            if book_id not in book_ids:
                overview = get_overview(book_id)
                short_desc = book['description'][:150] if len(book['description']) > 150 else book['description']
                favorite = Favorite(book_id=book_id, title=book['title'], poster_url=book['image'],
                                    user_id=current_user.get_id(),
                                    overview=overview, short_description=short_desc,
                                    author=book['authors'])
                db_sess.add(favorite)
                db_sess.commit()
                return render_template('search_by_title.html', title="Найденные книги", params=books, query=query,
                                       message='Книга успешно добавлена')
            else:
                return render_template('search_by_title.html', title="Найденные книги", params=books, query=query,
                                       message='Книга уже в Избранном')

    if not books:
        return render_template('search_by_title.html', books=[], query=query, message="Ничего не найдено")

    return render_template('search_by_title.html', params=books, query=query)


def main():
    db_session.global_init("db/book_mood.db")
    # app.register_blueprint(jobs_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
