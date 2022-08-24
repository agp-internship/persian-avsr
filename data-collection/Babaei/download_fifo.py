import os
import json
import logging
import requests
from tqdm import tqdm
from utils.fifo import mkfifo_exist_ok


def download_pipe(quality: str='480'):
    pipe_file = f'./data/{quality}.pipe'
    logger = logging.getLogger('scraper.telewebion_remote')
    mkfifo_exist_ok(pipe_file, logger)

    logger.info(f'waiting to receive links from {pipe_file} ...')
    with open(pipe_file, 'r') as fifo:
        isQuit = False
        while True:
            if isQuit:
                break

            links = fifo.readlines()
            if len(links) == 0:
                continue

            links = list(map(lambda x: x[:-1], links))
            logger.info(f'{len(links)} new {quality}p video links retrieved.')

            logger.info('Start Downloading...')
            try:
                for i in range(len(links)):
                    try:
                        link = links[i]
                        if link == 'QUIT':
                            isQuit = True
                            break
                        logger.info(f'downloading {link} ...')
                        video_id = link.split('/')[-3]
                        filename = '-'.join(link.split('/')[-3:-1]) + '.mp4'

                        r = requests.get(link, allow_redirects=True, stream=True)
                        total = int(r.headers.get('content-length', 0))

                        dir_name = f'./data/videos/{video_id}/{quality}'
                        os.makedirs(dir_name, exist_ok=True)

                        metadata_path = f'{dir_name}/{video_id}-meta.json'
                        with open(metadata_path, 'w') as metadata:
                            meta_dict = dict()
                            meta_dict['Download Time'] = r.headers.get("Date")
                            meta_dict['Video Last Modified'] = r.headers.get("Last-Modified")
                            meta_dict['Video Size'] = total
                            json.dump(meta_dict, metadata)
                        logger.info(f'the metadata of video has written to {metadata_path}')

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
                        logger.info(f'video [{video_id}] has written to {file_path}')

                    except requests.exceptions.HTTPError as errh:
                        logger.error(f"Http Error: {errh}", exc_info=True)
                    except requests.exceptions.ConnectionError as errc:
                        logger.error(f"Error Connecting: {errc}", exc_info=True)
                    except requests.exceptions.Timeout as errt:
                        logger.error(f"Timeout Error: {errt}", exc_info=True)
                    except requests.exceptions.RequestException as err:
                        logger.error(f"OOps: Something Else {err}", exc_info=True)
            except KeyboardInterrupt:
                logger.debug('Program is exiting...')
                logger.debug('exit')

if __name__ == '__main__':
    download_pipe()