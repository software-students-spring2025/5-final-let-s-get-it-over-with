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



@app.route("/generate-comment", methods=["POST"])
def generate_comment():
    # Retrieve the image and decode it
    print("DEBUG: Connection Successful") 
    #Extract image field from JSON data set in a request
    data = request.json.get("image")
    if not data:
        return jsonify({"error": "No image data received"}), 400

    try:
        _, encoded = data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
    except (ValueError, BinasciiError):
        return jsonify({"error": "Invalid base64 image"}), 400

    # process the image (e.g., analyze facial expression) 
    #image isnt being used?
    image = Image.open(BytesIO(image_bytes))

    # Simulate what the bot would "see" and say
    prompt = "Write a short, fun, Twitch-style comment reacting to a webcam stream. Spam emojis and Twitch lingo. Keep it casual."
 

    #ERROR: 
    try:
        # send request to OpenAI to generate twitch style comment
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a viewer of a Twitch livestream."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8, # makes the response more random and fun
            max_tokens=20   # limits response length 
        )
        print("RESPONSE:", response)
        message = response.choices[0].message.content
        print("MESSAGE", message)
        return jsonify({"comment": message})
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