from time import sleep
from requests import post
from threading import Thread
from datetime import time, datetime

from .exceptions import SendMsgError
from .base import Base
from .azure import Azure


class EmptyTask(Thread):

    def __init__(self):
        super().__init__()

    def run(self):
        input("Press any key to exit ...\n")


class MainTask(Base, Thread):

    def __init__(self, debug=False):
        Base.__init__(self, module_path=__name__, debug=debug)
        Thread.__init__(self)

    @property
    def loop(self):
        return self.__class__.loop

    @loop.setter
    def loop(self, value):
        self.__class__.loop = value

    def send_to_webhook(self, msg):
        response = post(
            self.config["webhook"]["url"],
            data={"content": msg},
            proxies=self.config["proxies"]
        )
        if not response.status_code in [200, 204]:
            raise SendMsgError(f"Webhook returned status code - {response.status_code}, " + 
                               f"reason: '{response.reason}'")

    def format_msg(self, prs):
        msg = "Active Pull Requests:\n```"
        for pr in prs:
            approv_list = [r["approved"] for r in pr["reviewers"]]
            reviewers_count = len(approv_list)
            approv_reviewers_count = len(list(filter(lambda x: x, approv_list)))
            msg += f"[{pr['author']}] [{approv_reviewers_count}/{reviewers_count}] " + \
                   f"({pr['id']}) {pr['title']}\n"
        msg += "\n```"
        return msg

    def run(self):
        try:
            azure = Azure()
            while self.loop:
                datetime_now = datetime.now().replace(microsecond=0)
                despatch_list = [datetime.combine(datetime_now.today(), time(**despatch)) for despatch in self.config["despatch"]]
                if datetime_now in despatch_list:
                    self.send_to_webhook(self.format_msg(azure.team.get_pull_requests()))
                else:
                    sleep(1)
        except Exception as e:
            self.logger.error(e)
