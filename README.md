

```md
# 🏠 Buca Emlak Fiyat Tahmin ve Yönetim Sistemi

> İzmir Buca bölgesine ait emlak verilerini analiz eden, makine öğrenmesi ile fiyat tahmini yapan ve kullanıcıların ilan yönetimi yapabildiği, mikroservis tabanlı tam kapsamlı bir web uygulaması.

---

## 📑 İçindekiler

1. Proje Özeti  
2. Özellikler  
3. Sistem Mimarisi  
4. Teknoloji Yığını  
5. Klasör Yapısı  
6. Makine Öğrenmesi Süreci  
7. Kurulum ve Çalıştırma  
   - Veritabanı  
   - ML Servisi (gRPC)  
   - Backend API (SOA)  
   - Web Arayüzü  
8. Kullanım Senaryosu  
9. API Uç Noktaları  
10. Katkıda Bulunma  
11. Lisans  
12. İletişim  

---

## 🔎 Proje Özeti

Bu proje, Buca (İzmir) bölgesindeki emlak ilanlarını analiz etmek, fiyat tahmini yapmak ve kullanıcıların ilanlarını yönetmesini sağlamak amacıyla geliştirilmiştir.  

Sistem; veri kazıma, makine öğrenmesi, servis odaklı mimari (SOA) ve web arayüzünü tek bir çatı altında birleştirir. Ölçeklenebilir, modüler ve gerçek dünya projelerine uygun bir yapı hedeflenmiştir.

---

## ✨ Özellikler

- 🔍 Yapay zeka destekli anlık fiyat tahmini  
- 📊 Mahalle ve sokak bazlı istatistikler  
- 🔐 Kullanıcı kayıt, giriş ve yetkilendirme  
- 📝 İlan ekleme, düzenleme ve listeleme  
- 🤖 Entegre AI chatbot  
- 🗺️ Konum bazlı gelişmiş filtreleme  

---

## 🏗 Sistem Mimarisi

Proje, hibrit mikroservis (SOA) mimarisi ile tasarlanmıştır:

- **Data Scraper (Python)**  
  Emlak verilerini toplayan özel veri kazıma aracı

- **ML Servisi (gRPC)**  
  Eğitilmiş makine öğrenmesi modellerini barındıran ve fiyat tahmini yapan servis

- **Backend API (Node.js / TypeScript)**  
  İş mantığı, kullanıcı yönetimi ve ML servisi ile haberleşme

- **Web UI (FastAPI)**  
  Kullanıcının sistemle etkileşime girdiği ön yüz

---

## 🛠 Teknoloji Yığını

| Katman | Teknolojiler |
|------|-------------|
| Makine Öğrenmesi | Python, Pandas, NumPy, Scikit-learn, XGBoost |
| RPC | gRPC, Protobuf |
| Backend | Node.js, TypeScript, Express, Mongoose |
| Web | FastAPI, Jinja2, HTML, CSS |
| Veritabanı | MongoDB |
| Araçlar | Git, VS Code, PyCharm |

---

## 📂 Klasör Yapısı

```

buca_real_estate_prediction/
├── data/
├── database/
├── ml-services/
├── protos/
├── scraper/
├── soa/
├── web-ui/
└── README.md

````

---

## 🧠 Makine Öğrenmesi Süreci

1. Veri temizleme  
2. Özellik seçimi  
3. Veri hazırlama  
4. 10+ algoritma ile model eğitimi  
5. En iyi model: **Ridge Regression**  
6. Model, gRPC servisi ile yayına alınır  

---

## 🚀 Kurulum ve Çalıştırma

### Ön Koşullar

- Python 3.10+  
- Node.js & npm  
- MongoDB  

### 1️⃣ Veritabanı

```bash
mongorestore --db realEstateDb ./database/realEstateDb
````

### 2️⃣ ML Servisi

```bash
cd ml-services
pip install -r requirements.txt
python grpc_server.py
```

### 3️⃣ Backend API

```bash
cd soa
npm install
npm run dev
```

### 4️⃣ Web Arayüzü

```bash
cd web-ui
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 📈 Kullanım Senaryosu

