from datetime import *

from telegram import ForceReply, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import db


async def empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Seleziona un comando dal menù per iniziare!")


last_handler = empty


async def default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await last_handler(update, context)


async def handle_ask_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, direction):
    reply_markup = ReplyKeyboardMarkup([["Conferma"], ["Annulla"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Conferma l'inserimento: hai " + ("speso" if direction else "incassato") + str(status["price"]) + "€ nella categoria '" + status[
            "category"] + "' in data " + str(status["date"]) + (
            "." if status["note"] == "" else ". Hai anche messo come nota: '" + status["note"] + "'."), reply_markup=reply_markup)
    status["last_request"] = "confirm"


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_handler
    if update.message.text.lower() == "conferma":
        db.insert_transaction((status["price"], status["category"], status["note"], status["date"].strftime("%Y-%m-%d")))
        await update.message.reply_text("Inserimento avvenuto con successo!")
    else:
        await update.message.reply_text("Inserimento annullato.")
    status["last_request"] = "idle"
    last_handler = empty


default_status = {
    "last_request": "idle",
    "price": 0.0,
    "category": "",
    "note": "",
    "date": datetime.now()
}

status = default_status

default_category_status = {
    "last_request": "idle",
    "name": "",
    "type": ""
}

category_status = default_category_status


async def base_operation(update: Update, context: ContextTypes.DEFAULT_TYPE, direction: bool):
    if status["last_request"] == "idle":
        status["last_request"] = "waiting_price"
        await update.message.reply_text("Quanto hai " + ("speso" if direction else "incassato") + "?")
    elif status["last_request"] == "waiting_price":
        try:
            status["price"] = abs(float(update.message.text))
            if direction:
                status["price"] = -status["price"]
        except:
            await update.message.reply_text("Errore: inserire un numero!")
            return True

        keyboard = []
        for cat in db.get_categories_with_type("outcome" if direction else "income"):
            keyboard.append([KeyboardButton(cat)])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Inserisci la categoria", reply_markup=reply_markup)
        status["last_request"] = "waiting_category"
    elif status["last_request"] == "waiting_category":
        status["category"] = update.message.text
        reply_markup = ReplyKeyboardMarkup([["Sì"], ["No"]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Vuoi inserire una nota?", reply_markup=reply_markup)
        status["last_request"] = "waiting_note_yn"
    elif status["last_request"] == "waiting_note_yn":
        if update.message.text == "Sì":
            await update.message.reply_text("Inserire il testo della nota:")
            status["last_request"] = "waiting_note"
        else:
            return False
    elif status["last_request"] == "waiting_note":
        status["note"] = update.message.text
        return False
    else:
        return False
    return True


async def new_transaction_today(update: Update, context: ContextTypes.DEFAULT_TYPE, direction):
    res = await base_operation(update, context, direction)
    if res:
        pass
    elif status["last_request"] == "confirm":
        await handle_confirmation(update, context)
    elif not res:
        await handle_ask_confirm(update, context, direction)
    else:
        await update.message.reply_text("Status " + status["last_request"] + " not supported yet.")
        status["last_request"] = "idle"


async def new_transaction_past(update: Update, context: ContextTypes.DEFAULT_TYPE, direction):
    global last_handler
    res = await base_operation(update, context, direction)
    if res:
        pass
    elif status["last_request"] == "waiting_date":
        try:
            status["date"] = datetime.strptime(update.message.text, '%d/%m/%Y')
        except:
            await update.message.reply_text("La data inserita non è nel formato corretto (dd/mm/yyyy)!")
            return True
        if status["date"] > datetime.now():
            await update.message.reply_text("La data inserita è nel futuro: inserisci una data precedente a oggi!")
            return True
        await handle_ask_confirm(update, context, direction)
    elif status["last_request"] == "confirm":
        await handle_confirmation(update, context)
    elif not res:
        await update.message.reply_text("Inserisci la data (dd/mm/yyyy):")
        status["last_request"] = "waiting_date"
    else:
        await update.message.reply_text("Status " + status["last_request"] + " not supported yet.")
        status["last_request"] = "idle"


async def new_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_handler
    last_handler = new_cost
    await new_transaction_today(update, context, True)


async def new_cost_past(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_handler
    last_handler = new_cost_past
    await new_transaction_past(update, context, True)


async def new_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_handler
    last_handler = new_income
    await new_transaction_today(update, context, False)


async def new_income_past(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_handler
    last_handler = new_income_past
    await new_transaction_past(update, context, False)


async def new_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_handler
    last_handler = new_category
    if category_status["last_request"] == "idle":
        category_status["last_request"] = "waiting_name"
        await update.message.reply_text("Inserire il nome della categoria:")
    elif category_status["last_request"] == "waiting_name":
        if update.message.text in [x[0] for x in db.get_all_categories()]:
            await update.message.reply_text("Questa categoria esiste già.")
            return

        reply_markup = ReplyKeyboardMarkup([["Entrata"], ["Uscita"], ["Entrambi"]], resize_keyboard=True, one_time_keyboard=True)
        category_status["name"] = update.message.text
        await update.message.reply_text("Seleziona il tipo di categoria:", reply_markup=reply_markup)
        category_status["last_request"] = "waiting_type"
    elif category_status["last_request"] == "waiting_type":
        if update.message.text == "Entrata":
            category_status["type"] = "income"
        if update.message.text == "Uscita":
            category_status["type"] = "outcome"
        if update.message.text == "Entrambe":
            category_status["type"] = "both"

        reply_markup = ReplyKeyboardMarkup([["Conferma"], ["Annulla"]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Conferma l'inserimento della categoria " + category_status["name"] + " di tipo " + category_status["type"], reply_markup=reply_markup)
        category_status["last_request"] = "confirm"
    elif category_status["last_request"] == "confirm":
        if update.message.text.lower() == "conferma":
            db.insert_category((category_status["name"], category_status["type"]))
            await update.message.reply_text("Inserimento avvenuto con successo!")
        else:
            await update.message.reply_text("Inserimento annullato.")
        category_status["last_request"] = "idle"
        last_handler = empty
    else:
        await update.message.reply_text("Status " + status["last_request"] + " not supported yet.")
        status["last_request"] = "idle"


async def list_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = "Lista delle categorie:\n"
    for c in db.get_all_categories():
        res += c[0] + " - " + c[1] + "\n"
    await update.message.reply_text(res)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Inculati non ho ancora scritto la documentazione ;)")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global category_status
    global status
    global last_handler
    category_status = default_category_status
    status = default_status
    last_handler = empty

    await update.message.reply_text("Reset avvenuto con successo!")
