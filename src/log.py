from PyQt5.QtWidgets import QTextEdit
import logging, time


class QTextEditLogger(logging.Handler, QTextEdit):
    def __init__(self, parent):
        super().__init__()
        self.widget = QTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.resize(parent.size())

    def emit(self, record):
        log = self.format(record)
        self.widget.append(log)
        self.widget.ensureCursorVisible()

    def clear(self):
        self.widget.clear()


class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime(self.default_time_format, ct)
            if self.default_msec_format:
                s = '%s:%03d' % (s, record.msecs)
        return s


def Custom_Log(edit):
    # 配置根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    handler = QTextEditLogger(edit)
    handler.setFormatter(CustomFormatter('%(asctime)s [%(levelname)s] : %(message)s'))
    root_logger.addHandler(handler)
