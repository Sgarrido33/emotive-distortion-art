# Instalación de Neuro-Arte Interactivo

![Python](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)
![C++](https://img.shields.io/badge/Firmware-C%2B%2B%20%2F%20Arduino-00599C?logo=arduino&logoColor=white)
![OpenCV](https://img.shields.io/badge/Computer_Vision-OpenCV-5C3EE8?logo=opencv&logoColor=white)
![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%2B%20Sensors-red)

> **Una instalación de arte interactivo que explora la percepción humana distorsionando la realidad visual en función de estímulos emocionales físicos.**

![Installation Overview](docs/images/installation-overview.jpg)

## Concepto del Proyecto

Este proyecto fusiona **IoT (Internet of Things)** con **Procesamiento Digital de Imágenes**. El objetivo es materializar cómo las emociones alteran nuestra percepción de la realidad.

El usuario interactúa con un "cerebro" físico hecho de plasticera equipado con sensores táctiles. Cada región del cerebro representa un estado emocional (Furia, Alegría, Tristeza, Satisfacción). Al estimular una región, el sistema captura ese input y transforma algorítmicamente una imagen proyectada en tiempo real, aplicando filtros de visión artificial que simulan visualmente esa emoción.

---

## Arquitectura Técnica

El sistema funciona mediante una comunicación serial constante entre el controlador físico y la unidad de procesamiento gráfico.

![Tech Setup](docs/images/tech-setup-laptop.jpg)
*(Laptop recibiendo datos del ESP32 vía Serial)*

### 1. Hardware (El Controlador)
* **Microcontrolador:** ESP32 (Programado en C++).
* **Sensores:** 4x Sensores Táctiles Capacitivos TTP223.
* **Lógica:** El firmware utiliza un sistema de polling para detectar estados HIGH en los pines 13, 12, 14, 27. Envía el ID del sensor disparado (0-3) vía Serial a 9600 baudios.

### 2. Software (Procesamiento Visual)
* **Core:** Python 3.10 + OpenCV (cv2).
* **Comunicación:** Librería pyserial para la lectura asíncrona de datos del ESP32.
* **Interfaz:** Tkinter para el registro de participantes y filtrado de datos.
* **Gestión de Datos:** Almacenamiento de sesiones y metadatos en formato JSON.

---

## Algoritmos de Distorsión (Computer Vision)

El núcleo del proyecto reside en `main.py`, donde se aplican transformaciones matriciales sobre la imagen base según la emoción detectada:

![Visual Distortion Output](docs/images/visual-distortion-output.jpg)
*(Ejemplo de salida: Aplicación de ruido y distorsión de color de varios participantes en una sola matriz a modo de presentación al público)*

| Emoción / Cuadrante | Técnica de Procesamiento (OpenCV/Numpy) | Efecto Visual |
|---------------------|-----------------------------------------|---------------|
| **Alarma y Tensión** | np.roll (Pixel Shifting) + Inyección de Canal Rojo | Efecto "Glitch" y ansiedad visual. |
| **Tristeza y Apatía** | Desaturación HSV + cv2.addWeighted (Tinte Azul) + Viñeta Gaussiana | Visión de túnel y colores apagados. |
| **Euforia y Activación** | Aumento de canal V (Brillo) en HSV + cv2.addWeighted (Tinte Amarillo) | Hipersaturación y luminosidad. |
| **Aversión** | cv2.remap con funciones Sinusoidales | Deformación líquida y ondulada de la imagen. |

---

## Diseño del Hardware

El cerebro fue modelado manualmente para alojar la electrónica. Los sensores están mapeados estratégicamente a zonas de la corteza cerebral asociadas teóricamente a dichas emociones.

![Brain Sensors Detail](docs/images/brain-sensors-detail.jpg)

---

## Estructura del Proyecto

```text
/firmware
    └── arduinofile.ino       # Código C++ para el ESP32
/src
    ├── main.py               # Script principal (OpenCV + Serial)
    ├── filtros.py            # Módulo de búsqueda y filtrado de participantes
    ├── Transformaciones/     # Output
    └── images/               # Imágenes base para proyección
/docs                         # Fotografías
```

## Instalación y uso

### 1. Hardware:
Conectar el ESP32 vía USB. Asegurar que los sensores TTP223 estén alimentados a 3.3V/5V.

### 2. Configuración:

Verificar el puerto COM en `main.py`:

```text
SERIAL_PORT = 'COM9' # Ajustar según tu sistema
```

### 3. Ejecución:

```bash
pip install opencv-python pyserial numpy
python src/main.py
```

### 4. Interacción:

* Ingresar datos del participante en la GUI.
* Tocar los sensores del cerebro para activar filtros.
* Presionar tecla 4 para resetear la imagen.
* Presionar q para guardar la sesión y salir.

## Disclaimer

Este proyecto fue desarrollado como una instalación artística interactiva, demostrando la capacidad de integrar sensores físicos de bajo costo con algoritmos de procesamiento de imagen.