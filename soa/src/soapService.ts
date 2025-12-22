import * as soap from 'soap';
import { Express } from 'express';
// Eğer veritabanından çekmek isterseniz Listing modelini import edebilirsiniz
import Listing from './models/Listing'; 


const wsdlXML = `
<definitions name="BucaEmlakService"
             targetNamespace="http://com.buca.emlak/wsdl/BucaEmlakService.wsdl"
             xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="http://com.buca.emlak/wsdl/BucaEmlakService.wsdl"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema">

    <message name="GetListingInfoRequest">
        <part name="listingId" type="xsd:string"/>
    </message>

    <message name="GetListingInfoResponse">
        <part name="price" type="xsd:string"/>
        <part name="info" type="xsd:string"/>
    </message>

    <portType name="RealEstatePort">
        <operation name="getListingInfo">
            <input message="tns:GetListingInfoRequest"/>
            <output message="tns:GetListingInfoResponse"/>
        </operation>
    </portType>

    <binding name="RealEstateBinding" type="tns:RealEstatePort">
        <soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="getListingInfo">
            <soap:operation soapAction="getListingInfo"/>
            <input>
                <soap:body use="encoded" namespace="urn:xmethods-delayed-quotes" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
            </input>
            <output>
                <soap:body use="encoded" namespace="urn:xmethods-delayed-quotes" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
            </output>
        </operation>
    </binding>

    <service name="BucaEmlakService">
        <port name="RealEstatePort" binding="tns:RealEstateBinding">
            <soap:address location="http://localhost:5001/soap/buca"/>
        </port>
    </service>
</definitions>
`;


const serviceObject = {
    BucaEmlakService: {
        RealEstatePort: {
            getListingInfo: function(args: { listingId: string }, callback: any) {
                console.log('SOAP İsteği Alındı. Listing ID:', args.listingId);

                // NOT: Burada normalde await Listing.findById(args.listingId) yapılır.
                // Projeyi bozmamak için şimdilik örnek veri dönüyoruz.
                
                const responseData = {
                    price: "4.500.000 TL",
                    info: `Buca'daki ${args.listingId} numaralı ilan için SOAP servisi cevap verdi.`
                };

                // callback(hata, cevap)
                callback(null, responseData);
            }
        }
    }
};


export const initSoapService = (app: Express) => {
    soap.listen(app, '/soap/buca', serviceObject, wsdlXML, function(){
      console.log('📢 SOAP Servisi Başlatıldı!');
      console.log('   WSDL Adresi: http://localhost:5001/soap/buca?wsdl');
    });
};