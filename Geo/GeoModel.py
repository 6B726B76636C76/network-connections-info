from dataclasses import dataclass

@dataclass
class GeoData:
    ip: str
    network: str
    city: str
    country: str
    continent: str
    lt: float
    ln: float
    
