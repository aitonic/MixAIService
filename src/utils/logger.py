# 解决多进程日志写入混乱问题
import gzip
import logging
import logging.handlers
import os
import re
import socket
import sys
import time
from datetime import (
    datetime, 
    timedelta, 
    timezone
)

from logging.handlers import TimedRotatingFileHandler


class CommonTimedRotatingFileHandler(TimedRotatingFileHandler):

    @property
    def dfn(self) -> str:
        """Get the filename with current time sequence.

        Returns:
            str: Generated filename with timestamp suffix.
        """
        current_time = int(time.time())
       
        dst_now = time.localtime(current_time)[-1]
        t = self.rolloverAt - self.interval

        if self.utc:
            time_tuple = time.gmtime(t)
        else:
            time_tuple = time.localtime(t)
            dst_then = time_tuple[-1]

        # 如果 DST 状态不同，则调整时间
        if dst_now != dst_then:
            addend = 3600 if dst_now else -3600
            time_tuple = time.localtime(t + addend)

        # 根据时间生成文件名
        dfn = self.rotation_filename(self.baseFilename + "." + time.strftime(self.suffix, time_tuple))
        return dfn

    def compute_rollover(self, current_time: float) -> int:
        """Calculate rollover time.

        Args:
            current_time (float): Current timestamp.

        Returns:
            int: Calculated rollover timestamp.

        """
        # Round the time
        t_str = time.strftime(self.suffix, time.localtime(current_time))
        t = time.mktime(time.strptime(t_str, self.suffix))
        return TimedRotatingFileHandler.computeRollover(self, t)

    def do_gzip(self, old_log: str) -> None:
        """Compress specified log file using gzip.

        Args:
            old_log (str): Path to the log file to be compressed.

        Returns:
            None

        """
        try:
            with open(old_log) as old, gzip.open(old_log + '.gz', 'wt') as comp_log:
                comp_log.writelines(old)
            os.remove(old_log)
        except Exception as e:
            print(f"Failed to compress log file: {e}")
            pass

    def should_rollover(self) -> int:
        """Determine whether to perform log rollover:
        
        1. Perform rollover when archive file already exists
        2. Perform rollover when current time >= rollover time point
        """
        dfn = self.dfn
        t = int(time.time())
        if t >= self.rolloverAt or os.path.exists(dfn):
            return 1
        return 0

    def do_rollover(self) -> None:
        """Perform rollover operation.
        
        1. Update file handle
        2. Handle existing files
        3. Process backup count
        4. Update next rollover time point
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple

        dfn = self.dfn

        # Handle existing archived log files
        if not os.path.exists(dfn) and not os.path.exists(dfn + ".gz"):
            self.rotate(self.baseFilename, dfn)
            self.do_gzip(dfn)

        # Control backup count
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        # Handle delay
        if not self.delay:
            self.stream = self._open()

        # Update rollover time point
        current_time = int(time.time())
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at = new_rollover_at + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dst_at_rollover = time.localtime(new_rollover_at)[-1]
            dst_now = time.localtime(current_time)[-1]
            if dst_now != dst_at_rollover:
                addend = -3600 if not dst_now else 3600  # 使用三元操作符简化逻辑
                new_rollover_at += addend
        self.rolloverAt = new_rollover_at


# 获取项目的根目录（假设当前文件位于项目内）
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # 或更具体的路径逻辑

# 构造 logs 目录路径
default_logs_path = os.path.join(project_root, "logs")


server_name = os.getenv('SERVER.NAME', 'common-log')
server_logging_path = os.getenv('SERVER.LOGGING.PATH', default_logs_path)

class LoggerFormatter(logging.Formatter):
    """Custom log formatter that supports adding context information."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record.

        Args:
            record (logging.LogRecord): Log record object.

        Returns:
            str: Formatted log string.
        """
        # 示例逻辑，可以自定义格式化操作
        # record.traceId = thread_local.getTraceId()
        ss = logging.Formatter.format(self, record)
        return ss

class MessageFormatter(logging.Formatter):
    """Custom message formatter that supports adding timestamps and message processing."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with timestamp.

        Args:
            record (logging.LogRecord): Log record object.

        Returns:
            str: Formatted log string.
        """
        # Add timestamp
        record.timestamp = get_current_iso()
        return super().format(record)

    def format_message(self, record: logging.LogRecord) -> str:
        """Format log message content.

        Args:
            record (logging.LogRecord): Log record object.

        Returns:
            str: Formatted message string.
        """
        # Replace special characters
        record.message = record.message.replace('{', '【').replace('}', '】').replace('"', '``').replace("'", '`')
        return super().formatMessage(record)

def get_current_iso() -> str:
    """Get current time in ISO 8601 format.

    Returns:
        str: Current time in ISO 8601 format.
    """
    # Get current time
    current_time = datetime.now(timezone(timedelta(hours=8)))

    # Format time to ISO 8601
    formatted_time = current_time.isoformat()
    return formatted_time

'''
日志模块
'''
hostname = socket.gethostname()
rq = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
log_date = rq[:10]
if not os.path.exists(f"{server_logging_path}/{server_name}"):
    os.makedirs(f"{server_logging_path}/{server_name}", exist_ok=True)
LOG_FILENAME = f'{server_logging_path}/{server_name}/{server_name}-{hostname}.log'
JSON_FILENAME = f'{server_logging_path}/{server_name}/{server_name}-{hostname}.json'
# fmt = LoggerFormatter('[%(traceId)s][%(threadName)s][%(funcName)s][%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fmt = LoggerFormatter('[%(levelname)s][%(asctime)s][%(threadName)s][%(funcName)s][%(filename)s:%(lineno)d] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class ColorFormatter(logging.Formatter):
    """Formatter that adds colors to specific keywords in log messages."""

    # ANSI escape codes for colors
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    # Keywords to colorize and their corresponding colors
    keyword_colors = {
        "INFO": green,
        "DEBUG": yellow,  # Example: You might want DEBUG in a different color
        "WARNING": yellow,
        "ERROR": red,
        "CRITICAL": bold_red,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record and highlight keywords with colors.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record as a string with color highlights.

        """
        record.message = record.getMessage()
        # format_str = '[%(threadName)s][%(funcName)s][%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s'
        format_str = '[%(levelname)s][%(asctime)s][%(threadName)s][%(funcName)s][%(filename)s:%(lineno)d] - %(message)s'
        formatter = logging.Formatter(format_str, datefmt='%Y-%m-%d %H:%M:%S')
        msg = formatter.format(record)
        
        for keyword, color in self.keyword_colors.items():
            # Escape special characters in the keyword for regex
            escaped_keyword = re.escape(keyword)
            
            # Replace the keyword with the colored version using regex
            msg = re.sub(
                rf"\b({escaped_keyword})\b",  # Match whole words only
                rf"{color}\1{self.reset}",
                msg,
                flags=re.IGNORECASE
            )

        return msg

