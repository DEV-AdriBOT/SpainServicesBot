import os
import json
from telegram import Update, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

PRODUCTS_FILE = "productos.json"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))


def load_products():
    if not os.path.isfile(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return
    data = " ".join(context.args).split(";")
    if len(data) < 3:
        await update.message.reply_text("Formato incorrecto. Usa: /add nombre;precio;descripción")
        return
    nombre, precio, descripcion = data[0].strip(), data[1].strip(), ";".join(data[2:]).strip()
    productos = load_products()
    new_id = max([p["id"] for p in productos], default=0) + 1
    productos.append({"id": new_id, "nombre": nombre, "precio": precio, "descripcion": descripcion})
    save_products(productos)
    await update.message.reply_text(f"Servicio agregado con ID {new_id}.")


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Formato incorrecto. Usa: /del ID")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID inválido.")
        return
    productos = load_products()
    productos = [p for p in productos if p["id"] != target_id]
    save_products(productos)
    await update.message.reply_text(f"Servicio con ID {target_id} eliminado.")


async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return
    productos = load_products()
    if not productos:
        await update.message.reply_text("No hay servicios aún.")
    else:
        msg = "\n".join([f"{p['id']}: {p['nombre']} – €{p['precio']}" for p in productos])
        await update.message.reply_text(msg)


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    productos = load_products()
    if not productos:
        await update.message.reply_text("No hay servicios disponibles en este momento.")
    else:
        lines = [f"• *{p['nombre']}* – €{p['precio']}\n_{p['descripcion']}_" for p in productos]
        await update.message.reply_text("\n\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    condiciones = (
        "🔹 Todos los servicios son digitales; una vez adquiridos no se aceptan devoluciones.\n"
        "🔹 Si algo no funciona como esperabas, haremos lo posible por ayudarte, pero no admitimos reclamaciones.\n"
        "🔹 Al usar nuestros servicios aceptas estos términos sin posibilidad de disputa.\n"
    )
    await update.message.reply_text(condiciones)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Bienvenido a SpainServices!\n"
        "Usa /catalogo para ver nuestros servicios disponibles.\n"
        "Si eres el administrador, usa /add, /del y /list para gestionar el catálogo.\n"
        "Consulta /terms para conocer nuestros términos y condiciones."
    )


def main():
    if not BOT_TOKEN or OWNER_ID == 0:
        print("BOT_TOKEN y OWNER_ID deben estar configurados en las variables de entorno.")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("del", delete))
    app.add_handler(CommandHandler("list", list_products))
    app.add_handler(CommandHandler("catalogo", catalog))
    app.add_handler(CommandHandler("terms", terms))
    app.add_handler(CommandHandler("start", start))
    print("Bot en marcha...")
    app.run_polling()


if __name__ == "__main__":
    main()
