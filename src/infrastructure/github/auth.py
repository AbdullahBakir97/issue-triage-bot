"""GitHub App JWT authentication."""

from __future__ import annotations

import time

import jwt

__all__ = ["GitHubAppAuth"]


class GitHubAppAuth:
    """Handles GitHub App JWT token generation and installation token exchange."""

    def __init__(self, app_id: str, private_key: str) -> None:
        """Initialize with GitHub App credentials.

        Args:
            app_id: The GitHub App ID.
            private_key: The PEM-encoded private key for the App.
        """
        self._app_id = app_id
        self._private_key = private_key
        self._installation_tokens: dict[int, tuple[str, float]] = {}

    def generate_jwt(self) -> str:
        """Generate a JWT for GitHub App authentication.

        The JWT is valid for 10 minutes as per GitHub's requirements.
        """
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),
            "iss": self._app_id,
        }
        return jwt.encode(payload, self._private_key, algorithm="RS256")

    async def get_installation_token(self, installation_id: int, http_client: object) -> str:
        """Get an installation access token, using cache if valid.

        Args:
            installation_id: The GitHub App installation ID.
            http_client: An httpx.AsyncClient instance for making requests.

        Returns:
            A valid installation access token.
        """
        cached = self._installation_tokens.get(installation_id)
        if cached:
            token, expires_at = cached
            if time.time() < expires_at - 60:
                return token

        app_jwt = self.generate_jwt()

        # Type ignore for httpx client duck typing
        response = await http_client.post(  # type: ignore[union-attr]
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        response.raise_for_status()
        data = response.json()

        token = data["token"]
        # Cache with approximate expiration (1 hour)
        self._installation_tokens[installation_id] = (token, time.time() + 3600)

        return token
