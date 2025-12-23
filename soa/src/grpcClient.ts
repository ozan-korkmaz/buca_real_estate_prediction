import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';

const PROTO_PATH = path.resolve(__dirname, '../../protos/buca.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
});

const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

const RealEstateService = (protoDescriptor as any).RealEstateService;

if (!RealEstateService) {
    console.error("❌ gRPC Hata: Proto içindeki RealEstateService yüklenemedi!");
    console.log("Mevcut Descriptor:", protoDescriptor);
    throw new Error("RealEstateService constructor bulunamadı.");
}

const client = new RealEstateService(
    '127.0.0.1:50051',
    grpc.credentials.createInsecure()
);

export default client;