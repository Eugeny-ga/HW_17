# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


directors_schema = DirectorSchema(many=True)
director_schema = DirectorSchema()

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


genres_schema = GenreSchema(many=True)
genre_schema = GenreSchema()


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        genre_id = request.args.get('genre_id')
        print(type(genre_id))
        director_id = request.args.get('director_id')
        if director_id and genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id, Movie.director_id == director_id).all()
        elif director_id:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id).all()
        elif genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()
        else:
            movies = Movie.query.all()

        return movies_schema.dump(movies), 200

    def post(self):
        req_data = request.json
        new_movie = Movie(**req_data)
        db.session.add(new_movie)
        db.session.commit()
        return "", 201


@movies_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        movie = Movie.query.get(id)
        if not movie:
            return "", 404
        return movie_schema.dump(movie), 200

    def put(self, id):
        new_data = request.json
        movie = Movie.query.get(id)
        if not movie:
            return "", 404
        movie.title = new_data.get("title")
        movie.description = new_data.get("description")
        movie.trailer = new_data.get("trailer")
        movie.year = new_data.get("year")
        movie.rating = new_data.get("rating")
        movie.genre_id = new_data.get("genre_id")
        movie.director_id = new_data.get("director_id")

        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, id):
        movie = Movie.query.get(id)
        if not movie:
            return "", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = Director.query.all()
        return directors_schema.dump(directors), 200
    def post(self):
        req_json = request.json
        director = Director(**req_json)
        with db.session.begin():
            db.session.add(director)
        return "", 201


@directors_ns.route('/<int:id>')
class DirectorView(Resource):
    def put(self, id):
        req_json = request.json
        director = Director.query.get(id)
        if not director:
            return "", 404
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 201

    def delete(self, id):
        director = Director.query.get(id)
        if not director:
            return "", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genres_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = Genre.query.all()
        return genres_schema.dump(genres), 200

    def post(self):
        req_data = request.json
        genre = Genre(**req_data)
        with db.session.begin():
            db.session.add(genre)
        return "", 201


@genres_ns.route("/<int:id>")
class GenreView(Resource):
    def put(self, id):
        req_data = request.json
        genre = Genre.query.get(id)
        if not genre:
            return "", 404
        genre.name = req_data.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 201

    def delete(self, id):
        genre = Genre.query.get(id)
        if not genre:
            return "", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204



if __name__ == '__main__':
    app.run(debug=True)
