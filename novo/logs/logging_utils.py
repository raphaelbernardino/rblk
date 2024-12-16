import logging

import coloredlogs


def create_logger(name=None, level='INFO', use_filehandler=False):
    if name is None:
        name = __name__

    # Create a custom logger
    logger = logging.getLogger(name)

    if use_filehandler:
        # Create a filehandler object
        fh = logging.FileHandler('./relatorio.log', mode='a')
        # fh.setLevel(logging.INFO)
        fh.setLevel(logging.DEBUG)

        # Create a ColoredFormatter to use as formatter for the FileHandler
        formatter = logging.Formatter('[%(asctime)s] [%(name)-20s] [L.%(lineno)5d] [%(levelname)-5s] %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # https://coloredlogs.readthedocs.io/en/latest/api.html#coloredlogs.DEFAULT_FIELD_STYLES
    field_colors = coloredlogs.DEFAULT_FIELD_STYLES
    field_colors['levelname'] = {'bold': True, 'color': 'yellow'}

    # https://coloredlogs.readthedocs.io/en/latest/api.html#coloredlogs.DEFAULT_LEVEL_STYLES
    level_colors = coloredlogs.DEFAULT_LEVEL_STYLES

    coloredlogs.install(
        logger=logger,
        fmt='\r[%(asctime)s] [%(name)-20s] [L.%(lineno)5d] [%(levelname)-5s] %(message)s',
        level=level,
        level_styles=level_colors,
        field_styles=field_colors,
    )

    return logger
