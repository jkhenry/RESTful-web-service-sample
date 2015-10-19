from flask import Flask, jsonify, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'jk':
        return 'python'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401, avoid showing the ugly login dialog box
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

movies = [
    {
        'id': 1,
        'title': u'The Man from Earth',
        'type': u'Indie film',
        'director': u'Richard Schenkman',
    },
    {
        'id': 2,
        'title': u'12 Angry Men',
        'type': u'Drama',
        'director': u'Sidney Lumet',
    },
    {
        'id': 3,
        'title': u'Mad Max: Fury Road',
        'type': u'Science fiction film',
        'director': u'George Miller',
    }
]

movie_fields = {
    'title': fields.String,
    'type': fields.String,
    'director': fields.String,
    'uri': fields.Url('movie')
}


class MovieListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No title provided',
                                   location='json')
        self.reqparse.add_argument('type', type=str, default="",
                                   location='json')
        self.reqparse.add_argument('director', type=str, default="",
                                   location='json')
        super(MovieListAPI, self).__init__()

    def get(self):
        return {'movies': [marshal(movie, movie_fields) for movie in movies]}

    def post(self):
        args = self.reqparse.parse_args()
        movie = {
            'id': movies[-1]['id'] + 1,
            'title': args['title'],
            'type': args['type'],
            'director': args['director'],
        }
        movies.append(movie)
        return {'movie': marshal(movie, movie_fields)}, 201


class MovieAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('type', type=str, location='json')
        self.reqparse.add_argument('director', type=str, location='json')
        super(MovieAPI, self).__init__()

    def get(self, id):
        movie = [movie for movie in movies if movie['id'] == id]
        if len(movie) == 0:
            abort(404)
        return {'movie': marshal(movie[0], movie_fields)}

    def put(self, id):
        movie = [movie for movie in movies if movie['id'] == id]
        if len(movie) == 0:
            abort(404)
        movie = movie[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                movie[k] = v
        return {'movie': marshal(movie, movie_fields)}

    def delete(self, id):
        movie = [movie for movie in movies if movie['id'] == id]
        if len(movie) == 0:
            abort(404)
        movies.remove(movie[0])
        return {'result': True}


api.add_resource(MovieListAPI, '/api/movies', endpoint='movies')
api.add_resource(MovieAPI, '/api/movies/<int:id>', endpoint='movie')


if __name__ == '__main__':
    app.run(debug=True)
