import os
import requests
from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

# Vérifie que la clé OpenAI est bien définie
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ L'environnement OPENAI_API_KEY n'est pas défini !")
client = OpenAI(api_key=OPENAI_API_KEY)

# Token GitHub (PR comments)
GH_TOKEN = "SHA256:kMJS9VJFqkWVVdWP90i+IjXZLDQcomk+3CD4OM1kljc"

def analyze_code(code):
    prompt = f"""
You are an expert code reviewer.
Analyze the following code and provide:
- bugs
- improvements
- security issues
- performance tips

Code:
{code}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


# -----------------------------
# Route ping pour tester le serveur
# -----------------------------
@app.get("/")
def root():
    return {"message": "Server is running! GitHub webhook is ready."}


# -----------------------------
# Webhook GitHub
# -----------------------------
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    # Vérifie si c'est l'ouverture d'une PR
    if payload.get("action") == "opened" and "pull_request" in payload:
        files_url = payload["pull_request"]["url"] + "/files"
        headers = {"Authorization": f"token {GH_TOKEN}"}

        files = requests.get(files_url, headers=headers).json()

        review_text = ""

        for f in files:
            if f.get("patch"):
                review = analyze_code(f["patch"])
                review_text += f"\n### File: {f['filename']}\n{review}\n"

        comment_url = payload["pull_request"]["comments_url"]
        data = {"body": f"🤖 AI Code Review\n{review_text}"}

        requests.post(comment_url, headers=headers, json=data)

        print("AI review posted!")

    return {"status": "ok"}
