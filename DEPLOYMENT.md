# Production Deployment Guide

## O'zgarishlar

Botingiz endi production-ready:

- ✅ **Error Handling**: Barcha xatolar ushlangan, bot crash bo'lmaydi
- ✅ **Graceful Shutdown**: To'g'ri to'xtash mexanizmi
- ✅ **File Logging**: Barcha loglar `logs/` papkada saqlanadi
- ✅ **Auto-Restart**: Docker yoki systemd orqali avtomatik qayta ishga tushish
- ✅ **Health Monitoring**: Bot holatini tekshirish
- ✅ **Deployment Scripts**: Oson deploy va backup

## Tezkor Boshlanish

### Docker bilan (tavsiya etiladi)

```bash
# Botni ishga tushirish
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f

# Botni to'xtatish
docker-compose down

# Qayta ishga tushirish
docker-compose restart
```

### Deploy qilish

```bash
# Yangilanish va deploy
./deployment/deploy.sh
```

### Backup

```bash
# Manual backup
./deployment/backup.sh

# Cron job uchun (har kuni 03:00 da)
0 3 * * * cd /home/shukurjon/projects/botrobo && ./deployment/backup.sh
```

## Serverga O'rnatish

### 1. Docker bilan (oson)

```bash
# Project papkasiga o'ting
cd /home/shukurjon/projects/botrobo

# .env faylni sozlang (allaqachon bor)
# BOT_TOKEN, DB_NAME, ADMIN_IDS

# Ishga tushiring
docker-compose up -d

# Loglarni kuzating
docker-compose logs -f
```

### 2. Systemd bilan (Docker siz)

```bash
# Virtual environment yarating
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database migration
alembic upgrade head

# Systemd service o'rnating
sudo cp deployment/botrobo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable botrobo
sudo systemctl start botrobo

# Statusni tekshiring
sudo systemctl status botrobo

# Loglarni ko'ring
sudo journalctl -u botrobo -f
```

## Monitoring

### Status tekshirish

```bash
# Health check
python healthcheck.py

# Status fayl
cat logs/bot_status.txt

# Docker status
docker-compose ps
```

### Logs

Loglar `logs/` papkada:
- `bot.log` - barcha loglar
- `error.log` - faqat xatolar
- `bot_status.txt` - bot holati

```bash
# Oxirgi 100 qator
tail -100 logs/bot.log

# Xatolarni ko'rish
tail -100 logs/error.log

# Real-time monitoring
tail -f logs/bot.log
```

## Muammolarni Hal Qilish

### Bot ishga tushmayapti

```bash
# Loglarni tekshiring
docker-compose logs --tail=100

# yoki
cat logs/error.log

# .env faylni tekshiring
cat .env

# Database migration
docker-compose exec app alembic upgrade head
```

### Bot to'xtab qoldi

```bash
# Qayta ishga tushirish
docker-compose restart

# Status
docker-compose ps

# Health check
docker-compose exec app python healthcheck.py
```

### Internet uzildi

Bot avtomatik ravishda qayta ulanishga harakat qiladi. Loglarni kuzating:

```bash
docker-compose logs -f | grep -i "network\|error\|retry"
```

## Xavfsizlik

- ✅ `.env` fayl gitda yo'q
- ⚠️ Bot tokenini hech qachon share qilmang
- ⚠️ Serverda firewall sozlang
- ⚠️ Regular backup oling

## Foydali Buyruqlar

```bash
# Resource usage
docker stats botrobo_app

# Disk usage
du -sh logs/ data/ backups/

# Clean old logs
find logs/ -name "*.log.*" -mtime +7 -delete

# Database backup
cp data/bot_v2.sqlite3 data/backup_$(date +%Y%m%d).sqlite3
```

## Avtomatlashtirilgan Deploy (GitHub Actions)

Kodni har safar `main` branchga push qilganingizda server avtomatik yangilanishi uchun GitHub Actions o'rnatildi.

### Sozlash qadamlari:

1.  GitHub-dagi repository-ingizga kiring (`Settings` -> `Secrets and variables` -> `Actions`).
2.  Quyidagi **Secrets**-larni qo'shing:
    -   `HOST`: Serveringiz IP manzili.
    -   `USERNAME`: Serverga ulanadigan foydalanuvchi nomi.
    -   `PASSWORD`: Serveringizga SSH orqali ulanish paroli.

3.  Serverda loyiha manzili `/home/shukurjon/projects/botrobo` ekanligiga ishonch hosil qiling.

Endi har safar kodni push qilganingizda, GitHub avtomatik ravishda serverga ulanadi va Docker konteynerlarini yangilaydi.
