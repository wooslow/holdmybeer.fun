import os
import json
import logging
from random import randint

import sib_api_v3_sdk
from dotenv import load_dotenv

from .html import REGISTER_HTML_CODE, RESET_PASSWORD_HTML_CODE
from ..database import redis, DatabaseSession

load_dotenv()

logger = logging.getLogger(__name__)


class EmailRepository:
    def __init__(self) -> None:
        self.__init_email_api()

    def __init_email_api(self) -> None:
        """Initialize the email API client."""
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = os.getenv("API_KEY_EMAIL")
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        logger.info("Email API client initialized.")

    async def _send_mail(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> dict:
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"email": "no-reply@holdmybeer.fun", "name": "HoldMyBeer Fun"},
            subject=subject,
            html_content=html_content
        )

        try:
            self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Verification email sent to {to_email}.")
            return {"status": "success", "message": "Verification email sent."}
        except Exception as error:
            logger.exception("Unexpected error during email challenge creation.: %s", error)
            return {"status": "error", "message": "Internal server error."}

    @staticmethod
    def _generate_code() -> str:
        """Generate a random 6-digit code."""
        return str(randint(100000, 999999))

    async def create_challenge(self, email: str, type_of_challenge: str) -> dict:
        """Create and send a challenge code to the user's email."""
        code = self._generate_code()

        if type_of_challenge == "register":
            html = REGISTER_HTML_CODE.replace("{{CODE}}", code)
        elif type_of_challenge == "reset_password":
            html = RESET_PASSWORD_HTML_CODE.replace("{{CODE}}", code)
        else:
            logger.error(f"Invalid challenge type: {type_of_challenge}")
            return {"status": "error", "message": "Invalid challenge type."}

        await redis.setex(
            f"challenge:{email}",
            900,
            json.dumps({"code": code, "email": email, "type_of_challenge": type_of_challenge})
        )

        logger.info(f"Challenge code {code} created for {email}.")

        return await self._send_mail(
            to_email=email,
            subject="Verification Code",
            html_content=html
        )

    @staticmethod
    async def verify_challenge(email: str, code: str, database: DatabaseSession) -> dict:
        """Verify the challenge code provided by the user."""
        from ..auth import AuthService

        challenge_data = await redis.get(f"challenge:{email}")

        if not challenge_data:
            logger.warning(f"Challenge expired or not found for {email}.")
            return {"status": "error", "message": "Challenge expired.", "code": 401}

        try:
            challenge = json.loads(challenge_data)
        except json.JSONDecodeError:
            logger.error(f"Corrupted challenge data for {email}.")
            return {"status": "error", "message": "Internal server error.", "code": 500}

        if challenge.get("code") != code:
            logger.warning(f"Invalid challenge code for {email}.")
            return {"status": "error", "message": "Invalid verification code.", "code": 400}

        if challenge.get("type_of_challenge") == "register":
            logger.info(f"User {email} is registering.")
            await AuthService(database).after_email_verification(email)

        await redis.delete(f"challenge:{email}")
        logger.info(f"Email {email} successfully verified by {challenge.get('type_of_challenge')}.")

        return {
            "status": "success",
            "code": code,
            "email": email,
            "type_of_challenge": challenge.get("type_of_challenge")
        }
