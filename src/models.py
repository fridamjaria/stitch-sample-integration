from pydantic import BaseModel, Field


class PaymentRequestWebhookResponseModel(BaseModel):
    id: str
    filter_type: list[str]
    secret: str
    url: str


class GeneratePaymentRequestUrlModel(BaseModel):
    amount: int = Field(..., example=5)
    currency: str = Field(..., example="ZAR")
    payment_reference: str = Field(..., example="KombuchaFizz")
    beneficiary_reference: str = Field(..., example="Joe-Fizz-01")
    external_reference: str = Field(..., example="example-e32e5478-325b-4869-a53e-2021727d2afe")
    beneficiary_name: str = Field(..., example="FizzBuzz Co.")
    beneficiary_bank_id: str = Field(..., example="fnb")
    beneficiary_account_nummber: str = Field(..., example="123456789")
    merchant: str = Field(..., example="{merchantId: '123', merchantName: 'Acme Inc'}")
    