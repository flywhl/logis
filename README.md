<div align="center">
  
  ![logo](https://github.com/user-attachments/assets/70bdda50-51ca-453e-9098-69d6668924fd)

  [Discord](https://discord.gg/kTkF2e69fH) • [Website](https://flywhl.dev) • [Installation](#installation)
  <br/>
  <br/>
</div>

## Features

`logis` turns your commit history into a searchable scientific log.

Every time you run an experiment, your code will be auto-committed with metadata in the commit message.


## Installation

* `uv add logis`

## Usage

* Put the `@commit` decorator on your experiment function.
* `logis` will store hyperparameters and metrics as metadata in the commit message.
* Query your scientific log, e.g. `logis query metrics.accuracy < 0.8`.

```python
from logis import commit, Run

@commit
def my_experiment(run: Run) -> Metrics:

    # ... experiment stuff

    run.set_hyperparameters({
        "lr": 0.001,
        "epochs": 100,
    })

    # ... more experiment stuff

    run.set_metrics({
        "accuracy": 0.9,
    })

if __name__ == "__main__":
    my_experiment()
```

Then run your experiment:

```
$ python experiment.py

Generating commit with message:

    exp: run my_experiment at 2025-02-10 18:39:18.759230

    ---

    {
      "experiment": "my_experiment",
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
$ logis query metrics.accuracy > 0.8

Found 1 commit(s):

    af6cd7
```


## Development

* `git clone https://github.com/flywhl/logis.git`
* `cd logis`
* `uv sync`
* `just test`

## Flywheel

Science needs better software tools. [Flywheel](https://flywhl.dev/) is an open source collective building simple tools to preserve scientific momentum, inspired by devtools and devops culture. Join our Discord [here](discord.gg/fd37MFZ7RS).
