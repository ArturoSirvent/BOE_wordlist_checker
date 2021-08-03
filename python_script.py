#!/usr/bin/env python
import requests
import re 
import fitz
import os
import subprocess
import glob

from datetime import date, datetime, timedelta


#useful function for missing days 
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta


#obtenemos el día
today=datetime.today()
day=today.day
month=today.month
year=today.year
weekday=today.weekday()
num_dias_mes=[26,24,27,26,26,26,27,26,26,26,26,27]
dias_extra=[4,0,0,3,5,1,3,6,2,4,0,2]


#añadimos código para que se revisen los días de los que no hay informe porque no encendí el ordenador

#get all the file names and do data instances with them
os.chdir("/home/arturo/BOE/BOES")
lista_dias=glob.glob("*.pdf")
lista_instancias_dias=[]
#loop entre los dias para guardarlos como dates instances
for dia in lista_dias:
	num_dia,num_mes,num_ano=dia.replace(".pdf","").split("_")
	lista_instancias_dias.append(date(int(num_ano),int(num_mes),int(num_dia)))


#primer día desde el que se revisa
first_day=date(2021,7,28)
date_today=today.date()
lista_dias_faltantes=[]
#loop over the missing days, minus today, today will be done below.
for result in perdelta(first_day, date_today, timedelta(days=1)):
	if (result not in lista_instancias_dias)&(result!=date_today)&(result.weekday()!=6):
		lista_dias_faltantes.append(result)

#ya tenemos todos los dias faltantes que no son domingo, ahora solo queda que se descargue y se haga un informe
# lo pondré al final


#que no sea domindo que no hay boe
if not (weekday==6):
	#tenemos que calcular el orden
	sum_acumulada=sum(num_dias_mes[:month-1])
	orden=sum_acumulada+day-(day+dias_extra[month-1])//7

	#el url tiene esta forma
	url=f"https://www.boe.es/boe/dias/{year}/{str(month).zfill(2)}/{str(day).zfill(2)}/pdfs/BOE-S-2021-{orden}.pdf"

	#descargamos el boe
	archivo=requests.get(url)
	nombre=f"{str(day).zfill(2)}_{str(month).zfill(2)}_{year}.pdf"
	carpeta=f"/home/arturo/Documentos/proyectos_programacion/python/CHECK_BOE/BOES"

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
			with open("/home/arturo/Documentos/proyectos_programacion/python/CHECK_BOE/lista_palabras.txt","r") as palabras_file:
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
						coincidencias_list.append(f"{m+1}.- Palabra \"{i}\", encontrada. Contexto: {texto[j.start()-90:j.start()+90]}.\n\n")
						coincidencias_list_short.append(f"Palabra \"{i}\", encontrada.\n")
					del result
			
			#al terminar de comprobar las palabras miramos si la lista de coincidencias esta vacia o no
			if coincidencias_list:
				mensaje_final_largo="".join(coincidencias_list)
				mensaje_final="".join(coincidencias_list_short)
				#y si hay mensaje final, lo guardamos
				nombre_aux=nombre.replace(".pdf","")
				with open(f"{carpeta}/{nombre_aux}_summary.txt","w") as file2:
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
		
		
		
		
#para los días que faltan
for today in lista_dias_faltantes:

	day=today.day
	month=today.month
	year=today.year

	#tenemos que calcular el orden
	sum_acumulada=sum(num_dias_mes[:month-1])
	orden=sum_acumulada+day-(day+dias_extra[month-1])//7

	#el url tiene esta forma
	url=f"https://www.boe.es/boe/dias/{year}/{str(month).zfill(2)}/{str(day).zfill(2)}/pdfs/BOE-S-2021-{orden}.pdf"

	#descargamos el boe
	archivo=requests.get(url)
	nombre=f"{str(day).zfill(2)}_{str(month).zfill(2)}_{year}.pdf"
	carpeta=f"/home/arturo/Documentos/proyectos_programacion/python/CHECK_BOE/BOES"

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
			with open("/home/arturo/Documentos/proyectos_programacion/python/CHECK_BOE/lista_palabras.txt","r") as palabras_file:
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
						coincidencias_list.append(f"{m+1}.- Palabra \"{i}\", encontrada. Contexto: {texto[j.start()-90:j.start()+90]}.\n\n")
						coincidencias_list_short.append(f"Palabra \"{i}\", encontrada.\n")
					del result
			
			#al terminar de comprobar las palabras miramos si la lista de coincidencias esta vacia o no
			if coincidencias_list:
				mensaje_final_largo="".join(coincidencias_list)
				mensaje_final="".join(coincidencias_list_short)
				#y si hay mensaje final, lo guardamos
				nombre_aux=nombre.replace(".pdf","")
				with open(f"{carpeta}/{nombre_aux}_summary.txt","w") as file2:
					file2.write(mensaje_final_largo)
				subprocess.run(["/usr/bin/notify-send", f"BINGO dia {today}", f"{mensaje_final}"])
			
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
		
		
