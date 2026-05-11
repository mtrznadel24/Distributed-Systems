const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const packageDefinition = protoLoader.loadSync('../proto/schema.proto');
const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

const infoClient = new protoDescriptor.InfoService('localhost:8080', grpc.credentials.createInsecure());
const streamClient = new protoDescriptor.StreamService('localhost:8080', grpc.credentials.createInsecure());

for (let i = 1; i < 11; i++) {
    infoClient.ComputeSquare({ number: i }, (error, response) => {
        if (error) {
            console.error(error);
        } else {
            console.log(`Server ${response.serverId}, Square: ${response.result}, Time: ${response.currentTime}`);
        }
});
}

const stream = streamClient.MonitorServerUsage({});

stream.on('data', (data) => {
    console.log(`Server ${data.serverId}, Usage: ${data.usage}, Time: ${data.currentTime}`);
});

stream.on('end', () => {
    console.log("Stream stopped.");
});
