from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()  # Load environment variables

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS quotes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content TEXT NOT NULL,
                  mood TEXT,
                  author TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    mood_filter = request.args.get('mood', '')
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()

    if mood_filter:
        c.execute(
            "SELECT content, mood, author, timestamp FROM quotes WHERE mood = ? ORDER BY timestamp DESC", (mood_filter,))
    else:
        c.execute(
            "SELECT content, mood, author, timestamp FROM quotes ORDER BY timestamp DESC")

    quotes = c.fetchall()

    # Get unique moods for filter
    c.execute("SELECT DISTINCT mood FROM quotes")
    available_moods = [mood[0] for mood in c.fetchall()]

    conn.close()
    return render_template('index.html', quotes=quotes, available_moods=available_moods, selected_mood=mood_filter)


@app.route('/add_quote', methods=['GET', 'POST'])
def add_quote():
    if request.method == 'POST':
        quote = request.form['quote']
        mood = request.form['mood']
        author = request.form.get('author', 'Anonymous')

        conn = sqlite3.connect('quotes.db')
        c = conn.cursor()
        c.execute("INSERT INTO quotes (content, mood, author, timestamp) VALUES (?, ?, ?, ?)",
                  (quote, mood, author, datetime.now()))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    return render_template('add_quote.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            conn = sqlite3.connect('quotes.db')
            c = conn.cursor()
            c.execute("SELECT * FROM quotes")
            all_quotes = c.fetchall()
            conn.close()
            return render_template('admin.html', quotes=all_quotes)
    return render_template('admin_login.html')


@app.route('/delete_quote/<int:quote_id>', methods=['POST'])
def delete_quote(quote_id):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
