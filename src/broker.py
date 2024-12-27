from flask import Flask, request, jsonify
import uuid

class Peer:

    def __init__(self, port, ip, id):
        self.port = port
        self.ip = ip
        self.id = id
        self.isReady = False
    
    def jsonify(self):
        return {"port": self.port, "ip": self.ip, "id": str(self.id), "isReady": self.isReady}
        

app = Flask(__name__)

# In-memory storage for registered peers
peers = []



@app.route('/reg', methods=['POST'])
def register():
    data = request.json
    ip = request.remote_addr
    id = uuid.uuid4()
    peers.append(Peer(data['port'], ip, id))
    print(json_peers())
    return jsonify({'message': 'Peer registered successfully', 'id': id})

@app.route('/peers', methods=['GET'])
def get_peers():
    return json_peers()

@app.route('/status/<string:connect_id>', methods=['GET'])
def get_status(connect_id):

    for peer in peers:
        if str(peer.id) == connect_id:
            return peer.jsonify(), 200

    response = jsonify(message="Peer is not ready for connection")
    return response, 204
    


def json_peers():
    json = []
    for peer in peers:
        json.append(peer.jsonify())
    return json

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)