from scraper.telewebion import TelewebionScraper

if __name__ == "__main__":
    with TelewebionScraper() as tele_obj:
        tele_obj.run(days=2)  