import os
from storage.storage import Storage
from flask import Flask, request, jsonify
from zk.publisher import ServicePublisher

SERVICE_PORT = int(os.environ['SERVICE_PORT'])
ZK_HOSTS = os.environ['ZK_HOSTS']

app = Flask(__name__)
storage = Storage(
    host=os.environ['DB_HOST'],
    port=int(os.environ['DB_PORT']),
    db=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    passwd=os.environ['DB_PASS']
)


@app.route('/', methods=['GET'])
def index():
    return 'Storage web service up and running!'


@app.route('/visits', methods=['GET'])
def visits():
    last_n = int(request.args.get('n'))
    return jsonify(storage.last_n_visits(last_n))


@app.route('/stats', methods=['POST'])
def stats():
    stats_data = request.get_json()
    storage.insert_statistics(stats_data)
    return jsonify(success=True)


if __name__ == '__main__':
    service_publisher = ServicePublisher(hosts=ZK_HOSTS, timeout=10, publish_port=SERVICE_PORT)
    app.run(host='0.0.0.0', port=SERVICE_PORT)
