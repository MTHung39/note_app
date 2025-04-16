from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# Lấy URL kết nối PostgreSQL từ biến môi trường
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO notes (title, content) VALUES (%s, %s)', (title, content))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        cur.execute('UPDATE notes SET title = %s, content = %s WHERE id = %s', (new_title, new_content, note_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    else:
        cur.execute('SELECT * FROM notes WHERE id = %s', (note_id,))
        note = cur.fetchone()
        cur.close()
        conn.close()
        return render_template('edit.html', note=note)

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM notes WHERE id = %s', (note_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/init-db')
def init_db_route():
    try:
        init_db()
        return "✅ Database initialized!"
    except Exception as e:
        return f"❌ Failed to init DB: {e}"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
