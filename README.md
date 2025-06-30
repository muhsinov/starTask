# Startask

`Startask` — bu kompaniyalar ichidagi ishlarni boshqarish (To-Do) tizimi.  
FastAPI, PostgreSQL, Docker, va AWS EC2 texnologiyalari yordamida qurilgan.

---

## ✨ Xususiyatlar

- Bosh manager kompaniya yaratadi
- Ishchilar va bo‘limlar qo‘shiladi
- Har bir bo‘lim yoki ishchiga tasklar beriladi
- JWT token asosida autentifikatsiya
- Docker + GitHub Actions orqali CI/CD

---

## 🚀 Ishga tushirish (lokalda)

```bash
# virtual muhit yaratish
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# kutubxonalarni o‘rnatish
pip install -r requirements.txt

# serverni ishga tushurish
uvicorn app.main:app --reload
