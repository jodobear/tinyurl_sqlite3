from flask import Flask, request, render_template, redirect

import string, sqlite3, base64, hashlib

from math import floor
from sqlite3 import OperationalError

from urllib.parse import urlparse
str_encode = str.encode

from string import ascii_lowercase, ascii_uppercase

# Assuming urls.db is in your app root folder
app = Flask(__name__)
host = 'http://localhost:5000/'


def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INT PRIMARY KEY AUTOINCREMENT,
        URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass

def get_hash(url):
    return hashlib.md5(str(url).encode()).hexdigest()[:6]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = str_encode(request.form.get('url-submit'))
        if urlparse(original_url).scheme == '':
            url = 'http://' + original_url
        else:
            url = original_url
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO WEB_URL (URL) VALUES (?)',
                [base64.urlsafe_b64encode(url)]
            )
            encoded_string = get_hash(res.lastrowid)
        return render_template('home.html', short_url=host + encoded_string)
    return render_template('home.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded = toBase10(short_url)
    url = host  # fallback if no URL is found
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL FROM WEB_URL WHERE ID=?', [decoded])
        try:
            short = res.fetchone()
            if short is not None:
                url = base64.urlsafe_b64decode(short[0])
        except Exception as e:
            print(e)
    return redirect(url)


if __name__ == '__main__':
    # check if database table is created
    table_check()
    app.run(debug=True, host="0.0.0.0")
