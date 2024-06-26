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


#building lexer
lexer = Usage_Example.lexer

#building parser
pars = parser.LR1Parser(G, verbose=False)

number = 0

#testing simple arithmetic expressions
testcase0 = ('{let x = 1 in'
             ' let y = x := 4 * x in '
             'print(x+y);}')

testcase1 = 'let x = 4 in print(x);'

testcase2 = 'if (true & false | true) print(1) else {print(2);};'

testcase3 = 'print((((1+2)^3)*4)/5);'

# todo bug con @
testcase4 = 'let a = "42" in print(if (4 < 2) "1" else 5@@"Hola"@4);'
#
testcase5 = ('type A (a,b) { b = 0; a = 0; c = 0; d: int; getX() => self.a; }'
             'let a = new A(4,5) in print(a);')

testcase6 = ('type A { b = 0; a = 0; c = 0; d: int; getX() => self.b; }'
              'type B inherits A { b = "hola"; c = 1; getX() => base(); }'
              'function p(a) => a;'
              'protocol N { f(): int; '
              '             g( a: int ): int; }'
              'protocol S extends M { h(): int; }'
              'protocol M  { i(): int; }'
              'protocol J extends M {k():int;}'
              'let a = new B() in '
              'if (a is Object) print(a.getX()) else a.getX();')

testcase7 = 'let a = range(1,10) in print(a[1]);'

testcase8 = 'let a = [1,2,3,4] in for (x in a) print(x) else print(a);'

testcase9 = 'let a = [x^2 || x in range(1,4)] in print(a);'

testcase10 = ('let a = 4 in '
              '{'
              'let b = a := "Hola" in print(a);'
              'a := 7;'
              'print(a);'
              '}')

testcase11 = ('type A { b = 0; a = 0; c = 0; d: int; getX() => self.b; }'
              'type B inherits A { b = "hola"; c = 1; getX() => base(); }'
              'function p(a) => a;'
              'protocol N { f(): int; '
              '             g( a: int ): int; }'
              'protocol S extends M { h(): int; }'
              'protocol M  { i(): int; }'
              'protocol J extends M {k():int;}'
              'let a = new B() in '
              'if ( ! (a is B)) print(1) else if (4>3) p(4) else print(a);')

testcase12 = ('{let a=[1,2,3,4] in '
              '{ a[1] := 5;'
              'print(a);};'
              'print(4);};')

# testcase1 = 'log(4.5,4);'
#
# #testing function declaration
# testcase2 = ('function main() => print(1+2); '
#              '4;')
#
# testcase10 = ('function f(x,y) => sin(x+y); '
#               '4;')

#
# testcase6 = '42;'
#
# #testing nested expressions

#
# testcase9 = 'print(sin(pi));'
#
# #testing concatenation
# testcase11 = 'print(1@"Yes");'
testcase38 = 'print(1@"Yes"@"No");'
testcase13 = ('function f(x,y) {print(sin(x+y));'
              '                 print(5);}'
              ' print(f(4,2));')
testcase14 = 'let msg = "Hello" in print(msg);'
testcase15 = ' let number = 42, test = "The meaning of life is" in print(test@@number);'
testcase16 = 'let number = 42 in (let text = "The meaning of life is" in ( print(text@number)));'
testcase17 = 'let a = 6, b = a*7 in print(b);'
testcase18 = 'let a=7, b=10,c=20 in {print(a);print(b);print(c);};'
testcase19 = 'let a = (let b =6 in b*7) in print(a);'
testcase20 = 'print(let b =6 in b*7);'
testcase21 = 'let a =20 in {let a =42 in print (a); print(a);};'
testcase22 = 'let a=0 in {print(a); a := 1; print(a);};'
testcase23 = 'let a =0 in let b = a := 1 in {print(a); print(b);};'
testcase24 = 'let a = 42 in if (a == 2) print(1) else print(2);'
testcase25 = 'let a = 2 in if (a ==2) {print(1);} else print(2);'

#testing while
testcase26 = 'let a = 10 in while (a > 0) {print(a); a := a - 1;} else {print(a);}'

#testing for
testcase27 = 'for (x in range(1,10)) print(x) else print(4);'

#testing protocol declaration
testcase28 = 'protocol Hashable { hash(): int; } 4;'
testcase29 = 'protocol Equatable extends Hashable { equals(other:Object): Boolean; } 4;'

