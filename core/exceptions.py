class BaseConfugError(ValueError):
    pass

class ProjectNotFoundError(BaseConfugError):
    pass

class TeamNotFoundError(BaseConfugError):
    pass

class RepositoryNotFoundError(BaseConfugError):
    pass

class ConfigUpploadError(BaseConfugError):
    pass

class TeamMembersListEmpty(BaseConfugError):
    pass

class SendMsgError(SystemError):
    pass