import logging
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Google Sheets setup ===
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name(
    "/home/ubuntu/newhire-bot/workload-for-assistants-f353572d180c.json",
    SCOPE
)
GSHEET = gspread.authorize(CREDS)
SPREADSHEET = GSHEET.open("Workload for Assistants")

# Chat ID → Название компании
CHAT_COMPANY_MAP = {
    -641179811: "Bonu | BLS",
    -952593601: "Ali Uz Trans",
    -886861116: "Horizon |SunnyHorizon",
    -4845163185: "Father and Sons",
    -4118861668: "Lymar | Bermet",
    -959389426: "DR Trans",
    -2680483606: "Truck Cap",
    -4718126142: "Bog Transport",
    -4922448088: "Along Roads",
    -4769712410: "UCL",
    -4979351832: "Space Y",
    -4717295202: "Muramaster | Nomad | Global",
    -4268988399: "Koltrans",
    -4603729244: "Abla",
    -4511623337: "ASA | Jorgo",
    -4052477599: "SIV",
    -4200825225: "Alinea | Travel",
    -4672873979: "DKD",
    -3179550524: "Ohio Truck Hub",
    -4814638484: "Mate Motors",
    -4276079213: "AK Diksi",
    -4648676040: "Speedel",
    -4748315732: "NS Cargo",
    -2566823527: "BEK",
    -4618741642: "GEM",
    -4594341933: "Kaddat",
    -4768048466: "BOB",
    -2677163999: "Ezgo",
    -2582390925: "Kamuna",
    -4740883511: "Sunny Cargo",
    -4719608356: "SFS",
    -4163197906: "Rodum",
    -4576605422: "GEFF",
    -4773055699: "USP",
    -4621714948: "Pacific",
    -4919161800: "Fedtrans",
    -4722892554: "Sediqi",
    -4655460623: "ITransport",
    -4782332920: "Shark Trans",
    -4638523696: "Eddanz",
    -995673635: "SR",
    -4702008735: "IS",
    -4213969790: "M and G",
    -4786535869: "Nemets",
    -4745120183: "Avalon",
    -4126769539: "ATA",
    -4653938586: "Chubei",
    -4907027649: "AutoCraft",
    -4682510814: "AXU",
    -4731725333: "Green Road",
    -4701025390: "Top Line",
    -4649157975: "Tajroad",
    -4819419371: "D&M",
    -4788225180: "HY",
    -4585303350: "US Autotransport",
    -4988144586: "TM Carrier",
    -4859432961: "Cargix",
    -4780730105: "Y-Bay",
    -4988976325: "0Mar",
    -4884851917: "Shueg",
    -4277592397: "US Carrier",
    -4799504965: "Transglobe",
}

# === Логирование ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Обработка сообщений ===
async def handle_newhire_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.edited_message or update.message
    if not message or not message.text:
        return

    chat_id = message.chat.id
    text = message.text
    logger.info(f"Message in chat {chat_id}: {text}")

    if "#newhire" not in text.lower():
        return

    match = re.search(r"#newhire\s+(.+?)\s*[-–]?\s*consent\s+signed", text, re.IGNORECASE)
    if not match:
        await message.reply_text("⚠️ Please use format: #newhire Firstname Lastname Consent signed")
        return

    driver_name = match.group(1).strip().title()
    now = datetime.now().strftime("%m/%d/%Y")
    company_name = CHAT_COMPANY_MAP.get(chat_id, "Unknown")

    try:
        worksheet = SPREADSHEET.worksheet("Joana")
        worksheet.append_row([driver_name, now, company_name])
        logger.info(f"Added: {driver_name} | {company_name}")
        await message.reply_text(f"✅ Added to spreadsheet: {driver_name} | {company_name}")
    except Exception as e:
        logger.error(f"Error writing to sheet: {e}")
        await message.reply_text(f"⚠️ Failed to add {driver_name} to spreadsheet.")
# === Запуск бота ===
app = ApplicationBuilder().token("8197361714:AAGRStEOg93duxnxH_id0597kEcEeC1x_AQ").build()
app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_newhire_message))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_newhire_message))

if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()













