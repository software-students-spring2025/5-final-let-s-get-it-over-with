"""
ML Client - Processes and send webcam images to openAI API to generate comments
"""
import base64
import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
from binascii import Error as BinasciiError

from openai import OpenAI
from io import BytesIO
from PIL import Image 
import random

import cv2
import mediapipe as mp
import numpy as np
import traceback # for debugging
from random import choice, randint

# Flask app
app = Flask(__name__)

# load the mongoDB database
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbots"]
collection = db["messages"]

# Load OpenAI API key  
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key = openai_api_key)

# Fake usernames pool
user_pool = [
    "PixelPunk42", "NoScopeNate", "GGnGrace", "SnackAttack", "LootGoblin",
    "ClutchMaster", "VibeCheck", "StreamQueen", "LagSlayer", "CamChamp",
    "EmoteLord", "WaffleWizard", "CritKitty", "BoomHeadshot", "TTV_Jay",
    "SaltySocks", "PotionPete", "ChillCaster", "MemeMachine", "XPHunter"
]

# # Random colors and Twitch-like badge emojis
# user_styles = {user: {
#     "color": f"hsl({randint(0, 360)}, 70%, 60%)",  # vibrant color
#     "badge": choice(["🟪", "🔰", "⭐", "👑", "📛", "💬", "🎮"])
# } for user in user_pool}
    
@app.route("/generate-comment", methods=["POST"])
def generate_comment():
    # Retrieve the image and decode it
    print("DEBUG: Connection Successful") 
    # Extract image field from JSON data set in a request
    data = request.json.get("image")
    if not data:
        return jsonify({"error": "No image data received"}), 400

    # Extract and decode the incoming image into bytes
    try:
        _, encoded = data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
    except (ValueError, BinasciiError):
        return jsonify({"error": "Invalid base64 image"}), 400

    # convert bytes to pixels and process the image (e.g., analyze facial expression) 
    #image isnt being used?
    # image = Image.open(BytesIO(image_bytes))
    try:
        # Convert to OpenCV format
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if image_cv is None:
            raise ValueError("cv2.imdecode failed — possibly invalid image")

        # Detect face landmarks using Mediapipe
        mp_face = mp.solutions.face_mesh
        with mp_face.FaceMesh(static_image_mode=True) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

        expression = "neutral"
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            # smile detector using mouth corner distance and openness
            left_mouth= landmarks[61]  # mouth left corner
            right_mouth = landmarks[100]  # mouth right corner
            mouth_width = ((right_mouth.x - left_mouth.x) ** 2 + (right_mouth.y - left_mouth.y) ** 2) ** 0.5

            top_lip = landmarks[13]    # upper lip
            bottom_lip = landmarks[14] # lower lip
            mouth_height = abs(top_lip.y - bottom_lip.y)

            # NEEDS finetunning: frown detector: mouth corners are down
            mouth_center = landmarks[13]
            avg_corner_y = (left_mouth.y + right_mouth.y) / 2
            frown_check = mouth_center.y < avg_corner_y  # center pulled up = sad/frown

            # NEEDS finetunning: Sangry face detector based on eyebrow height difference and distance between two brows
            left_eyebrow = landmarks[70]
            left_eye = landmarks[159]
            right_eyebrow = landmarks[300]
            right_eye = landmarks[386]

            eyebrow_lift_left = left_eyebrow.y - left_eye.y
            eyebrow_lift_right = right_eyebrow.y - right_eye.y
            avg_eyebrow_lift = (eyebrow_lift_left + eyebrow_lift_right) / 2

            # Inner eyebrow pinch (near center)
            inner_left = landmarks[105]   
            inner_right = landmarks[334]
            eyebrow_pinch = abs(inner_left.x - inner_right.x)

            scores = {"smiling": 0, "angry": 0, "frowning": 0, "neutral": 1}

            # Smile score
            if mouth_width > 0.08 and mouth_height > 0.015:
                scores["smiling"] += 2

            # Angry score (eyebrow pulled down)
            if avg_eyebrow_lift < 0.015 and eyebrow_pinch < 0.035:
                scores["angry"] += 2

            # Frown score (mouth center higher than corners)
            if frown_check:
                scores["frowning"] += 2

            # Pick expression with highest score
            expression = max(scores, key=scores.get)

        # NEEDS finetunning
        mp_hands = mp.solutions.hands
        with mp_hands.Hands(static_image_mode=True, max_num_hands=2) as hands:
            hand_results = hands.process(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

        if hand_results.multi_hand_landmarks:
            expression = "waving"

    except Exception as e:
        print("ERROR during image analysis:", e)
        traceback.print_exc()
        return jsonify({"error": "Image processing failed", "details": str(e)}), 500

    print("Detected expression:", expression)
    # Simulate what the bot would "see" and say
<<<<<<< HEAD
    reaction_prompt = f"Write a short, fun, Twitch-style comment reacting to a webcam stream where the streamer looks like they're {expression}. Spam emojis and Twitch lingo. Keep it casual."
    
    random_prompt = random.choice([
        "Write a funny Twitch chat message with gamer lingo.",
        "Say something hype or supportive in Twitch style.",
        "Drop a playful comment you'd see in a Twitch livestream chat.",
        "React to the gameplay or stream vibe in a short Twitch message.",
        "Tease the  Twitch streamer like you're a regular viewer."
    ])

    # Randomly decide prompt type (70% reaction-based, 30% random)
    prompt = reaction_prompt if random.random() < 0.7 else random_prompt
=======
    prompt = "Write a comment reacting to a stream."
 
>>>>>>> e803f98f653a40d27ab3e958de7ef31415728f13

    try:
        # send request to OpenAI to generate twitch style comment
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are one of thousands of active viewers of the popular live streamer PrestonGames and love to participate in the chat. You are funny, type fast, use twich lingo like pog, lmao, kek, and also ask occasional questions. keep your responses short, less than 5 words. respond in either all lowercase or all caps"},
                {"role": "user",
                  "content": [
                        {"type": "text", "text": "React to this frame from the stream."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
                    ]}
            ],
            temperature=0.8,            # makes the response more random and fun
            presence_penalty=0.3,       # encourages more variety
            max_tokens=20               # limits response length 
        )
        print("RESPONSE:", response)
        message = response.choices[0].message.content
        print("MESSAGE", message)

        username = random.choice(user_pool)

        return jsonify({
            "comment": message,
            "username": username,
        })

    except Exception as e:
        print("DEBUG: IS THIS THE PROBLEM??")
        print ("EXCEPTION:", e)
        print ("EXCEPTION TYPE:", e.__class__)
        return jsonify({"error": str(e)}), 500   


