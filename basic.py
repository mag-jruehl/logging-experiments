import jsonmsg_Logger
import logging


logger = logging.getLogger("mdspo")

logger.debug("hi")

logger.summary_json("this is summary")
logger.warning("something aint right...")
