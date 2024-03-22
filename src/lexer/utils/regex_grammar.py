from src.cmp.pycompiler import Grammar
from src.Lexer.Utils.regex_ast import *

StringChars = (" a b c d e f g h i j k l m n o p q r s t u v w x y z "
               " A B C D E F G H I J K L M N O P Q R S T U V W X Y Z "
               " % & # $ ^ _  = , : ; - / < > { } @ ! "
               " 0 1 2 3 4 5 6 7 8 9 ")

RegexChars = " [ ] ( ) | . ~ \\ + * ? "


G = Grammar()

# Non Terminal
s = G.NonTerminal('Regex', startSymbol=True)

comp = G.NonTerminal('Comp')
atomicpart = G.NonTerminal('AtomicPart')
branchpart = G.NonTerminal('BranchPart')
string = G.NonTerminal('String')
charbody = G.NonTerminal('CharBody')
character = G.NonTerminal('Character')
operators = G.NonTerminal('Operators')
slashclass = G.NonTerminal("SlashClass")

# Terminal
obracket = G.Terminal('[')
cbracket = G.Terminal(']')
opar = G.Terminal('(')
cpar = G.Terminal(')')
orx = G.Terminal('|')
dot = G.Terminal('.')
script = G.Terminal('~')
slash = G.Terminal('\\')
plus = G.Terminal('+')
star = G.Terminal('*')
interr = G.Terminal('?')
charsymbol = G.Terminal("\'")
chardoublesymbol = G.Terminal("\"")
stringchars = G.Terminals(StringChars)
allchars = G.Terminal('°')

# Productions
s %= branchpart, lambda h, s: s[1]

branchpart %= comp, lambda h, s: s[1]
branchpart %= comp + branchpart, lambda h, s: ConcatNode(left=s[1], right=s[2])
branchpart %= comp + orx + branchpart, lambda h, s: UnionNode(left=s[1], right=s[3])

comp %= atomicpart, lambda h, s: s[1]
comp %= atomicpart + operators, lambda h, s: s[2](child=s[1]),

atomicpart %= string, lambda h, s: s[1]
atomicpart %= opar + branchpart + cpar, lambda h, s: s[2]
atomicpart %= obracket + charbody + cbracket, lambda h, s: s[2]

whitespace = G.Whitespace()
string %= whitespace, lambda h, s: SymbolNode(value=s[1].lex)
string %= slash + slashclass, lambda h, s: s[2]
string %= charsymbol, lambda h, s: SymbolNode(value=s[1].lex)
string %= chardoublesymbol, lambda h, s: SymbolNode(value=s[1].lex)
for char in stringchars:
    string %= char, lambda h, s: SymbolNode(value=s[1].lex)

slashclass %= allchars, lambda h, s: AllCharsNode()
for terminal in [obracket, cbracket, opar, cpar, orx, dot, script, slash,  plus,  star, interr, charsymbol, chardoublesymbol]:
    slashclass %= terminal, lambda h, s: SymbolNode(value=s[1].lex)

operators %= plus, lambda h, s: PlusNode
operators %= star, lambda h, s: ClosureNode
operators %= interr, lambda h, s: InterrogationNode

charbody %= character, lambda h, s: s[1]
charbody %= character + charbody, lambda h, s: ConcatNode(left=s[1], right=s[2])

character %= string, lambda h, s: s[1]
character %= string + script + string, lambda h, s: ScriptNode(left=s[1], right=s[3])