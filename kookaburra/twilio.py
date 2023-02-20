from twilio.rest import Client

from kookaburra.exc import KookaburraException
from kookaburra.settings import env


class TwilioService:
    def __init__(self) -> None:
        self.client = Client(
            env.TWILIO_ACCOUNT_SID,
            env.TWILIO_AUTH_TOKEN,
        )

    def send_message(
        self,
        from_number: str,
        to_number: str,
        message: str,
    ) -> None:
        self.client.messages.create(
            to=to_number,
            from_=from_number,
            body=message,
        )

    def provision_phone_number(self) -> str:
        options = self.client.available_phone_numbers("US").fetch().local.list(limit=10)
        phone_number = [p.phone_number for p in options if p.capabilities["SMS"]]
        if not phone_number:
            raise KookaburraException("No phone numbers available. Try again later.")
        phone_number = phone_number[0]
        incoming_phone_number = self.client.incoming_phone_numbers.create(
            phone_number=phone_number,
            sms_url=f"{env.KOOKABURRA_URL}/api/v0/sms",
        )
        return incoming_phone_number.phone_number

    async def release_phone_number(self, phone_number: str) -> None:
        await self.client.incoming_phone_numbers(phone_number).delete()


twilio_svc = TwilioService()
