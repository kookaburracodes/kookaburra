import json
import time
from typing import List, Tuple

from google.cloud import storage

from kookaburra.const import BUCKET_NAME
from kookaburra.models import Llm
from kookaburra.types import BaseResponse
from kookaburra.utils import _phone_hash


class GsService:
    def __init__(self) -> None:
        self.gs = storage.Client()

    async def upload_sms_chat(
        self,
        llm: Llm,
        body: dict,
        response: BaseResponse,
    ) -> None:
        bucket = self.gs.get_bucket(BUCKET_NAME)
        _from = _phone_hash(body["From"])
        _t = int(time.time() * 1000)
        blob = bucket.blob(f"{llm.id}/{_from}/{_t}/chat.json")
        blob.upload_from_string(
            data=json.dumps(
                {
                    "_in": body["Body"],
                    "_out": response.message,
                    "timestamp": _t,
                }
            )
        )

    async def get_sms_chat_history(
        self,
        llm: Llm,
        phone_number: str,
    ) -> List[Tuple[str, str]]:
        bucket = self.gs.get_bucket(BUCKET_NAME)
        _phone_number = _phone_hash(phone_number)
        blobs = bucket.list_blobs(
            prefix=f"{llm.id}/{_phone_number}",
        )
        content = []
        for blob in blobs:
            content.append(json.loads(blob.download_as_string()))
        chat_history = [
            (chat["_in"], chat["_out"])
            for chat in sorted(content, key=lambda x: x["timestamp"])
        ]
        return chat_history


gs_svc = GsService()
