from flask import Flask
from flask_graphql import GraphQLView

def create_app(sch):
    app = Flask(__name__)
    app.add_url_rule(
        '/interface',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=sch,
            graphiql=True # for having the GraphiQL interface
        )
    )
    @app.route('/hello ')
    def index():
        return "<p>Hello from Graphql</p>"

    return app

