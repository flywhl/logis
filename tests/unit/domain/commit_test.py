from pydantic import BaseModel

from mthd.domain.git import ExperimentState


def test_commitmessage_format_success():
    class Hypers(BaseModel):
        a: int
        b: float
        c: str

    msg = ExperimentState(
        summary="test",
        hyperparameters=Hypers(a=1, b=2.0, c="3").model_dump(),
    )

    print(msg.as_commit_message())
