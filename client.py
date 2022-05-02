import socket
import pickle
import time
import numpy as np
from flask import Flask, request, send_file
from flask_cors import CORS
from server import CLIENT_CONN_TYPE, MAIN_PORT

SERVER_ADDRESS = ('localhost',MAIN_PORT)

app = Flask(__name__)
CORS(app)

@app.route('/',methods=['GET'])
def home():
  return send_file('./index.html')

@app.route('/compute',methods=['POST'])
def compute():
  if(request.method=='POST'):
    try:
      request_data = request.get_json()
      opcode = request_data['opcode']
      data = np.array(request_data['data'])

      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect(SERVER_ADDRESS)
      s.send(str(CLIENT_CONN_TYPE).encode())
      time.sleep(0.0001)
      s.send(pickle.dumps((opcode,data)))
      result = pickle.loads(s.recv(4096))
      s.close()

      return {'result': int(result)}
    except Exception as e:
      print(e)
      return 'Error'

if __name__ == '__main__':
  app.run(debug=True)