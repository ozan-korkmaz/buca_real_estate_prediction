import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';

const PROTO_PATH = path.join(__dirname, '../../protos/buca.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
});

const bucaProto: any = grpc.loadPackageDefinition(packageDefinition).bucapackage;


export const grpcClient = new bucaProto.BucaService(
    'localhost:50051', 
    grpc.credentials.createInsecure()
);