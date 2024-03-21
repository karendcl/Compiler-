from src.cmp.grammar import G
import src.cmp.grammar as grammar
from src.parser import parser, utils
from src.lexer.utils.token import Token
import json

pars = parser.LR1Parser(G, True)

#testing simple expressions
testcase0 = [
    Token('1', grammar.num),
    Token('+', grammar.plus),
    Token('2', grammar.num),
    Token(';', grammar.semi_colon),
    Token('$', G.EOF)
]


testcase1 = [
    Token('1', grammar.num),
    Token('+', grammar.plus),
    Token('2', grammar.num),
    Token('*', grammar.star),
    Token('3', grammar.num),
    Token(';', grammar.semi_colon),
    Token('$', G.EOF)
]


testcase2 = [
    Token('function', grammar.function),
    Token('main', grammar.idx),
    Token('(', grammar.opar),
    Token(')', grammar.cpar),
    Token('=>', grammar.rarrow),
    Token('print', grammar.printx),
    Token('(', grammar.opar),
    Token('1', grammar.num),
    Token('+', grammar.plus),
    Token('2', grammar.num),
    Token(')', grammar.cpar),
    Token(';', grammar.semi_colon),
    Token('print', grammar.printx),
    Token('(', grammar.opar),
    Token('1', grammar.num),
    Token('+', grammar.plus),
    Token('2', grammar.num),
    Token(')', grammar.cpar),
    Token(';', grammar.semi_colon),
    Token('$', G.EOF)
]

testcase3 = [
    Token('{', grammar.curly_o),
    Token('let', grammar.let),
    Token('x', grammar.idx),
    Token('=', grammar.equal),
    Token('1', grammar.num),
    Token('in', grammar.inx),
    Token('x', grammar.idx),
    Token(';', grammar.semi_colon),
    Token('}', grammar.curly_c),
    Token('$', G.EOF)]

testcase4 = [
    Token('{', grammar.curly_o),
    Token('let', grammar.let),
    Token('x', grammar.idx),
    Token('=', grammar.equal),
    Token('1', grammar.num),
    Token('in', grammar.inx),
    Token('let', grammar.let),
    Token('y', grammar.idx),
    Token('=', grammar.equal),
    Token('2', grammar.num),
    Token('in', grammar.inx),
    Token('x', grammar.idx),
    Token('+', grammar.plus),
    Token('y', grammar.idx),
    Token(';', grammar.semi_colon),
    Token('}', grammar.curly_c),
    Token('$', G.EOF)]

def testing(testcase, should_assert = True):
    try:
        parse, operations = pars([t.token_type for t in testcase], get_shift_reduce=True)
        ast = parser.evaluate_reverse_parse(parse, operations, testcase)
        if should_assert:
            assert True
    except Exception as e:
        if should_assert:
            print(e)
            assert False


testcases = []
while True:
    try:
        testcases.append(eval(f'testcase{len(testcases)}'))
    except:
        break

for i, testcase in enumerate(testcases):
    print(f'Testcase {i}:')
    testing(testcase)





# utils.parser_to_json(pars)
#
# pars2 = utils.json_to_parser()
#
# assert pars.action == pars2.action
# assert pars.goto == pars2.goto
# assert pars.G == pars2.G




