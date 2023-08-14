import json

from enum import Enum
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


class StitchWebhookEvents(str, Enum):
    payment = "payment"
    payment_confirmation = "payment.confirmation"
    payment_initiation = "payment-initiation"
    payment_initiation_confirmation = "payment-initiation.confirmation"
    refund = "refund"
    disbursement = "disbursement"
    settlement = "settlement"
    direct_deposit = "direct-deposit"
    transaction = "transaction"


class CreateWebhookSubscriptionRequest(BaseModel):
    url: str = Field(..., example="https://webhook.site/43ad7b98-f9e6-410f-83fa-cc2568b348bb")
    events: list[StitchWebhookEvents] = Field(..., example=json.dumps([event.value for event in StitchWebhookEvents]))


class CreateRefundRequest(BaseModel):
    amount: int = Field(..., example=1)
    currency: str = Field(..., example="ZAR")
    reason: str = Field(..., example="fraudulent")
    nonce: str = Field(..., example="XcnQUSskj4F4mF6K")
    beneficiary_reference: str = Field(..., example="refund-test-reference")
    payment_request_id: str


class CreateCardPaymentRequest(BaseModel):
    amount: int = Field(..., example=1)
    currency: str = Field(..., example="ZAR")
    external_reference: str = Field(..., example="random-external-id")
    merchant: str = Field(..., example="Acme Inc")
    payer_reference: str = Field(..., example="payer-ref")
    beneficiary_reference: str = Field(..., example="ben-ref")
