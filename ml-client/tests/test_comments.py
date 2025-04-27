import cv2
import mediapipe as mp
import numpy as np
from io import BytesIO
from PIL import Image
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import comments
import base64

def analyze_expression(image_bytes):
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image_cv is None:
        raise ValueError("cv2.imdecode failed — possibly invalid image")

    mp_face = mp.solutions.face_mesh
    with mp_face.FaceMesh(static_image_mode=True) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

    expression = "neutral"
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        left_mouth = landmarks[61]
        right_mouth = landmarks[100]
        mouth_width = ((right_mouth.x - left_mouth.x) ** 2 + (right_mouth.y - left_mouth.y) ** 2) ** 0.5

        top_lip = landmarks[13]
        bottom_lip = landmarks[14]
        mouth_height = abs(top_lip.y - bottom_lip.y)

        mouth_center = landmarks[13]
        avg_corner_y = (left_mouth.y + right_mouth.y) / 2
        frown_check = mouth_center.y < avg_corner_y

        left_eyebrow = landmarks[70]
        left_eye = landmarks[159]
        right_eyebrow = landmarks[300]
        right_eye = landmarks[386]

        eyebrow_lift_left = left_eyebrow.y - left_eye.y
        eyebrow_lift_right = right_eyebrow.y - right_eye.y
        avg_eyebrow_lift = (eyebrow_lift_left + eyebrow_lift_right) / 2

        inner_left = landmarks[105]
        inner_right = landmarks[334]
        eyebrow_pinch = abs(inner_left.x - inner_right.x)

        scores = {"smiling": 0, "angry": 0, "frowning": 0, "neutral": 1}

        if mouth_width > 0.08 and mouth_height > 0.015:
            scores["smiling"] += 2

        if avg_eyebrow_lift < 0.015 and eyebrow_pinch < 0.035:
            scores["angry"] += 2

        if frown_check:
            scores["frowning"] += 2

        expression = max(scores, key=scores.get)

    mp_hands = mp.solutions.hands
    with mp_hands.Hands(static_image_mode=True, max_num_hands=2) as hands:
        hand_results = hands.process(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

    if hand_results.multi_hand_landmarks:
        expression = "waving"

    return expression

def get_test_image_bytes():
    img = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()

def test_expression_analysis_returns_valid_expression():
    image_bytes = get_test_image_bytes()
    expression = analyze_expression(image_bytes)
    assert expression in {"neutral", "smiling", "angry", "frowning", "waving"}


