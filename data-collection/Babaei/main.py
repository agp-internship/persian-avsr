import sys
from scraper.telewebion import TelewebionScraper
from argparse import ArgumentParser

parser = ArgumentParser(description='Script to scrape telewebion archive videos')

parser.add_argument('-d', '--days', action='store', default=1, type=int, help='how many days to be scraped by script from today to the past')
parser.add_argument('-c', '--channel', action='store', default='irinn', help='channel that you want to scrape its archive')
parser.add_argument('-a', '--auto', action='store_true', help='enable automatic scrape.')
parser.add_argument('-n', '--no-extract', action='store_false', help='disable extracting video links')
parser.add_argument('--download', action='store', choices=['480', '720', '1080'], help='enable download when extracting links have done.')

if __name__ == "__main__":
    args = parser.parse_args()
    with TelewebionScraper() as tele_obj:
        if args.no_extract:
            if args.auto:
                tele_obj.automatic_scrape(args.days)
            else:
                tele_obj.run(days=args.days, channel=args.channel)
        if args.download:
            tele_obj.download(quality=args.download)
