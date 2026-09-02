import math

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision


class HandTracker:
    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (9, 10), (10, 11), (11, 12),
        (13, 14), (14, 15), (15, 16),
        (17, 18), (18, 19), (19, 20),
        (0, 17), (2, 5), (5, 9), (9, 13), (13, 17),
    ]

    LANDMARK_NAMES = [
        "wrist", "thumb_cmc", "thumb_mcp", "thumb_ip", "thumb_tip",
        "index_mcp", "index_pip", "index_dip", "index_tip",
        "middle_mcp", "middle_pip", "middle_dip", "middle_tip",
        "ring_mcp", "ring_pip", "ring_dip", "ring_tip",
        "pinky_mcp", "pinky_pip", "pinky_dip", "pinky_tip",
    ]

    def __init__(self, max_hands=2, detection_confidence=0.5, tracking_confidence=0.5):
        self.max_hands = max_hands
        self.tip_ids = [4, 8, 12, 16, 20]
        base_options = mp_python.BaseOptions(model_asset_path="hand_landmarker.task")
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.results = None

    def _to_mp_image(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    def find_hands(self, frame, draw=True):
        mp_image = self._to_mp_image(frame)
        self.results = self.landmarker.detect(mp_image)
        if draw:
            self._draw_landmarks(frame)
        return frame

    def _draw_landmarks(self, frame):
        if not self.results.hand_landmarks:
            return
        h, w, _ = frame.shape
        for hand_landmarks in self.results.hand_landmarks:
            points = [
                (int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks
            ]
            for conn in self.HAND_CONNECTIONS:
                p1 = points[conn[0]]
                p2 = points[conn[1]]
                cv2.line(frame, p1, p2, (0, 255, 0), 2)
            for point in points:
                cv2.circle(frame, point, 4, (0, 0, 255), -1)

    def get_positions(self, frame, hand_index=0):
        lm_list = []
        if self.results.hand_landmarks and hand_index < len(self.results.hand_landmarks):
            h, w, _ = frame.shape
            for id, lm in enumerate(self.results.hand_landmarks[hand_index]):
                lm_list.append((id, int(lm.x * w), int(lm.y * h)))
        return lm_list

    def fingers_up(self, lm_list):
        fingers = []
        if len(lm_list) < 21:
            return fingers

        if lm_list[self.tip_ids[0]][1] > lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        for i in range(1, 5):
            if lm_list[self.tip_ids[i]][2] < lm_list[self.tip_ids[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def get_finger_count(self, lm_list):
        fingers = self.fingers_up(lm_list)
        return sum(fingers)

    def get_landmark_pos(self, lm_list, landmark_id):
        if landmark_id < len(lm_list):
            return (lm_list[landmark_id][1], lm_list[landmark_id][2])
        return None

    def distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def is_pinch(self, lm_list, threshold=40):
        if len(lm_list) < 21:
            return False
        thumb_tip = self.get_landmark_pos(lm_list, 4)
        index_tip = self.get_landmark_pos(lm_list, 8)
        if thumb_tip and index_tip:
            return self.distance(thumb_tip, index_tip) < threshold
        return False

    def detect_gesture(self, lm_list):
        if len(lm_list) < 21:
            return "none"

        fingers = self.fingers_up(lm_list)
        total = sum(fingers)

        if total == 0:
            return "fist"
        elif total == 5:
            return "open"
        elif fingers == [0, 1, 0, 0, 0]:
            return "point"
        elif fingers == [0, 1, 1, 0, 0]:
            return "peace"
        elif total == 1 and fingers[0] == 1:
            return "thumbs_up"
        elif self.is_pinch(lm_list):
            return "pinch"
        return "other"

    def release(self):
        if hasattr(self, "landmarker"):
            self.landmarker.close()
