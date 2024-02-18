from flask import Flask, request, jsonify
import pika
import threading
import json
import os, requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.auth_svc_address = os.getenv('AUTH_SVC_ADDRESS')
# how to handle
privilege={
    "admin":{"edit":True,"view":True,"update":True,"delete":True},
    "user":{"edit":False,"view":True,"update":False,"delete":False},
    }

item_list =[]
# Establish a connection to RabbitMQ using a separate thread
def connect_to_rabbit():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='demo.bar.item.add')
    return channel

# Callback function to handle incoming messages
def callback(ch, method, properties, body):
    global item_list
    json_obj = json.loads(body)
    itm = json_obj["item"]
    item_list.append(itm)
    print(item_list)
    print(f" [x] Received {body}")

# Start the consumer in a separate thread, using a non-blocking connection
def run_consumer():
    channel = connect_to_rabbit()  # Get the channel within the thread
    channel.basic_consume(queue='demo.bar.item.add', on_message_callback=callback, auto_ack=True)
    print(" [*] Waiting for messages. To exit, press Ctrl+C")
    channel.start_consuming()

rabbitmq_thread = threading.Thread(target=run_consumer)
rabbitmq_thread.start()

@app.route('/',methods=['GET'])
def hello():
    return 'Hello, Wod!'

@app.route('/item',methods=['GET'])
def item():
    return jsonify({"item":item_list})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
