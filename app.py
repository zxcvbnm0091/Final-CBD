from flask import Flask, request, render_template, session, flash, redirect, url_for
import re
import psycopg2.extras

from db import db_connection

def match(text):
  if re.search('[A-Z]+$', text):
    return(False)
  else:
    return(True)

app = Flask(__name__)
app.secret_key = 'THISISMYSECRETKEY'

# Home Page
@app.route('/')
def home():
    if session:
        conn = db_connection()
        cur = conn.cursor()
        user_id = session['user_id']
        print(user_id)
        # Notes
        sql = """
            SELECT id, title, content, user_id, datetime
            FROM notes
            WHERE user_id = %s
            ORDER BY datetime
        """ % (user_id)
        cur.execute(sql)
        notes = cur.fetchall()
        print(notes)

        # Todo List
        sql2 = """
            SELECT tdl.id, tdl.todo, tdl.user_id
            FROM todolist tdl
            WHERE tdl.user_id =%s
            ORDER BY id DESC
        """ % (user_id)
        cur.execute(sql2)
        todo = cur.fetchall()

        cur.close()
        conn.close()
        return render_template('home.html', notes=notes, todo=todo)

    return render_template('login.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    """ function to show and process login page """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        conn = db_connection()
        cur = conn.cursor()
        sql = """
            SELECT id, fullname, username
            FROM users
            WHERE username = '%s' AND password = '%s'
        """ % (username, password)
        cur.execute(sql)
        user = cur.fetchone()
        print(user[1])

        error = ''
        if user is None:
            error = 'Wrong credentials. No user found'
        else:
            session.clear()
            session['user_id'] = user[0]
            session['fullname'] = user[1]
            return redirect(url_for('home'))

        flash(error)
        cur.close()
        conn.close()

    return render_template('login.html')

# Logout Function
@app.route('/logout')
def logout():
    """ function to do logout """
    session.clear()  
    return render_template('login.html')

# SignUp Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'fullname' in request.form:
        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        print(username)
        print(email)
        print(password)
        #_hashed_password = generate_password_hash(password)

        #Check if account exists
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        users = cur.fetchone()
        print(users)
        if users:
            flash('Account with the same username is already exists!')
        elif not re.search("[A-Z]",password):
            flash('Password must contain at least one uppercase')
        else:
            cur.execute("INSERT INTO users (fullname, username, email, password) VALUES (%s,%s,%s,%s)", (fullname, username, email, password))
            conn.commit()
            flash('Register Success')
            return redirect(url_for('login'))

        cur.close()
        conn.close()

    elif request.method == 'POST':
        flash('Please fill out the form!')

    return render_template('signup.html')

@app.route('/newnotes', methods=['GET', 'POST'])
def newnotes():
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'title' in request.form and 'content' in request.form:
        title = request.form['title']
        content = request.form['content']
        datetime = 'current_timestamp'
        user_id = session['user_id']
        
        sql = """
            INSERT INTO notes (user_id, title, content, datetime) 
            VALUES (%s, '%s', '%s', %s) 
            """ % (user_id, title, content, datetime)
        cur.execute(sql)
        conn.commit()
        print(sql)
        cur.close()
        conn.close()
        return redirect(url_for('home')) 
        
    return render_template('newnotes.html')

# Notes
# View Notes Page
@app.route('/viewnote/<int:notes_id>', methods=['GET', 'POST'])
def viewnotes(notes_id):
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """
    SELECT id, title, content, user_id, datetime
    FROM notes
    WHERE id = %s
    """ % notes_id

    cur.execute(sql)
    note = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('viewnotes.html', note=note)

#Edit Notes Page
@app.route('/editnote/<int:notes_id>', methods=['GET', 'POST'])
def editnotes(notes_id):
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'title' in request.form and 'content' in request.form:
        title = request.form['title']
        content = request.form['content']
        datetime = 'current_timestamp'

        title = title.strip()
        content = content.strip()
        
        sql = """
            UPDATE notes SET title = '%s', content = '%s', datetime = %s
            """ % (title, content, datetime)
        cur.execute(sql)
        conn.commit()
        print(sql)
        cur.close()
        conn.close()
        return redirect(url_for('home')) 

    conn = db_connection()
    cur = conn.cursor()
    sql = """
    SELECT id, title, content, user_id, datetime
    FROM notes
    WHERE id = %s
    """ % notes_id
    cur.execute(sql)
    note = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('editnotes.html', note=note)

# Delete notes function
@app.route('/delete/<int:notes_id>', methods=['GET', 'POST'])
def delete(notes_id):
    # check if user is logged in
    if not session:
        return redirect(url_for('login'))

    conn = db_connection()
    cur = conn.cursor()
    sql = 'DELETE FROM notes WHERE id = %s' % notes_id
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
    return redirect (url_for('home'))

# Todo List
# New Todo List Page
@app.route('/newtodolist', methods=['GET', 'POST'])
def newtodolist():
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'todolist' in request.form:
        todolist = request.form['todolist']
        user_id = session['user_id']
        
        sql = """
            INSERT INTO todolist (user_id, todo) 
            VALUES (%s, '%s') 
            """ % (user_id, todolist)
        cur.execute(sql)
        conn.commit()
        print(sql)
        cur.close()
        conn.close()
        return redirect(url_for('home')) 
        
    return render_template('newtodo.html')
# Delete Todo list function
@app.route('/deletetodo/<int:todo_id>', methods=['GET', 'POST'])
def deletetodo(todo_id):
    # check if user is logged in
    if not session:
        return redirect(url_for('login'))

    conn = db_connection()
    cur = conn.cursor()
    sql = """ DELETE FROM todolist WHERE id = %s""" % todo_id
    cur.execute(sql)
    print(sql)
    cur.close()
    conn.commit()
    conn.close()
    return redirect (url_for('home'))