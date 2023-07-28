import base64
import hashlib
import json
import requests
import secrets
import uvicorn

from fastapi import FastAPI
from graphqlclient import GraphQLClient
from urllib.parse import urlencode

from settings import settings
from src.models import PaymentRequestWebhookResponseModel


app = FastAPI(title="Stitch sample integration")

graphql_client = GraphQLClient("https://api.stitch.money/graphql")

def get_access_token():
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

@app.get("/payment_request")
async def generate_payment_request_url():
    client_token = get_access_token()
    graphql_client.inject_token(f"Bearer {client_token['access_token']}")
    print("The access token is: ", client_token['access_token'])
    print("___________________________________________________________")
    
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
            "quantity": 1,
            "currency": "ZAR"
        },
        "payerReference": "KombuchaFizz",
        "beneficiaryReference": "Joe-Fizz-01",
        "externalReference": "example-e32e5478-325b-4869-a53e-2021727d2afe",
        "beneficiaryName": "FizzBuzz Co.",
        "beneficiaryBankId": "fnb",
        "beneficiaryAccountNumber": "123456789",
        "merchant": "{merchantId: '123', merchantName: 'Acme Inc'}"
    }
    
    response = graphql_client.execute(query, variables)
    
    return json.loads(response)
    
    
# @app.post("/subscribe/payment")
# async def create_payment_subscription():
#     webhook_return_url = "https://localhost:8000/webhoooks/payment"

#     query = f"""
#         mutation clientWebhookAdd {{
#             clientWebhookAdd(input: {{
#                 url: {webhook_return_url},
#                 filterTypes: ["payments"]
#             }}) {{
#                 url
#                 filterTypes
#                 secret
#                 id
#             }}
#         }}
#     """
    
#     client_token = get_access_token()
#     graphql_client.inject_token(f"Bearer {client_token['access_token']}")
#     response = graphql_client.execute(query)
    
#     return json.loads(response)
    

# @app.post("/webhoooks/payment")
# async def webhooks_payment_request(data: PaymentRequestWebhookResponseModel):
#     return data
    

@app.get("/return")
async def return_url():
    """
    Method to handle redirect once the user has completed payment
    """
    return 200, "Ok"


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