class Logger:

    log_instance = None

    @staticmethod
    def _get_logger() -> logging.Logger:
        """Get logger instance.

        Returns:
            logging.Logger: Configured logger instance.
        """
        if Logger.log_instance is not None:
            return Logger.log_instance
        # logging.basicConfig(filename=LOG_FILENAME, encoding='utf-8', level=logging.INFO)
        log = logging.getLogger("")
        log.setLevel(logging.INFO)
        # console
        console_handle = logging.StreamHandler(sys.stdout)
        console_handle.setFormatter(ColorFormatter())  # Use the custom color formatter
        console_handle.setLevel(logging.INFO)

        # file
        # file_handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when='D', interval=1, backupCount=365, encoding="utf-8")
        file_handler = CommonTimedRotatingFileHandler(LOG_FILENAME, backupCount=7, encoding="utf-8", when='D')
        file_handler.setFormatter(fmt)
        file_handler.setLevel(logging.INFO)

        # json
        # json_handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when='D', interval=1, backupCount=365, encoding="utf-8")
        json_handler = CommonTimedRotatingFileHandler(JSON_FILENAME, backupCount=7, encoding="utf-8", when='D')
        fmt_json = '{"@timestamp" : "%(timestamp)s", "threadName":"%(threadName)s", "funcName":"%(funcName)s", "asctime": "%(asctime)s","service": "'+server_name+'", "filename": "%(filename)s", "line": "%(lineno)d", "levelname": "%(levelname)s", "message": "%(message)s"}'
        # json_fmatter.formatMessage()
        # json_handler.setFormatter(StrFormatter(fmt_json))
        # json_handler.setFormatter(logging.Formatter(fmt_json))
        json_handler.setFormatter(MessageFormatter(fmt_json))
        json_handler.setLevel(logging.INFO)

        log.addHandler(file_handler)
        log.addHandler(console_handle)
        log.addHandler(json_handler)

        Logger.log_instance = log
        return Logger.log_instance


logger = Logger._get_logger()
