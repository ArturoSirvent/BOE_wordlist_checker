#!/usr/bin/env python
import requests
import re 
import fitz
import os
import subprocess
import datetime as dt

#obtenemos el día
today=dt.datetime.today()
day=today.day
month=today.month
year=today.year
weekday=today.weekday()
#this numbers really are only valid for 2021
num_dias_mes=[26,24,27,26,26,26,27,26,26,26,26,27]
#que no sea domindo que no hay boe
if not (weekday==6):
	#tenemos que calcular el orden
	sum_acumulada=sum(num_dias_mes[:month-1])
	orden=sum_acumulada+day-day//7

	#el url tiene esta forma
	url=f"https://www.boe.es/boe/dias/{year}/{str(month).zfill(2)}/{str(day).zfill(2)}/pdfs/BOE-S-2021-{orden}.pdf"

	#descargamos el boe
	archivo=requests.get(url)
	nombre=f"{str(day).zfill(2)}_{str(month).zfill(2)}_{year}.pdf"
	carpeta=f"/home/user/Main_Folder/BOES"

	#lo primero de todo, vemos que se ha descargado bien
	if archivo.ok:

		if not(nombre in os.listdir(carpeta)):

			#despues comprobamos que no lo hemos decargado ya hoy
			with open(f"{carpeta}/{nombre}","wb") as file1:
			    file1.write(archivo.content)
			    
			    
			#si el archivo esta bien, y además es la primera vez que lo abrimos en el dia
			#vamos a hacer la comprobacion de la lista de palabras
			
			#primero cargamos el texto del BOE
			doc = fitz.open(f"{carpeta}/{nombre}")  # open document
			texto=""
			for page in doc:  # iterate the document pages
			    texto += page.get_text()  # get plain text (is in UTF-8))
			texto=texto.lower().replace("\n", " ")
			texto=re.sub(" +"," ",texto)


			#leemos la lista de palabras buscadas
			with open("/home/user/Main_Folder/lista_palabras.txt","r") as palabras_file:
	    			lista_palabras=[i.strip() for i in palabras_file.read().lower().split("\n") if i]
			
			#por ultimo tenemos que hacer una comprobación de las palabras que sí estan, y si no hubiera ninguna mencionar que no había nada
			#además voy a añadir un poco del texto qeu acompaña a la palabra de interés, quiza 30 letras delante y 30 detrás.
			coincidencias_list=[]
			coincidencias_list_short=[]
			for i in lista_palabras:
				#el regex es asi para que solo matchée palabras no partes de palabras como UC, o UV...
				result=re.finditer(fr"\b{i}\b",texto)
				if result:
					#result=list(result)
					for m,j in enumerate(result):
						coincidencias_list.append(f"{m+1}.- Palabra \"{i}\", encontrada. Contexto: {texto[j.start()-60:j.start()+60]}.\n\n")
						coincidencias_list_short.append(f"Palabra \"{i}\", encontrada.\n")
					del result
			
			#al terminar de comprobar las palabras miramos si la lista de coincidencias esta vacia o no
			if coincidencias_list:
				mensaje_final_largo="".join(coincidencias_list)
				mensaje_final="".join(coincidencias_list_short)
				#y si hay mensaje final, lo guardamos
				nombre_aux=nombre.replace(".pdf",".txt")
				with open(f"{carpeta}/{nombre_aux}_summary","w") as file2:
					file2.write(mensaje_final_largo)
				subprocess.run(["/usr/bin/notify-send", "BINGO", f"{mensaje_final}"])
			
			else:
				mensaje_final="No habia nada en el BOE de hoy ({day}/{month}/{year})."
				subprocess.run(["/usr/bin/notify-send", "NADA", f"{mensaje_final}"])
			
			#y el mensaje final lo sacamos como una notificacion

				
		else:
			#si ya lo tenemos descargado pues pasamos
			pass

		    
		    
	else:
		mensaje="El URL está mal o no disponible"
		subprocess.run(["/usr/bin/notify-send","--icon=error ",f"{mensaje}"])
