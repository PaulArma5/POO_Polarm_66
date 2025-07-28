import random

class Robot:
    def __init__(self, nombre, energia, escudo=30, habilidad=None):
        self.nombre = nombre
        self.energia = energia
        self.escudo = escudo
        self.estado = "Activo"
        self.habilidad_usada = False
        self.habilidad = habilidad
        self.danio_total_recibido = 0
        self.danio_total_infligido = 0

    def recibir_danio(self, cantidad):
        if self.estado == "Destruido":
            return
        danio_reducido = int(cantidad * (1 - self.escudo / 100))
        self.energia -= danio_reducido
        self.danio_total_recibido += danio_reducido
        if self.energia <= 0:
            self.energia = 0
            self.estado = "Destruido"

    def usar_habilidad(self, oponente=None):
        if self.habilidad and not self.habilidad_usada:
            self.habilidad_usada = True
            return self.habilidad(self, oponente)
        return None


def fe(robot, _=None):
    robot.energia = max(robot.energia, 50)
    return f"{robot.nombre} usó Fe. Su energía se restauró a {robot.energia}."

def milagro(robot, _=None):
    robot.escudo += 50
    return f"{robot.nombre} usó Milagro. Su escudo ahora es {robot.escudo}%."

def mirada_asesina(robot, _=None):
    return "doble_ataque"

def rosita_blanca(robot, _=None):
    if robot.energia < 10:
        robot.energia = 10
    return f"{robot.nombre} usó Rosita Blanca. Ahora tiene al menos 10 de energía."
