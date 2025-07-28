# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 14:42:42 2024

@author: Usuario
"""

import os
import yt_dlp as youtube_dl
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        '¡Hola! Envíame un enlace de YouTube y descargaré la música para ti.'
    )

async def handle_message(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    await update.message.reply_text('Descargando...')
    await download_audio(url, update)

async def download_audio(url, update: Update) -> None:
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    try:

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')


        await update.message.reply_audio(audio=open(file_name, 'rb'))


        await update.message.reply_text('¡Tu canción se ha descargado correctamente! Ahora puedes enviar otro enlace.')


        os.remove(file_name)

    except Exception as e:

        await update.message.reply_text(f'Hubo un error al descargar el archivo: {e}')


def main() -> None:

    application = Application.builder().token("7303373971:AAFxRxBVPiJLVnA1vCHNw-cLESTU-VajnDo").build()


    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    application.run_polling()

if __name__ == "__main__":
    main()
