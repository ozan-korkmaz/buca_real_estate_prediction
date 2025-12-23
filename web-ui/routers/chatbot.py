import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"]
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("UYARI: GEMINI_API_KEY .env dosyasında bulunamadı! Chatbot çalışmayabilir.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
]

# Model Ayarları
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    generation_config=generation_config,
    safety_settings=SAFETY_SETTINGS
)

SYSTEM_INSTRUCTION = """
Sen Buca Emlak Tahmin Sistemi'nin yapay zeka asistanısın. 
İsmin 'Buca Emlak Asistanı'.
Görevin: Kullanıcılara İzmir Buca bölgesindeki emlak fiyatları, yaşam koşulları, ulaşım ve genel emlak piyasası hakkında yardımcı olmak.
Özelliklerin:
1. Kibar, yardımsever ve Türkçeyi düzgün kullanan bir dille konuş.
2. Sadece emlak, konut, Buca bölgesi ve proje ile ilgili sorulara cevap ver.
3. Eğer kullanıcı alakasız bir konu sorarsa, kibarca sadece emlak konularında yardımcı olabileceğini belirt.
4. Cevapların çok uzun olmasın, özet ve anlaşılır olsun.
"""

class ChatRequest(BaseModel):
    message: str

@router.post("/ask")
async def ask_gemini(request: ChatRequest):
    """
    Frontend'den gelen mesajı alır, Gemini'ye iletir ve cevabı döndürür.
    """
    try:
        if not GEMINI_API_KEY:
             return {"response": "Sistem hatası: API Key bulunamadı."}

        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nKullanıcı: {request.message}\nAsistan:"
        
        response = model.generate_content(full_prompt)
        
        try:
            return {"response": response.text}
        except ValueError:
            # Eğer model cevabı filtrelediyse veya boş döndüyse
            print(f"Gemini Cevap Üretemedi. Feedback: {response.prompt_feedback}")
            return {"response": "Üzgünüm, bu sorunuza şu an cevap veremiyorum (Güvenlik filtresi veya teknik bir sınır). Lütfen sorunuzu farklı bir şekilde sorunuz."}

    except Exception as e:
        print(f"Genel Chatbot Hatası: {e}")
        return {"response": "Üzgünüm, şu an bağlantıda bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin."}