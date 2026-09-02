import cv2
import random
import time


class RPSGame:
    def __init__(self):
        self.choices = ["piedra", "papel", "tijera"]
        self.emojis = {"piedra": "✊", "papel": "✋", "tijera": "✌️"}
        self.scores = {"player": 0, "cpu": 0, "ties": 0}
        self.state = "waiting"
        self.player_choice = None
        self.cpu_choice = None
        self.result_text = ""
        self.result_color = (255, 255, 255)
        self.countdown = 0
        self.last_change_time = 0
        self.cooldown = 0

    def detect_gesture(self, lm_list):
        if len(lm_list) < 21:
            return None

        fingers = []
        # Pulgar
        if lm_list[4][1] > lm_list[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # Otros dedos
        for i in [8, 12, 16, 20]:
            if lm_list[i][2] < lm_list[i - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        total = sum(fingers)

        if total == 0:
            return "piedra"
        elif total == 5:
            return "papel"
        elif fingers == [0, 1, 1, 0, 0] or fingers == [0, 1, 0, 0, 0]:
            return "tijera"
        return None

    def resolve(self, player, cpu):
        if player == cpu:
            self.scores["ties"] += 1
            self.result_text = "EMPATE!"
            self.result_color = (0, 255, 255)
        elif (
            (player == "piedra" and cpu == "tijera")
            or (player == "papel" and cpu == "piedra")
            or (player == "tijera" and cpu == "papel")
        ):
            self.scores["player"] += 1
            self.result_text = "GANASTE!"
            self.result_color = (0, 255, 0)
        else:
            self.scores["cpu"] += 1
            self.result_text = "PERDISTE!"
            self.result_color = (0, 0, 255)

    def update(self, lm_list):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        gesture = self.detect_gesture(lm_list)

        if gesture and gesture != self.player_choice:
            self.player_choice = gesture
            self.last_change_time = time.time()
            self.state = "ready"
        elif gesture is None:
            self.state = "waiting"
            self.player_choice = None

        if self.state == "ready" and self.player_choice:
            if time.time() - self.last_change_time > 1.5:
                self.cpu_choice = random.choice(self.choices)
                self.resolve(self.player_choice, self.cpu_choice)
                self.state = "result"
                self.cooldown = 90

    def draw(self, frame):
        h, w = frame.shape[:2]

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        score_text = f"Jugador: {self.scores['player']}  |  CPU: {self.scores['cpu']}  |  Empates: {self.scores['ties']}"
        cv2.putText(frame, score_text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        if self.state == "waiting":
            cv2.putText(
                frame,
                "Muestra tu mano: Piedra, Papel o Tijera",
                (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )
        elif self.state == "ready":
            cv2.putText(
                frame,
                f"Tu mano: {self.player_choice.upper()} - Manten quieto...",
                (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
        elif self.state == "result":
            cv2.putText(
                frame,
                f"Tu: {self.player_choice.upper()}  vs  CPU: {self.cpu_choice.upper()}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
            cv2.putText(
                frame,
                self.result_text,
                (w // 2 - 120, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                self.result_color,
                4,
            )

        return frame

    def reset(self):
        self.scores = {"player": 0, "cpu": 0, "ties": 0}
        self.state = "waiting"
        self.player_choice = None
        self.cpu_choice = None
        self.result_text = ""
