import grpc
import time
import socket
import psutil
import random
from concurrent import futures
from datetime import datetime

import schema_pb2
import schema_pb2_grpc

class Server(schema_pb2_grpc.InfoServiceServicer, schema_pb2_grpc.StreamServiceServicer):

    def ComputeSquare(self, request, context):
        print("Received ComputeSquare request")
        delay = random.uniform(1, 5) 
        time.sleep(delay)
        number = request.number
        result = number * number
        return schema_pb2.MathResponse(
            server_id=socket.gethostname(),
            result=result,
            current_time=datetime.now().strftime("%H:%M:%S")
        )

    def MonitorServerUsage(self, request, context):
        print("Received MonitorServerUsage request")
        while True:
            cpu_usage = psutil.cpu_percent(interval=None)
            ram_usage = psutil.virtual_memory().percent
            usage = f"CPU: {cpu_usage}%, RAM: {ram_usage}%"

            yield schema_pb2.UsageResponse(
                server_id=socket.gethostname(),
                usage=usage,
                current_time=datetime.now().strftime("%H:%M:%S")
            )
            time.sleep(3)

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    schema_pb2_grpc.add_InfoServiceServicer_to_server(Server(), server)
    schema_pb2_grpc.add_StreamServiceServicer_to_server(Server(), server)

    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()