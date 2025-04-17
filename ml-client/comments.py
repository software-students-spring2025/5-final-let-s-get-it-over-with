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


# Flask app
app = Flask(__name__)

# load the mongoDB database
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbots"]
collection = db["messages"]

# Load OpenAI API key 
client = OpenAI()
# openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/generate-comment", methods=["POST"])
def generate_comment():
    # Retrieve the image and decode it
    print("DEBUG: Connection Successfull")
    data = request.json.get("image")
    if not data:
        return jsonify({"error": "No image data received"}), 400

    try:
        _, encoded = data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
    except (ValueError, BinasciiError):
        return jsonify({"error": "Invalid base64 image"}), 400

    # process the image (e.g., analyze facial expression)
    image = Image.open(BytesIO(image_bytes))

    # Simulate what the bot would "see" and say
    prompt = "Write a short, fun, Twitch-style comment reacting to a webcam stream. Spam emojis and Twitch lingo. Keep it casual."

    try:
        # send request to OpenAI to generate twitch style comment
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a viewer of a Twicth livestream."},
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)