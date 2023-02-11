import urllib.parse

from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from twilio.rest import Client

from kookaburra.exc import KookaburraException
from kookaburra.llm import llm_svc
from kookaburra.log import log
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

    async def respond(self, request: Request, psql: AsyncSession) -> None:
        _body = await request.body()
        body = {
            v.split("=")[0]: v.split("=")[1]
            for v in urllib.parse.unquote_plus(_body.decode("utf8")).split("&")
        }
        llm = await llm_svc.get_llm_by_phone_number(
            phone_number=body["To"],
            psql=psql,
        )
        if not llm:
            log.error(f"Could not find LLM for phone number {body['To']}")
            return
        response = await llm_svc.respond(
            llm=llm,
            message=body["Body"],
        )
        self.send_message(
            from_number=body["To"],
            to_number=body["From"],
            message=response.message,
        )


twilio_svc = TwilioService()
