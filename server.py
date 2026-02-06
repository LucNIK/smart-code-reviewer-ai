import requests
from fastapi import FastAPI, Request

app = FastAPI()

GH_TOKEN = "TON_PERSONAL_ACCESS_TOKEN_ICI"  # ton token GitHub

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    if payload.get("action") == "opened" and "pull_request" in payload:
        pr_url = payload["pull_request"]["comments_url"]
        data = {"body": "🤖 AI review started! This is a test comment."}
        headers = {"Authorization": f"token {GH_TOKEN}"}
        requests.post(pr_url, headers=headers, json=data)
        print("Commentaire posté sur la PR !")

    return {"status": "ok"}
