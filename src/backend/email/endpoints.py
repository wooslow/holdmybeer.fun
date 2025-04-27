import logging

from fastapi import APIRouter, Response

from .service import EmailService
from .shemas import EmailChallengeSchema, EmailVerifyChallengeSchema
from ..database import DatabaseSession

logger = logging.getLogger(__name__)
email_router = APIRouter(tags=["email"])


@email_router.post("/challenge", response_model=EmailChallengeSchema)
async def verify_challenge(
    response: Response,
    challenge: EmailVerifyChallengeSchema,
    database: DatabaseSession,
):
    email_service = EmailService()
    result = await email_service.verify_challenge(challenge, database)

    if not result:
        response.status_code = 400
        return {"message": "Invalid challenge"}

    return result
