class MessageTemplates:
    
    @staticmethod
    def create_pull_request(*, is_draft, author, reviewers, title, url):
        pull_request = MessageTemplatesPullRequest()
        pull_request.is_draft = is_draft
        pull_request.author = author
        pull_request.reviewers = reviewers
        pull_request.title = title
        pull_request.url = url
        return pull_request

    @staticmethod
    def create_pull_requests(pull_requests):
        msg_parts = []
        msg = ""

        for pull_request in pull_requests:
            if len(msg + str(pull_request)) < 1800:
                msg += str(pull_request) + "\n"
            else:
                msg_parts.append(msg)
                msg = str(pull_request) + "\n"

        msg_parts.append(msg)

        return tuple(msg_parts)

class MessageTemplatesPullRequest:

    def __str__(self):
        return f"`[{'d' if self.is_draft else 'p'}]`[`[{self.author}] " + \
               f"[{self.get_approv_status()}] {self.title}`]({self.url})"

    def get_approv_status(self):
        approv_list = [r["approved"] for r in self.reviewers]
        reviewers_count = len(approv_list)
        approv_reviewers_count = len(list(filter(lambda x: x, approv_list)))
        return f"{approv_reviewers_count}/{reviewers_count}"