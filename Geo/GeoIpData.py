from Geo.GeoModel import GeoData
import geoip2.database
from Logger.logger import logger

DB_PATH = './Database/Databases/GeoLite2-City.mmdb'
AVAILABLE_LANGUAGES = ['de', 'en', 'es', 'fr', 'ja', 'pt-BR', 'ru', 'zh-CN']
reader: geoip2.database.Reader | None = None

try:
    reader = geoip2.database.Reader(DB_PATH)
    meta = reader.metadata()
    logger.info(
        f"GeoIP database loaded: {DB_PATH} | "
        f"{meta.database_type} | "
        f"Build: {meta.build_epoch} | "
        f"Languages: {', '.join(meta.languages)}"
    )
except Exception as e:
    logger.error(f"Failed to load GeoIP database: {e}")
    raise
    

async def get_ip_data(ip: str, language: str) -> GeoData | None:
    
    language = language if language in AVAILABLE_LANGUAGES else "en"
    if reader is None:
        logger.error("GeoIP reader is not initialized!")
        return None

    try:
        response = reader.city(ip)
        
        city = response.city.names.get(language, "Undefined city") if response.city.names else "Undefined city"
        country = response.country.names.get(language, "Undefined country") if response.country.names else "Undefined country"
        continent = response.continent.names.get(language, "Undefined continent") if response.continent.names else "Undefined continent"
        lt = response.location.latitude
        ln = response.location.longitude
        network = str(response.traits.network) if response.traits.network else None
        
        logger.debug(f"GeoIP success: {ip} → {city}, {country}")        
        return GeoData (
                ip,
                network,
                city,
                country,
                continent,
                lt,
                ln
        )
    except geoip2.errors.AddressNotFoundError:
        logger.debug(f"IP {ip} not found in GeoLite2 database")
        return None
    except Exception as e:
        logger.error(f"GeoIP lookup error for {ip}: {e}")
        return None
    
    
def close_geoip_reader() -> None:
    global reader
    if reader is not None:
        reader.close()
        logger.info("GeoIP reader closed")
        reader = None