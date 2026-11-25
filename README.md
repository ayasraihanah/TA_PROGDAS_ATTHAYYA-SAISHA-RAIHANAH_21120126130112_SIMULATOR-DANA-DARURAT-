# TA_PROGDAS_ATTHAYYA-SAISHA-RAIHANAH_21120126130112_Simulator_Tabungan_dengan_Sistem_Penalti_(SaveQuest)-

SaveQuest - Simulator Tabungan Gamifikasi

Tugas Akhir mata kuliah Teknologi Informasi. 
Aplikasi desktop (Python + tkinter) yang mengubah kebiasaan menabung menjadi game RPG bergaya pixel art.

# 🎮 CONCEPT
# Game Elements — Real-life Adaptation

- **HP Bar**
  - Kesehatan dompet: saldo Dana Darurat dibandingkan dengan targetnya.

- **HEAL**
  - Menabung: HP meningkat dan pemain mendapatkan XP.

- **DAMAGE**
  - Jajan impulsif: HP berkurang dan XP dipotong sebagai penalti.

- **Critical Hit / Heal**
  - Transaksi besar (≥ 10% target) memberikan efek 2x.

- **Boss**
  - Wishlist gadget: menabung untuk menyerang boss sampai HP boss habis.

- **Level & XP**
  - Semakin rajin menabung, semakin tinggi gelar pemain.
  - Gelar: Rookie Saver sampai Legendary Tycoon.

- **Game Over**
  - Dana Darurat habis (HP = 0).

---

# ✨ FITUR PLANNING

- **HP Bar System**
  - HP bar bersegmen dengan 5 hati.
  - Warna berubah sesuai kondisi:
    - 🟢 Hijau
    - 🟡 Kuning
    - 🔴 Merah

- **XP & Level System**
  - Sistem XP, level, dan gelar karakter.

- **Boss Battle**
  - Wishlist gadget berperan sebagai boss.
  - HP boss berkurang setiap kali pemain menabung.

- **Battle Log**
  - Riwayat transaksi dengan indikator warna.

- **Animation & Visual Effects**
  - Bintang berkedip.
  - Hero bergerak naik-turun.
  - Teks melayang.
  - Kilatan layar saat HEAL atau DAMAGE.

- **Auto Save System**
  - Data tersimpan otomatis ke `savedata.json`.
