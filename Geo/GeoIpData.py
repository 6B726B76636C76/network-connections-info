import asyncio
import geoip2.errors
import geoip2.database
from Geo.GeoModel import GeoData
from Logger.logger import logger

language = "en"
reader: geoip2.database.Reader | None = None

def init_reader(db_path: str) -> geoip2.database.Reader | None :
    
    global reader
    if reader is not None:
        return

    try:
        reader = geoip2.database.Reader(f"{db_path}/GeoLite2-City.mmdb")
        meta = reader.metadata()
        
        logger.info(
            f"GeoIP database loaded: {db_path} | "
            f"{meta.database_type} | "
            f"Build: {meta.build_epoch} | "
        )
        return reader
    
    except Exception as e:
        
        logger.critical(f"Failed to load GeoIP database: {e}")
        raise RuntimeError("Cannot initialize GeoIP reader") from e

async def get_ip_data_by_db(ip: str, db_path: str) -> GeoData:
    
    if ip == "192.168.0.1":
        return GeoData(ip=ip, network=None, city=None, country=None)

    if reader is None:
        init_reader(db_path)

    loop = asyncio.get_running_loop()

    try:
        response = await loop.run_in_executor(None, lambda: reader.city(ip))
        city = response.city.names.get(language) if response.city.names else None
        country = response.country.names.get(language) if response.country.names else None
        network = str(response.traits.network) if response.traits.network else None

        if not city and not country:
            logger.debug(f"GeoIP lookup: {ip} has no city or country info")
        else:
            logger.debug(f"GeoIP success: {ip} → {city}, {country}")

        return GeoData(ip=ip, network=network, city=city, country=country)

    except geoip2.errors.AddressNotFoundError as e:
        
        logger.debug(f"IP {ip} not found in GeoLite2 database. {e}")
        return GeoData(ip=ip, network=None, city=None, country=None)

    except Exception as e:
        
        logger.error(f"GeoIP lookup error for {ip}: {e}")
        return GeoData(ip=ip, network=None, city=None, country=None)

def close_geoip_reader() -> None:
    global reader
    if reader is not None:
        reader.close()
        logger.info("GeoIP reader closed")
        reader = None