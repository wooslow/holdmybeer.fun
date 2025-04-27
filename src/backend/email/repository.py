import os
import json
import logging
from random import randint
from datetime import timedelta

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

from .html import HTML_CODE
from ..database import redis, DatabaseSession

load_dotenv()

logger = logging.getLogger(__name__)


class EmailRepository:
    def __init__(self) -> None:
        self.max_age_seconds = int(timedelta(minutes=15).total_seconds())
        self._init_email_api()

    def _init_email_api(self) -> None:
        """Initialize the email API client."""
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = os.getenv("API_KEY_EMAIL")
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

    async def create_challenge(self, email: str, type_of_challenge: str) -> dict:
        """Create and send a challenge code to the user's email."""
        code = str(randint(100000, 999999))

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            sender={"email": "no-reply@holdmybeer.fun", "name": "HoldMyBeer Fun"},
            subject="Verify Your Email Address",
            html_content=HTML_CODE.replace("{{CODE}}", code)
        )

        try:
            await redis.setex(
                f"challenge:{email}",
                self.max_age_seconds,
                json.dumps({"code": code, "email": email, "type_of_challenge": type_of_challenge})
            )
            self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Verification email sent to {email}.")
            return {"status": "success", "message": "Verification email sent."}

        except ApiException as e:
            logger.error(f"Failed to send email: {e}")
            return {"status": "error", "message": "Failed to send verification email."}

        except Exception as e:
            logger.exception("Unexpected error during email challenge creation.")
            return {"status": "error", "message": "Internal server error."}

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
        logger.info(f"Email {email} successfully verified.")

        return {
            "status": "success",
            "code": code,
            "email": email,
            "type_of_challenge": challenge.get("type_of_challenge")
        }
