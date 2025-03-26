import os
def total_matricula(m,des):
	tot_m= m * (1 - des)
	return tot_m
while(True):
	os.system("cls")
						
	n = int(input("Número de alumnos: "))
	while n<0:
		n = int(input("Número de alumnos: "))
	total = 0
	for i in range(n):
		m = float(input(f"Matrícula del alumno {i + 1}: "))
		while m<0:
			m = float(input(f"Matrícula del alumno {i + 1}: "))
		nt = int(input(f"Número de notas del alumno {i + 1}: "))
		while nt<0:
			nt = int(input(f"Número de notas del alumno {i + 1}: "))		
		suma_n = 0
		for j in range(nt):
			nota = float(input(f"Ingrese la nota {j + 1} del alumno {i + 1}: "))
			suma_n += nota
		promedio = suma_n / nt
		if promedio >= 9.1:
			des = 0.15
		elif 7.0 <= promedio < 9.0:
			des = 0.08
		else:
			des = 0.06
   		total += total_matricula(m,des)

	print(f"El total a pagar por concepto de matrículas es: ${total}")
	na=input("Desea Continuar N/S: ")
	if op in ["n","N"]:		break


