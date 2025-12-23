import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';

// Dosya yolunun doğruluğundan emin ol (soa/src içindeysen ../../protos/buca.proto)
const PROTO_PATH = path.resolve(__dirname, '../../protos/buca.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
});

// Proto dosyasını yükle
const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

// Paketsiz yapıda doğrudan servise erişiyoruz
const RealEstateService = (protoDescriptor as any).RealEstateService;

if (!RealEstateService) {
    console.error("❌ gRPC Hata: Proto içindeki RealEstateService yüklenemedi!");
    console.log("Mevcut Descriptor:", protoDescriptor);
    throw new Error("RealEstateService constructor bulunamadı.");
}

// Python gRPC sunucusu varsayılan olarak 50051 portunda çalışır
const client = new RealEstateService(
    '127.0.0.1:50051',
    grpc.credentials.createInsecure()
);

export default client;