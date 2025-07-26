from flask import Flask, request
from dotenv import load_dotenv
import os
import requests
import json


app = Flask(__name__)
load_dotenv()

VERIFY_TOKEN = "mcat_instadose_123"
ACCESS_TOKEN = os.getenv("IG_PAGE_ACCESS_TOKEN")

# Load latest MCAT question for reply logic
with open("quiz_of_the_day.json", "r") as f:
    LAST_QUIZ = json.load(f)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verification handshake from Meta
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    if request.method == "POST":
        data = request.get_json()
        print("[ok] Received webhook:", json.dumps(data, indent=2))

        try:
            for entry in data["entry"]:
                for event in entry["messaging"]:
                    sender_id = event["sender"]["id"]
                    message_text = event.get("message", {}).get("text", "").strip().upper()

                    if message_text in ["A", "B", "C", "D"]:
                        reply = build_feedback(message_text)
                        send_reply(sender_id, reply)
        except Exception as e:
            print("❌ Error processing webhook:", e)

        return "ok", 200

def build_feedback(user_answer):
    correct = LAST_QUIZ["answer"].upper()
    is_correct = (user_answer == correct)

    emoji = "✅" if is_correct else "❌"
    status = "Correct!" if is_correct else f"Oops! Correct answer was {correct}"

    return f"""{emoji} {status}

📘 Explanation: {LAST_QUIZ['explanation']}
🧠 Mnemonic: {LAST_QUIZ['mnemonic']}
💬 Mom’s Quote: {LAST_QUIZ['quote']}
🩺 AMCAS Tip: {LAST_QUIZ['amcas_tip']}"""

def send_reply(recipient_id, message):
    url = "https://graph.facebook.com/v19.0/me/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }

    print(f"📤 Sending reply to {recipient_id}:\n{message}")
    res = requests.post(url, headers=headers, json=payload)
    print("📦 Reply Status:", res.status_code, res.text)

if __name__ == "__main__":
    print("[ok] Webhook running on http://localhost:5000")
    print("[internet] Use your LocalTunnel URL (e.g., https://tired-pots-act.loca.lt/webhook) in Meta Webhook config")
    app.run(port=5000)



