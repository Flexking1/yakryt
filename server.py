import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Разрешаем фронтенду отправлять запросы на бэкенд (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретный адрес твоего сайта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- НАСТРОЙКА SMTP ДЛЯ GMAIL ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "nikitapilman556@gmail.com"  # Твоя почта (строго латиницей!)
SMTP_PASSWORD = "tdsk whdr qbog gwoz"

# Временное хранилище кодов в памяти сервера (в реальных проектах используют Redis/БД)
verification_codes = {}

class EmailRequest(BaseModel):
    email: EmailStr

class VerifyRequest(BaseModel):
    email: EmailStr
    code: str

def send_smtp_email(to_email: str, code: str):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = "🔐 Код авторизации NEON SHOP"

    body = f"""
    <html>
        <body style="background-color: #06060c; color: #ffffff; font-family: sans-serif; padding: 20px; text-align: center;">
            <h2 style="color: #ff0055;">NEON SHOP</h2>
            <p style="font-size: 16px;">Ваш одноразовый код для входа в систему:</p>
            <div style="background: #111122; border: 2px solid #00ffcc; display: inline-block; padding: 15px 30px; font-size: 24px; font-weight: bold; color: #00ffcc; letter-spacing: 5px; border-radius: 8px; margin: 20px 0;">
                {code}
            </div>
            <p style="color: #888; font-size: 12px;">Если вы не запрашивали этот код, просто проигнорируйте письмо.</p>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка отправки почты: {str(e)}")

@app.post("/api/send-code")
async def send_code(data: EmailRequest):
    # Генерируем 4-значный код
    code = str(random.randint(1000, 9999))
    verification_codes[data.email] = code
    
    # Отправляем на почту
    send_smtp_email(data.email, code)
    return {"status": "success", "message": "Код отправлен"}

@app.post("/api/verify-code")
async def verify_code(data: VerifyRequest):
    if data.email in verification_codes and verification_codes[data.email] == data.code:
        # Удаляем код после успешной проверки
        del verification_codes[data.email]
        return {"status": "success", "message": "Авторизация успешна"}
    else:
        raise HTTPException(status_code=400, detail="Неверный или устаревший код")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="Flexking1.github.io")