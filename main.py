import logging
import os
import re
import requests

from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
ApplicationBuilder,
ContextTypes,
MessageHandler,
filters
)


# ==========================================
# AYARLAR
# ==========================================

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@firsat_city"


# ==========================================
# LOG SİSTEMİ
# ==========================================

logging.basicConfig(
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
level=logging.INFO
)

logger = logging.getLogger(name)


# ==========================================
# ÜRÜN BİLGİLERİNİ ÇEK
# ==========================================

def get_product_details(url):

    headers = {
"User-Agent": (
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
"AppleWebKit/537.36 (KHTML, like Gecko) "
"Chrome/120.0.0.0 Safari/537.36"
),
"Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

try:

    response = requests.get(
url,
headers=headers,
timeout=15,
allow_redirects=True
)

    response.raise_for_status()

    soup = BeautifulSoup(
    response.text,
    "html.parser"
)

title = "İndirimli Ürün"
price = "Fiyat için ürünü inceleyin"
image_url = None


# ==================================
# TRENDYOL
# ==================================

if "trendyol.com" in url.lower():

title_tag = (
soup.find("h1", class_="pr-new-br")
or soup.find("h1")
)

if title_tag:
title = title_tag.get_text(
" ",
strip=True
)

price_tag = (
soup.find("span", class_="prc-dsc")
or soup.find("span", class_="prc-slg")
)

if price_tag:
price = price_tag.get_text(
" ",
strip=True
)

image_tag = (
soup.find(
"img",
class_="detail-big-image"
)
or soup.find("img")
)

if image_tag:

image_url = (
image_tag.get("src")
or image_tag.get("data-src")
)


# ==================================
# AMAZON
# ==================================

elif (
"amazon.com" in url.lower()
or "amazon.com.tr" in url.lower()
or "amzn.eu" in url.lower()
):

title_tag = soup.find(
"span",
id="productTitle"
)

if title_tag:
title = title_tag.get_text(
" ",
strip=True
)

price_tag = (
soup.find(
"span",
class_="a-offscreen"
)
or soup.find(
"span",
class_="a-price-whole"
)
)

if price_tag:
price = price_tag.get_text(
" ",
strip=True
)

image_tag = soup.find(
"img",
id="landingImage"
)

if image_tag:
image_url = (
image_tag.get("src")
or image_tag.get("data-old-hires")
)


# ==================================
# HEPSİBURADA
# ==================================

elif "hepsiburada.com" in url.lower():

title_tag = (
soup.find(
"h1",
id="product-name"
)
or soup.find("h1")
)

if title_tag:
title = title_tag.get_text(
" ",
strip=True
)

price_tag = (
soup.find(
"span",
id="offered-price"
)
or soup.find(
"div",
class_="price-val"
)
)

if price_tag:
price = price_tag.get_text(
" ",
strip=True
)

image_tag = (
soup.find(
"img",
class_="product-image"
)
or soup.find("img")
)

if image_tag:
image_url = (
image_tag.get("src")
or image_tag.get("data-src")
)


return title, price, image_url


except Exception as error:

logger.exception(
"Ürün bilgileri alınırken hata oluştu: %s",
error
)

return (
"İndirimli Ürün",
"Fiyat için ürünü inceleyin",
None
)


# ==========================================
# TELEGRAM'DAN GELEN MESAJI İŞLE
# ==========================================

async def handle_message(
update: Update,
context: ContextTypes.DEFAULT_TYPE
):

if not update.message:
return

if not update.message.text:
return

text = update.message.text.strip()


# ==================================
# LİNK BUL
# ==================================

urls = re.findall(
r"https?://[^\s]+",
text
)

if not urls:

await update.message.reply_text(
"❌ Lütfen geçerli bir ürün linki gönderin."
)

return


url = urls[0].rstrip(
".,;:!?)]}"
)


await update.message.reply_text(
"🔎 Ürün bilgileri çekiliyor...\n"
"⏳ Lütfen birkaç saniye bekleyin."
)


# ==================================
# ÜRÜN BİLGİLERİNİ AL
# ==================================

title, price, image_url = get_product_details(
url
)


# ==================================
# TELEGRAM PAYLAŞIM METNİ
# ==================================

caption = (
"🔥 <b>SÜPER FIRSAT!</b>\n\n"
f"📌 <b>{title}</b>\n"
f"💰 <b>Fiyat:</b> {price}\n\n"
"👇 <b>Ürünü incelemek için:</b>"
)


# ==================================
# SATIN AL BUTONU
# ==================================

keyboard = [
[
InlineKeyboardButton(
"🛍️ Ürünü İncele / Satın Al",
url=url
)
]
]

reply_markup = InlineKeyboardMarkup(
keyboard
)


# ==================================
# KANALA GÖNDER
# ==================================

try:

if image_url:

await context.bot.send_photo(
chat_id=CHANNEL_ID,
photo=image_url,
caption=caption,
parse_mode="HTML",
reply_markup=reply_markup
)

else:

await context.bot.send_message(
chat_id=CHANNEL_ID,
text=caption,
parse_mode="HTML",
reply_markup=reply_markup
)


await update.message.reply_text(
"✅ Fırsat başarıyla kanala gönderildi!"
)


except Exception as error:

logger.exception(
"Telegram gönderim hatası: %s",
error
)

await update.message.reply_text(
"⚠️ Kanala gönderirken bir hata oluştu.\n\n"
f"Hata: {error}"
)

Sessiz Sinema:
# ==========================================
# BOTU BAŞLAT
# ==========================================

def main():

if not TOKEN:

raise ValueError(
"BOT_TOKEN bulunamadı!\n"
"Render Environment Variables bölümüne "
"BOT_TOKEN eklemelisin."
)


application = (
ApplicationBuilder()
.token(TOKEN)
.build()
)


application.add_handler(
MessageHandler(
filters.TEXT & ~filters.COMMAND,
handle_message
)
)


print("🤖 İNDİRİM CİTY BOTU ÇALIŞIYOR...")


application.run_polling()


# ==========================================
# PROGRAMI ÇALIŞTIR
# ==========================================

if __name__ == '__main__':
main()


# ==========================================
# PROGRAMI ÇALIŞTIR
# ==========================================

if __name__ == "__main__":
    main()
