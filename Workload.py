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

# ===== User ID → Worksheet =====
USER_WORKSHEET_MAP = {
    -7466706259: "Joana",
    -8024856816: "Vanessa",
    -6621571568: "Lyra"
}

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
LOG_DIR = "/home/ubuntu/newhire-bot/logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, "newhire.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Обработка сообщений ===
async def handle_newhire_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.edited_message or update.message
    if not message:
        return

    text = (message.text or message.caption or "").strip()
    if not text:
        return

    chat_id = message.chat.id
    chat_title = message.chat.title or "Private Chat"
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    # логирование любого сообщения
    logger.info(f"📩 Chat: {chat_title} ({chat_id}) | From: {user_name} ({user_id}) | Text: {text}")

    # если чат не в списке — логируем отдельно
    if chat_id not in CHAT_COMPANY_MAP:
        logger.warning(f"⚠️ Новый чат! Неизвестный chat_id: {chat_id} | Title: {chat_title}")

    # ищем тег #newhire
    if "#newhire" not in text.lower():
        return

    # Определяем имя листа для ассистента
    worksheet_name = USER_WORKSHEET_MAP.get(user_id)
    if not worksheet_name:
        logger.warning(f"⚠️ User_id {user_id} не найден в USER_WORKSHEET_MAP.")
        return

    # Парсим имя водителя
    match = re.search(r"#newhire\s+(.+?)\s*[-–]?\s*consent\s+signed", text, re.IGNORECASE)
    if not match:
        await message.reply_text("⚠️ Please use format: #newhire Firstname Lastname consent signed")
        return

    driver_name = match.group(1).strip().title()
    now = datetime.now().strftime("%m/%d/%Y")
    company_name = CHAT_COMPANY_MAP.get(chat_id, chat_title or "Unknown")

    worksheet = SPREADSHEET.worksheet(worksheet_name)
    worksheet.append_row([driver_name, now, company_name])

    await message.reply_text(f"✅ Added {driver_name} ({company_name}) to {worksheet_name} list.")
    logger.info(f"✅ Added {driver_name} ({company_name}) to {worksheet_name}")

# === Запуск бота ===
app = ApplicationBuilder().token("8197361714:AAGRStEOg93duxnxH_id0597kEcEeC1x_AQ").build()
app.add_handler(MessageHandler(filters.ALL, handle_newhire_message))

print("🤖 Бот запущен и логирует все сообщения...")
app.run_polling()

















