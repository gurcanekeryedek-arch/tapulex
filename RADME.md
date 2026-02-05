# 🏛️ TapuLex

**TapuLex**, Tapu ve Kadastro işlemleriyle ilgili **kanun, yönetmelik, tebliğ, genelge ve resmi uygulamalara dayalı** olarak çalışan,  
**yapay zekâ destekli bir rehber ve danışman chatbotudur**.

TapuLex, mevzuat dışına çıkmadan, referanslı ve kontrollü cevaplar üretmeyi hedefler.

---

## 🎯 Projenin Amacı

Tapu ve Kadastro süreçleri;
- Karmaşık mevzuat
- Sık değişen uygulamalar
- Yanlış yorumlanmaya açık hükümler

nedeniyle hem vatandaşlar hem de kurum çalışanları için zorlayıcıdır.

**TapuLex**, bu karmaşıklığı azaltmak için:
- Mevzuata dayalı bilgi sunar
- Yanlış yönlendirmeyi engeller
- “Bilmiyorsam bilmiyorum” prensibiyle çalışır

---

## ✨ Temel Özellikler

- ⚖️ **Mevzuat Odaklı Yapay Zekâ**
  - Tapu Kanunu
  - Kadastro mevzuatı
  - İkincil düzenlemeler (yönetmelik, tebliğ, genelge)

- 📚 **RAG (Retrieval-Augmented Generation) Mimari**
  - Sadece yüklenen ve doğrulanmış dokümanlara dayanır
  - Halüsinasyon riskini minimize eder

- 🧠 **Kontrollü Yanıt Mekanizması**
  - Belge yoksa cevap vermez
  - Gerekirse “Bu konuda mevzuatta açık hüküm bulunmamaktadır” der

- 🔐 **KVKK ve Veri Güvenliği Odaklı**
  - Kişisel veri işlemez
  - Kullanıcı oturumları izole çalışır

- 🏢 **Kurum İçi ve Vatandaş Odaklı Kullanım**
  - İç destek botu
  - Bilgilendirme ve yönlendirme aracı

---

## 🧱 Teknik Mimari (Özet)

- **Backend:** Python (FastAPI)
- **AI Model:** OpenAI API (GPT-4o-mini)
- **Veritabanı:** Supabase (PostgreSQL + pgvector)
- **Vektörleme:** Chunk + Embedding tabanlı
- **Prompt Güvenliği:** Sistem + Guardrail Prompt

---

## 🔍 Çalışma Prensibi

1. Mevzuat dokümanları sisteme yüklenir
2. Dokümanlar parçalara (chunk) ayrılır
3. Vektör veritabanına kaydedilir
4. Kullanıcı soru sorar
5. Soru sadece ilgili dokümanlarla eşleştirilir
6. Cevap **yalnızca bu içeriklerden** üretilir

---

## ⚠️ Hukuki Uyarı

> **TapuLex bir hukuki danışmanlık hizmeti değildir.**  
> Üretilen yanıtlar bilgilendirme amaçlıdır.  
> Bağlayıcı ve resmi görüş niteliği taşımaz.  
> Nihai işlemler için ilgili idare ve mevzuat esas alınmalıdır.

---

## 🧭 İsim Anlamı

**TapuLex = Tapu + Lex (Hukuk)**

Latince *Lex*, “kanun” anlamına gelir.  
TapuLex, tapu ve kadastro mevzuatında **referans noktası** olmayı hedefler.

---

