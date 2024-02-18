from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os, requests
import json
import pika

load_dotenv()
try:
    # Establish a connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
except pika.exceptions.AMQPError as e:
    print(f"RabbitMQ error: {e}")


app = Flask(__name__)
app.auth_svc_address = os.getenv('AUTH_SVC_ADDRESS')


item_list=[]

privilege={
    "admin":{"edit":True,"view":True,"update":True,"delete":True},
    "user":{"edit":False,"view":True,"update":False,"delete":False},
    }

@app.route('/foo', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    
    response = requests.post(
        f"http://{app.auth_svc_address}/validate",
        headers={"Authorization": token},
    )
   
    if response.status_code != 200:
        return 'not authorized', 403
    else:
        return jsonify({"foo":"bar"})
    

@app.route('/item', methods=['POST'])
def add_item():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    
    if request.method != 'POST' or request.is_json == False:
        return jsonify({'error': 'Invalide data format'}), 401
    
    response = requests.post(
        f"http://{app.auth_svc_address}/validate",
        headers={"Authorization": token},
    )
   
    if response.status_code == 200:
        response_data = json.loads(response.text)
         # Access the 'role' key
        role_value = response_data.get('role')

        if privilege[role_value]["edit"]:
            # Declare a queue
            data = request.get_json()
            value = data.get('item')
            item_list.append(value)
            
            channel.basic_publish(
            exchange="",
            routing_key="demo.bar.item.add",
            body=json.dumps(data,separators=(',', ':')),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),)

            data["success"]= True
            return jsonify(data)
        else:
            return 'not authorized', 403
    else:
        return 'not authorized', 403

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
