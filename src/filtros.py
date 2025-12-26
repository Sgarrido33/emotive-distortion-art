import os
import json
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

TRANSFORMACIONES_DIR = "Transformaciones"
IMG_FINAL_NOMBRE = "imagen_final.png"
JSON_NOMBRE = "datos.json"

def buscar_participantes(criterios):
    resultados = []
    if not os.path.exists(TRANSFORMACIONES_DIR):
        messagebox.showerror("Error", f"La carpeta '{TRANSFORMACIONES_DIR}' no fue encontrada.")
        return resultados

    for nombre_carpeta in os.listdir(TRANSFORMACIONES_DIR):
        ruta_carpeta = os.path.join(TRANSFORMACIONES_DIR, nombre_carpeta)
        
        if os.path.isdir(ruta_carpeta) and nombre_carpeta.startswith("Participante "):
            json_path = os.path.join(ruta_carpeta, JSON_NOMBRE)
            
            if not os.path.exists(json_path):
                continue

            with open(json_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            coincide = True

            # (Los filtros de imagen, género, distrito y edad se quedan igual que antes)
            imagen_filtro = criterios['imagen_base']
            if coincide and imagen_filtro != "Todas":
                if datos.get('imagen_base') != imagen_filtro:
                    coincide = False

            genero_filtro = criterios['genero']
            if coincide and genero_filtro != "Todos": 
                if datos.get('genero') != genero_filtro:
                    coincide = False

            distrito_filtro = criterios['distrito'].strip().lower()
            if coincide and distrito_filtro:
                if datos.get('distrito', '').lower() != distrito_filtro:
                    coincide = False
            
            if coincide and (criterios['edad_min'] or criterios['edad_max']):
                try:
                    edad_participante = int(datos.get('edad'))
                    if criterios['edad_min']:
                        if edad_participante < int(criterios['edad_min']):
                            coincide = False
                    if coincide and criterios['edad_max']:
                        if edad_participante > int(criterios['edad_max']):
                            coincide = False
                except (ValueError, TypeError, KeyError):
                    coincide = False

            # --- CORRECCIÓN: Lógica para encontrar el nombre del archivo ---
            if coincide:
                # Intenta obtener el nombre dinámico del archivo desde el JSON
                nombre_final = datos.get("nombre_archivo_final") 
                
                # Si no existe (porque son datos antiguos), usa el nombre por defecto
                if not nombre_final:
                    nombre_final = IMG_FINAL_NOMBRE # 'imagen_final.png'

                ruta_imagen_final = os.path.join(ruta_carpeta, nombre_final)
                if os.path.exists(ruta_imagen_final):
                    resultados.append(ruta_imagen_final)
    return resultados

def crear_mosaico(lista_imagenes, columnas=4, ancho_thumb=300, alto_thumb=300):
    if not lista_imagenes:
        return None

    imagenes = [cv2.resize(cv2.imread(p), (ancho_thumb, alto_thumb)) for p in lista_imagenes]
    
    n_imagenes = len(imagenes)
    filas = (n_imagenes - 1) // columnas + 1
    
    mosaico = np.zeros((filas * alto_thumb, columnas * ancho_thumb, 3), dtype=np.uint8)
    
    for i, img in enumerate(imagenes):
        fila_actual = i // columnas
        columna_actual = i % columnas
        y_offset = fila_actual * alto_thumb
        x_offset = columna_actual * ancho_thumb
        mosaico[y_offset:y_offset + alto_thumb, x_offset:x_offset + ancho_thumb] = img
        
    return mosaico


def iniciar_busqueda(root, entries):
    criterios = {
        "imagen_base": entries["imagen_base"].get(),
        "genero": entries["genero"].get(),
        "distrito": entries["distrito"].get(),
        "edad_min": entries["edad_min"].get(),
        "edad_max": entries["edad_max"].get()
    }
    
    root.withdraw()
    rutas_imagenes = buscar_participantes(criterios)
    
    if not rutas_imagenes:
        messagebox.showinfo("Sin resultados", "No se encontraron participantes que cumplan con los criterios.")
        root.deiconify()
        return

    mosaico_final = crear_mosaico(rutas_imagenes)
    
    if mosaico_final is not None:
        cv2.imshow("Resultados del Filtro (Presiona cualquier tecla para cerrar)", mosaico_final)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    root.destroy()

def main():
    root = tk.Tk()
    root.title("Filtrar Resultados de Participantes")

    frame = tk.Frame(root, padx=15, pady=15)
    frame.pack()

    # --- NUEVO: Menú desplegable para filtrar por Imagen ---
    tk.Label(frame, text="Imagen Base:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="w", pady=5)
    
    # Llenamos la lista de opciones leyendo la carpeta de imágenes
    try:
        IMAGES_DIR = "images"
        opciones_imagen = ["Todas"] + [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
    except FileNotFoundError:
        opciones_imagen = ["Todas"] # Si no encuentra la carpeta, solo muestra "Todas"

    imagen_filtro_var = tk.StringVar(value=opciones_imagen[0])
    combo_imagen = ttk.Combobox(frame, textvariable=imagen_filtro_var, values=opciones_imagen, state="readonly", width=28, font=("Helvetica", 11))
    combo_imagen.grid(row=0, column=1, columnspan=3, sticky="w")


    # --- Resto de campos ajustados ---
    tk.Label(frame, text="Género:", font=("Helvetica", 11)).grid(row=1, column=0, sticky="w", pady=5)
    genero_filtro_var = tk.StringVar(value="Todos")
    frame_genero = tk.Frame(frame)
    frame_genero.grid(row=1, column=1, columnspan=3, sticky="w")
    tk.Radiobutton(frame_genero, text="Todos", variable=genero_filtro_var, value="Todos", font=("Helvetica", 10)).pack(side="left")
    tk.Radiobutton(frame_genero, text="M", variable=genero_filtro_var, value="M", font=("Helvetica", 10)).pack(side="left", padx=5)
    tk.Radiobutton(frame_genero, text="F", variable=genero_filtro_var, value="F", font=("Helvetica", 10)).pack(side="left", padx=5)
    tk.Radiobutton(frame_genero, text="NB", variable=genero_filtro_var, value="NB", font=("Helvetica", 10)).pack(side="left", padx=5)

    tk.Label(frame, text="Distrito:", font=("Helvetica", 11)).grid(row=2, column=0, sticky="w", pady=5)
    entry_distrito = tk.Entry(frame, width=30, font=("Helvetica", 11))
    entry_distrito.grid(row=2, column=1, columnspan=3)

    tk.Label(frame, text="Rango de Edad:", font=("Helvetica", 11)).grid(row=3, column=0, sticky="w", pady=5)
    entry_edad_min = tk.Entry(frame, width=10, font=("Helvetica", 11))
    entry_edad_max = tk.Entry(frame, width=10, font=("Helvetica", 11))
    entry_edad_min.grid(row=3, column=1)
    entry_edad_max.grid(row=3, column=2)

    tk.Label(frame, text="(Dejar campos en blanco para no filtrar por ellos)", font=("Helvetica", 9, "italic")).grid(row=4, column=0, columnspan=3, pady=10)

    entries = {
        "imagen_base": imagen_filtro_var, # Añadido
        "genero": genero_filtro_var,
        "distrito": entry_distrito,
        "edad_min": entry_edad_min,
        "edad_max": entry_edad_max
    }

    btn_filtrar = tk.Button(frame, text="Filtrar", font=("Helvetica", 12, "bold"), command=lambda: iniciar_busqueda(root, entries))
    btn_filtrar.grid(row=5, column=0, columnspan=3, pady=10, ipadx=10)

    root.eval('tk::PlaceWindow . center')
    root.mainloop()

if __name__ == "__main__":
    main()