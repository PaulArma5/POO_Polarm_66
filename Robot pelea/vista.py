def mostrar_estado(robot):
    print(f"🤖 {robot.nombre} | Energía: {robot.energia} | Estado: {robot.estado} | Escudo: {robot.escudo}%")

def mostrar_combate(atacante, defensor, danio):
    print(f"⚔️ {atacante.nombre} ataca a {defensor.nombre} con {danio} de daño!")

def mostrar_uso_habilidad(mensaje):
    if mensaje:
        print(f"✨ {mensaje}")

def mostrar_resultado_final(ganador, robots, rondas):
    print("\n🏁 TORNEO FINALIZADO")
    print(f"🏆 Ganador: {ganador.nombre}")
    print(f"🔁 Rondas jugadas: {rondas}")
    print("\n📊 Estadísticas por robot:")
    for r in robots:
        print(f"- {r.nombre}: Daño infligido = {r.danio_total_infligido}, Daño recibido = {r.danio_total_recibido}")
