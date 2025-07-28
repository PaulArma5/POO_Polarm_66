from modulo import LEDModel        
from vista import TelegramView  
from controlador  import TelegramController  

if __name__ == "__main__":
    TOKEN = '7576159730:AAF40kCysk09VM8hnM6K0QRhHS3p8GLCmL4'
    model = LEDModel(18)  
    view = TelegramView(TOKEN)  
    controller = TelegramController(model, view)  

    controller.start()  
    
    while True:
        if model.led_status:
            model.blink()
        else:
            model.stop_blinking()


