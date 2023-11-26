# Licenced under CC0.  See
# <https://creativecommons.org/publicdomain/zero/1.0/legalcode.en>.

# This program takes 1 command-line argument, a file containing a
# dot file produced by Vector's 'graph' subcommand.  It reads that
# dot file and prints a new dot graph to standard output.  The new
# dot graph is a more readable version of the original graph.

import argparse
import sys
from collections.abc import Sequence

from pygraphviz import AGraph


def main() -> None:
    args = parse_args()

    graph = (
        AGraph(string=sys.stdin.read())
        if args.input_file == "-"
        else AGraph(file=args.input_file)
    )

    clarify_graph(graph)

    print(graph.string())


def clarify_graph(graph: AGraph) -> None:
    in_subgraph_nodes = []
    out_subgraph_nodes = []

    for node in graph.nodes_iter():
        match node.attr["shape"]:
            case "trapezium":
                in_subgraph_nodes.append(node)
            case "invtrapezium":
                out_subgraph_nodes.append(node)

    in_subgraph = graph.add_subgraph(
        [node.name for node in in_subgraph_nodes], "sub_in"
    )
    in_subgraph.graph_attr["rank"] = "same"
    out_subgraph = graph.add_subgraph(
        [node.name for node in out_subgraph_nodes], "sub_out"
    )
    out_subgraph.graph_attr["rank"] = "same"
    # 2023-11-20: my definite recollection from yesterday is that
    # the subgraph doesn't appear unless you give it a name.  It's
    # also my recollection that this behaviour applies only to pygraphviz;
    # it wouldn't happen if you wrote your own dot file by hand.

    for node in graph.nodes_iter():
        match node.attr["shape"]:
            case "trapezium":
                node.attr["color"] = "green"
            case "diamond":
                node.attr["color"] = "orange"
            case "invtrapezium":
                node.attr["color"] = "magenta"

        node.attr["shape"] = "box"
        node.attr["style"] = "filled"


def parse_args(args: Sequence[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        help="""
        input file containing Dot output from Vector's 'graph' subcommand,
        or "-" to read from standard input
    """,
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    main()
