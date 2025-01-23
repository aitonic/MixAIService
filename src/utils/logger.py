import gzip
import logging
import logging.handlers
import os
import re
import socket
import sys
import time
import inspect
from datetime import datetime, timedelta, timezone
from logging.handlers import TimedRotatingFileHandler
from typing import List

# pydantic 基础模型，仅用于日志内容结构化存储
try:
    from pydantic import BaseModel
except ImportError:
    # 如果你的环境没有 pydantic，可以自行安装或去掉相关依赖
    BaseModel = None

# 如果需要 scarf_analytics 等函数，根据你项目的文件结构自行导入
# from src.utils.helpers.telemetry import scarf_analytics
# from src.utils.helpers.path import find_closest


class CommonTimedRotatingFileHandler(TimedRotatingFileHandler):
    """自定义的定时滚动文件处理器，可额外进行 gzip 压缩操作。"""

    @property
    def dfn(self) -> str:
        """生成带有时间戳的目标日志文件名。"""
        current_time = int(time.time())
        dst_now = time.localtime(current_time)[-1]
        t = self.rolloverAt - self.interval

        if self.utc:
            time_tuple = time.gmtime(t)
        else:
            time_tuple = time.localtime(t)
            dst_then = time_tuple[-1]

        # 如果 DST（夏令时）状态不同，则进行修正
        if dst_now != dst_then:
            addend = 3600 if dst_now else -3600
            time_tuple = time.localtime(t + addend)

        # 拼接最终文件名
        dfn = self.rotation_filename(self.baseFilename + "." + time.strftime(self.suffix, time_tuple))
        return dfn

    def compute_rollover(self, current_time: float) -> int:
        """计算下次滚动所需的时间点。"""
        t_str = time.strftime(self.suffix, time.localtime(current_time))
        t = time.mktime(time.strptime(t_str, self.suffix))
        return TimedRotatingFileHandler.computeRollover(self, t)

    def do_gzip(self, old_log: str) -> None:
        """对指定日志文件进行 gzip 压缩。"""
        try:
            with open(old_log, "r", encoding="utf-8") as old, gzip.open(old_log + '.gz', 'wt', encoding="utf-8") as comp_log:
                comp_log.writelines(old)
            os.remove(old_log)
        except Exception as e:
            print(f"Failed to compress log file: {e}")
            pass

    def should_rollover(self) -> int:
        """
        判断是否需要进行日志滚动：
        1. 如果压缩文件已存在
        2. 当前时间 >= 计划滚动时间
        """
        dfn = self.dfn
        t = int(time.time())
        if t >= self.rolloverAt or os.path.exists(dfn):
            return 1
        return 0

    def do_rollover(self) -> None:
        """执行滚动逻辑，并处理日志备份和压缩。"""
        if self.stream:
            self.stream.close()
            self.stream = None

        dfn = self.dfn

        # 如果目标文件（或其 .gz 压缩包）不存在，则进行转储并压缩
        if not os.path.exists(dfn) and not os.path.exists(dfn + ".gz"):
            self.rotate(self.baseFilename, dfn)
            self.do_gzip(dfn)

        # 清理历史备份
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        # 如果不延迟，则重新打开流
        if not self.delay:
            self.stream = self._open()

        # 更新下次滚动的时间点
        current_time = int(time.time())
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at += self.interval

        # 如果跨越了 DST，需要做相应修正
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dst_at_rollover = time.localtime(new_rollover_at)[-1]
            dst_now = time.localtime(current_time)[-1]
            if dst_now != dst_at_rollover:
                addend = -3600 if not dst_now else 3600
                new_rollover_at += addend
        self.rolloverAt = new_rollover_at


# 获取项目的根目录（示例做法，根据需要自行修改）
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
default_logs_path = os.path.join(project_root, "logs")

server_name = os.getenv('SERVER.NAME', 'common-log')
server_logging_path = os.getenv('SERVER.LOGGING.PATH', default_logs_path)


class LoggerFormatter(logging.Formatter):
    """自定义的通用日志格式化器，可在此插入线程 ID、traceID 等上下文信息。"""

    def format(self, record: logging.LogRecord) -> str:
        ss = super().format(record)
        return ss


class MessageFormatter(logging.Formatter):
    """
    自定义的消息格式化器：
    - 在日志中插入 ISO8601 时间戳
    - 替换特殊字符
    """

    def format(self, record: logging.LogRecord) -> str:
        """在日志记录中增加 timestamp 字段。"""
        record.timestamp = get_current_iso()
        return super().format(record)

    def format_message(self, record: logging.LogRecord) -> str:
        """将日志消息中的特殊字符进行替换。"""
        record.message = record.message.replace('{', '【').replace('}', '】').replace('"', '``').replace("'", '`')
        return super().formatMessage(record)