* Kullanıcı kayıt olur ve giriş yapar
* İlan ekler veya listeleri görüntüler
* Yapay zeka destekli fiyat tahmini alır
* Bölgesel analizleri inceler

---

## 🔌 API Uç Noktaları (Örnek)

```
POST   /auth/register
POST   /auth/login
GET    /listings
POST   /listings
POST   /predict
```

---

## 🤝 Katkıda Bulunma

1. Repo forkla
2. Feature branch oluştur
3. Commit at
4. Pull Request aç

---

## 📄 Lisans

MIT Lisansı

---

## 📬 İletişim

Geliştirici: **Ozan Korkmaz**
E-posta: [ozankorkmaz.dev@gmail.com](mailto:ozankorkmaz.dev@gmail.com)
GitHub: [https://github.com/ozan-korkmaz](https://github.com/ozan-korkmaz)

---

---

# 🏠 Buca Real Estate Price Prediction & Management System

> A full-stack, microservice-based web application that analyzes real estate data in the Buca (Izmir) region and predicts property prices using machine learning models.

---

## 📑 Table of Contents

1. Project Overview
2. Features
3. System Architecture
4. Tech Stack
5. Folder Structure
6. Machine Learning Pipeline
7. Installation & Setup
8. Usage
9. API Endpoints
10. Contributing
11. License
12. Contact

---

## 🔎 Project Overview

This project provides an end-to-end real estate platform combining data scraping, machine learning, SOA backend architecture, and a web-based user interface.

---

## ✨ Features

* AI-powered real-time price prediction
* Neighborhood-based analytics
* User authentication & authorization
* Property listing management
* Integrated AI chatbot
* Advanced location-based filtering

---

## 🏗 System Architecture

* Data Scraper (Python)
* ML Service (gRPC)
* Backend API (Node.js / TypeScript)
* Web UI (FastAPI)

---

## 🛠 Tech Stack

| Layer    | Technologies                                 |
| -------- | -------------------------------------------- |
| ML       | Python, Pandas, NumPy, Scikit-learn, XGBoost |
| RPC      | gRPC, Protobuf                               |
| Backend  | Node.js, TypeScript, Express                 |
| Frontend | FastAPI, Jinja2                              |
| Database | MongoDB                                      |

---

## 📂 Folder Structure

```
buca_real_estate_prediction/
├── data/
├── database/
├── ml-services/
├── protos/
├── scraper/
├── soa/
├── web-ui/
```

---

## 🧠 Machine Learning Pipeline

* Data cleaning
* Feature selection
* Model training (10+ algorithms)
* Best model: Ridge Regression
* Served via gRPC

---

## 🚀 Installation & Setup

Steps are identical to the Turkish section above.

---

## 📈 Usage

* Register & login
* Add property listings
* Get AI price predictions
* Explore analytics

---

## 🔌 API Endpoints

```
POST /auth/register
POST /auth/login
GET  /listings
POST /predict
```

---

## 🤝 Contributing

Fork → Branch → Commit → Pull Request

---

## 📄 License

MIT License

---

## 📬 Contact

Developer: **Berat Zengin**
GitHub: [https://github.com/devberatzengin](https://github.com/devberatzengin)

Developer: **Mehmet Bozkurt**
GitHub: [https://github.com/mehmetbozkurt0](https://github.com/mehmetbozkurt0)

Developer: **Ozan Korkmaz**
GitHub: [https://github.com/ozan-korkmaz](https://github.com/ozan-korkmaz)

```

---

Istersen bir sonraki seviyeye gecelim:
- Swagger / OpenAPI dokumani  
- Docker + docker-compose  
- CI/CD badge ve pipeline  
- Akademik rapor / sunum  

Bu repo artik **“ders projesi” degil, portfolio projesi** seviyesinde. 🔥
```
