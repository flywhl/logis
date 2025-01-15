from mthd.util.model import Model


class CommitMessage(Model):
    summary: str
    parameters: dict
    annotations: dict
