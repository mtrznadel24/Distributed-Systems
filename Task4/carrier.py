import pika
import json

def choose_services():
    options = {
        "1": "queue_personnel",
        "2": "queue_cargo",
        "3": "queue_satellite"
    }

    while True:
        print("1 - Personnel transport")
        print("2 - Cargo transport")
        print("3 - Satellite placement")

        choice = input("Select two services (enter numbers separated by space, e.g., '1 2'): ")
        selected = choice.split()

        if len(selected) == 2 and selected[0] in options and selected[1] in options:
            if selected[0] == selected[1]:
                print("You selected the same service twice. Try again.")
                continue

            return [options[selected[0]], options[selected[1]]]
        else:
            print("Invalid format. Enter two numbers separated by a space, from 1 to 3.")


class Carrier:
    def __init__(self, services):
        self.services = services

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='space_exchange', exchange_type='topic')

        tasks_config = {
            'queue_personnel': 'task.personnel',
            'queue_cargo': 'task.cargo',
            'queue_satellite': 'task.satellite'
        }

        for queue_name, routing_key in tasks_config.items():
            self.channel.queue_declare(queue=queue_name)
            self.channel.queue_bind(exchange='space_exchange', queue=queue_name, routing_key=routing_key)

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.admin_queue_name = result.method.queue

        self.channel.queue_bind(exchange='space_exchange', queue=self.admin_queue_name, routing_key='admin.carrier')
        self.channel.queue_bind(exchange='space_exchange', queue=self.admin_queue_name, routing_key='admin.all')

    def on_callback(self, ch, method, properties, body):
        request_data = json.loads(body)

        if request_data.get("sender") == "ADMIN":
            print(f"\nADMIN: {request_data.get('message')}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        agency_name = request_data.get("agency")
        task_id = request_data.get("task_id")
        task_type = request_data.get("type")

        print(f"\nReceived task #{task_id} ({task_type}) from {agency_name}.")

        reply_routing_key = f"ack.{agency_name}"
        reply_message = {
            "status": "done",
            "task_id": task_id,
            "message": f"Carrier completed task {task_type}"
        }

        ch.basic_publish(
            exchange='space_exchange',
            routing_key=reply_routing_key,
            body=json.dumps(reply_message)
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_listening(self):
        self.channel.basic_qos(prefetch_count=1)

        for service in self.services:
            self.channel.basic_consume(
                queue=service,
                on_message_callback=self.on_callback
            )

        self.channel.basic_consume(
            queue=self.admin_queue_name,
            on_message_callback=self.on_callback
        )

        print('\n Waiting for tasks...')
        self.channel.start_consuming()


if __name__ == '__main__':
    services = choose_services()

    carrier = Carrier(services)

    try:
        carrier.start_listening()
    except KeyboardInterrupt:
        print("\nCarrier shut down. Disconnected from RabbitMQ.")