#testing iterables declaration
testcase30 = 'let numbers = [1,2,3,4,5,6,7,8] in for (x in numbers) print(x) else print(numbers);'
testcase31 = 'let numbers = [x^2 || x in range(1,10)] in print(x);'
testcase32 = 'print("The \\"message\\" is " @ 1);'

#testing type declaration
testcase33 = ('type Point {  x = 0; y = 0; getX()=> self.x; getY()=> self.getX();}'
              'let pt = new Point() in print("x: " @ pt.getX() @ " y: " @ pt.getY());')

#testing instance and function calls
testcase34 = 'let pt = new Point() in print("x: " @ pt.getX() @ " y: " @ pt.getY());'

#testing indexation
testcase35 = 'let vector = [1,2,3,4] in print(vector[0]);'

#testing power operator
testcase36 = 'print(5*2^3*4);'

#testing modulo operator
testcase37 = 'print(3^5%2^5);'

testcase39 = 'print(sin(3^4));'
testcase40= ('function fact(x) => let f =1 in for (i in range(1,x+1)) f := f*i else 4;'
             'print(fact(4));')

testcase41 = ('function fib(n) => if ( n<2 ) n else ( fib ( n-1 ) + fib ( n-2 ) );'
              'print(fib(20));')

testcase42 = 'print(4*-8);'

testcase43 = 'print((let a = 4 in a) @ "hola");'

testcase44 = 'let a = b as c in a;'

testcase45 = 'print(let a = if ("a" is string) 4 else 5 in a);'

testcase46 = ('type a { b() => new a(); d() => print(4);}'
              'let c = new a() in c.b();')

testcase47 = 'print(4+5+6 as int);'

testcase48 = 'let a =42 in let mod = a%3 in print(if (mod==1) "Magic" elif (mod % 3 == 0) "Woke" else "Dumb");'

testcase49 = ('type A {}'
              '4;')

testcase50 = 'print(4 as string);'



formatter = FormatVisitor()
evaluator = Evaluator()

def testing(testcase, id):
    global number
    try:
        parse, operations = pars([t.token_type for t in testcase], get_shift_reduce=True)
        ast = parser.evaluate_reverse_parse(parse, operations, testcase)
        # print(ast)
        # print(formatter.visit(ast))

        #COLLECTING TYPES
        type_collector = TypeCollector.TypeCollector(errors=[])
        type_collector.visit(ast)
        # print(type_collector.context)

        #CHECKING CIRCULAR DEPENDENCIES
        type_builder = TypeBuilder.TypeBuilder1(type_collector.context, type_collector.errors)
        type_builder.visit(ast)
        if check_for_circular_dependencies(type_collector.context):
            type_collector.errors.append('Circular dependence present')

        #RESETTING TYPES BUILT
        for i in type_collector.context.protocols:
            pr = type_collector.context.get_protocol(i)
            pr.children = []
            pr.parents = pr.orig_parent
        for i in type_collector.context.types:
            tp = type_collector.context.get_type(i)
            tp.parent = tp.orig_parent
            tp.children = []
            # print(tp)

        # print(type_collector.context)

        #BUILDING ACTUAL TYPES AND METHODS OF TYPES AND PROTOCOLS
        type_builder = TypeBuilder.TypeBuilder2(type_collector.context, type_collector.errors)
        type_builder.visit(ast)
        # print(type_collector.context)
        # print(type_builder.errors)

        #CHECKING RETURN TYPES
        type_checker = TypeChecker.TypeChecker(type_collector.context, type_collector.errors)
        scope : Scope = type_checker.visit(ast)


        if type_checker.errors == []:
            eval = Evaluator(type_checker.context)
            eval.visit(ast)
        else:
            print(type_checker.errors)

        print('\x1b[6;30;42m' + f'Test {id} passed!' + '\x1b[0m')
    except Exception as e:
        number +=1
        print(e)
        print('\x1b[6;30;41m' + f'Test {id} failed!' + '\x1b[0m')


testcases = []
while True:
    try:
        testcases.append(eval(f'testcase{len(testcases)}'))
    except:
        break

for i, testcase in enumerate(testcases):
        testcase = lexer(testcase)
        testing(testcase, i)


print(f'{number} tests failed')
