from conf import DB_CONFIG
from flask import Flask, request, jsonify, abort
from models import bc10_clients, bc10_oasis, bc10_transactions, run
from db import loadsession, paginate

db_conf = DB_CONFIG

app = Flask(__name__)

#session = loadsession(db_conf)

# add datetimea field into bc10_oasis

@app.route('/', methods=['GET'])
def index():
    endpoints = ['/api/v1/clients', '/api/v1/stat']
    return jsonify({'endpoints': endpoints})

@app.route('/api/v1/clients/<int:oasis_id>', methods=['GET'])
def get_clients(oasis_id=None):
    session = loadsession(db_conf)
    if oasis_id:
        query = session.query(bc10_oasis).filter(bc10_oasis.oasis_id == oasis_id)
        data = query.first()
        result = jsonify({ 'result': []})
    else:
        query = session.query(bc10_oasis).all()
        result = 


if __name__ == '__main__':
    app.run(debug=True, port=8000)


