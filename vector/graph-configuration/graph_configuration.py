# This program supports Python 3.11+.

# To learn how to use this program, run it with the "--help" option.

import argparse
import json
import string
import sys
import textwrap
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

Rankdir: TypeAlias = Literal["TB", "BT", "LR", "RL"]


def main() -> None:
    args = parse_args()

    vector_config_json = sys.stdin.read()
    vector_config = json.loads(vector_config_json)

    graph = Graph(args.rankdir)

    for source in vector_config["sources"]:
        graph.add_source(source)

    for transform in vector_config["transforms"]:
        graph.add_transform(transform)

    for sink in vector_config["sinks"]:
        graph.add_sink(sink)

    def add_edges(components: dict[str, Any]) -> None:
        for component_id, component in components.items():
            for i in component.get("inputs", []):
                # The edge will have a label if the input is from a transform
                # of type Route.  See
                # <https://vector.dev/docs/reference/configuration/transforms/route/#outputs>.
                if isinstance(i, dict):
                    # This format is produced by "vector convert-config".
                    # It seems to be undocumented at time of writing this
                    # sentence.
                    edge = Edge(i["component"], component_id, i.get("port"))
                elif isinstance(i, str):
                    parts = i.split(".", 1)
                    label = parts[1] if len(parts) == 2 else None
                    edge = Edge(parts[0], component_id, label)
                else:
                    raise Exception(f"unexpected type for component input: {type(i)}")
                graph.add_edge(edge)

    add_edges(vector_config["transforms"])
    add_edges(vector_config["sinks"])

    print(graph.to_dot())


@dataclass
class Edge:
    head: str
    tail: str
    label: str | None

    def to_dot(self) -> str:
        return f"{self.head} -> {self.tail}{self._possible_label_dot()}"

    def _possible_label_dot(self) -> str:
        return (
            ""
            if self.label is None
            else ' [label="' + self.label.replace('"', '\\"') + '"]'
            # The rules for quoting of labels (and strings generally)
            # are at <https://graphviz.org/doc/info/lang.html>.
        )


class Graph:
    sources: list[str]
    transforms: list[str]
    sinks: list[str]
    edges: list[Edge]
    rankdir: Rankdir

    def __init__(self, rankdir: Rankdir):
        self.sources = []
        self.transforms = []
        self.sinks = []
        self.edges = []
        self.rankdir = rankdir

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

    def add_sink(self, sink: str) -> None:
        self.sinks.append(sink)

    def add_source(self, source: str) -> None:
        self.sources.append(source)

    def add_transform(self, transform: str) -> None:
        self.transforms.append(transform)

    def to_dot(self) -> str:
        final_template = textwrap.dedent(self._DOT_TEMPLATE)
        return string.Template(final_template).substitute(
            rankdir=self.rankdir,
            sources_dot="; ".join(self.sources),
            transforms_dot="; ".join(self.transforms),
            sinks_dot="; ".join(self.sinks),
            edges_dot="; ".join(e.to_dot() for e in self.edges),
        )

    _DOT_TEMPLATE = """\
      digraph vector_configuration {
        graph [rankdir=$rankdir]
        node [shape=box, style=filled, color=orange]

        subgraph sources {
          graph [rank=same]
          node [color=green]
          $sources_dot
        }

        subgraph sinks {
          graph [rank=same]
          node [color=magenta]
          $sinks_dot
        }

        $transforms_dot

        $edges_dot
      }
    """


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="""
            This program reads a Vector configuration in JSON
            format from standard input. It outputs a graph to
            standard output that shows data flow between components
            in the configuration.  The graph is in Dot format (see
            <https://graphviz.org/doc/info/lang.html>).  The generated
            graph is better than the one produced by Vector's 'graph'
            subcommand.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--rankdir",
        "-r",
        default="TB",
        choices=["TB", "BT", "LR", "RL"],
        help="rankdir of Graphviz digraph (see <https://graphviz.org/docs/attrs/rankdir/>)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
