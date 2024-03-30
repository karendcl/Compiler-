import src.cmp.grammar
from src.cmp.grammar import G
import src.cmp.grammar as grammar
from src.parser import parser, utils
from src.cmp.utils import Token
from src.lexer.utils.regexs import Regexs
from src.lexer import Usage_Example
import json
from src.cmp.ast import *
from src.cmp.format_visitor import *
from src.evaluator.my_own import *
from src.semantic_checker import TypeCollector
from src.semantic_checker import TypeBuilder
from src.semantic_checker import TypeChecker
from src.cmp.semantic import Context, Scope
from src.semantic_checker.toold.graph import check_for_circular_dependencies

lexer = None
pars = None

def building():
    global lexer, pars
    #building lexer
    lexer = Usage_Example.lexer

    #building parser
    pars = parser.LR1Parser(G, verbose=False)
    return lexer, parser

def compiling(stream_of_tokens):
    parse, operations = pars([t.token_type for t in stream_of_tokens], get_shift_reduce=True)
    ast = parser.evaluate_reverse_parse(parse, operations, stream_of_tokens)
    print(ast)

    # COLLECTING TYPES
    type_collector = TypeCollector.TypeCollector(errors=[])
    type_collector.visit(ast)
    print(type_collector.context)

    # CHECKING CIRCULAR DEPENDENCIES
    type_builder = TypeBuilder.TypeBuilder1(type_collector.context, type_collector.errors)
    type_builder.visit(ast)
    if check_for_circular_dependencies(type_collector.context):
        type_collector.errors.append('Circular dependence present')

        # RESETTING TYPES BUILT
    for i in type_collector.context.protocols:
        pr = type_collector.context.get_protocol(i)
        pr.children = []
        pr.parents = pr.orig_parent
    for i in type_collector.context.types:
        tp = type_collector.context.get_type(i)
        tp.parent = tp.orig_parent
        tp.children = []
        print(tp)

    print(type_collector.context)

    # BUILDING ACTUAL TYPES AND METHODS OF TYPES AND PROTOCOLS
    type_builder = TypeBuilder.TypeBuilder2(type_collector.context, type_collector.errors)
    type_builder.visit(ast)
    print(type_collector.context)
    print(type_builder.errors)

    # CHECKING RETURN TYPES
    type_checker = TypeChecker.TypeChecker(type_collector.context, type_collector.errors)
    scope: Scope = type_checker.visit(ast)
    print(type_checker.errors)

    if type_checker.errors == []:
        eval = Evaluator(type_checker.context)
        eval.visit(ast)

    running()

def running():
    print("==============================================")
    code = ''
    name_of_file = input('Name of file in this folder: (ex.hulk) ')
    with open(name_of_file, 'r') as f:
        code = f.read()

    tokens = lexer(code)

    compiling(tokens)




def main():
    global lexer, parser
    building()
    running()


if __name__ == '__main__':
    main()
code = lexer(code)



