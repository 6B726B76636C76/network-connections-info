from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from typing import Optional, Union


@dataclass
class GeoData:
    ip: str
    network: str | None
    city: str | None
    country: str | None

    @staticmethod
    def localhost() -> 'GeoData':
        return GeoData(
            ip="os",
            network="None",
            city="None",
            country="None"
        )

