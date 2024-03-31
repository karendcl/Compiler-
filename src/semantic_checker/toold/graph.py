from src.cmp.ast import TypeDeclarationNode, ProtocolDeclarationNode
from typing import List, Union
from src.cmp.ast import *
from src.cmp.semantic import Context
from graphlib import TopologicalSorter


class Graph:
    def __init__(self, nodes, context):
        self.nodes = nodes
        self.edges = {}

        for t in nodes:

            self.edges[t] = []

        for t in nodes:
            type_ = context.get_type_or_protocol(t)

            try:
                if type_.parents:
                    for e in type_.parents:
                        self.edges[e.name].append(t)
            except:
                try:

                    if type_.parent:
                        try:
                            self.edges[type_.parent].append(t)
                        except:
                            self.edges[type_.parent.name].append(t)
                except:
                    pass


    def __str__(self):
        s = ""
        for t in self.nodes:
            s += f"{t} -> {self.edges[t]}\n"
        return s

    def __repr__(self):
        return self.__str__()


def topological_order(types: list, context):
    graph = Graph(types, context)
    cycle = False
    try:
        ts = TopologicalSorter(graph.edges)
        tuple(ts.static_order())
    except:
        cycle = True
    return cycle


def check_for_circular_dependencies(context: Context):
    list_ = [i for i in context.types.keys()]
    list_ += [i for i in context.protocols.keys()]

    return topological_order(list_, context)

