from flask import Flask
from flask_graphql import GraphQLView

def create_app(sch):
    app = Flask(__name__)
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=sch,
            graphiql=True
        )
    )

    return app

