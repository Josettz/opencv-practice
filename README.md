# 🖐️ Hand Gesture Controller

Proyecto de práctica con **OpenCV** y **MediaPipe** que permite controlar diferentes modos interactivos mediante gestos de mano capturados por la cámara web.

---

## Características

### 1. 🎆 Partículas y Efectos
Emite efectos de partículas desde la yema del dedo índice: fuego, chispas, magia y efecto fuente. Incluye trazos que siguen el movimiento de la mano.

### 2. 🎨 Dibujo Virtual
Dibuja libremente en pantalla usando el dedo índice. Soporta formas (círculo, rectángulo), cambio de color, deshacer/rehacer y borrado total.

### 3. ✊✌️✋ Piedra, Papel o Tijera
Juega contra la computadora usando gestos de mano. El sistema detecta tu jugada, la compara con la CPU y actualiza el marcador.

---

## Requisitos Previos

- Python 3.14 o superior
- Cámara web conectada

---

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/opencv-gesture-controller.git
cd opencv-gesture-controller
```

2. Instalar dependencias:

```bash
pip install opencv-python mediapipe numpy
```

3. Ejecutar:

```bash
python main.py
```

---

## Controles

### Menú Principal

| Gestión / Tecla | Acción |
|------------------|--------|
| 1 dedo levantado | Seleccionar Partículas y Efectos |
| 2 dedos levantados | Seleccionar Dibujo Virtual |
| 3 dedos levantados | Seleccionar Piedra, Papel o Tijera |
| `Q` | Salir de la aplicación |
| `ESC` | Volver al menú (dentro de un modo) |

### Modo Partículas y Efectos

| Gestión / Tecla | Acción |
|------------------|--------|
| Mano abierta | Modo fuego |
| Puño cerrado | Modo chispas |
| 1 dedo (índice) | Modo magia |
| 2 dedos (paz) | Modo fuente |
| `ESC` | Volver al menú |

### Modo Dibujo Virtual

| Gestión / Tecla | Acción |
|------------------|--------|
| Mano abierta | Dibujar libremente |
| Puño cerrado | Detener dibujo |
| 1 dedo (índice) | Marcar punto |
| 2 dedos (paz) | Deshacer último trazo |
| Pulgar arriba | Limpiar todo |
| Pinza (pulgar + índice) | Cambiar color |
| `Z` | Deshacer |
| `Y` | Rehacer |

### Modo Piedra, Papel o Tijera

| Gestión / Tecla | Acción |
|------------------|--------|
| Puño (Piedra) | Jugar Piedra |
| Mano abierta (Papel) | Jugar Papel |
| 2 dedos (Tijera) | Jugar Tijera |
| `R` | Reiniciar marcador |
| `ESC` | Volver al menú |

> **Nota:** En el modo Piedra, Papel o Tijera, el gesto debe mantenerse quieto durante 1.5 segundos para registrarse.

---

## Estructura del Proyecto

```
Opencv/
├── main.py              # Punto de entrada principal, menú y bucle de modos
├── hand_tracker.py      # Clase HandTracker (detección de manos con MediaPipe)
├── drawing.py           # Modo Dibujo Virtual (VirtualDrawer + GestureInterpreter)
├── particles.py         # Sistema de partículas y trazos
├── rps_game.py          # Lógica del juego Piedra, Papel o Tijera
└── hand_landmarker.task # Modelo de MediaPipe para detección de manos
```

| Archivo | Descripción |
|---------|-------------|
| `main.py` | Orquesta la aplicación: captura de video, menú interactivo y ejecución de los 3 modos |
| `hand_tracker.py` | Abstracción sobre MediaPipe Tasks: detección de landmarks, conteo de dedos y clasificación de gestos |
| `drawing.py` | Canvas virtual con gestos para dibujar, cambiar colores, deshacer y formas |
| `particles.py` | Sistema de partículas con física (gravedad, vida, opacidad) y trazos de dedo |
| `rps_game.py` | Juego contra la CPU con detección de gesto, temporización y marcador |
| `hand_landmarker.task` | Modelo pre-entrenado de MediaPipe para detección de 21 landmarks por mano |

---

## Tecnologías

- **OpenCV** — Captura de video, dibujo gráfico y procesamiento de imágenes
- **MediaPipe Tasks** — Detección y seguimiento de manos en tiempo real
- **NumPy** — Manipulación de arrays y cálculos numéricos
- **Python** — Lenguaje de programación

---

## Licencia

Este es un proyecto de práctica con fines educativos.
