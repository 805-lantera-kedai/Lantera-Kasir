from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("kasir.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu TEXT,
            harga INTEGER,
            jumlah INTEGER,
            total INTEGER,
            tanggal TEXT
        )
    """)
    conn.commit()
    conn.close()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kasir Lantera Kedai Mbu Osa</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <div class="container py-4">
    <h2 class="text-center mb-4">💰 Kasir <span class="text-primary">Lantera Kedai Mbu Osa</span></h2>
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <form method="POST" class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Nama Menu</label>
            <input type="text" name="menu" class="form-control" required>
          </div>
          <div class="col-md-4">
            <label class="form-label">Harga Satuan (Rp)</label>
            <input type="number" name="harga" class="form-control" required>
          </div>
          <div class="col-md-3">
            <label class="form-label">Jumlah</label>
            <input type="number" name="jumlah" class="form-control" required>
          </div>
          <div class="col-md-1 d-flex align-items-end">
            <button type="submit" class="btn btn-success w-100">+</button>
          </div>
        </form>
      </div>
    </div>
    <div class="card shadow-sm">
      <div class="card-body">
        <h5 class="mb-3">🧾 Riwayat Transaksi Hari Ini ({{ tanggal }})</h5>
        <div class="table-responsive">
          <table class="table table-striped table-bordered">
            <thead class="table-light">
              <tr>
                <th>No</th>
                <th>Menu</th>
                <th>Harga</th>
                <th>Jumlah</th>
                <th>Total</th>
                <th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {% for row in data %}
              <tr>
                <td>{{ loop.index }}</td>
                <td>{{ row[1] }}</td>
                <td>Rp{{ row[2] }}</td>
                <td>{{ row[3] }}</td>
                <td><b>Rp{{ row[4] }}</b></td>
                <td>
                  <a href="/edit/{{ row[0] }}" class="btn btn-warning btn-sm">Edit</a>
                  <a href="/hapus/{{ row[0] }}" class="btn btn-danger btn-sm"
                     onclick="return confirm('Hapus transaksi ini?')">Hapus</a>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        <h5 class="text-end mt-3">💵 Total Hari Ini: <b class="text-success">Rp{{ total_harian }}</b></h5>
      </div>
    </div>
  </div>
</body>
</html>
"""

HTML_EDIT = """
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Edit Transaksi</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <div class="container py-4">
    <div class="card shadow-sm">
      <div class="card-body">
        <h3 class="mb-3">✏️ Edit Transaksi</h3>
        <form method="POST" class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Nama Menu</label>
            <input type="text" name="menu" value="{{ data[1] }}" class="form-control" required>
          </div>
          <div class="col-md-4">
            <label class="form-label">Harga (Rp)</label>
            <input type="number" name="harga" value="{{ data[2] }}" class="form-control" required>
          </div>
          <div class="col-md-4">
            <label class="form-label">Jumlah</label>
            <input type="number" name="jumlah" value="{{ data[3] }}" class="form-control" required>
          </div>
          <div class="col-12">
            <button type="submit" class="btn btn-primary">Simpan</button>
            <a href="/" class="btn btn-secondary">Kembali</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    conn = sqlite3.connect("kasir.db")
    c = conn.cursor()
    tanggal = datetime.now().strftime("%Y-%m-%d")
    if request.method == "POST":
        menu = request.form["menu"]
        harga = int(request.form["harga"])
        jumlah = int(request.form["jumlah"])
        total = harga * jumlah
        c.execute("INSERT INTO transaksi (menu, harga, jumlah, total, tanggal) VALUES (?, ?, ?, ?, ?)",
                  (menu, harga, jumlah, total, tanggal))
        conn.commit()
    c.execute("SELECT * FROM transaksi WHERE tanggal=?", (tanggal,))
    data = c.fetchall()
    total_harian = sum(row[4] for row in data)
    conn.close()
    return render_template_string(HTML_PAGE, data=data, tanggal=tanggal, total_harian=total_harian)

@app.route("/hapus/<int:id>")
def hapus(id):
    conn = sqlite3.connect("kasir.db")
    c = conn.cursor()
    c.execute("DELETE FROM transaksi WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect("kasir.db")
    c = conn.cursor()
    if request.method == "POST":
        menu = request.form["menu"]
        harga = int(request.form["harga"])
        jumlah = int(request.form["jumlah"])
        total = harga * jumlah
        c.execute("UPDATE transaksi SET menu=?, harga=?, jumlah=?, total=? WHERE id=?",
                  (menu, harga, jumlah, total, id))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    c.execute("SELECT * FROM transaksi WHERE id=?", (id,))
    data = c.fetchone()
    conn.close()
    return render_template_string(HTML_EDIT, data=data)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

