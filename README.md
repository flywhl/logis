<div align="center">
  
  ![logo](https://github.com/user-attachments/assets/cb3ddb4f-5f40-4231-9efe-29e045705dda)

  [Discord](https://discord.gg/kTkF2e69fH) • [Website](https://flywhl.dev) • [Installation](#installation)
  <br/>
  <br/>
</div>

## Features

`mthd` turns your commit history into a searchable scientific log.

Every time you run an experiment, your code will be auto-committed with metadata in the commit message.


## Installation

* `uv add mthd`

## Usage

* Put the `@commit` decorator on your experiment function.
* `mthd` will store hyperparameters and metrics as metadata in the commit message.
* Query your scientific log, e.g. `mthd query metrics.accuracy < 0.8`.

```python
from mthd import commit
from pydantic import BaseModel

class Hypers(BaseModel):

    lr: float
    epochs: int


class Metrics(BaseModel):

    accuracy: float


@commit(hypers="hypers")
def my_experiment(hypers: Hypers) -> Metrics:
    ...
    # experiment
    ...

    metrics = Metrics(...)

    return metrics
```

Then run your experiment:

```
$ python experiment.py

Generating commit with message:

    exp: run test at 2025-02-10 18:39:18.759230

    ---

    {
      "experiment": "test",
      "hyperparameters": {
        "lr": 0.001,
        "epochs": 100,
      },
      "metrics": {
        "accuracy": 0.9,
      },
      "uuid": "94871de1-4d6c-4e70-9c9d-60ec11df1159",
      "artifacts": null,
      "annotations": null,
      "timestamp": "2025-02-10T18:39:18.759230"
    }
```

Finally, query for relevant commits:

```
$ mthd query metrics.accuracy > 0.8

Found 1 commit(s):

    af6cd7
```


## Development

* `git clone https://github.com/flywhl/mthd.git`
* `cd mthd`
* `uv sync`
* `just test`

## Flywheel

Science needs better software tools. [Flywheel](https://flywhl.dev/) is an open source collective building simple tools to preserve scientific momentum, inspired by devtools and devops culture. Join our Discord [here](discord.gg/fd37MFZ7RS).
