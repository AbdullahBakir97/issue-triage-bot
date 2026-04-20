"""GitHub webhook HMAC signature verification."""

from __future__ import annotations

import hashlib
import hmac

from src.domain.exceptions import WebhookValidationError

__all__ = ["WebhookVerifier"]


class WebhookVerifier:
    """Verifies GitHub webhook signatures using HMAC-SHA256."""

    def __init__(self, secret: str) -> None:
        """Initialize with the webhook secret.

        Args:
            secret: The shared webhook secret configured in GitHub.
        """
        self._secret = secret.encode("utf-8")

    def verify(self, payload: bytes, signature: str) -> bool:
        """Verify a webhook payload against its signature.

        Args:
            payload: The raw request body bytes.
            signature: The X-Hub-Signature-256 header value.

        Returns:
            True if the signature is valid.

        Raises:
            WebhookValidationError: If verification fails.
        """
        if not signature:
            raise WebhookValidationError("Missing webhook signature")

        if not signature.startswith("sha256="):
            raise WebhookValidationError("Invalid signature format")

        expected_signature = (
            "sha256=" + hmac.HMAC(self._secret, payload, hashlib.sha256).hexdigest()
        )

        if not hmac.compare_digest(signature, expected_signature):
            raise WebhookValidationError("Invalid webhook signature")

        return True