@app.route("/process-question", methods=["POST"])
def process_question():
    # Get the question from the request
    data = request.json
    if not data or 'question' not in data:
        return jsonify({"error": "No question received"}), 400
    
    question = data['question']
    response_count = min(data.get('responseCount', 1), 5)  # Cap at 5 responses
    
    try:
        responses = []
        
        # Generate multiple responses with different personas
        personas = [
            "You're an excited and upbeat Twitch viewer who uses lots of emojis.",
            "You're a calm and supportive Twitch viewer who gives thoughtful responses.",
            "You're a funny Twitch viewer who likes to make jokes and puns.",
            "You're a Twitch viewer who's very knowledgeable about gaming and tech.",
            "You're a Twitch viewer who uses lots of slang and Twitch-specific terms."
        ]
        
        random.shuffle(personas)
        
        # Generate response_count responses using different personas
        for i in range(response_count):
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": personas[i % len(personas)] + "IMPORTANT: Always sound like a real, chill human who genuinely loves watching Twitch. Never mention you're AI—just be a casual gamer/viewer with personal takes, keep it under 2 sentences, and feel free to drop emojis"},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens= 30
            )
            
            message = response.choices[0].message.content
            responses.append(message)
            print(f"VOICE RESPONSE {i+1}:", message)
        
        # Return all responses
        return jsonify({"responses": responses})
    
    except Exception as e:
        print("ERROR PROCESSING QUESTION:", e)
        print("ERROR TYPE:", e.__class__)
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)