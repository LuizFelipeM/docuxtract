<<<<<<< Updated upstream
=======
from datetime import timedelta
>>>>>>> Stashed changes
import logging
import os
import jwt
from dataclasses import dataclass

from src.logger import logger
from .custom_exceptions import BadCredentialsException, UnableCredentialsException


@dataclass
class JsonWebToken:
    """Perform JSON Web Token (JWT) validation using PyJWT"""

    jwt_access_token: str
    auth0_issuer_url: str = f"https://{os.getenv("AUTH0_DOMAIN")}/"
    auth0_audience: str = os.getenv("AUTH0_AUDIENCE")
    algorithm: str = "RS256"
    jwks_uri: str = f"{auth0_issuer_url}.well-known/jwks.json"

    def validate(self):
        try:
            payload = self.decode()
            if payload:
                return payload
            raise BadCredentialsException
        except jwt.exceptions.PyJWKClientError as ex:
            logger.log(logging.ERROR, str(ex))
            raise UnableCredentialsException
        except jwt.exceptions.InvalidTokenError as ex:
            logger.log(logging.ERROR, str(ex))
            raise BadCredentialsException

    def decode(self):
        jwks_client = jwt.PyJWKClient(self.jwks_uri)
        jwt_signing_key = jwks_client.get_signing_key_from_jwt(
            self.jwt_access_token
        ).key
        payload = jwt.decode(
            self.jwt_access_token,
            jwt_signing_key,
            algorithms=self.algorithm,
            audience=self.auth0_audience,
            issuer=self.auth0_issuer_url,
<<<<<<< Updated upstream
=======
            options={"verify_exp": True, "leeway": timedelta(seconds=10)},
>>>>>>> Stashed changes
        )
        return payload
