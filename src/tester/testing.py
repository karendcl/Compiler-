import src.cmp.grammar
from src.cmp.grammar import G
import src.cmp.grammar as grammar
from src.parser import parser, utils
from src.cmp.utils import Token
from src.lexer.utils.regexs import Regexs
from src.lexer import Usage_Example
import json

#building lexer
lexer = Usage_Example.lexer

#building parser
pars = parser.LR1Parser(G, verbose=True)

#testcases
testcase0 = '1+2;'
testcase1 = '1+2*3;'
testcase2 = ('function main() => print(1+2); '
             '4;')
testcase3 = '{let x = 1 in x;}'
testcase4 = ('{let x = 1 in'
             ' let y = 2 in '
             'x+y;}')
testcase5 = 'if(1==1) print(1) else {print(2);}'
testcase6 = '42;'
testcase7 = 'print((((1+2)^3)*4)/5);'
testcase8 = 'let a = 42 in print(if (a == 2) "1" else "2");'
testcase9 = 'print(sin(pi));'
testcase10 = ('function f(x,y) => sin(x+y); '
              '4;')
testcase11 = 'print(1@"Yes");'
testcase12 = 'print(1@"Yes"@"No");'
testcase13 = ('function f(x,y) {sin(x+y);'
              '                 print(5);}'
              ' 4;')
testcase14 = 'let msg = "Hello" in print(msg);'
testcase15 = ' let number = 42, test = "The meaning of life is" in print(test@@number);'
testcase16 = 'let number = 42 in (let text = "The meaning of life is" in ( print(test@number)));'
testcase17 = 'let a = 6, b = a*7 in print(b);'
testcase18 = 'let a=7, b=10,c=20 in {print(a);print(b);print(c);}'
testcase19 = 'let a = (let b =6 in b*7) in print(a);'
testcase20 = 'print(let b =6 in b*7);'
testcase21 = 'let a =20 in {let a =42 in print (a); print(a);}'
testcase22 = 'let a=0 in {print(a); a := 1; print(a);}'
testcase23 = 'let a =0 in let b = a := 1 in {print(a); print(b);};'
testcase24 = 'let a = 42 in if (a == 2) print(1) else print(2);'
testcase25 = 'let a = 2 in if (a ==2) {print(1);} else print(2);'
testcase26 = 'let a = 10 in while (a > 0) {print(a); a := a - 1;}'
testcase27 = 'for (x in range(1,10)) print(x);'
testcase28 = 'protocol Hashable { hash(): Number; } 4;'
testcase29 = 'protocol Equatable extends Hashable { equals(other: Object): Boolean; } 4;'
testcase30 = 'let numbers = [1,2,3,4,5,6,7,8] in for (x in numbers) print(x);'
testcase31 = 'let numbers = [x^2 || x in range(1,10)] in print(x);'
testcase32 = 'print("The \\"message is " @ 1);'
testcase33 = 'type Point { x = 0; y=0; getX()=> self.x;} print(a);'
testcase34 = 'let pt = new Point() in print("x: " @ pt.getX() @ " y: " @ pt.getY());'
testcase35 = 'let vector = [1,2,3,4] in print(vector[0]);'
#testing power operator
testcase36 = 'print(5*2^3*4);'
#testing modulo operator
testcase37 = 'print(3^5%2^5);'


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
    print(f'Testcase {i}: {testcase}')
    testcase = lexer(testcase)
    testing(testcase)



