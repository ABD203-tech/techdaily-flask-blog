# TechDaily Premium Blog App
from flask import Flask, render_template_string, request, redirect, session
from werkzeug.utils import secure_filename
import sqlite3, os

app = Flask(__name__)
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def init_db():
    with sqlite3.connect("techdaily.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image TEXT
        )''')

style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
body {
  margin: 0; padding: 0;
  font-family: 'Outfit', sans-serif;
  background: #0A0C10;
  color: white;
}
nav {
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo { font-size: 1.5rem; font-weight: 900; color: #EEFF00; }
.nav-links a {
  color: #EEE; margin-left: 1.5rem; text-decoration: none;
  font-weight: 500; transition: 0.3s;
}
.nav-links a:hover { color: #4D3DFF; }

header.hero {
  padding: 4rem 2rem; text-align: center;
}
.hero h1 {
  font-size: 3rem;
  color: #EEFF00;
}
.hero p {
  color: #aaa; font-size: 1.1rem;
}

.container {
  max-width: 1000px; margin: auto; padding: 2rem;
}

.article-grid {
  display: grid; gap: 2rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
.article-card {
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 1.5rem;
  transition: transform 0.3s;
}
.article-card:hover {
  transform: translateY(-5px);
}
.article-card h3 { color: #EEFF00; }
.read-more {
  color: #4D3DFF;
  text-decoration: none;
  font-weight: bold;
}

section {
  margin-top: 4rem;
  background: rgba(255,255,255,0.03);
  padding: 2rem;
  border-radius: 10px;
}

form input, form textarea {
  width: 100%;
  padding: 0.8rem;
  margin: 1rem 0;
  background: #111;
  color: white;
  border: 1px solid #333;
  border-radius: 8px;
}
form button {
  background: #4D3DFF;
  color: white;
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}
form button:hover { background: #3728e3; }

img.preview {
  max-width: 100%;
  margin-top: 1rem;
  border-radius: 10px;
  box-shadow: 0 0 10px #000;
}

footer {
  text-align: center;
  padding: 2rem;
  color: #777;
}
</style>
"""

home_page = style + """
<nav>
  <div class="logo">TechDaily</div>
  <div class="nav-links">
    <a href="#about">About</a>
    <a href="#contact">Contact</a>
    <a href="/admin">Admin</a>
  </div>
</nav>
<header class="hero">
  <h1>TechDaily Blog</h1>
  <p>Exploring Daily Tech, AI & Future Trends</p>
</header>
<div class="container">
  <div class="article-grid">
    {% for post in posts %}
    <div class="article-card">
      {% if post[3] %}
      <img src="/static/uploads/{{ post[3] }}" class="preview">
      {% endif %}
      <h3>{{ post[1] }}</h3>
      <p>{{ post[2][:100] }}...</p>
      <a class="read-more" href="/blog/{{ post[0] }}">Read More →</a>
    </div>
    {% endfor %}
  </div>
</div>
<section id="about" class="container">
  <h2>👨‍💻 About Me</h2>
  <p>Hi, I’m Charoliya Abdullah from Palanpur, Gujarat, studying IT diploma. My goal is to become a data scientist and build future-ready apps.</p>
</section>
<section id="contact" class="container">
  <h2>📞 Contact</h2>
  <p><strong>Email:</strong> abdullacharoliya@hotmail.com</p>
  <p><strong>Location:</strong> Palanpur, Gujarat</p>
</section>
<footer>
  &copy; 2025 TechDaily by Abdullah Charoliya
</footer>
"""

blog_page = style + """
<nav><div class='logo'>TechDaily</div><div class='nav-links'><a href='/'>Home</a></div></nav>
<header class="hero"><h1>{{ post[1] }}</h1></header>
<div class="container">
  {% if post[3] %}<img src="/static/uploads/{{ post[3] }}" class="preview">{% endif %}
  <p>{{ post[2] }}</p>
  <a href="/" class="read-more">← Back to Home</a>
</div>
<footer>&copy; 2025 TechDaily</footer>
"""

login_page = style + """
<header class="hero"><h1>🔐 Admin Login</h1></header>
<div class="container">
  <form method="POST">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Login</button>
  </form>
</div>
"""

admin_page = style + """
<header class="hero"><h1>📊 Admin Dashboard</h1></header>
<div class="container">
  <a href="/create" class="read-more">➕ New Post</a> |
  <a href="/logout" class="read-more">Logout</a>
  <hr>
  {% for post in posts %}
    <div class="article-card" style="margin-top:1rem;">
      <h3>{{ post[1] }}</h3>
      <p>{{ post[2][:100] }}...</p>
      <a href="/blog/{{ post[0] }}" class="read-more">View</a> |
      <a href="/delete/{{ post[0] }}" class="read-more" style="color:red;">Delete</a>
    </div>
  {% endfor %}
</div>
"""

create_page = style + """
<header class="hero"><h1>✍️ Create Post</h1></header>
<div class="container">
  <form method="POST" enctype="multipart/form-data">
    <input type="text" name="title" placeholder="Post Title" required>
    <textarea name="content" placeholder="Content" rows="8" required></textarea>
    <input type="file" name="image">
    <button type="submit">Publish</button>
  </form>
  <a href="/admin" class="read-more">← Back</a>
</div>
"""

@app.route("/")
def home():
    with sqlite3.connect("techdaily.db") as conn:
        posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    return render_template_string(home_page, posts=posts)

@app.route("/blog/<int:id>")
def blog(id):
    with sqlite3.connect("techdaily.db") as conn:
        post = conn.execute("SELECT * FROM posts WHERE id=?", (id,)).fetchone()
    return render_template_string(blog_page, post=post)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "123":
            session["logged_in"] = True
            return redirect("/admin")
    return render_template_string(login_page)

@app.route("/admin")
def admin():
    if not session.get("logged_in"): return redirect("/login")
    with sqlite3.connect("techdaily.db") as conn:
        posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    return render_template_string(admin_page, posts=posts)

@app.route("/create", methods=["GET", "POST"])
def create():
    if not session.get("logged_in"): return redirect("/login")
    if request.method == "POST":
        file = request.files.get("image")
        filename = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        with sqlite3.connect("techdaily.db") as conn:
            conn.execute("INSERT INTO posts (title, content, image) VALUES (?, ?, ?)",
                         (request.form["title"], request.form["content"], filename))
        return redirect("/admin")
    return render_template_string(create_page)

@app.route("/delete/<int:id>")
def delete(id):
    if session.get("logged_in"):
        with sqlite3.connect("techdaily.db") as conn:
            conn.execute("DELETE FROM posts WHERE id=?", (id,))
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

import os

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


