import os
import errno


def mkfifo_exist_ok(fifo_path, logger):
    """
    :param:
    `fifo_path` - str               - the path to create fifo file
    `logger`    - logging.Logger    - logger object

    :description:
    Create fifo file without raising error for already existing of the 
    file.
    """
    try:
        logger.info(f'make fifo file in {fifo_path}')
        os.mkfifo(fifo_path)
    except OSError as oe:
        # check if file exist, don't raise exception
        if oe.errno != errno.EEXIST:
            logger.error('error in making pipe file', exc_info=True)
            raise
        else:
            logger.info(f'{fifo_path} already exists')