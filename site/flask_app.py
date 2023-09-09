## flask_app.py
from flask import Flask, render_template, request, make_response, redirect
import sqlite3
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=['POST'])
def login():
    if request.method == 'POST' and 'id_lector' in request.form:
        id_lector = request.form["id_lector"]

        con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        sql = "SELECT * FROM lectores WHERE id_lector = ?"
        res = cur.execute(sql, [id_lector])
        lector = res.fetchone()
        con.close()

        if lector is None: # el usuario NO existe            
            con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
            cur = con.cursor()
            query = "INSERT INTO lectores(id_lector) VALUES (?)"
            res = cur.execute(query, [id_lector])
            con.commit()
            con.close()
        
        res = make_response(redirect("/recomendaciones"))
        res.set_cookie('id_lector', id_lector)
        return res
    else:
        return make_response(redirect("/")) 


@app.route("/recomendaciones")
def recomendaciones():
    id_lector = request.cookies.get('id_lector')

    con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    ## crear las recomendaciones
    sql = "SELECT * FROM libros LIMIT 9"
    res = cur.execute(sql)
    libros = res.fetchall()

    sql = "SELECT * FROM lectores where id_lector = ?"
    res = cur.execute(sql, [id_lector])
    lector = cur.fetchone()
    
    con.close()

    return render_template("recomendaciones.html", libros=libros, lector=lector)

@app.route("/detalle/<id_libro>")
def libro(id_libro):
    id_lector = request.cookies.get('id_lector')

    con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    ## info del libro
    sql = "SELECT * FROM libros WHERE id_libro = ?"
    res = cur.execute(sql, [id_libro])
    libro = res.fetchone()
    
    ## recomendaciones 
    sql = "SELECT * FROM libros WHERE autor = ? AND id_libro != ? LIMIT 5"
    res = cur.execute(sql, [libro["autor"], id_libro])
    libros = res.fetchall()

    con.close()

    return render_template("detalle.html", libro=libro, libros=libros)
#to run
#--app flask_app run