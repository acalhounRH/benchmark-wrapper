import logging
import os

has_a_tty = os.isatty(1)  # test stdout


def color_me(color):
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"

    color_seq = COLOR_SEQ % (30 + color)

    def closure(msg):
        return color_seq + msg + RESET_SEQ

    return closure


class ColoredFormatter(logging.Formatter):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    colors = {
        'WARNING': color_me(YELLOW),
        'DEBUG': color_me(BLUE),
        'CRITICAL': color_me(RED),
        'ERROR': color_me(RED),
        'INFO': color_me(GREEN)
    }

    def __init__(self, msg, use_color=True, datefmt=None):
        logging.Formatter.__init__(self, msg, datefmt=datefmt)
        self.use_color = use_color

    def format(self, record):
        orig = record.__dict__
        record.__dict__ = record.__dict__.copy()
        levelname = record.levelname

        prn_name = levelname + ' ' * (8 - len(levelname))
        if (levelname in self.colors) and has_a_tty:
            record.levelname = self.colors[levelname](prn_name)
        else:
            record.levelname = prn_name

        # super doesn't work here in 2.6 O_o
        res = logging.Formatter.format(self, record)
        # res = super(ColoredFormatter, self).format(record)

        # restore record, as it will be used by other formatters
        record.__dict__ = orig
        return res


def setup_loggers(logger_name, def_level=logging.DEBUG, log_fname=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(def_level)
    sh = logging.StreamHandler()
    sh.setLevel(def_level)

    FMT = "%Y-%m-%dT%H:%M:%SZ"

    log_format = '%(asctime)s - %(levelname)s - %(processName)s - %(module)s: %(message)s'
    colored_formatter = ColoredFormatter(log_format, datefmt=FMT)

    sh.setFormatter(colored_formatter)
    logger.addHandler(sh)

    if log_fname is not None:
        # add check for existing file with same name if so move old log to .old.
        # will only preserve a single .old file.
        if os.path.exist(log_fname):
            backup = "%s.old" % log_fname
            os.rename(log_fname, backup)
        fh = logging.FileHandler(log_fname)
        formatter = logging.Formatter(log_format, datefmt=FMT)
        fh.setFormatter(formatter)
        fh.setLevel(def_level)
        logger.addHandler(fh)
    else:
        fh = None
