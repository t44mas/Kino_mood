import requests
import random

API_KEY = "AIzaSyCAbAWA_ksxmrana6fb26m8-ugT6QTcvyI"


def get_books_by_genre(genre, amount=10):
    start_index = 3 * random.randint(0, 30)
    url = f"https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&maxResults={amount}&langRestrict=ru&startIndex={start_index}&key={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json().get("items", [])

    results = []
    for item in data:
        volume = item.get("volumeInfo", {})
        image = volume.get("imageLinks", {}).get("thumbnail", "")
        title = volume.get("title", "Без названия")
        authors = ", ".join(volume.get("authors", []))
        description = volume.get("description", "")
        book_id = item.get("id", "")

        results.append((image, title, authors, description, book_id))

    return results


def get_book_by_id(volume_id):
    url = f"https://www.googleapis.com/books/v1/volumes/{volume_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    data = response.json().get("volumeInfo", {})
    title = data.get("title", "Без названия")
    image = data.get("imageLinks", {}).get("thumbnail", "")
    authors = ", ".join(data.get("authors", []))
    description = data.get("description", "")
    year_published = data.get("publishedDate", "")
    publisher = data.get("publisher", "")
    full_genre = data.get("categories", "")[0] if data.get("categories", "") else "None"
    results = {'title': title, 'image': image, 'authors': authors, 'description': description,
               'year_published': year_published,
               'publisher': publisher, 'full_genre': full_genre}
    return results
