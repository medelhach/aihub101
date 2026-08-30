import asyncio
import socket
from ipaddress import ip_address
from urllib.parse import urlsplit

from app.modules.content_ingestion.exceptions import ContentValidationError


class SSRFGuard:
    async def validate(self, url: str, allowed_domains: tuple[str, ...]) -> None:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"}:
            raise ContentValidationError("Source URL must use HTTP or HTTPS.")
        if parsed.username or parsed.password or not parsed.hostname:
            raise ContentValidationError("Source URL contains invalid authority information.")

        hostname = parsed.hostname.rstrip(".").casefold()
        normalized_domains = tuple(domain.rstrip(".").casefold() for domain in allowed_domains)
        if not normalized_domains or not any(
            hostname == domain or hostname.endswith(f".{domain}") for domain in normalized_domains
        ):
            raise ContentValidationError(
                "Source URL host is not allowlisted.",
                details={"hostname": hostname},
            )

        addresses = await asyncio.to_thread(self._resolve, hostname, parsed.port)
        if not addresses:
            raise ContentValidationError("Source URL host did not resolve.")
        for address in addresses:
            parsed_address = ip_address(address)
            if not parsed_address.is_global:
                raise ContentValidationError(
                    "Source URL resolves to a non-public address.",
                    details={"hostname": hostname},
                )

    @staticmethod
    def _resolve(hostname: str, port: int | None) -> set[str]:
        return {
            str(result[4][0])
            for result in socket.getaddrinfo(
                hostname,
                port or 443,
                type=socket.SOCK_STREAM,
            )
        }
