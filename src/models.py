from pydantic import BaseModel


class PaymentRequestWebhookResponseModel(BaseModel):
    id: str
    filter_type: list[str]
    secret: str
    url: str
