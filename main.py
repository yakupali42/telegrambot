import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Logging ayarları
logging.basicConfig(
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
level=logging.INFO
)

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

def get_product_details(url):
session = requests.Session()
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
}

try:
response = session.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.content, 'html.parser')

title = "İndirimli Ürün"
price = "Fiyat bilgisi çekilemedi"
image_url = None

if "trendyol.com" in url:
title_tag = soup.find('h1', class_='pr-new-br')
if title_tag:
title = title_tag.text.strip()
price_tag = soup.find('span', class_='prc-dsc')
if price_tag:
price = price_tag.text.strip()
img_tag = soup.find('img', class_='detail-section-img')
if img_tag and 'src' in img_tag.attrs:
image_url = img_tag['src']

elif "amazon.com" in url or "amzn.eu" in url:
title_tag = soup.find('span', id='productTitle')
if title_tag:
title = title_tag.text.strip()
price_tag = soup.find('span', class_='a-offscreen')
if price_tag:
price = price_tag.text.strip()
img_tag = soup.find('img', id='landingImage')
if img_tag and 'src' in img_tag.attrs:
image_url = img_tag['src']

elif "hepsiburada.com" in url:
title_tag = soup.find('h1', id='product-name')
if title_tag:
title = title_tag.text.strip()
price_tag = soup.find('span', class_='price')
if price_tag:
price = price_tag.text.strip()
img_tag = soup.find('img', class_='product-image')
if img_tag and 'src' in img_tag.attrs:
image_url = img_tag['src']

return title, price, image_url

except Exception as e:
logging.error(f"Detay çekme hatası: {e}")
return "İndirimli Ürün", "Fiyat bilgisi alınamadı", None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
# URL Tespiti
urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', update.message.text)
if not urls:
await update.message.reply_text("Lütfen geçerli bir ürün linki gönderin.")
return

url = urls[0]
await update.message.reply_text("Ürün bilgileri çekiliyor, lütfen bekleyin...")

title, price, image_url = get_product_details(url)

caption_text = f"🔥 *SÜPER FIRSAT!*\n\n📦 *{title}*\n💰 *Fiyat:* {price}\n\n⚡ Kaçırmamak için hemen inceleyin!"

keyboard = [[InlineKeyboardButton("🛍 Ürünü İncele / Satın Al", url=url)]]
reply_markup = InlineKeyboardMarkup(keyboard)

try:
if image_url:
await context.bot.send_photo(
chat_id=CHANNEL_ID,
photo=image_url,
caption=caption_text,
parse_mode="Markdown",
reply_markup=reply_markup
)
else:
await context.bot.send_message(
chat_id=CHANNEL_ID,
text=f"{caption_text}\n\n*(Görsel çekilemedi)*",
parse_mode="Markdown",
reply_markup=reply_markup
)
await update.message.reply_text("✅ Başarıyla kanalda paylaşıldı!")
except Exception as e:
await update.message.reply_text(f"⚠ Kanala gönderirken hata oluştu: {e}")

if __name__ == '__main__' :
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
print("Bot çalışıyor...")
app.run_polling()
