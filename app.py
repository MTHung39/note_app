from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import psycopg2
import os

app = Flask(__name__)

# Lấy URL kết nối PostgreSQL từ biến môi trường
DATABASE_URL = "postgresql://postgres:Hung0309!@localhost:5432/MTH_db"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT, content TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    search = request.args.get('q', '')
    conn = get_db_connection()
    cur = conn.cursor()
    if search:
        cur.execute("SELECT * FROM notes WHERE title ILIKE %s OR content ILIKE %s ORDER BY id DESC",
                    (f'%{search}%', f'%{search}%'))
    else:
        cur.execute('SELECT * FROM notes ORDER BY id DESC')
    notes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', notes=notes, search=search)

@app.route('/add', methods=['POST'])
def add_note():
    title = request.form['title']
    content = request.form['content']
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        c.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?', (new_title, new_content, note_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        c.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
        note = c.fetchone()
        conn.close()
        return render_template('edit.html', note=note)

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)