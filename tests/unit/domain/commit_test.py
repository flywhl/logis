from pydantic import BaseModel

from mthd.domain.commit import CommitMessage


def test_commitmessage_format_success():
    class Hypers(BaseModel):
        a: int
        b: float
        c: str

    msg = CommitMessage(
        summary="test",
        hyperparameters=Hypers(a=1, b=2.0, c="3"),
    )

    print(msg.format())
