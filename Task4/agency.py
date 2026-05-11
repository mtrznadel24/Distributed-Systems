import uuid
import pika
import json
import threading


class Agency:
    def __init__(self, name):
        self.name = name
        self.keys = {"1": "task.personnel", "2": "task.cargo", "3": "task.satellite"}

        self.consume_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.consume_channel = self.consume_connection.channel()
        self.consume_channel.exchange_declare(exchange='space_exchange', exchange_type='topic')

        result = self.consume_channel.queue_declare(queue='', exclusive=True)
        self.reply_queue_name = result.method.queue

        self.consume_channel.queue_bind(exchange='space_exchange', queue=self.reply_queue_name,
                                        routing_key=f'ack.{self.name}')
        self.consume_channel.queue_bind(exchange='space_exchange', queue=self.reply_queue_name,
                                        routing_key='admin.agency')
        self.consume_channel.queue_bind(exchange='space_exchange', queue=self.reply_queue_name, routing_key='admin.all')

        self.publish_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.publish_channel = self.publish_connection.channel()
        self.publish_channel.exchange_declare(exchange='space_exchange', exchange_type='topic')

    def on_callback(self, ch, method, properties, body):
        response = json.loads(body)

        if response.get("sender") == "ADMIN":
            print(f"\nADMIN: {response.get('message')}")
        else:
            print(f"\n System confirm: Task #{response['task_id']} completed by carrier!")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Select task type (1-3): ", end="", flush=True)

    def start_listening(self):
        self.consume_channel.basic_consume(
            queue=self.reply_queue_name,
            on_message_callback=self.on_callback
        )

        thread = threading.Thread(target=self.consume_channel.start_consuming)
        thread.daemon = True
        thread.start()

    def send_task(self, task_type):
        task_id = str(uuid.uuid4())[:8]
        routing_key = self.keys.get(task_type)

        if not routing_key:
            print("Invalid task type! Please select 1, 2, or 3.")
            return

        payload = {
            "agency": self.name,
            "task_id": task_id,
            "type": routing_key.split('.')[1]
        }

        self.publish_channel.basic_publish(
            exchange='space_exchange',
            routing_key=routing_key,
            body=json.dumps(payload)
        )
        print(f"Dispatched: {payload['type']} (Task ID: {task_id})")


if __name__ == '__main__':
    agency_name = input("Enter Agency name: ")

    agency = Agency(agency_name)
    agency.start_listening()

    while True:
        print("\n--- Dispatch Task ---")
        print("1 - Personnel transport")
        print("2 - Cargo transport")
        print("3 - Satellite placement")

        task = input("Select task type (1-3): ")
        agency.send_task(task)