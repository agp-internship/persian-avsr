from scraper.telewebion import TelewebionScraper

with TelewebionScraper() as tele_obj:
    tele_obj.quit()
    tele_obj.download_pipe()