def get_current_iso() -> str:
    """返回当前时间的 ISO 8601 格式。"""
    current_time = datetime.now(timezone(timedelta(hours=8)))
    formatted_time = current_time.isoformat()
    return formatted_time


class ColorFormatter(logging.Formatter):
    """可以给不同级别的日志关键字着色的格式化器。"""

    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    keyword_colors = {
        "INFO": green,
        "DEBUG": yellow,
        "WARNING": yellow,
        "ERROR": red,
        "CRITICAL": bold_red,
    }

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        format_str = '[%(levelname)s][%(asctime)s][%(threadName)s][%(funcName)s][%(filename)s:%(lineno)d] - %(message)s'
        formatter = logging.Formatter(format_str, datefmt='%Y-%m-%d %H:%M:%S')
        msg = formatter.format(record)

        for keyword, color in self.keyword_colors.items():
            escaped_keyword = re.escape(keyword)
            msg = re.sub(
                rf"\b({escaped_keyword})\b",
                rf"{color}\1{self.reset}",
                msg,
                flags=re.IGNORECASE
            )
        return msg

# 如果需要结构化存储单条日志内容，可以使用 pydantic，或注释掉
class Log(BaseModel if 'BaseModel' in globals() else object):  # 避免 pydantic 未安装导致错误
    """ 日志内容的数据模型，用于在内存中保存结构化信息 """
    msg: str
    level: str 
    time: float
    source: str


