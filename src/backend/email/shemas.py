from pydantic import BaseModel


class EmailChallengeSchema(BaseModel):
    code: str
    email: str
    type_of_challenge: str


class EmailVerifyChallengeSchema(BaseModel):
    email: str
    code: str


class EmailAfterChallengeSchema(BaseModel):
    result: bool
