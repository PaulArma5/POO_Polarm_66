import telepot

class Vista:
    def __init__(self, token):
        self.bot = telepot.Bot(token)

    def enviar_mensaje(self, chat_id, mensaje):
        self.bot.sendMessage(chat_id, mensaje)
