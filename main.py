from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peliculas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Pelicula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    calificacion = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'genero': self.genero,
            'calificacion': self.calificacion
        }


@app.route("/")
def home():
    return jsonify({"message": "Bienvenido al sistema de películas!!!"})


@app.route("/peliculas", methods=["GET"])
def get_peliculas():
    peliculas = Pelicula.query.all()
    return jsonify([pelicula.to_dict() for pelicula in peliculas])


@app.route("/peliculas/<int:id>", methods=["GET"])
def get_pelicula(id):
    obj_pelicula = Pelicula.query.get(id)
    if obj_pelicula:
        return jsonify(obj_pelicula.to_dict())
    else:
        return jsonify({"error": "No existe la película solicitada"}), 404


@app.route("/peliculas", methods=["POST"])
def add_pelicula():
    data = request.get_json()
    
    
    if not data or not all(k in data for k in ('titulo', 'genero', 'calificacion')):
        return jsonify({"error": "Faltan campos requeridos: titulo, genero, calificacion"}), 400
    
    obj_new = Pelicula(
        titulo=data['titulo'], 
        genero=data['genero'], 
        calificacion=data['calificacion']
    )
    db.session.add(obj_new)
    db.session.commit()
    return jsonify(obj_new.to_dict()), 201


@app.route("/peliculas/<int:id>", methods=["PUT"])
def update_pelicula(id):
    data = request.get_json()
    obj_pelicula = Pelicula.query.get(id)
    
    if obj_pelicula:
        obj_pelicula.titulo = data.get('titulo', obj_pelicula.titulo)
        obj_pelicula.genero = data.get('genero', obj_pelicula.genero)
        obj_pelicula.calificacion = data.get('calificacion', obj_pelicula.calificacion)
        db.session.commit()
        return jsonify(obj_pelicula.to_dict())
    else:
        return jsonify({"error": "No existe la película para actualizar"}), 404


@app.route("/peliculas/<int:id>", methods=["DELETE"])
def delete_pelicula(id):
    obj_pelicula = Pelicula.query.get(id)
    if obj_pelicula:
        db.session.delete(obj_pelicula)
        db.session.commit()
        return jsonify({"message": "Película eliminada correctamente"})
    else:
        return jsonify({"error": "No existe la película para eliminar"}), 404


@app.route("/peliculas/genero/<string:genero>", methods=["GET"])
def get_peliculas_by_genero(genero):
    peliculas = Pelicula.query.filter_by(genero=genero).all()
    if peliculas:
        return jsonify([pelicula.to_dict() for pelicula in peliculas])
    else:
        return jsonify({"message": f"No hay películas del género '{genero}'"}), 404


@app.route("/peliculas/calificacion/<float:minima>", methods=["GET"])
def get_peliculas_by_calificacion(minima):
    peliculas = Pelicula.query.filter(Pelicula.calificacion >= minima).all()
    if peliculas:
        return jsonify([pelicula.to_dict() for pelicula in peliculas])
    else:
        return jsonify({"message": f"No hay películas con calificación >= {minima}"}), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)