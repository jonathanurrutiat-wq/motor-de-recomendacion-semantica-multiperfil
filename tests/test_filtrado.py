import sqlite3


from src.db.filtered import filter as filtro


def crear_db(ruta):
    with sqlite3.connect(ruta) as conexion:
        conexion.execute("CREATE TABLE films (film_slug TEXT, title TEXT, director TEXT)")
        conexion.execute("CREATE TABLE reviews (review_id INTEGER, film_slug TEXT, rating TEXT, lang TEXT, likes INTEGER, review_text TEXT)")
        conexion.executemany("INSERT INTO films VALUES (?, ?, ?)", [("larga", "Larga", "A"), ("corta", "Corta", "B")])
        filas = [(i, "larga", "★★★", "en", i, "texto largo " * 20) for i in range(30)]
        filas += [(100, "larga", "★", "en", 999, "muy corta")]                      # se descarta por corta
        filas += [(200 + i, "corta", "★★", "es", i, "otra reseña " * 20) for i in range(5)]  # película con pocas reseñas
        conexion.executemany("INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?)", filas)


def test_leer_resenias_db(tmp_path, monkeypatch):
    ruta = tmp_path / "reviews.db"
    crear_db(ruta)
    monkeypatch.setattr(filtro, "MAX_RESENIAS_POR_PELICULA", 10)
    df = filtro.leer_resenias_db(ruta)
    assert set(df["film_id"]) == {"larga"}              # "corta" tiene menos de MIN_RESENIAS_POR_PELICULA
    assert len(df) == 10                                 # máximo por película
    assert df["likes"].tolist() == sorted(df["likes"], reverse=True)  # las con más likes primero
    assert (df["review_text"].str.len() >= filtro.MIN_CARACTERES_RESENIA).all()


def test_db_sin_tablas(tmp_path):
    ruta = tmp_path / "otra.db"
    sqlite3.connect(ruta).execute("CREATE TABLE x (a INTEGER)").connection.commit()
    assert filtro.leer_resenias_db(ruta) is None


def test_parse_rating():
    assert filtro.parse_rating("★★★½") == 3.5
    assert filtro.parse_rating(None) == 0.0
    assert filtro.parse_rating(float("nan")) == 0.0
