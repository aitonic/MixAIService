# 解决多进程日志写入混乱问题
import gzip
import logging
import logging.handlers
import os
import socket
import sys
import time
from datetime import datetime, timedelta, timezone
from logging.handlers import TimedRotatingFileHandler


class CommonTimedRotatingFileHandler(TimedRotatingFileHandler):

    @property
    def dfn(self) -> str:
        """获取当前时间序列的文件名。

        Returns:
            str: 生成的文件名，包含时间戳后缀。

        """
        current_time = int(time.time())
        # 获取当前时间，并将其转换为 TimeTuple
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
        """计算滚动时间。

        Args:
            current_time (float): 当前时间戳。

        Returns:
            int: 计算得到的滚动时间点（时间戳）。

        """
        # 将时间取整
        t_str = time.strftime(self.suffix, time.localtime(current_time))
        t = time.mktime(time.strptime(t_str, self.suffix))
        return TimedRotatingFileHandler.computeRollover(self, t)

    def do_gzip(self, old_log: str) -> None:
        """将指定日志文件进行 gzip 压缩。

        Args:
            old_log (str): 要压缩的日志文件路径。

        Returns:
            None

        """
        try:
            with open(old_log) as old, gzip.open(old_log + '.gz', 'wt') as comp_log:
                comp_log.writelines(old)
            os.remove(old_log)
        except Exception as e:
            print(f"压缩日志文件失败: {e}")
            pass

    def should_rollover(self) -> int:
        """是否应该执行日志滚动操作：
        
        1、存档文件已存在时，执行滚动操作
        2、当前时间 >= 滚动时间点时，执行滚动操作
        """
        dfn = self.dfn
        t = int(time.time())
        if t >= self.rolloverAt or os.path.exists(dfn):
            return 1
        return 0

    def do_rollover(self) -> None:
        """执行滚动操作。
        
        1、文件句柄更新
        2、存在文件处理
        3、备份数处理
        4、下次滚动时间点更新
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple

        dfn = self.dfn

        # 存档log 已存在处理
        if not os.path.exists(dfn) and not os.path.exists(dfn + ".gz"):
            self.rotate(self.baseFilename, dfn)
            self.do_gzip(dfn)

        # 备份数控制
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        # 延迟处理
        if not self.delay:
            self.stream = self._open()

        # 更新滚动时间点
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



server_name = os.getenv('SERVER.NAME', 'common-log')
server_logging_path = os.getenv('SERVER.LOGGING.PATH', '~/apps/logs')

class LoggerFormatter(logging.Formatter):
    """自定义日志格式化器，支持附加上下文信息。"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录。

        Args:
            record (logging.LogRecord): 日志记录对象。

        Returns:
            str: 格式化后的日志字符串。

        """
        # 示例逻辑，可以自定义格式化操作
        # record.traceId = thread_local.getTraceId()
        ss = logging.Formatter.format(self, record)
        return ss

class MessageFormatter(logging.Formatter):
    """自定义消息格式化器，支持附加时间戳和消息处理。"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录，添加时间戳。

        Args:
            record (logging.LogRecord): 日志记录对象。

        Returns:
            str: 格式化后的日志字符串。

        """
        # 添加时间戳
        record.timestamp = get_current_iso()
        return super().format(record)

    def format_message(self, record: logging.LogRecord) -> str:
        """格式化日志消息内容。

        Args:
            record (logging.LogRecord): 日志记录对象。

        Returns:
            str: 格式化后的消息字符串。

        """
        # 替换特殊字符
        record.message = record.message.replace('{', '【').replace('}', '】').replace('"', '``').replace("'", '`')
        return super().formatMessage(record)

def get_current_iso() -> str:
    """获取当前时间的 ISO 8601 格式字符串。

    Returns:
        str: 当前时间的 ISO 8601 格式字符串。

    """
    # 获取当前时间
    current_time = datetime.now(timezone(timedelta(hours=8)))

    # 格式化时间为ISO 8601格式
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
fmt = LoggerFormatter('[%(threadName)s][%(funcName)s][%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class Logger:

    log_instance = None

    @staticmethod
    def _get_logger() -> logging.Logger:
        """获取日志记录器实例。

        Returns:
            logging.Logger: 配置完成的日志记录器实例。

        """
        if Logger.log_instance is not None:
            return Logger.log_instance
        # logging.basicConfig(filename=LOG_FILENAME, encoding='utf-8', level=logging.INFO)
        log = logging.getLogger("")
        log.setLevel(logging.INFO)
        # console
        console_handle = logging.StreamHandler(sys.stdout)
        console_handle.setFormatter(fmt)
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
