import pika
import threading
import json


class Admin:
    def __init__(self):
        self.consume_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.consume_channel = self.consume_connection.channel()
        self.consume_channel.exchange_declare(exchange='space_exchange', exchange_type='topic')

        result = self.consume_channel.queue_declare(queue='', exclusive=True)
        self.listen_queue = result.method.queue
        self.consume_channel.queue_bind(exchange='space_exchange', queue=self.listen_queue, routing_key='#')

        self.publish_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.publish_channel = self.publish_connection.channel()
        self.publish_channel.exchange_declare(exchange='space_exchange', exchange_type='topic')

    def on_callback(self, ch, method, properties, body):
        data = json.loads(body)
        routing_key = method.routing_key

        if routing_key.startswith('admin.'):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"\nReceived message on key '{routing_key}': {data}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Select target (1-Agencies, 2-Carriers, 3-All): ", end="", flush=True)

    def start_listening(self):
        self.consume_channel.basic_consume(queue=self.listen_queue, on_message_callback=self.on_callback)
        thread = threading.Thread(target=self.consume_channel.start_consuming)
        thread.daemon = True
        thread.start()

    def broadcast(self, target_choice, message):
        keys = {"1": "admin.agency", "2": "admin.carrier", "3": "admin.all"}
        routing_key = keys.get(target_choice)

        if not routing_key:
            print("Invalid target!")
            return

        payload = {"sender": "ADMIN", "message": message}

        self.publish_channel.basic_publish(
            exchange='space_exchange',
            routing_key=routing_key,
            body=json.dumps(payload)
        )
        print(f"Broadcast sent on key: {routing_key}")


if __name__ == '__main__':
    admin = Admin()
    admin.start_listening()

    while True:
        print("\n--- Admin Broadcast ---")
        print("1 - To Agencies")
        print("2 - To Carriers")
        print("3 - To All")

        choice = input("Select target (1-3): ")
        msg = input("Enter message: ")
        admin.broadcast(choice, msg)