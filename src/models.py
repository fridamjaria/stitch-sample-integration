from pydantic import BaseModel, Field


class PaymentRequestWebhookResponse(BaseModel):
    id: str
    filter_type: list[str]
    secret: str
    url: str


class GeneratePaymentRequestUrlRequest(BaseModel):
    amount: int = Field(..., example=1)
    currency: str = Field(..., example="ZAR")
    payment_reference: str = Field(..., example="Stitch Test")
    beneficiary_reference: str = Field(..., example="Testlocal")
    external_reference: str = Field(..., example="random-external-id")
    beneficiary_name: str = Field(..., example="FizzBuzz Co.")
    beneficiary_bank_id: str = Field(..., example="fnb")
    beneficiary_account_nummber: str = Field(..., example="123456789")
    merchant: str = Field(..., example="Acme Inc")


class PaymentInitiationRequest(BaseModel):
    id: str
    url: str


class GeneratePaymentRequestUrlResponse(BaseModel):
    id: str
    url: str
