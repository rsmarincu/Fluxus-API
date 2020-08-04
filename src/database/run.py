from app.app import create_app
from app.gql.openml_schema import schema
from app import settings

app = create_app(schema)

if __name__ == '__main__':
    app.run(port="8080", host="0.0.0.0")
