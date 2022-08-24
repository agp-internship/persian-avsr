import sys


def set_webdriver_based_platform():
    platform = sys.platform
    if platform.startswith('win'):
        return './geckodriver/geckodriver.exe'
    elif platform == 'linux':
        return './geckodriver/geckodriver'
    else:
        print(f'can not detect this platform. {platform=}')
        sys.exit(-1)