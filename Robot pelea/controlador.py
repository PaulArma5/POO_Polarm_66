from modulo import Robot, fe, milagro, mirada_asesina, rosita_blanca
from vista import mostrar_estado, mostrar_combate, mostrar_uso_habilidad, mostrar_resultado_final
import random
import time

habilidades = [fe, milagro, mirada_asesina, rosita_blanca]
robots = []

for i in range(4):
    nombre = input("Ingrese el nombre del robot: ")
    habilidad = habilidades[i]
    robots.append(Robot(nombre, 100, escudo=30, habilidad=habilidad))

print("\n🔋 Estado inicial de los robots:")
for r in robots:
    mostrar_estado(r)

print("\n🤖 ¡Comienza el torneo todos contra todos!")
rondas = 0

for i in range(len(robots)):
    for j in range(i + 1, len(robots)):
        r1, r2 = robots[i], robots[j]
        print(f"\n⚔️ Duelo entre {r1.nombre} y {r2.nombre}")
        ronda_duelo = 1
        while r1.estado == "Activo" and r2.estado == "Activo":
            print(f"\n🔁 Ronda {ronda_duelo}")
            atacante, defensor = (r1, r2) if random.choice([True, False]) else (r2, r1)

            for robot in (r1, r2):
                mensaje = robot.usar_habilidad(oponente=(r2 if robot == r1 else r1))
                mostrar_uso_habilidad(mensaje)

            danio = random.randint(10, 30)
            mensaje_habilidad = atacante.habilidad.__name__ if atacante.habilidad else ""

            if atacante.habilidad_usada and mensaje_habilidad == "mirada_asesina":
                mostrar_combate(atacante, defensor, danio)
                defensor.recibir_danio(danio)
                atacante.danio_total_infligido += danio

                mostrar_combate(atacante, defensor, danio)
                defensor.recibir_danio(danio)
                atacante.danio_total_infligido += danio
            else:
                mostrar_combate(atacante, defensor, danio)
                defensor.recibir_danio(danio)
                atacante.danio_total_infligido += danio

            mostrar_estado(defensor)
            ronda_duelo += 1
            time.sleep(0.5)
        rondas += ronda_duelo

vivos = [r for r in robots if r.estado == "Activo"]
ganador = vivos[0] if vivos else robots[0]

mostrar_resultado_final(ganador, robots, rondas)
