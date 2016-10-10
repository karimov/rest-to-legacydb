import datetime

from conf import DB_CONFIG
from flask import Flask, request, jsonify, abort
from models import bc10_clients, bc10_oasis, bc10_transactions
from db import loadsession, page

from sqlalchemy import and_, or_

strptime = '%Y%m%d'

db_conf = DB_CONFIG

PER_PAGE = 10

app = Flask(__name__)

session = loadsession(db_conf)

host = '127.0.0.1'
port = '8000'
_client_url_ = '/api/v1/clients'
_stat_url_ = '/api/v1/stat'

# go to begining of the month

def _month():
    now = datetime.datetime.now().date()
    start = datetime.datetime(now.year, now.month, 1)
    start = start.date().isoformat().replace('-', '')
    end = now.isoformat().replace('-', '')
    return start, end

# add datetimea field into bc10_oasis

# endpoints

@app.route('/', methods=['GET'])
def index():
    endpoints = ['/api/v1/clients', '/api/v1/stat']
    return jsonify({'endpoints': endpoints})

# To get a client object by id

@app.route('/api/v1/clients/<int:oasis_id>', methods=['GET', 'POST'])
def get_client(oasis_id):
    if request.method == 'GET':
        query = session.query(bc10_oasis).filter(bc10_oasis.oasis_id == oasis_id)
        result = query.first()
        if not result:
            return jsonify({ 'result': []})
        else:
            return jsonify({ 'result': [result.serialize]})
    if request.method == 'POST':
        status = request.json.get('status')
        query = session.query(bc10_oasis).filter(bc10_oasis.oasis_id == oasis_id)
        new_oasis = query.first()
        new_oasis.status = status
        new_oasis.bc10_oasis.status = status
        try:
            session.add(new_oasis)
            session.commit()
            return jsonify({'message': True})
        except:
            session.rollback()
            abort(400)

# Paginated output

@app.route('/api/v1/clients', defaults={'p':1})
@app.route('/api/v1/clients/page/<int:p>', methods=['GET'])
def get_cliemts_page(p):
    if request.method == 'GET':
        query =  session.query(bc10_oasis)
        pg = page.Page.paginate(query, p, PER_PAGE)
        items = pg.items
        next_page = pg.next_page
        previous_page = pg.previous_page

        result = {'result': [item.serialize for item in items],
                    'pages': [{ 'next_page':  _client_url_+'/page/'+str(next_page),
                                'prev_page': _client_url_+'/page/'+str(previous_page)
                            }]
                }

        return jsonify(result)


# To create a new client

@app.route('/api/v1/clients', methods=['POST'])
def post_clioents():
    oasis_id = request.json.get('oasis_id')
    oasis_name = request.json.get('oasis_name')
    status = 'active'

    if oasis_id and oasis_name:
        new_client = bc10_clients(name=oasis_name, client_api_url='http', status=status)
        new_oasis = bc10_oasis(oasis_id=oasis_id, oasis_name=oasis_name, bc10_oasis=new_client, status=status)
        try:
            session.add(new_oasis)
            session.commit()
            return jsonify({'message': True})
        except:
            session.rollback()
            abort(400)

# To collect the statistics 

@app.route('/api/v1/stat/<int:oasis_id>', defaults={'from_date': _month()[0], 'to_date': _month()[1], 'p':1 })
@app.route('/api/v1/stat/<int:oasis_id>/<string:from_date>/<string:to_date>/page/<int:p>', methods=['GET'])
def get_stat_p(p,from_date, to_date, oasis_id):
    _id = oasis_id
    _from_date = datetime.datetime.strptime(from_date, strptime)
    _to_date = datetime.datetime.strptime(to_date, strptime)
    oasis = session.query(bc10_oasis).filter(bc10_oasis.oasis_id == _id).first()

    if oasis:
        client_id = oasis.bc10_oasis.client_id
        transactions = session.query(bc10_transactions)
        f = transactions.filter(and_(bc10_transactions.client_id == client_id,
                                bc10_transactions.datetime <= _to_date,
                                bc10_transactions.datetime >= _from_date))

        pg = page.Page.paginate(f, p, PER_PAGE)
        items = pg.items
        next_page = pg.next_page
        previous_page = pg.previous_page

        result = {'result': [item.serialize for item in items],
                    'pages': [{ 'next_page':  _stat_url_+'/'+str(oasis_id)+'/'+str(from_date)+'/'+str(to_date)+'/page/'+str(next_page),
                            'prev_page': _stat_url_+'/'+str(oasis_id)+'/'+str(from_date)+'/'+str(to_date)+'/page/'+str(previous_page)
                        }]
                }

        return jsonify(result)
    else:
        abort(404)



if __name__ == '__main__':
    app.run(debug=True, port=8080)


