import requests
import uvicorn

from fastapi import FastAPI
from settings import settings


app = FastAPI(title="Stitch sample integration")

@app.get("/client_token")
async def get_client_access_token():
    STITCH_AUTH_URL = "https://secure.stitch.money/connect/token"
    response = requests.post(STITCH_AUTH_URL, data={
        "client_id": settings.STITCH_CLIENT_ID,
        "scope": "client_paymentrequest",
        "client_secret": settings.STITCH_CLIENT_SECRET,
        "audience": STITCH_AUTH_URL,
        "grant_type": "client_credentials",
    })
    
    # raise error for non 2xx response
    response.raise_for_status()
    
    return response.json()

@app.get("/return")
async def return_url():
    return 200, "Ok"


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
