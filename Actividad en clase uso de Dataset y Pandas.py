import pandas as pd
titulos = pd.read_csv("C:/Users/lab/.spyder-py3/titles.csv")
print(titulos.head(10))
print("\n"*2)
elenco = pd.read_csv("C:/Users/lab/.spyder-py3/cast.csv", encoding="utf-8")
print(elenco.head(10))

print(len(titulos))

print(titulos[titulos["title"]== "Romeo and Juliet"].sort_values("year").head(1))

print(titulos[titulos["title"].str.contains("Spiderman", na=False)].sort_values("year"))
print(titulos[titulos["title"].str.contains("Cannibal", na=False)].sort_values("year"))

print(len(titulos[titulos["year"] == 1980]))
print(len(titulos[titulos["year"] == 2020]))

print(len(titulos[(titulos["year"] >=1950)&(titulos["year"] <=1959)]))

print(titulos[titulos["title"]=="Batman"].sort_values("year"))

print(titulos[titulos["title"]=="Start Wars"],titulos[titulos["title"]
                                                      .str.contains("Star War",na=False)])



#Papeles

print(len(elenco[elenco["title"]=="The Godfather"]))

print(len(elenco[(elenco["title"]== "The Godfather")&(elenco["n"].isna())]))

#ACTIVIDAD

#Título más repetido
print("Titulo más repetido:\n", titulos["title"].value_counts().head(1).to_string())

#Década con más películas
print("Década con más películas:", str((titulos["year"] // 10 * 10).value_counts().idxmax()) + "s", (titulos["year"] // 10 * 10).value_counts().max())

#Películas con más personajes
personajes_por_pelicula = elenco["title"].value_counts().head(10)
print("Películas con más personajes:\n" + personajes_por_pelicula.to_string())

#Papeles de Leonardo DiCaprio
print(elenco[elenco["name"] == "Leonardo DiCaprio"])

#Películas que comienzan con 'The'
print(titulos[titulos["title"].str.startswith("The", na=False)])

#Personajes femeninos más comunes

print("Personajes femeninos más comunes:",elenco[elenco['type'] == 'actress']['character'].value_counts().head(10))

#Papeles de un actor o actriz a elección
print(elenco[elenco["name"] == "Dwayne Johnson"])









