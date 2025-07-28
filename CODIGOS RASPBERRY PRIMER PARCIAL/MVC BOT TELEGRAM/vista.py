import telepot

class TelegramView:
    def __init__(self, token):
        self.bot = telepot.Bot(token)

    def send_message(self, chat_id, message):
        self.bot.sendMessage(chat_id, message)

    def send_welcome_message(self, chat_id):
        self.send_message(chat_id, 'Bienvenido a este hermoso bot usa /Prendetepapacuichan para encender el LED y /Apagatepapacuichan para apagarlo')

    def send_invalid_command_message(self, chat_id):
        self.send_message(chat_id, 'Ewe usa lo que te pide >:c  /Prendetepapacuichan o /Apagatepapacuichan.')
    
    def send_led_on_message(self, chat_id):
        self.send_message(chat_id, 'LED encendido funcionando por que asi lo quiso taita caiza')

    def send_led_off_message(self, chat_id):
        self.send_message(chat_id, 'LED apagado por que papa cuichan lo quizo')
