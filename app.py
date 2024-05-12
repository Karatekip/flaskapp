from flask import Flask, request, render_template, session, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'IhvM&P11!'
app.config['MYSQL_DB'] = 'logins'
mysql = MySQL(app)

# Secret key for session management
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if not username or not password:
        return 'Username and password are required.', 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cur.fetchone()
    cur.close()

    if user:
        session['username'] = username
        return redirect(url_for('personal_page'))
    else:
        return render_template('login.html', error='Invalid username or password.')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            return 'Username and password are required.', 400

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            return render_template('login.html', error='Username already exists. Please choose a different username.')

        # If username is not taken, proceed with registration
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        session['username'] = username
        return redirect(url_for('personal_page'))

    return render_template('registration_form.html')

@app.route('/personal_page', methods=['GET', 'POST'])
def personal_page():
    if 'username' in session:
        username = session['username']
        
        if request.method == 'POST':
            # Get the note from the form
            note = request.form['note']
            
            # Update the notes in the database
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET notes = %s WHERE username = %s", (note, username))
            mysql.connection.commit()
            cur.close()
        
        # Retrieve user's notes from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT notes FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        
        # If user has notes, pass them to the template
        if user and user[0]:
            notes = user[0]
        else:
            notes = ""
        
        return render_template('personal_page.html', username=username, notes=notes)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
