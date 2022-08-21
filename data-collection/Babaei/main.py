from datetime import datetime
import sys
import re
import jdatetime
from scraper.telewebion import TelewebionScraper
from argparse import ArgumentParser

parser = ArgumentParser(description='Script to scrape telewebion archive videos')

parser.add_argument('-d', '--days', action='store', default=1, type=int, help='how many days to be scraped by script from today to the past')
parser.add_argument('-c', '--channel', action='store', default='irinn', help='channel that you want to scrape its archive')
parser.add_argument('-a', '--auto', action='store_true', help='enable automatic scrape.')
parser.add_argument('-s', '--start-date', action='store', help='determine start date to extract links from. ex: 1401-01-30')
parser.add_argument('-n', '--no-extract', action='store_false', help='disable extracting video links')
parser.add_argument('--download', action='store', choices=['480', '720', '1080'], help='enable download when extracting links have done.')

if __name__ == "__main__":
    args = parser.parse_args()
    if args.start_date:
        results = re.match(r'^(?P<year>\d{4})-(?P<month>[0-1]{1}\d{1})-(?P<day>[0-3]{1}\d{1})$', args.start_date)
        if results:
            start_date_dict = results.groupdict()
            year    = int(start_date_dict['year'])
            month   = int(start_date_dict['month'])
            day     = int(start_date_dict['day'])
            
            start_date = jdatetime.date(year, month, day)

        else:
            print('start date format is not valid.\nValid Pattern: ex: 1401-01-30')
            sys.exit(0)

    with TelewebionScraper() as tele_obj:
        if args.no_extract:
            if args.auto:
                tele_obj.automatic_scrape(args.days)
            else:
                tele_obj.run(days=args.days, start_date=start_date, channel=args.channel)
        tele_obj.logger.info('Close browser Window.')
        tele_obj.quit()
        if args.download:
            tele_obj.logger.info('Close browser Window.')
            tele_obj.quit()
            tele_obj.download(quality=args.download)
