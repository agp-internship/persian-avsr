from scraper.telewebion import TelewebionScraper
from getpass import getuser
with TelewebionScraper() as tele_obj:
    tele_obj.quit()
    tele_obj.logger.info(f'current user: {getuser()}')
    tele_obj.write_links(isPipe=True)