## Introduction

`graph_configuration.py` is a simple program to help
[Vector](https://vector.dev/) administrators.
It was developed with
[Vector 0.34.1](https://github.com/vectordotdev/vector/releases/tag/v0.34.1).
It needs nothing but a Python interpreter and works with
Python 3.11+.

## Usage message

```
usage: graph_configuration.py [-h] [--rankdir {TB,BT,LR,RL}]

This program reads a Vector configuration in JSON format from standard input.
It outputs a graph to standard output that shows data flow between components
in the configuration. The graph is in Dot format (see
<https://graphviz.org/doc/info/lang.html>). The generated graph is better than
the one produced by Vector's 'graph' subcommand.

options:
  -h, --help            show this help message and exit
  --rankdir {TB,BT,LR,RL}, -r {TB,BT,LR,RL}
                        rankdir of Graphviz digraph (see
                        <https://graphviz.org/docs/attrs/rankdir/>) (default:
                        TB)
```

You can get the above by running:

```sh
python3 graph_configuration.py --help
```
