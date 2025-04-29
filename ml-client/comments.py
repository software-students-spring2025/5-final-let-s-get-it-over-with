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
import traceback  # for debugging
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
openai_client = OpenAI(api_key=openai_api_key)

# Fake usernames pool
user_pool = [
    "PixelPunk42", "noScopeNate", "gGnGrac3", "snack_att4ck", "lootg0blin",
    "clutchM4ster", "v1beCheck", "streamqueen7", "lagSlay3r", "camchmp",
    "3mot3Lord", "w4ffleWizard", "cr1tK1tty", "boom_headsh0t", "ttv_jay",
    "s4ltySocks", "p0tionPet3", "ch1llcaster", "mememachine23", "xpHunt3r",
    "afk_ang3l", "qu1ckscope_su3", "m4na_mus3", "t1ltedtina", "gh0st_ping",
    "respawnRon77", "dps_Daisy_", "banhamm3r", "troll.tam3r", "dr0pBearDan",
    "claptrapKev", "p1xelP1rat3", "ggGalaxyx", "echo_essence", "nerf.n1na",
    "xpleech3r", "metamilo", "snaccPacc", "baitm4ster", "camp_k1ng",
    "pingPanda_", "zoomerZ3d", "mute_m1k3", "framedropfred", "potionNova",
    "silentSn1pez", "no0bslayer", "alt_tab_tom", "queueQueen88", "sweatl0rd",
    "tofuOverlord", "kiw1juiice", "bl1nk.n0pe", "muffinmistake", "yeet_2025",
    "casualfr1day", "rebootedkat", "breadslice_v2", "emoj1spammer", "null_typ3",
    "glitchgr4ndpa", "nightOwl44", "3mberw1ng", "boba_overdose", "xtraCheezy",
    "flatpackfiend", "coldbrew_99", "moon.bag", "flashbang12", "whalecry",
    "meowm0d", "tripletacos", "awk_r3na", "spookyCarrot", "404_user_here",
    "sushi_dad", "kr0n0z", "b3ep_b00p", "quiet.clickz", "goldfish_wish",
    "void_vibes", "killYourWiFi", "simpForStars", "duck_onboard", "milkdrop_7",
    "blank_space", "nerdSoup123", "jackedApplet", "bitz.n.bobs", "fresh_oats",
    "warmboot", "1c3cubee", "rage_p0et", "nvm.ok", "offbeat.drumz",
    "gummyphon3", "leaf.exe", "tvstaticcc", "tripwire.me", "catfactz_irl", "gl1tchm0de", "snaccident", "voidlet", "b33pbloop", "fraggot", 
    "sh4dowfax", "n1ghtbloom", "dr1zzle", "crunchee", "laggedout", 
    "p1x3lburn", "m0n0chrome", "wobbl3", "tw33kz", "hushbyte", 
    "gr1mble", "f1zzletop", "v1beseek3r", "snoozaloo", "blurzt", 
    "sp00kify", "j1ggletank", "zapple", "muxify", "chompr"
]

  
@app.route("/generate-comment", methods=["POST"])
def generate_comment():
    # Retrieve the image and decode it
    print("DEBUG: Connection Successful")
    # Extract image field from JSON data set in a request
    data = request.json.get("image")
    session_username = request.json.get("username") # Might need to remove this 
    if not data:
        return jsonify({"error": "No image data received"}), 400

    # Extract and decode the incoming image into bytes
    try:
        _, encoded = data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
    except (ValueError, BinasciiError):
        return jsonify({"error": "Invalid base64 image"}), 400

    # convert bytes to pixels and process the image (e.g., analyze facial expression) 
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
            left_mouth = landmarks[61]  # mouth left corner
            right_mouth = landmarks[100]  # mouth right corner
            mouth_width = (
                (right_mouth.x - left_mouth.x) ** 2 
                + (right_mouth.y - left_mouth.y) ** 2
            ) ** 0.5

            top_lip = landmarks[13]  # upper lip
            bottom_lip = landmarks[14]  # lower lip
            mouth_height = abs(top_lip.y - bottom_lip.y)

            # NEEDS finetunning: frown detector: mouth corners are down
            mouth_center = landmarks[13]
            avg_corner_y = (left_mouth.y + right_mouth.y) / 2
            frown_check = mouth_center.y < avg_corner_y  # center pulled up = sad/frown

            # NEEDS finetunning: angry face detector based on eyebrow height difference and distance between two brows
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
    # Remove the session_username??
    reaction_prompt = f"Write a short, fun, Twitch-style comment reacting to a webcam stream where the streamer looks like they're {expression} in less than 5 words"
    video_prompt = "React to this frame from the stream"

    # Randomly decide prompt type (60% video-based, 40% reaction to facial expressions)
    prompt = video_prompt if random.random() < 0.6 else reaction_prompt

    try:
        # send request to OpenAI to generate twitch style comment
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": 'You are one of thousands of active viewers of a live streamer and love to participate in the chat. You are funny, type fast, use twich lingo like pog, lmao, kek, and also ask occasional questions. keep your responses short, less than 5 words. respond in either all lowercase or all caps',
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": prompt,
                        },
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                        },
                     ],
                },
            ],
            temperature=0.8,  # makes the response more random and fun
            presence_penalty=0.3,  # encourages more variety
            max_tokens=20  # limits response length 
        )
        print("RESPONSE:", response)
        message = response.choices[0].message.content
        print("MESSAGE", message)

        username = random.choice(user_pool)

        return jsonify(
            {
                "comment": message,
                "username": username,
            }
        )

    except Exception as e:
        print("DEBUG: IS THIS THE PROBLEM??")
        print("EXCEPTION:", e)
        print("EXCEPTION TYPE:", e.__class__)
        return jsonify({"error": str(e)}), 500


@app.route("/process-question", methods=["POST"])
def process_question():
    # Get the question from the request
    data = request.json
    if not data or "question" not in data:
        return jsonify({"error": "No question received"}), 400
    
    question = data["question"]
    response_count = min(data.get("responseCount", 1), 5)  # Cap at 5 responses
    
    try:
        responses = []
        
        # Generate multiple responses with different personas
        personas = [
            "You're an excited and upbeat Twitch viewer who uses lots of emojis.",
            "You're a calm and supportive Twitch viewer who gives thoughtful responses.",
            "You're a funny Twitch viewer who likes to make jokes and puns.",
            "You're a Twitch viewer who's very knowledgeable about gaming and tech.",
            "You're a Twitch viewer who uses lots of slang and Twitch-specific terms.",
        ]
        
        random.shuffle(personas)
        
        # Generate response_count responses using different personas
        for i in range(response_count):
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": personas[i % len(personas)] + "You are one of thousands of active viewers of a live streamer and love to participate in the chat. You are funny, type fast, use twich lingo like pog, lmao, kek, and also ask occasional questions. keep your responses short, less than 5 words. respond in either all lowercase or all caps",
                    },
                    {
                        "role": "user", 
                        "content": question,
                    }
                ],
                temperature=0.7,
                max_tokens=20
            )
            
            message = response.choices[0].message.content
            random_username = random.choice(user_pool)

            # Instead of just appending message, append a dictionary
            responses.append({
                "username": random_username,
                "comment": message
            })

            print(f"VOICE RESPONSE {i+1}: {message} from {random_username}")
        
        # Return all responses
        return jsonify({"responses": responses})
    
    except Exception as e:
        print("ERROR PROCESSING QUESTION:", e)
        print("ERROR TYPE:", e.__class__)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)