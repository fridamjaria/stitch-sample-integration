import base64
import hashlib
import json
import requests
import secrets
import uvicorn

from fastapi import FastAPI, Body, HTTPException
from urllib.parse import quote, urlencode

from settings import settings
from src.models import (
    CreateWebhookSubscriptionRequest,
    GeneratePaymentRequestUrlRequest,
    GeneratePaymentRequestUrlResponse,
    PaymentInitiationRequest,
    PaymentRequestWebhookResponse
)


app = FastAPI(title="Stitch sample integration")

STITCH_API_URL = "https://api.stitch.money/graphql"
STITCH_AUTH_URL = "https://secure.stitch.money/connect/token"
REDIRECT_URI = "https://localhost:8000/return"


def get_access_token():
    
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


def get_headers():
    client_token = get_access_token()
    bearer_token = f"Bearer {client_token['access_token']}"
    print("The access token is: ", bearer_token)
    print("_______________________________________________________")
    headers = { 
        "Content-Type": "application/json",
        "Authorization": bearer_token
    }
    
    return headers


@app.get("/client_token")
async def get_client_access_token():
    return get_access_token()


@app.get("/user_auth_url")
async def get_user_authorization_url():
    def generate_nonce_or_state():
        bytes = secrets.token_bytes(32)
        hex = bytes.hex()
        return hex
    
    def generate_code_verifier_and_challenge():
        # this should be between 43 and 128
        verifier_length = 56

        code_verifier = secrets.token_urlsafe(96)[:verifier_length]
        hashed = hashlib.sha256(code_verifier.encode("ascii")).digest()
        encoded = base64.urlsafe_b64encode(hashed)
        code_challenge = encoded.decode("ascii")[:-1]
        
        return code_verifier, code_challenge
    
    # 1. Obtain the auth code
    code_verifier, code_challenge = generate_code_verifier_and_challenge()
    
    nonce = generate_nonce_or_state()
    state = generate_nonce_or_state()
    
    query_params = {
        "client_id": settings.STITCH_CLIENT_ID,
        "scope": "client_paymentrequest",
        "client_secret": settings.STITCH_CLIENT_SECRET,
        "response_type": "code",
        "redirect_uri": "https://localhost:8000/return",
        "nonce": nonce,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
        
    authorization_url = "https://secure.stitch.money/connect/authorize?" + urlencode(query_params)
    
    return authorization_url


@app.post("/payment_request", response_model=GeneratePaymentRequestUrlResponse)
async def generate_payment_request_url(body: GeneratePaymentRequestUrlRequest = Body(...)):
    query = """
        mutation CreatePaymentRequest(
            $amount: MoneyInput!,
            $payerReference: String!,
            $beneficiaryReference: String!,
            $externalReference: String,
            $beneficiaryName: String!,
            $beneficiaryBankId: BankBeneficiaryBankId!,
            $beneficiaryAccountNumber: String!,
            $merchant: String
        ) {
            clientPaymentInitiationRequestCreate(input: {
                amount: $amount,
                payerReference: $payerReference,
                beneficiaryReference: $beneficiaryReference,
                externalReference: $externalReference,
                beneficiary: {
                    bankAccount: {
                        name: $beneficiaryName,
                        bankId: $beneficiaryBankId,
                        accountNumber: $beneficiaryAccountNumber
                    }
                },
                merchant: $merchant
            }) {
                paymentInitiationRequest {
                    id
                    url
                }
            }  
        }
    """
    
    variables = {
        "amount": {
            "quantity": body.amount,
            "currency": body.currency,
        },
        "payerReference": body.payment_reference,
        "beneficiaryReference": body.beneficiary_reference,
        "externalReference": body.external_reference,
        "beneficiaryName": body.beneficiary_name,
        "beneficiaryBankId": body.beneficiary_bank_id,
        "beneficiaryAccountNumber": body.beneficiary_account_nummber,
        "merchant": body.merchant,
    }
    
    response = requests.post(
        url=STITCH_API_URL, 
        data=json.dumps({"query": query, "variables": variables}), 
        headers=get_headers()
    )
    
    response_data = response.json()
    
    if "errors" in response_data:
        raise HTTPException(status_code=500, detail=response_data)
    
    payment_initiation_request = PaymentInitiationRequest.model_validate(
        response_data["data"]["clientPaymentInitiationRequestCreate"]["paymentInitiationRequest"]
    )

    return GeneratePaymentRequestUrlResponse(
        id=payment_initiation_request.id, 
        url=f"{payment_initiation_request.url}?redirect_uri={quote(REDIRECT_URI)}"
    )
    
    
@app.post("/webhooks/subscribe")
async def create_webhook_subscription(data: CreateWebhookSubscriptionRequest):
    query = f"""
        mutation clientWebhookAdd {{
            clientWebhookAdd(input: {{
                url: "{data.url}",
                filterTypes: {json.dumps([event.value for event in data.events])}
            }}) {{
                url
                filterTypes
                secret
                id
            }}
        }}
    """
    
    response = requests.post(
        url=STITCH_API_URL, 
        data=json.dumps({"query": query}), 
        headers=get_headers()
    )
    
    response_data = response.json()
    
    if "errors" in response_data:
        raise HTTPException(status_code=500, detail=response_data)
    
    return response.json()


@app.get("/webhooks/dashboard_link")
async def generate_dashboard_link():
    query = """
        query GenerateDashboardLink {
            client {
                webhookLogin {
                    url
                }
            }
        }
    """
    # query = f"""
    #     query GenerateDashboardLink {{
    #         client {{
    #             webhookLogin {{
    #             url
    #             }}
    #         }}
    #     }}
    # """
    
    response = requests.post(
        url=STITCH_API_URL, 
        data=json.dumps({"query": query}), 
        headers=get_headers()
    )
    
    response_data = response.json()
    
    if "errors" in response_data:
        raise HTTPException(status_code=500, detail=response_data)
    
    return response.json()


@app.get("/return")
async def redirect():
    return 200, "Ok"


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
