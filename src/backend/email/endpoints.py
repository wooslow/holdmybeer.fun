import logging

from fastapi import APIRouter

from .service import EmailService
from .shemas import EmailChallengeSchema, EmailVerifyChallengeSchema
from ..database import DatabaseSession

logger = logging.getLogger(__name__)
email_router = APIRouter(tags=["email"])


@email_router.post("/challenge", response_model=EmailChallengeSchema)
async def verify_challenge(
    challenge: EmailVerifyChallengeSchema,
    database: DatabaseSession,
):
    email_service = EmailService()
    return await email_service.verify_challenge(challenge, database)
