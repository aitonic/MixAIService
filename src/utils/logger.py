# 解决多进程日志写入混乱问题
import os, time, gzip
from logging.handlers import TimedRotatingFileHandler


class CommonTimedRotatingFileHandler(TimedRotatingFileHandler):

    @property
    def dfn(self):
        currentTime = int(time.time())
        # get the time that this sequence started at and make it a TimeTuple
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." + time.strftime(self.suffix, timeTuple))

        return dfn

    def computeRollover(self, currentTime):
        # 将时间取整
        t_str = time.strftime(self.suffix, time.localtime(currentTime))
        t = time.mktime(time.strptime(t_str, self.suffix))
        return TimedRotatingFileHandler.computeRollover(self, t)

    def doGzip(self, old_log):
        try:
            with open(old_log) as old:
                with gzip.open(old_log + '.gz', 'wt') as comp_log:
                    comp_log.writelines(old)
            os.remove(old_log)
        except:
            pass

    def shouldRollover(self, record):
        """
        是否应该执行日志滚动操作：
        1、存档文件已存在时，执行滚动操作
        2、当前时间 >= 滚动时间点时，执行滚动操作
        """
        dfn = self.dfn
        t = int(time.time())
        if t >= self.rolloverAt or os.path.exists(dfn):
            return 1
        return 0

    def doRollover(self):
        """
        执行滚动操作
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
            self.doGzip(dfn)

        # 备份数控制
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        # 延迟处理
        if not self.delay:
            self.stream = self._open()

        # 更新滚动时间点
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            dstNow = time.localtime(currentTime)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
       
import logging
import logging.handlers
import os
import socket
import sys
import time
from datetime import datetime, timezone, timedelta

server_name = os.getenv('server.name', 'common-log')
server_logging_path = os.getenv('server.logging.path', '~/apps/logs')

class LoggerFormatter(logging.Formatter):
    
    def format(self, record):
        # record.traceId = thread_local.getTraceId()
        ss = logging.Formatter.format(self, record)
        return ss

class MessageFormatter(logging.Formatter):
    
    def format(self, record):
        # record.traceId = thread_local.getTraceId()
        record.timestamp = get_current_iso()
        
        return logging.Formatter.format(self, record)
    
    def formatMessage(self, record):
        record.message = record.message.replace('{', '【').replace('}', '】').replace('"', '``').replace("'", '`')
        return super().formatMessage(record)

def get_current_iso():
    
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
    
    logInstance = None

    @staticmethod
    def _get_logger():
        if Logger.logInstance is not None:
            return Logger.logInstance
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
        
        Logger.logInstance = log
        return Logger.logInstance
    

logger = Logger._get_logger()