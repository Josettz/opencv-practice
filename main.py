import cv2
import numpy as np
from hand_tracker import HandTracker
from particles import ParticleSystem, TrailSystem
from drawing import VirtualDrawer, GestureInterpreter
from rps_game import RPSGame


def draw_menu(frame, selected):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    title = "HAND GESTURE CONTROLLER"
    cv2.putText(frame, title, (w // 2 - 250, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    modes = [
        ("1. Particulas y Efectos", (0, 200, 255)),
        ("2. Dibujo Virtual", (255, 200, 0)),
        ("3. Piedra Papel o Tijera", (0, 255, 100)),
    ]

    for i, (text, color) in enumerate(modes):
        y = 150 + i * 80
        bg_color = (60, 60, 60) if selected == i else (40, 40, 40)
        border_color = color if selected == i else (100, 100, 100)
        cv2.rectangle(frame, (w // 2 - 200, y - 30), (w // 2 + 200, y + 30), bg_color, -1)
        cv2.rectangle(frame, (w // 2 - 200, y - 30), (w // 2 + 200, y + 30), border_color, 2)
        cv2.putText(frame, text, (w // 2 - 170, y + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    instructions = [
        "Muestra tu mano con los dedos para seleccionar:",
        "1 dedo = Opcion 1  |  2 dedos = Opcion 2  |  3 dedos = Opcion 3",
        "Presiona Q para salir",
    ]
    for i, text in enumerate(instructions):
        cv2.putText(frame, text, (w // 2 - 280, h - 80 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

    return frame


def draw_hud(frame, mode_name, extra_info=""):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 45), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    cv2.putText(frame, f"Modo: {mode_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    if extra_info:
        cv2.putText(frame, extra_info, (w - 350, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.putText(frame, "ESC = Menu  |  Q = Salir", (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
    return frame


def mode_particles(cap, tracker):
    particles = ParticleSystem(max_particles=1000)
    trails = TrailSystem(max_points=60)
    effect_mode = 0
    effect_names = ["Fuego", "Brillo", "Magia", "Fountain"]
    colors = [(0, 100, 255), (255, 255, 255), (255, 0, 255), (0, 255, 0)]

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame = tracker.find_hands(frame, draw=True)

        hands_count = 0
        if tracker.results.hand_landmarks:
            hands_count = len(tracker.results.hand_landmarks)

            for hand_idx in range(hands_count):
                lm_list = tracker.get_positions(frame, hand_idx)
                if len(lm_list) >= 21:
                    index_tip = lm_list[8][1], lm_list[8][2]
                    palm = lm_list[0][1], lm_list[0][2]

                    color = colors[effect_mode]
                    trails.add_point(hand_idx, index_tip[0], index_tip[1], color)

                    if effect_mode == 0:
                        particles.emit_fire(index_tip[0], index_tip[1], 5)
                    elif effect_mode == 1:
                        particles.emit_sparkle(index_tip[0], index_tip[1], 6)
                    elif effect_mode == 2:
                        particles.emit_magic(index_tip[0], index_tip[1], 8)
                    elif effect_mode == 3:
                        for dx in range(-15, 16, 5):
                            particles.emit(palm[0] + dx, palm[1], 2, color)

        particles.update()
        particles.draw(frame)
        trails.draw(frame)

        extra = f"Efecto: {effect_names[effect_mode]} | Manos: {hands_count} | Particulas: {len(particles.particles)}"
        frame = draw_hud(frame, "Particulas y Efectos", extra)

        cv2.putText(
            frame,
            "Muneca: Cambia efecto  |  Puño: Limpia",
            (10, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        cv2.imshow("Hand Controller", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break
        elif key == ord("q"):
            return "quit"
        elif key == ord(" "):
            effect_mode = (effect_mode + 1) % len(effect_names)
            trails.clear()

    return "menu"


def mode_drawing(cap, tracker):
    drawer = VirtualDrawer()
    interpreter = GestureInterpreter()
    color_idx = 0
    colors = [
        (0, 255, 255),
        (255, 0, 255),
        (255, 255, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 255),
    ]
    color_names = ["Amarillo", "Magenta", "Cyan", "Verde", "Rojo", "Blanco"]

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame = tracker.find_hands(frame, draw=False)

        gesture_text = ""
        if tracker.results.hand_landmarks:
            lm_list = tracker.get_positions(frame, 0)
            if len(lm_list) >= 21:
                index_tip = lm_list[8][1], lm_list[8][2]
                gesture = tracker.detect_gesture(lm_list)
                gesture_text = interpreter.interpret(gesture, index_tip[0], index_tip[1], drawer)

                cv2.circle(frame, index_tip, 8, drawer.brush_color, -1)
                cv2.circle(frame, index_tip, 12, (255, 255, 255), 1)

        tracker._draw_landmarks(frame)

        drawer.draw(frame)

        color_name = color_names[color_idx] if color_idx < len(color_names) else "?"
        extra = f"Gesto: {gesture_text} | Color: {color_name} | Trazos: {len(drawer.lines)}"
        frame = draw_hud(frame, "Dibujo Virtual", extra)

        instructions = [
            "Mano abierta = Dibujar  |  Puño = Parar",
            "2 dedos = Undo  |  Pulgar arriba = Limpiar",
            "Pinza = Cambiar color  |  1 dedo = Stampa",
        ]
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (10, 80 + i * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        cv2.imshow("Hand Controller", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break
        elif key == ord("q"):
            return "quit"

    return "menu"


def mode_rps(cap, tracker):
    game = RPSGame()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame = tracker.find_hands(frame, draw=True)

        if tracker.results.hand_landmarks:
            lm_list = tracker.get_positions(frame, 0)
            game.update(lm_list)
        else:
            game.state = "waiting"

        frame = game.draw(frame)
        frame = draw_hud(frame, "Piedra Papel o Tijera", "Muestra un gesto y mantente quieto")

        cv2.imshow("Hand Controller", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break
        elif key == ord("q"):
            return "quit"
        elif key == ord("r"):
            game.reset()

    return "menu"


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Error: No se pudo abrir la camara")
        return

    tracker = HandTracker(max_hands=2)
    selected_mode = 0

    cv2.namedWindow("Hand Controller", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame = tracker.find_hands(frame, draw=True)

        finger_count = 0
        if tracker.results.hand_landmarks:
            lm_list = tracker.get_positions(frame, 0)
            if len(lm_list) >= 21:
                finger_count = tracker.get_finger_count(lm_list)

                if finger_count >= 1 and finger_count <= 3:
                    selected_mode = finger_count - 1

        frame = draw_menu(frame, selected_mode)
        cv2.imshow("Hand Controller", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("1") or (key == 13 and selected_mode == 0):
            result = mode_particles(cap, tracker)
            if result == "quit":
                break
        elif key == ord("2") or (key == 13 and selected_mode == 1):
            result = mode_drawing(cap, tracker)
            if result == "quit":
                break
        elif key == ord("3") or (key == 13 and selected_mode == 2):
            result = mode_rps(cap, tracker)
            if result == "quit":
                break

    cap.release()
    tracker.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
