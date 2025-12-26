import cv2
import numpy as np
import serial
import time
import tkinter as tk
import os               
import json             
import random
from datetime import datetime 

TRANSFORMACIONES_DIR = "Transformaciones"  
SERIAL_PORT = 'COM9' 
BAUD_RATE = 9600
IMAGE_PATH = 'imagen_original.jpg'
def obtener_siguiente_numero_participante(base_dir):
    try:
        carpetas_existentes = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        numeros = []
        for carpeta in carpetas_existentes:
            if carpeta.startswith("Participante "):
                try:
                    numeros.append(int(carpeta.split(" ")[1]))
                except (ValueError, IndexError):
                    continue
        return max(numeros) + 1 if numeros else 1
    except FileNotFoundError:
        return 1
    
def obtener_datos_participante():
    root = tk.Tk()
    root.title("Datos del Participante")


    edad_var = tk.StringVar()
    distrito_var = tk.StringVar()
    genero_var = tk.StringVar(value="NB") 

    
    tk.Label(root, text="Edad:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_edad = tk.Entry(root, textvariable=edad_var, width=30, font=("Helvetica", 12))
    entry_edad.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Género:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    
    frame_genero = tk.Frame(root)
    frame_genero.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    
    tk.Radiobutton(frame_genero, text="Masculino", variable=genero_var, value="M", font=("Helvetica", 11)).pack(side="left")
    tk.Radiobutton(frame_genero, text="Femenino", variable=genero_var, value="F", font=("Helvetica", 11)).pack(side="left", padx=10)
    tk.Radiobutton(frame_genero, text="No Binario", variable=genero_var, value="NB", font=("Helvetica", 11)).pack(side="left")
    
    tk.Label(root, text="Distrito:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
    entry_distrito = tk.Entry(root, textvariable=distrito_var, width=30, font=("Helvetica", 12))
    entry_distrito.grid(row=2, column=1, padx=10, pady=5)

    btn_continuar = tk.Button(root, text="Continuar", font=("Helvetica", 12, "bold"), command=root.destroy)
    btn_continuar.grid(row=3, column=0, columnspan=2, pady=20)
    
    root.eval('tk::PlaceWindow . center')
    root.mainloop()
    
    edad = edad_var.get()
    genero = genero_var.get()
    distrito = distrito_var.get()
    
    return edad, genero, distrito

# Bloques de construccion
def emocion_alegria(img): 
    output_img = img.copy()
    tinte_amarillo = np.full(output_img.shape, (0, 220, 255), dtype=np.uint8)
    output_img = cv2.addWeighted(output_img, 0.95, tinte_amarillo, 0.035, 0) # menos peso del tinte - bajar
    hsv = cv2.cvtColor(output_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = np.clip(v * 1.02, 0, 255).astype(np.uint8) # para mas brillo - subir
    final_hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

def emocion_tristeza(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = np.clip(s * 0.97, 0, 255).astype(np.uint8)
    desaturada = cv2.cvtColor(cv2.merge([h, s, v]), cv2.COLOR_HSV2BGR)
    tinte_azul = np.full(desaturada.shape, (255, 150, 0), dtype=np.uint8)
    con_tinte = cv2.addWeighted(desaturada, 0.97, tinte_azul, 0.03, 0)
    alto, ancho = img.shape[:2]
    ksize_x = ancho + 1 if ancho % 2 == 0 else ancho
    ksize_y = alto + 1 if alto % 2 == 0 else alto
    kernel_x = cv2.getGaussianKernel(ksize_x, int(ancho * 0.5))
    kernel_y = cv2.getGaussianKernel(ksize_y, int(alto * 0.5))
    kernel = kernel_y * kernel_x.T
    kernel = kernel[0:alto, 0:ancho]
    mascara_norm = cv2.normalize(kernel, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    mascara_3ch = cv2.cvtColor(mascara_norm, cv2.COLOR_GRAY2BGR)
    con_viñeta_completa = cv2.multiply(con_tinte.astype(np.float32), mascara_3ch.astype(np.float32) / 255.0).astype(np.uint8)
    return cv2.addWeighted(img, 0.85, con_viñeta_completa, 0.15, 0)

def emocion_miedo(img):
    output_img = img.copy()
    output_img = np.clip(output_img * 0.98, 0, 255).astype(np.uint8)
    num_strips = 20
    strip_height = output_img.shape[0] // num_strips
    for i in range(num_strips):
        y1 = i * strip_height
        y2 = (i + 1) * strip_height
        shift = np.random.randint(-4, 4)
        strip = output_img[y1:y2, :]
        strip_shifted = np.roll(strip, shift, axis=1)
        output_img[y1:y2, :] = strip_shifted
    return output_img

def emocion_ira(img):
    output_img = img.copy()
    alto, ancho = output_img.shape[:2]
    porcentaje_ira = 0.01
    num_pixeles_a_cambiar = int(alto * ancho * porcentaje_ira)
    coordenadas_y = np.random.randint(0, alto, size=num_pixeles_a_cambiar)
    coordenadas_x = np.random.randint(0, ancho, size=num_pixeles_a_cambiar)
    color_rojo = [0, 0, 255]
    output_img[coordenadas_y, coordenadas_x] = color_rojo
    return output_img

def emocion_aversion(img):
    output_img = img.copy()
    tinte_verde = np.full(output_img.shape, (0, 200, 150), dtype=np.uint8)
    con_tinte = cv2.addWeighted(output_img, 0.9, tinte_verde, 0.1, 0)
    
    rows, cols = con_tinte.shape[:2]
    map_y, map_x = np.indices((rows, cols), dtype=np.float32)
    map_x = map_x + 1 * np.sin(map_y / 20) + 0.5 * np.cos(map_x / 15)
    map_y = map_y + 1 * np.cos(map_x / 20) + 0.5 * np.sin(map_y / 15)
    
    aversion_completa = cv2.remap(con_tinte, map_x, map_y, cv2.INTER_LINEAR)
    return cv2.addWeighted(img, 0.90, aversion_completa, 0.10, 0)

def emocion_confianza(img):
    img_nitida = cv2.convertScaleAbs(img, alpha=1.1, beta=5)
    img_desenfocada = cv2.GaussianBlur(img, (0, 0), sigmaX=30)
    alto, ancho = img.shape[:2]
    ksize_x = ancho + 1 if ancho % 2 == 0 else ancho
    ksize_y = alto + 1 if alto % 2 == 0 else alto
    kernel_x = cv2.getGaussianKernel(ksize_x, int(ancho * 0.4))
    kernel_y = cv2.getGaussianKernel(ksize_y, int(alto * 0.4))
    kernel = kernel_y * kernel_x.T
    kernel = kernel[0:alto, 0:ancho]
    
    mascara = cv2.normalize(kernel, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    mascara_3ch = cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0

    img_radial_blur = (img_nitida.astype(np.float32) * mascara_3ch + \
                       img_desenfocada.astype(np.float32) * (1.0 - mascara_3ch)).astype(np.uint8)
    confianza_completa = cv2.addWeighted(img_radial_blur, 0.7, img_desenfocada, 0.3, 0)
    return cv2.addWeighted(img, 0.85, confianza_completa, 0.15, 0)

def emocion_interes(img):
    borrosa = cv2.GaussianBlur(img, (21, 21), 0)
    alto, ancho = img.shape[:2]
    ksize_x = ancho + 1 if ancho % 2 == 0 else ancho
    ksize_y = alto + 1 if alto % 2 == 0 else alto
    kernel_x = cv2.getGaussianKernel(ksize_x, int(ancho * 0.45))
    kernel_y = cv2.getGaussianKernel(ksize_y, int(alto * 0.45))
    kernel = kernel_y * kernel_x.T
    kernel = kernel[0:alto, 0:ancho]
    mascara_norm = cv2.normalize(kernel, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    mascara_3ch = cv2.cvtColor(mascara_norm, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0
    img_float = img.astype(np.float32) / 255.0
    borrosa_float = borrosa.astype(np.float32) / 255.0
    enfocada = img_float * mascara_3ch + borrosa_float * (1.0 - mascara_3ch)
    return (enfocada * 255).astype(np.uint8)

# Funciones cuadrantes
def cuadrante_euforia_activacion(img):
    """(Positivo, Alta Energía) - Combina alegría e interés."""
    img_temp = emocion_alegria(img)
    img_final = emocion_interes(img_temp)
    return img_final

def cuadrante_alarma_tension(img):
    """(Negativo, Alta Energía) - Combina miedo e ira."""
    img_temp = emocion_miedo(img)
    img_final = emocion_ira(img_temp)
    return img_final

def cuadrante_tristeza_apatia(img):
    """(Negativo, Baja Energía) - Combina tristeza y aversión de forma balanceada."""
    img_temp = emocion_tristeza(img)
    img_final = emocion_aversion(img_temp)
    return img_final

def cuadrante_calma_seguridad(img):
    """(Positivo, Baja Energía) - Combina confianza con un sutil aumento de brillo."""
    
    img_temp = emocion_confianza(img)
    hsv = cv2.cvtColor(img_temp, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = np.clip(v * 1.02, 0, 255).astype(np.uint8)
    final_hsv = cv2.merge([h, s, v])
    img_final = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    
    return img_final

distorsiones_cuadrantes = {
    '0' : ("Alarma y Tensión", cuadrante_alarma_tension),
    '1' : ("Tristeza y Apatía", cuadrante_tristeza_apatia),
    '2' : ("Euforia y Activación", cuadrante_euforia_activacion),
    '3' : ("Calma y Seguridad", cuadrante_calma_seguridad),
}

os.makedirs(TRANSFORMACIONES_DIR, exist_ok=True)
edad_participante, genero_participante, distrito_participante = obtener_datos_participante()

if not edad_participante and not distrito_participante:
    print("El usuario cerró la ventana. Finalizando programa.")
    exit()

IMAGES_DIR = "images" 
try:
    lista_imagenes = [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if not lista_imagenes:
        raise FileNotFoundError
    imagen_base_seleccionada = random.choice(lista_imagenes)
    IMAGE_PATH = os.path.join(IMAGES_DIR, imagen_base_seleccionada)
    print(f"\nImagen base seleccionada aleatoriamente: {imagen_base_seleccionada}")

except FileNotFoundError:
    print(f"Error: La carpeta '{IMAGES_DIR}' no existe o está vacía. Asegúrate de que contenga imágenes.")
    exit()


participante_id = obtener_siguiente_numero_participante(TRANSFORMACIONES_DIR)
participante_dir = os.path.join(TRANSFORMACIONES_DIR, f"Participante {participante_id}")
os.makedirs(participante_dir, exist_ok=True)

datos_a_guardar = {
    "id_participante": participante_id,
    "edad": edad_participante,
    "genero": genero_participante,
    "distrito": distrito_participante,
    "imagen_base": imagen_base_seleccionada, 
    "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}


json_path = os.path.join(participante_dir, "datos.json")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(datos_a_guardar, f, ensure_ascii=False, indent=4)

print(f"\nSesión para: Participante {participante_id}")
print(f"Datos guardados en: {json_path}")

try:
    print(f"\nIntentando conectar al puerto {SERIAL_PORT}...")
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) 
    print("Conexión con ESP32 exitosa.")
except serial.SerialException as e:
    print(f"Error al conectar con el ESP32: {e}")
    esp32 = None

imagen_original = cv2.imread(IMAGE_PATH)
if imagen_original is None:
    print(f"Error: No se pudo cargar la imagen '{IMAGE_PATH}'.")
    if esp32: esp32.close()
    exit()

imagen_mostrada = imagen_original.copy()
cv2.namedWindow('Arte Interactivo Emocional')

print("\n--- ARTE INTERACTIVO EMOCIONAL ---")
print("Esperando datos desde los 4 sensores...")
for sensor_id, (nombre_cuadrante, _) in distorsiones_cuadrantes.items():
    print(f"  - Sensor '{sensor_id}' -> {nombre_cuadrante}")
print("  - Tecla '4' -> Restaurar imagen")
print("\nPresiona 'q' en la ventana para finalizar y guardar.")

while True:
    if esp32:
        try:
            if esp32.in_waiting > 0:
                dato_recibido = esp32.readline().decode('utf-8').strip()
                if dato_recibido:
                    if dato_recibido in distorsiones_cuadrantes:
                        nombre_cuadrante, funcion_cuadrante = distorsiones_cuadrantes[dato_recibido]
                        print(f"Recibido: [{dato_recibido}] -> {nombre_cuadrante}")
                        imagen_mostrada = funcion_cuadrante(imagen_mostrada)
        except serial.SerialException as e:
            print(f"Se perdió la conexión con el ESP32: {e}")
            esp32 = None

    cv2.imshow('Arte Interactivo Emocional', imagen_mostrada)
    
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    
    elif key == ord('4'):
        print("Tecla '4' presionada -> Restaurando imagen")
        imagen_mostrada = imagen_original.copy()

distrito_sanitizado = distrito_participante.replace(" ", "")
nombre_archivo_final = f"{genero_participante}_{edad_participante}_{distrito_sanitizado}.png"

datos_a_guardar["nombre_archivo_final"] = nombre_archivo_final
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(datos_a_guardar, f, ensure_ascii=False, indent=4)
imagen_final_path = os.path.join(participante_dir, nombre_archivo_final)
cv2.imwrite(imagen_final_path, imagen_mostrada)
print(f"\nImagen final guardada como '{nombre_archivo_final}' en la carpeta del Participante {participante_id}")

print("Cerrando conexión y finalizando.")
if esp32:
    esp32.close()
cv2.destroyAllWindows()