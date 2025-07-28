from telepot.loop import MessageLoop
import time

class TelegramController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def handle_message(self, msg):
        chat_id = msg['chat']['id']
        command = msg['text']

        if command == '/start':
            self.view.send_welcome_message(chat_id)
        elif command == '/Prendetepapacuichan':
            self.model.turn_on()
            self.view.send_led_on_message(chat_id)
        elif command == '/Apagatepapacuichan':
            self.model.turn_off()
            self.view.send_led_off_message(chat_id)
        else:
            self.view.send_invalid_command_message(chat_id)
            
    def start(self):
        MessageLoop(self.view.bot, self.handle_message).run_as_thread()

