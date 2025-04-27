from fastapi import HTTPException

from .repository import EmailRepository
from .shemas import EmailChallengeSchema, EmailVerifyChallengeSchema

from ..database import DatabaseSession


class EmailService:
    def __init__(self) -> None:
        self.email_repository = EmailRepository()

    async def send_challenge(self, email: str, type_of_challenge: str) -> EmailChallengeSchema:
        """ Function to send email challenge """

        challenge = await self.email_repository.create_challenge(email, type_of_challenge)

        if challenge.get('status') == 'error':
            raise HTTPException(status_code=400, detail="Invalid email")
        else:
            return EmailChallengeSchema(
                code=challenge['message'],
                email=email,
                type_of_challenge=type_of_challenge
            )

    async def verify_challenge(
        self,
        challenge: EmailVerifyChallengeSchema,
        database: DatabaseSession
    ) -> EmailChallengeSchema:
        """ Function to verify email challenge """

        after_challenge = await self.email_repository.verify_challenge(challenge.email, challenge.code, database)

        if after_challenge.get('status') == 'error':
            raise HTTPException(status_code=400, detail=after_challenge['message'])
        else:
            return EmailChallengeSchema(
                code=challenge.code,
                email=challenge.email,
                type_of_challenge=after_challenge['type_of_challenge']
            )
