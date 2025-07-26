import os
import requests
import openai
from dotenv import load_dotenv

# ==== Load secrets ====
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ACCESS_TOKEN = os.getenv("IG_PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("IG_PAGE_ID")
RECIPIENT_IG_USERNAME = "you_me_explore_experience"  # Your IG test handle

# ==== OpenAI Setup ====
openai.api_key = OPENAI_API_KEY

def generate_mcat_question():
    prompt = """Generate one high-yield MCAT-style Psychology/Sociology multiple-choice question.
Include:
- Question stem
- 4 choices (A–D)
- Correct answer (just letter)
- Short explanation
- Mnemonic
- Motivational quote from Mom
- AMCAS tip of the day

Return JSON format:
{
  "question": "...",
  "choices": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "B",
  "explanation": "...",
  "mnemonic": "...",
  "quote": "...",
  "amcas_tip": "..."
}"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return eval(response.choices[0].message.content)

def send_dm_to_inbox(message):
    """
    Sends the MCAT question to the page inbox (works if the user already messaged you).
    """
    url = f"https://graph.facebook.com/v19.0/me/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # For testing, you need the IG user to have messaged first to page inbox to establish a thread
    # Replace recipient ID with a known PSID (page-scoped user ID) if available
    payload = {
        "messaging_type": "UPDATE",
        "recipient": {
            # TEMP placeholder — requires webhook or thread from actual message
            "id": "<RECIPIENT_ID>"
        },
        "message": {
            "text": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Response:", response.status_code, response.text)

def main():
    quiz = generate_mcat_question()
    message = f"""🧠 MCAT InstaDose

{quiz['question']}
{quiz['choices'][0]}
{quiz['choices'][1]}
{quiz['choices'][2]}
{quiz['choices'][3]}

Reply A/B/C/D to answer."""

    print("=== Generated Quiz ===")
    print(message)
    print("======================")

    # TODO: send_dm_to_inbox(message)
    # Sending will work once a conversation is started manually in IG inbox

if __name__ == "__main__":
    main()
