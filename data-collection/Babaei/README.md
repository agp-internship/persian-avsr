# Telewebion Scraper
Simple script to scrape [telewebion.com](https://telewebion.com/) IPTV website and extract link of archive videos. To use this script just you need to run `main.py` and add how many days and which channel you want to scrape.
```bash
>>> python main.py -h
usage: main.py [-h] [-d DAYS] [-c CHANNEL] [-a] [-s START_DATE] [-n] [--download {480,720,1080}] [-r]
               [-f] [--docker DOCKER]

Script to scrape telewebion archive videos

options:
  -h, --help            show this help message and exit
  -d DAYS, --days DAYS  how many days to be scraped by script from today to the past
  -c CHANNEL, --channel CHANNEL
                        channel that you want to scrape its archive
  -a, --auto            enable automatic scrape.
  -s START_DATE, --start-date START_DATE
                        determine start date to extract links from. ex: 1401-01-30
  -n, --no-extract      disable extracting video links
  --download {480,720,1080}
                        enable download when extracting links have done.
  -r, --remote          enable using remote browser
  -f, --fifo            enable using fifo file for download (Linux only)
  --docker DOCKER       name of firefox container
```

## Requirements
- selenium
- jdatetime
- python-dotenv
- tqdm
- argparse
