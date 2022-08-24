import sys
import re
import jdatetime
import subprocess
from argparse import ArgumentParser
from utils.platform import set_webdriver_based_platform

from scraper.telewebion import TelewebionScraper
from scraper.telewebion_remote import TelewebionScraperRemote


parser = ArgumentParser(description='Script to scrape telewebion archive videos')

parser.add_argument('-d', '--days', action='store', default=1, type=int, help='how many days to be scraped by script from today to the past')
parser.add_argument('-c', '--channel', action='store', default='irinn', help='channel that you want to scrape its archive')
parser.add_argument('-a', '--auto', action='store_true', help='enable automatic scrape.')
parser.add_argument('-s', '--start-date', action='store', help='determine start date to extract links from. ex: 1401-01-30')
parser.add_argument('-n', '--no-extract', action='store_false', help='disable extracting video links')
parser.add_argument('--download', action='store', choices=['480', '720', '1080'], help='enable download when extracting links have done.')
parser.add_argument('-r', '--remote', action='store_true', help='enable using remote browser')
parser.add_argument('-f', '--fifo', action='store_true', help='enable using fifo file for download (Linux only)')
parser.add_argument('--docker', action='store', help='name of firefox container')

def handle(tele_obj, args, start_date=jdatetime.date.today(), isFIFO=False):
    """
    :param:
    tele_obj    - [TelewebionScraper | TelewebionScraperRemote] - scraper object
    args        - argparse.Namespace                            - namespace of arguments
    start_date  - jdatetime.date                                - start date to scrape
    isFIFO      - bool                                          - check if fifo is enable

    :description:
    handle running each method of tele_obj depends on 
    taken arguments.
    """
    if args.remote:
        tele_obj.logger.info('Using remote browser...')
    else:
        tele_obj.logger.info('Using Local browser...')

    if args.no_extract:
        if args.auto:
            tele_obj.automatic_scrape(args.days)
        else:
            if not args.start_date:
                start_date = jdatetime.date.today()
            tele_obj.run(
                args.days, 
                start_date, 
                args.channel,
                isFIFO
            )

    tele_obj.logger.info('Close browser Window.')
    tele_obj.quit()
    if args.download and not args.fifo:
        tele_obj.download(quality=args.download)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.download and args.fifo:
        subprocess.Popen(['python', 'download_fifo.py'], stdout=sys.stdout)

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
    else:
        start_date = jdatetime.date.today()

    if args.remote:
        tele_obj = TelewebionScraperRemote(domain=args.docker)
        handle(tele_obj, args, start_date, args.fifo)
    else:
        gecko_path = set_webdriver_based_platform()

        with TelewebionScraper(webdriver_path=gecko_path) as tele_obj:
            handle(tele_obj, args, start_date, args.fifo)
