import * as soap from "soap";
import path from "path";
import fs from "fs";
import Listing from "../models/Listing";

export const startListingSoapService = (app: any) => {
  try {

    // WSDL dosyasını string olarak okuyoruz
    const wsdlPath = path.resolve(__dirname, "listing.wsdl");
    
    if (!fs.existsSync(wsdlPath)) {
        console.error("🚨 HATA: listing.wsdl dosyası bu yolda bulunamadı:", wsdlPath);
        return;
    }

    const wsdlXML = fs.readFileSync(wsdlPath, "utf8");

    const service = {
      ListingService: {
        ListingPort: {
          GetListingById: async (args: any) => {
            console.log("DEBUG: GetListingById tetiklendi, ID:", args.listingId);
            try {
              const listing = await Listing.findById(args.listingId).lean();
              if (!listing) return { Fault: { code: "Server", string: "Listing not found" } };

              return {
                id: listing._id.toString(),
                title: listing.title,
                price: Number(listing.price),
                street: (listing as any).location_details?.street_name || "No address",
                description: listing.description || ""
              };
            } catch (err: any) {
              return { Fault: { code: "Server", string: err.message } };
            }
          }
        }
      }
    };

    soap.listen(app, "/soap/listing", service, wsdlXML, () => {
      console.log("🚀 SOAP Servisi Hazır ve WSDL yüklendi!");
    });

  } catch (error) {
    console.error("🚨 SOAP Başlatma Hatası:", error);
  }
};