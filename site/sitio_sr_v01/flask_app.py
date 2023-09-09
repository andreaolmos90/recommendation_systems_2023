from flask import Flask, request, render_template, make_response, redirect
import sqlite3
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


@app.route('/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST' and 'id_lector' in request.form:
        id_lector = request.form['id_lector']

        con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
        cur = con.cursor()
        query = """
            INSERT INTO lectores(id_lector)
            VALUES (?)
            ON CONFLICT DO NOTHING
        """
        res = cur.execute(query, (id_lector,))
        con.commit()
        con.close()

        res = make_response(redirect("/recomendaciones"))
        res.set_cookie('id_lector', id_lector)
        return res

    if request.method == 'GET' and 'id_lector' in request.cookies:
        res = make_response(redirect("/recomendaciones"))
        return res

    return render_template('login.html')


@app.route('/recomendaciones', methods=('GET', 'POST'))
def recomendaciones():
    id_lector = request.cookies.get('id_lector')

    con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    if request.method == 'POST':
        for id_libro in request.form.keys():
            rating = int(request.form[id_libro])

            query = """
                INSERT INTO interacciones(id_libro, id_lector, rating)
                VALUES (?, ?, ?)
                ON CONFLICT (id_libro, id_lector) DO UPDATE SET rating=?;
            """
            res = cur.execute(query, (id_libro, id_lector, rating, rating))
            con.commit()

    # libros en el top 9 que no haya puntuado ni visto el usuario
    query = """
    SELECT id_libro, AVG(rating) as rating, count(*) AS cant
        FROM interacciones
        WHERE id_libro NOT IN (SELECT id_libro FROM interacciones WHERE id_lector = ?)
          AND rating > 0
        GROUP BY 1
        ORDER BY 3 DESC, 2 DESC
        LIMIT 9
    """
    res = cur.execute(query, (id_lector,))
    id_libros = [i["id_libro"] for i in res.fetchall()]

    # pongo libros vistos con rating = 0
    for id_libro in id_libros:
        query = """
            INSERT INTO interacciones(id_libro, id_lector, rating)
            VALUES (?, ?, ?)
            ON CONFLICT (id_libro, id_lector) DO UPDATE SET rating=?            
            ;
        """
        res = cur.execute(query, (id_libro, id_lector, 0, 0))
    con.commit()

    query = "SELECT COUNT(*) AS cant FROM interacciones WHERE id_lector = ? AND rating > 0"
    res = cur.execute(query, (id_lector,))
    valorados = res.fetchone()[0]

    query = "SELECT COUNT(*) AS cant FROM interacciones WHERE id_lector = ? AND rating = 0"
    res = cur.execute(query, (id_lector,))
    ignorados = res.fetchone()[0]

    # leemos los datos de los libros seleccionados
    query = f"SELECT * FROM libros WHERE id_libro IN ({','.join(['?']*len(id_libros))})"
    res = cur.execute(query, id_libros)
    libros = res.fetchall()

    con.close()

    return render_template("recomendaciones.html", libros=libros, id_lector=id_lector, valorados=valorados, ignorados=ignorados)
