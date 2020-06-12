from app.app import create_app
from app.gql.openml_schema import schema
from app import settings

app =create_app(schema)

if __name__ == '__main__':
    app.run(
        host=settings.BIND_HOST,
        port=settings.BIND_PORT,
        debug=True
    )
