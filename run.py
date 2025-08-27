from app import create_app
from app.database import  create_table_if_not_exists

app = create_app()
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
