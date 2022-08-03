# Telewebion Scraper
Simple script to scrape [telewebion.com](https://telewebion.com/) iptv website and extract link of archive videos. To use this script just you need to run `main.py` and add how many days and which channel you want to scrape.
```bash
>>> python main.py -h
usage: sel.py [-h] [-d DAYS] [-c CHANNEL]

Script to scrape telewebion archive videos

optional arguments:
  -h, --help            show this help message and exit
  -d DAYS, --days DAYS  how many days to be scraped by script from today to the past
  -c CHANNEL, --channel CHANNEL
                        channel that you want to scrape its archive
```

## Requirements
- selenium
- jdatetime
- python-dotenv
- tqdm
- argparse