# === 合并 Logger，保持“代码一”的主体结构，融合“代码二”的部分逻辑 ===
class Logger:
    """
    统一的 Logger 类：
    - 保持代码一的全局 logging 配置和格式化处理。
    - 同时新增对日志的内存存储、verbose 模式切换、保存日志开关等功能。
    """
    log_instance: logging.Logger = None   # 全局共享的 logging.Logger
    file_handler: CommonTimedRotatingFileHandler = None
    console_handler: logging.StreamHandler = None
    json_handler: CommonTimedRotatingFileHandler = None

    # 新增：存储每条日志，用于后续分析或直接获取
    _logs: List[Log] = []
    _last_time: float = time.time()
    _verbose: bool = True
    _save_logs: bool = True
    
    @staticmethod
    def _calculate_time_diff() -> float:
        """计算与上一次写日志之间的时间差，用于统计执行时长等。"""
        now = time.time()
        time_diff = now - Logger._last_time
        Logger._last_time = now
        return time_diff

    @staticmethod
    def _invoked_from(level: int = 5) -> str:
        """推断调用 Logger 的类名，供内存记录使用。"""
        calling_class = None
        for frame_info in inspect.stack()[1:]:
            frame_locals = frame_info[0].f_locals
            calling_instance = frame_locals.get("self")
            if calling_instance and calling_instance.__class__ != Logger.__class__:
                calling_class = calling_instance.__class__.__name__
                break
            level -= 1
            if level <= 0:
                break
        return calling_class or "Unknown"

    @staticmethod
    def _get_logger() -> logging.Logger:
        """
        获取全局 logger；若已存在则返回同一个实例。
        包含控制台输出、文件输出（日志和 JSON 两种格式）。
        """
        if Logger.log_instance is not None:
            return Logger.log_instance

        log = logging.getLogger("")
        log.setLevel(logging.INFO)

        # 控制台 Handler（可根据 verbose 开关控制）
        Logger.console_handler = logging.StreamHandler(sys.stdout)
        Logger.console_handler.setFormatter(ColorFormatter())
        Logger.console_handler.setLevel(logging.INFO)
        log.addHandler(Logger.console_handler)

        # 文件 Handler
        hostname = socket.gethostname()
        rq = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
        log_date = rq[:10]

        if not os.path.exists(f"{server_logging_path}/{server_name}"):
            os.makedirs(f"{server_logging_path}/{server_name}", exist_ok=True)

        LOG_FILENAME = f'{server_logging_path}/{server_name}/{server_name}-{hostname}.log'
        JSON_FILENAME = f'{server_logging_path}/{server_name}/{server_name}-{hostname}.json'

        # 普通日志文件
        Logger.file_handler = CommonTimedRotatingFileHandler(
            LOG_FILENAME, backupCount=7, encoding="utf-8", when='D'
        )
        fmt = LoggerFormatter('[%(levelname)s][%(asctime)s][%(threadName)s][%(funcName)s][%(filename)s:%(lineno)d] - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
        Logger.file_handler.setFormatter(fmt)
        Logger.file_handler.setLevel(logging.INFO)
        log.addHandler(Logger.file_handler)

        # JSON 格式日志文件
        Logger.json_handler = CommonTimedRotatingFileHandler(
            JSON_FILENAME, backupCount=7, encoding="utf-8", when='D'
        )
        fmt_json = (
            '{"@timestamp" : "%(timestamp)s", "threadName":"%(threadName)s", "funcName":"%(funcName)s", '
            '"asctime": "%(asctime)s","service": "' + server_name + '", "filename": "%(filename)s", '
            '"line": "%(lineno)d", "levelname": "%(levelname)s", "message": "%(message)s"}'
        )
        Logger.json_handler.setFormatter(MessageFormatter(fmt_json))
        Logger.json_handler.setLevel(logging.INFO)
        log.addHandler(Logger.json_handler)

        Logger.log_instance = log
        return Logger.log_instance

    @staticmethod
    def log(message: str, level: int = logging.INFO):
        """
        供外部调用的统一日志接口：
        - 使用 logging 体系打印日志
        - 同时在内存中记录日志（_logs）
        """
        logger = Logger._get_logger()
        source = Logger._invoked_from()
        time_diff = Logger._calculate_time_diff()

        # 调用标准 logging
        if level == logging.INFO:
            logger.info(message)
        elif level == logging.WARNING:
            logger.warning(message)
        elif level == logging.ERROR:
            logger.error(message)
        elif level == logging.CRITICAL:
            logger.critical(message)
        else:
            logger.debug(message)

        # 记录在内存
        # 如果 pydantic 未安装，Log 类会是普通的 object，这里仅做示例
        if BaseModel:
            log_obj = Log(
                msg=message,
                level=logging.getLevelName(level),
                time=time_diff,
                source=source
            )
        else:
            # 无 pydantic 的简化存储结构
            log_obj = {
                "msg": message,
                "level": logging.getLevelName(level),
                "time": time_diff,
                "source": source
            }
        Logger._logs.append(log_obj)

    @staticmethod
    def get_logs() -> List:
        """返回所有内存日志记录。"""
        return Logger._logs

    @staticmethod
    def clear_logs():
        """清空内存中的日志记录。"""
        Logger._logs.clear()

    # === verbose 开关 ===
    @staticmethod
    def set_verbose(verbose: bool):
        """
        打开或关闭控制台输出，默认打开。
        """
        Logger._verbose = verbose
        # 先确保 logger 存在
        logger = Logger._get_logger()
        if Logger.console_handler:
            logger.removeHandler(Logger.console_handler)

        if verbose:
            Logger.console_handler.setLevel(logging.INFO)
            logger.addHandler(Logger.console_handler)

    @staticmethod
    def get_verbose() -> bool:
        return Logger._verbose

    # === 是否写入文件 ===
    @staticmethod
    def set_save_logs(save_logs: bool):
        """
        打开或关闭文件写入。若关闭，则移除文件 Handler；若开启，则添加文件 Handler。
        """
        Logger._save_logs = save_logs
        logger = Logger._get_logger()

        if not save_logs:
            # 移除 file_handler 和 json_handler
            if Logger.file_handler in logger.handlers:
                logger.removeHandler(Logger.file_handler)
            if Logger.json_handler in logger.handlers:
                logger.removeHandler(Logger.json_handler)
        else:
            # 再次添加回 file_handler, json_handler
            if Logger.file_handler not in logger.handlers:
                logger.addHandler(Logger.file_handler)
            if Logger.json_handler not in logger.handlers:
                logger.addHandler(Logger.json_handler)

    @staticmethod
    def get_save_logs() -> bool:
        return Logger._save_logs


# 初始化全局 logger（如果需要自动进行一些埋点、统计等，可在这里调用）
logger = Logger._get_logger()
# scarf_analytics()  # 如果需要，可以在此处调用外部统计函数

# # ========== 用法示例 ==========
# if __name__ == "__main__":
#     Logger.log("Hello, this is an info log.")
#     Logger.log("Check a warning!", level=logging.WARNING)
#     Logger.log("Severe error occurred", level=logging.ERROR)

#     print("Memory logs:", Logger.get_logs())

#     # 关闭控制台输出
#     Logger.set_verbose(False)
#     Logger.log("Console output turned OFF, but file logging remains.")

#     # 关闭文件日志输出
#     Logger.set_save_logs(False)
#     Logger.log("Now neither console nor file gets logs, but memory still records them.")

#     # 恢复控制台和文件
#     Logger.set_verbose(True)
#     Logger.set_save_logs(True)
#     Logger.log("Everything is back ON again.")
