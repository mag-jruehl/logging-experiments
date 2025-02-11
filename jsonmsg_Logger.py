import logging
import sys


class jsonmsg_Logger(logging.Logger):
    """this logger adds the type argument so it can be successfully formatted"""

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
    ):
        if not extra:
            extra = {}
        if "type" not in extra:
            extra["type"] = "unspecified"

        # this happens if a call to the regular loggers warning(), critical() or error() is made
        if level >= logging.WARNING:
            extra["type"] = "error"

        return super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

    # the following methods are used to create a json formatted message
    # they specify the type of json, which is used in further evaluation by our splunk
    # we could also write to another log level
    def summary_json(self, msg, *args, **kwargs):
        return self.info(msg, *args, extra={"type": "summary"}, **kwargs)

    def detail_json(self, msg, *args, **kwargs):
        return self.info(msg, *args, extra={"type": "detail"}, **kwargs)

    def debug_json(self, msg, *args, **kwargs):
        return self.info(msg, *args, extra={"type": "debug"}, **kwargs)

    def full_json(self, msg, *args, **kwargs):
        return self.info(msg, *args, extra={"type": "full"}, **kwargs)

    def error_json(self, msg, *args, **kwargs):
        return self.info(msg, *args, extra={"type": "error"}, **kwargs)


# now create the mdspo logger
# there will be handlers for
# - messages formatted to json and sent to splunk
# - messages printed to console for debugging purposes
# - critical / error messages sent to a seperate error logfile

logging.setLoggerClass(jsonmsg_Logger)
mdspo_logger = logging.getLogger("mdspo")
mdspo_logger.setLevel(logging.DEBUG)

RUNID = 321  # getrunid()
tojson_formatter = logging.Formatter(
    f"{{'time':%(asctime)s 'run_id':'{RUNID}', 'type':'%(type)s' 'message':'%(message)s'}}"
)

splunk_handler = logging.FileHandler("splunk.log")
splunk_handler.setLevel(logging.INFO)
splunk_handler.addFilter(lambda record: record.levelno == logging.INFO)  # only INFO
splunk_handler.setFormatter(tojson_formatter)
mdspo_logger.addHandler(splunk_handler)

error_handler = logging.FileHandler("error.log")
error_handler.setLevel(logging.WARNING)
error_handler.setFormatter(tojson_formatter)
mdspo_logger.addHandler(error_handler)

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.DEBUG)
debug_formatter = logging.Formatter("%(name)s-%(levelname)s: %(message)s")
console_handler.setFormatter(debug_formatter)
mdspo_logger.addHandler(console_handler)

mdspo_logger.debug("mdspo logger initialized")
