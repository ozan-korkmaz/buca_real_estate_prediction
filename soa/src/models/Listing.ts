import mongoose, { Schema, Document } from 'mongoose';

// TypeScript Tipleri (Kod yazarken kolaylık için)
export interface IListing extends Document {
    title: string;
    description: string;
    price: number;
    currency: string;
    status: string;
    tags: string[];
    property_specs: {
        gross_m2: number;
        net_m2: number;
        room_count: string;
        floor: number; // veya string olabilir, JSON'da number geldiği için number yaptım
        heating: string;
    };
    location_details: {
        street_name: string;
        site_name?: string;
        coordinates?: {
            lat: number;
            lon: number;
        };
    };
    agency_id?: string;       // Veritabanında string ID olarak duruyor
    neighborhood_id?: string; // Veritabanında string ID olarak duruyor
    created_at?: Date;
}

// Mongoose Şeması (Veritabanı kuralı)
const ListingSchema: Schema = new Schema(
    {
        title: { type: String, required: true },
        description: { type: String },
        price: { type: Number, required: true },
        currency: { type: String, default: 'TRY' },
        status: { type: String, default: 'active' },
        tags: [{ type: String }], // String dizisi

        // İç içe obje: Özellikler
        property_specs: {
            gross_m2: { type: Number },
            net_m2: { type: Number },
            room_count: { type: String },
            floor: { type: Number },
            heating: { type: String }
        },

        // İç içe obje: Konum
        location_details: {
            street_name: { type: String },
            site_name: { type: String },
            coordinates: {
                lat: { type: Number },
                lon: { type: Number }
            }
        },

        agency_id: { type: String },
        neighborhood_id: { type: String }
    },
    { timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' } }
);

// Frontend için _id -> id dönüşümü
ListingSchema.set('toJSON', {
    virtuals: true,
    versionKey: false,
    transform: function (doc, ret) { delete ret._id; }
});

// 'Listings' koleksiyonuna bağlan
export default mongoose.model<IListing>('Listing', ListingSchema, 'Listings');