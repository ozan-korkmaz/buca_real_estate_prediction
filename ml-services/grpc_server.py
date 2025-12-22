from concurrent import futures
import grpc
import time
import buca_pb2
import buca_pb2_grpc

class BucaServicer(buca_pb2_grpc.BucaServiceServicer):
    def HizliFiyatHesapla(self, request, context):
        print(f"⚡ gRPC İsteği Geldi! m2: {request.metrekare}, Yaş: {request.bina_yasi}")
        
        fiyat = (request.metrekare * 25000) - (request.bina_yasi * 5000)
        
        if fiyat < 0:
            fiyat = 0 

        return buca_pb2.HesapResponse(
            tahmini_fiyat=fiyat,
            mesaj="Bu veri Python servisinden gRPC protokolü ile geldi!"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    buca_pb2_grpc.add_BucaServiceServicer_to_server(BucaServicer(), server)
    
    server.add_insecure_port('[::]:50051') 
    print("🚀 gRPC Sunucusu 50051 portunda hazır")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()