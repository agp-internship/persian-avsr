import os
import glob


def load_valid_channels(path: str='./data/valid_channels.txt', logger=None) -> set:
    """
    :param:
    path        - str               -   path to valid_channels.txt file
    logger      - logging.Logger    -   Logger object to log

    :return:
    channels   - set   -   set of all valid channels in telewebion

    :description:
    This function, read `valid_channels.txt` and put them in a set
    """
    with open(path, 'r') as f:
        channels = set(map(lambda x: x.replace('\n', ''), f.readlines()))
    logger.info(f'{len(channels)} channels added to valid_channels')
    return channels

def load_downloaded_videos(dirname: str='./data/videos', logger=None) -> set:
    """
    :param:
    dirname     - str   -   path to downloaded videos directory

    :return:
    videos_id   - set   -   set of all downloaded videos ID

    :description:
    This function, check input directory to find all downloaded videos
    and extract its IDs in `videos_id` set object
    """
    fn_pattern = os.path.join(dirname, '*/*/*.mp4')
    videos_fn = glob.glob(fn_pattern)
    videos_id = set(map(lambda x: (x.split('/')[-1]).split('-')[0], videos_fn))
    # TODO: add logging here
    return videos_id


def load_extracted_links(dirname: str='./data/', logger=None) -> set:
    """
    :param:
    dirname     - str   -   path to directory of extracted links files

    :return:
    links_id   - set   -   set of all extracted video ID links

    :description:
    This function, check input directory to find extracted links files
    and extract its IDs in `links_id` set object
    """
    fn = os.path.join(dirname, '480.txt')
    links = []
    with open(fn) as f:
        links = list(f)
    links_id = set(map(lambda x: x.split('/')[-3], links))
    # TODO: add logging here
    return links_id
