from app import app
from waitress import serve


serve(app, host='127.0.0.1', port=8181)




