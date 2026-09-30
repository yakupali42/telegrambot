Sessiz Sinema:
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import requests
from bs4 import BeautifulSoup
import re
import json

# --- AYARLAR ---
TOKEN = "8289310189:AAEDzV60g_aoEJbY0MwsYspczX5UgUmryyo"
CHANNEL_ID = "@firsat_city"

logging.basicConfig(
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
level=logging.INFO
)

def get_product_details(url):
session = requests.Session()
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
}

try:
response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
soup = BeautifulSoup(response.content, 'html.parser')

title = None
image_url = None

# --- AMAZON ---
if "amazon" in url.lower():
title_tag = soup.find("span", id="productTitle") or soup.find("h1", id="title")
if title_tag:
title = title_tag.get_text().strip()

img_tag = soup.find("img", id="landingImage") or soup.find("img", id="imgBlkFront")
if img_tag:
dynamic_img = img_tag.get("data-a-dynamic-image")
if dynamic_img:
try:
img_dict = json.loads(dynamic_img)
image_url = list(img_dict.keys())[0]
except Exception:
pass
if not image_url:
image_url = img_tag.get("src") or img_tag.get("data-old-hires")

# --- GENEL META VE JSON-LD ---
if not title:
og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
if og_title and og_title.get("content"):
title = og_title["content"].strip()
elif soup.title and soup.title.string:
title = soup.title.string.strip()

if not image_url:
og_image = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
if og_image and og_image.get("content"):
image_url = og_image["content"]

if not image_url:
scripts = soup.find_all('script', type='application/ld+json')
for script in scripts:
try:
if script.string:
data = json.loads(script.string)
if isinstance(data, list):
data = data[0]
if 'image' in data:
if isinstance(data['image'], list):
image_url = data['image'][0]
elif isinstance(data['image'], str):
image_url = data['image']
elif isinstance(data['image'], dict) and 'url' in data['image']:
image_url = data['image']['url']
break
except Exception:
continue

if image_url:
if image_url.startswith("//"):
image_url = "https:" + image_url

if not title:
title = "Fırsat Ürünü!"

return title, image_url

except Exception as e:
print(f"Hata: {e}")
return "Fırsat Ürünü!", None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
message_text = update.message.text
urls = re.findall(r'https?://[^\s]+', message_text)

if not urls:
await update.message.reply_text("Lütfen geçerli bir ürün linki gönderin.")
return

product_url = urls[0]
await update.message.reply_text("Ürün bilgileri çekiliyor, lütfen bekleyin...")

Sessiz Sinema:
title, image_url = get_product_details(product_url)

caption_text = f"🔥 {title}"
keyboard = [[InlineKeyboardButton("🔗 Ürüne Git / Satın Al", url=product_url)]]
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
text=f"{caption_text}\n\n⚠️ *(Görsel çekilemedi)*",
parse_mode="Markdown",
reply_markup=reply_markup
)
await update.message.reply_text("✅ Başarıyla kanalda paylaşıldı!")
except Exception as e:
await update.message.reply_text(f"❌ Kanala gönderirken hata oluştu: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot çalışıyor...")
    app.run_polling()
