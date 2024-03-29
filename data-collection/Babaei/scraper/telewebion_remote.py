import os
import time
import json
import requests
import jdatetime
from tqdm import tqdm
from logging import getLogger
from argparse import Namespace
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, InvalidSessionIdException
from exceptions.exceptions import ChannelDoesNotExistException

from logger.logger import logger_config
from utils.fifo import mkfifo_exist_ok
from utils.load import (
    load_downloaded_videos,
    load_extracted_links, 
    load_valid_channels
)


class TelewebionScraperRemote(webdriver.Remote):

    def __init__(self, domain='localhost', close_browser=True):
        logger_config()
        self.logger = getLogger(__name__)

        self.elements               = None
        self.download_dict          = dict()
        self.download_quality       = ['480', '720', '1080']
        self.valid_channels         = load_valid_channels(logger=self.logger)
        self.downloaded_videos_id   = load_downloaded_videos()
        self.extracted_links_id     = load_extracted_links()

        options = Options()
        options.add_argument("--headless")
        self.close_browser = close_browser

        if not domain:
            domain = 'localhost'

        self.logger.info(domain)

        super(TelewebionScraperRemote, self).__init__(
            command_executor=f'http://{domain}:4444/wd/hub',
            options=options,
        )
        
        self.implicitly_wait(20)
        self.maximize_window()
        self.logger.info('TelewebionScraperRemote object initialized.')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.close_browser:
            self.logger.info('Close browser Window.')
            self.quit()

    def get_archive(self, date=jdatetime.date.today(), channel='irinn'):
        if channel not in self.valid_channels:
            raise ChannelDoesNotExistException(channel)

        date_str = date.strftime("%Y-%m-%d")
        date_str_without_zeropad = date_str.replace('-0', '-')
        url = f"https://telewebion.com/archive/{channel}/{date_str_without_zeropad}"
        self.logger.info(f'request sent to {url}')
        self.get(url)

    def set_cookie_auth(self):
        load_dotenv()

        self.add_cookie({'name': '__asc', 'value': os.getenv('__asc')})
        self.add_cookie({'name': '__auc', 'value': os.getenv('__auc')})
        self.add_cookie({'name': '_uniqueId', 'value': os.getenv('_uniqueId')})
        self.add_cookie({'name': 'token', 'value': os.getenv('token')})

        self.logger.info('Authentication cookie added.')

    def click_load_more_button(self):
        try:
            load_more_elem = WebDriverWait(self, 1).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'load-more'))
            )
            if load_more_elem:
                load_more_elem.click()
                self.logger.info('load-more button clicked.')
                return True
            return False
            
        except TimeoutException:
            self.logger.info('There is no load-more button.')
            return False

    def get_episodes(self, date, channel):
        app_cards = WebDriverWait(self, 20).until(
            EC.visibility_of_all_elements_located((By.TAG_NAME, 'app-card-cover-episode'))
        )

        elems_duration = [
            app_card.find_element(By.CSS_SELECTOR, 'div.col-5 > span')
            .get_attribute('innerHTML') 
            for app_card in app_cards
        ]
        info_frames = [
            app_card.find_element(By.CLASS_NAME, 'info-frame')
            for app_card in app_cards
        ]

        elems_episodes = []
        elems_programs = []

        for frame in info_frames:
            elems_episodes.append(frame.find_element(By.CSS_SELECTOR, 'a[href*="/episode/"]'))
            elems_programs.append(frame.find_element(By.CSS_SELECTOR, 'a[href*="/program/"]'))

        elems_links = [elem.get_attribute('href') for elem in elems_episodes]
        elems_title = [elem.get_attribute('title') for elem in elems_episodes]
        elems_program = [elem.get_attribute('title') for elem in elems_programs]
        
        self.logger.info(f"{len(elems_links)} episodes were found.")

        self.elements = [
            Namespace(
                link=elems_links[i],
                title=elems_title[i],
                program_name=elems_program[i],
                duration=elems_duration[i], 
                channel=channel,
                date=date
            )
            for i in range(len(elems_links))
            if elems_links[i].split('/')[-1] not in self.extracted_links_id
        ]

    def extract_link(self, link): 
        try:
            self.get(link)
            self.logger.info(f'request sent to {link}')
            self.implicitly_wait(20)

            # play_elem = WebDriverWait(driver, 20).until(
            #     EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Pause"]'))
            # )
            # play_elem.click()

            download_elem = WebDriverWait(self, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'fa-cloud-download'))
            )
            download_elem.click()
            self.logger.info('Download button clicked.')

            download_items = WebDriverWait(self, 20).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, 'download-item'))
            )

            download_links = {}
            for i in range(len(download_items)):
                download_links[self.download_quality[i]] = download_items[i].find_element(By.CSS_SELECTOR, 'a[href*="dl.telewebion.com"]').get_attribute('href')

            self.download_dict[link] = download_links
            self.logger.info('Download links extracted.')

            time.sleep(2)
        except KeyboardInterrupt:
            self.logger.debug('Program is exiting...')
            self.logger.debug('exit')
        except (NoSuchWindowException, InvalidSessionIdException):
            self.logger.debug('Browser closed', exc_info=True)
        except:
            self.logger.error('Download button not found.', exc_info=True)

    def get_link_per_channel_date(self, date, channel):
        self.get_archive(date, channel)
        self.set_cookie_auth()

        load_more_button_exist = True
        self.implicitly_wait(2)
        while load_more_button_exist:
            load_more_button_exist = self.click_load_more_button()
            time.sleep(0.1)
        self.implicitly_wait(20)

        self.get_episodes(date, channel)
        for elem in tqdm(self.elements):
            self.extract_link(elem.link)

    def write_links(self, isPipe: bool=False, quality: str='480'):

        if isPipe:
            pipe_file = f'./data/{quality}.pipe'
            mkfifo_exist_ok(pipe_file, self.logger)

            self.logger.info(f'opening {pipe_file} ...')
            with open(pipe_file, 'w') as fifo: 
                self.logger.info(f'{pipe_file} opened')
                for _, value in list(self.download_dict.items()):
                    fifo.write(value[quality] + '\n')
                
                # indicate end of file (<EOF>)
                fifo.write('QUIT\n')
                self.logger.info(f'all links wrote to {pipe_file}')
            
        else:
            os.makedirs('./data/', exist_ok=True)
            f_480   = open('./data/480.txt', 'a')
            f_720   = open('./data/720.txt', 'a')
            f_1080  = open('./data/1080.txt', 'a')

            for _, value in self.download_dict.items():
                f_480.write(value['480'] + '\n')
                f_720.write(value['720'] + '\n')
                f_1080.write(value['1080'] + '\n')

            f_480.close()
            f_720.close()
            f_1080.close()

        self.logger.info('Extracted links wrote to files.')
        self.download_dict.clear()

    def write_metadata(self):
        for elem in self.elements:
            video_id = elem.link.split('/')[-1]
            dir_name = f'./data/videos/{video_id}'
            os.makedirs(dir_name, exist_ok=True)

            filename = f'{dir_name}/{video_id}-metadata.json'
            with open(filename, 'w') as metadata:
                meta_dict = dict()
                meta_dict['Video ID'] = video_id
                meta_dict['Video Link'] = elem.link
                meta_dict['Video Title'] = elem.title
                meta_dict['Program Name'] = elem.program_name
                meta_dict['Video Duration'] = elem.duration
                meta_dict['Channel'] = elem.channel
                meta_dict['Extract Date (Jalali)'] = elem.date.strftime("%a, %d %b %Y")
                meta_dict['Extract Date (Gregorian)'] = elem.date.togregorian().strftime("%a, %d %b %Y")
                json.dump(meta_dict, metadata)

        self.elements.clear()


    def run(self, days=1, start_date=jdatetime.date.today(), channel='irinn', isFIFO=False):
        try:

            for i in range(days):
                date = start_date - jdatetime.timedelta(i)
                self.logger.info(f'{date} of {channel}')
                self.get_link_per_channel_date(date, channel)
                self.write_links(isFIFO)
                self.write_metadata()

        except ChannelDoesNotExistException as e:
            self.logger.error(f'{e}', exc_info=True)
        except KeyboardInterrupt:
            self.logger.debug('Program is exiting...')
            self.logger.debug('exit')
        except (NoSuchWindowException, InvalidSessionIdException):
            self.logger.debug('Browser closed.', exc_info=True)

    def automatic_scrape(self, days=30):
        try:

            self.logger.info('Automatic Scrape Started.')
            for channel in tqdm(self.valid_channels):
                self.logger.info(f'{days} days of {channel} is being scraped...')
                self.run(days, channel)

        except KeyboardInterrupt:
            self.logger.debug('Program is exiting...')
            self.logger.debug('exit')
        except (NoSuchWindowException, InvalidSessionIdException):
            self.logger.debug('Browser closed.', exc_info=True)

    def download(self, quality: str='480', force: bool=False):
        """
        :param:
        quality - str   - download quality of video
        force   - bool  - force to download downloaded videos again

        :description:
        Download extracted links in `./data/videos/` directory.
        """

        # load all extracted links
        with open(f'./data/{quality}.txt', 'r') as f:
            links = f.readlines()
            links = list(map(lambda x: x[:-1], links))

        # filter all links that already have been downloaded if there is no force
        if not force:
            links = list(filter(
                lambda x: x.split('/')[-3] not in self.downloaded_videos_id, 
                links
            ))

        links_num = len(links)
        self.logger.info(f'{quality}p video links loaded.')
        self.logger.info(f'{links_num} links are ready to download.')
        self.logger.info('Start Downloading...')
        try:
            for i in range(links_num):
                try:
                    self.logger.info(f'({i+1} of {links_num})')
                    link = links[i]
                    video_id = link.split('/')[-3]

                    dir_name = f'./data/videos/{video_id}/{quality}'
                    os.makedirs(dir_name, exist_ok=True)
                    filename = '-'.join(link.split('/')[-3:-1]) + '.mp4'

                    # ignore downloaded video links
                    if os.path.isfile(os.path.join(dir_name, filename)):
                        continue
                    r = requests.get(link, allow_redirects=True, stream=True)
                    total = int(r.headers.get('content-length', 0))


                    metadata_path = f'{dir_name}/{video_id}-meta.json'
                    with open(metadata_path, 'w') as metadata:
                        meta_dict = dict()
                        meta_dict['Download Time'] = r.headers.get("Date")
                        meta_dict['Video Last Modified'] = r.headers.get("Last-Modified")
                        meta_dict['Video Size'] = total
                        json.dump(meta_dict, metadata)
                    self.logger.info(f'the metadata of video has written to {metadata_path}')

                    file_path = f'{dir_name}/{filename}'
                    with open(file_path, 'wb') as f, tqdm(
                        desc=filename,
                        total=total,
                        unit='iB',
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as bar:
                        for data in r.iter_content(chunk_size=1024):
                            size = f.write(data)
                            bar.update(size)
                    self.logger.info(f'video [{video_id}] has written to {file_path}')

                except requests.exceptions.HTTPError as errh:
                    self.log.error(f"Http Error: {errh}", exc_info=True)
                except requests.exceptions.ConnectionError as errc:
                    self.logger.error(f"Error Connecting: {errc}", exc_info=True)
                except requests.exceptions.Timeout as errt:
                    self.logger.error(f"Timeout Error: {errt}", exc_info=True)
                except requests.exceptions.RequestException as err:
                    self.logger.error(f"OOps: Something Else {err}", exc_info=True)
        except KeyboardInterrupt:
            self.logger.debug('Program is exiting...')
            self.logger.debug('exit')
