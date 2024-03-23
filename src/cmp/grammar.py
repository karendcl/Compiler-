import math

from src.cmp.pycompiler import Grammar
from src.cmp.ast import *
from src.cmp.utils import selfToken

# grammar
G = Grammar()

# non-terminals
program = G.NonTerminal("<program>", startSymbol=True)
exp, exp_block, exp_list = G.NonTerminals("<exp> <exp-block> <exp-list>")
def_func = G.NonTerminal("<def-func>")

end_extended = G.NonTerminal("<end-extended>")
param_list, param = G.NonTerminals("<param-list> <param>")
arg_declaration = G.NonTerminal("<arg-declaration>")
let_exp, assign_var, assign_list = G.NonTerminals("<let-exp> <assign-var> <assign-list>")
mutate_var = G.NonTerminal("<mutate-var>")
conditional, condition = G.NonTerminals("<conditional> <condition>")
elif_block = G.NonTerminal("<elif-block>")
while_block = G.NonTerminal("<while-block>")
for_exp = G.NonTerminal("<for-exp>")
type_dec = G.NonTerminal("<type-dec>")
term, factor, atom, k, mod_= G.NonTerminals("<term> <factor> <atom> <k> <mod>")
statement = G.NonTerminal("<statement>")
def_protocol = G.NonTerminal("<def-protocol>")
method_declarations = G.NonTerminal("<method-declarations>")
def_method = G.NonTerminal("<def-method>")
instance = G.NonTerminal("<instance>")
# exp_or_block = G.NonTerminal("<exp-or-block>")
list_ = G.NonTerminal("<list>")
type_body, type_args = G.NonTerminals("<type-body> <type-args>")
attribute = G.NonTerminal("<attribute>")
vector, iterable = G.NonTerminals("<vector> <iterable>")
func_call = G.NonTerminal("<func-call>")
print_exp = G.NonTerminal("<print-exp>")
string_exp = G.NonTerminal("<string-exp>")
concatenable = G.NonTerminal("<concatenable>")
functions_in_type = G.NonTerminal("<functions-in-type>")
attr_call = G.NonTerminal("<attr-call>")
indexation = G.NonTerminal("<indexation>")


# region TERMINALS
curly_o , curly_c = G.Terminals("{ }")
square_o, square_c = G.Terminals("[ ]")
semi_colon , colon = G.Terminals("; :")
opar, cpar = G.Terminals("( )")
rarrow, given = G.Terminals("=> ||")
comma, dot = G.Terminals(", .")
let, inx = G.Terminals("let in")
equal, mut = G.Terminals("= :=")
ifx, elsex, elifx, whilex, forx, function = G.Terminals("if else elif while for function")
leq, less, equals, geq, greater, neq = G.Terminals("<= < == >= > !=")
sqrt, cos, sin, expon, log, rand = G.Terminals("sqrt cos sin expon log rand")
plus, minus, star, div, mod, pow, num, notx, andx, orx = G.Terminals("+ - * / % ^ num ! & |")
typex, new, inherits, isx, asx = G.Terminals("type new inherits is as")
protocol, extends = G.Terminals("protocol extends")
true, false = G.Terminals("true false")
concat, concat_space = G.Terminals("@ @@")
strx, idx, boolx, self = G.Terminals("str id bool self")
rangex = G.Terminal("range")
printx = G.Terminal("print")
PI, E = G.Terminals("PI E")


#productions


#------esto no me queda muy claro

program %= statement, lambda h, s: ProgramNode(s[1])

statement %= def_protocol + statement, lambda h, s: s[1]
statement %= type_dec + statement, lambda h, s: s[1]
statement %= def_func + statement, lambda h, s: s[1]
statement %= exp + semi_colon, lambda h, s: s[1]
statement %= exp, lambda h, s: s[1]
statement %= exp_block, lambda h, s: s[1]
statement %= exp_block + semi_colon, lambda h, s: s[1]

exp %= while_block, lambda h, s: s[1]
exp %= for_exp, lambda h, s: s[1]
exp %= print_exp, lambda h, s: s[1]
exp %= instance, lambda h, s: s[1]
exp %= mutate_var, lambda h, s: s[1]
exp %= string_exp, lambda h, s: s[1]
exp %= iterable, lambda h, s: s[1]

string_exp %= indexation + concatenable, lambda h, s: s[1]
string_exp %= let_exp, lambda h, s: s[1]
string_exp %= term + concatenable, lambda h, s: s[1]
string_exp %= strx + concatenable, lambda h, s: ConstantStringNode(s[1], s[1].lex[1:-1])
string_exp %= func_call + concatenable, lambda h, s: s[1]
string_exp %= attr_call + concatenable, lambda h, s: s[1]
string_exp %= conditional, lambda h, s: s[1]

concatenable %= concat + string_exp, lambda h, s: ""
concatenable %= concat_space + string_exp, lambda h, s: " "
concatenable %= G.Epsilon, lambda h, s: None

#-------------------------------------------

# exp_or_block %= exp + semi_colon, lambda h, s: s[1]
# exp_or_block %= exp_block, lambda h, s: s[1]

def_protocol %= protocol + idx + curly_o + method_declarations + curly_c, lambda h, s: ClassDeclarationNode(s[2], s[4], s[1], None)
def_protocol %= protocol + idx + extends + idx + curly_o + method_declarations + curly_c, lambda h, s: ClassDeclarationNode(s[2], s[4], s[1], s[3])

def_method %= idx + opar + param_list + cpar + colon + idx, lambda h, s: FuncDeclarationNode(s[1], s[3], s[6])

method_declarations %= def_method + semi_colon, lambda h, s: [s[1]]
method_declarations %= def_method + method_declarations, lambda h, s: [s[1]] + s[2]

type_dec %= typex + idx + type_args + curly_o + type_body + curly_c, lambda h, s: ClassDeclarationNode(s[2], s[4], s[1], None)
type_dec %= typex + idx + inherits + idx + curly_o + type_body + curly_c, lambda h, s: ClassDeclarationNode(s[2], s[5], s[1], s[4])

type_args %= opar + param_list + cpar, lambda h, s: s[2]
type_args %= G.Epsilon, lambda h, s: []

type_body %= functions_in_type, lambda h, s: [s[1]]
type_body %= functions_in_type + type_body, lambda h, s: [s[1]] + s[3]
type_body %= attribute + semi_colon, lambda h, s: [s[1]]
type_body %= attribute + semi_colon + type_body, lambda h, s: [s[1]] + s[3]

functions_in_type %= idx + opar + param_list + cpar + rarrow + exp + semi_colon, lambda h, s: FuncDeclarationNode(s[2], s[4], s[7])
functions_in_type %= idx + opar + param_list + cpar + exp_block, lambda h, s: FuncDeclarationNode(s[2], s[4], s[6])

attribute %= idx + equal + exp, lambda h, s: AttrDeclarationNode(s[1], None, s[3])
attribute %= idx + colon + idx, lambda h, s: AttrDeclarationNode(s[1], s[3], None)

instance %= new + idx + opar + param_list + cpar, lambda h, s: InstantiateNode(s[2], s[4], s[1])

end_extended %= G.Epsilon, lambda h, s: None

exp_block %= curly_o + exp_list + curly_c + end_extended, lambda h, s: s[2]

exp_list %= exp + semi_colon + exp_list, lambda h, s: [s[1]] + s[3]
exp_list %= exp + semi_colon, lambda h, s: [s[1]]

def_func %= function + idx + opar + param_list + cpar + rarrow + exp + semi_colon, lambda h, s: FuncDeclarationNode(s[2], s[4], s[7])
def_func %= function + idx + opar + param_list + cpar + exp_block, lambda h, s: FuncDeclarationNode(s[2], s[4], s[6])

#todo fix ast here
func_call %= idx + dot + func_call, lambda h, s: CallNode(s[1], s[3])
func_call %= idx + opar + param_list + cpar, lambda h, s: CallNode(s[1], s[3])
func_call %= idx + dot + idx, lambda h, s: CallNode(s[1], s[3])

param_list %= param, lambda h, s: [s[1]]
param_list %= param + comma + param_list, lambda h, s: [s[1]] + s[3]

arg_declaration %= idx + colon + idx, lambda h, s: (s[1], s[3])
arg_declaration %= idx, lambda h, s: (s[1], None)
arg_declaration %= G.Epsilon, lambda h, s: None

param %= arg_declaration, lambda h, s: s[1]

let_exp %= let + assign_list + inx + exp , lambda h, s: LetNode(s[2], s[4], s[1])
let_exp %= let + assign_list + inx + exp_block, lambda h, s: LetNode(s[2], s[4], s[1])

assign_list %= assign_var, lambda h, s: [s[1]]
assign_list %= assign_var + comma + assign_list, lambda h, s: [s[1]] + s[3]

assign_var %= idx + equal + exp, lambda h, s: AssignNode(s[1], s[3], s[2])

mutate_var %= idx + mut + exp, lambda h, s: AssignNode(s[1], s[3], s[2])

conditional %= ifx + opar + condition + cpar + exp + elif_block, lambda h, s: ConditionalNode(s[2], s[3], s[4], s[1])
conditional %= ifx + opar + condition + cpar + exp_block + elif_block, lambda h, s: ConditionalNode(s[2], s[3], s[4], s[1])

elif_block %= elsex + exp , lambda h, s: BlockNode(s[2], s[1])
elif_block %= elsex + exp_block, lambda h, s: s[2]
elif_block %= elifx + opar + condition + cpar + exp + elif_block, lambda h, s: ConditionalNode(s[2], s[3], s[4], s[1])
elif_block %= elifx + opar + condition + cpar + exp_block + elif_block, lambda h, s: ConditionalNode(s[2], s[3], s[4], s[1])

while_block %= whilex + opar + condition + cpar + exp + semi_colon, lambda h, s: LoopNode(s[2], s[3], s[1])
while_block %= whilex + opar + condition + cpar + exp_block, lambda h, s: LoopNode(s[2], s[3], s[1])

for_exp %= forx + opar + idx + inx + exp + cpar + exp + semi_colon, lambda h, s: ForNode(s[5], s[7], s[1], s[3])
for_exp %= forx + opar + idx + inx + exp + cpar + exp_block, lambda h, s: ForNode(s[5], s[7], s[1], s[3])

iterable %= vector, lambda h, s: s[1]
iterable %= rangex + opar + num + comma + num + cpar, lambda h, s: RangeNode(s[3], s[5], s[1])

vector %= square_o + list_ + square_c, lambda h, s: s[2]
vector %= square_o + exp + given + idx + inx + iterable + square_c, lambda h, s: s[2]

list_ %= exp, lambda h, s: [s[1]]
list_ %= exp + comma + list_, lambda h, s: [s[1]] + s[3]

indexation %= idx + square_o + exp + square_c, lambda h, s: IndexationNode(s[1], s[3])
indexation %= iterable + square_o + exp + square_c, lambda h, s: IndexationNode(s[1], s[3])


# todo add mod



#todo as is


term %= factor, lambda h, s: s[1]
term %= term + plus + factor, lambda h, s: PlusNode(s[1], s[3], s[2])
term %= term + minus + factor, lambda h, s: MinusNode(s[1], s[3], s[2])


factor %= mod_, lambda h, s: s[1]
factor %= factor + star + mod_, lambda h, s: StarNode(s[1], s[3], s[2])
factor %= factor + div + mod_, lambda h, s: DivNode(s[1], s[3], s[2])

mod_ %= k, lambda h, s: s[1]
mod_ %= mod_ + mod + k, lambda h, s: ModNode(s[1], s[3], s[2])

k %= atom, lambda h, s: s[1]
k %= k + pow + atom, lambda h, s: PowNode(s[1], s[3], s[2])


#todo fix minus num
atom %= idx, lambda h, s: VariableNode(s[1])
atom %= num, lambda h, s: ConstantNumNode(s[1])
atom %= minus + num, lambda h, s: NegNode(ConstantNumNode(s[2]), s[1])
atom %= opar + exp + cpar, lambda h, s: s[2]
atom %= sqrt + opar + exp + cpar, lambda h, s: SqrtNode(s[3], s[1])
atom %= cos + opar + exp + cpar, lambda h, s: CosNode(s[3], s[1])
atom %= sin + opar + exp + cpar, lambda h, s: SinNode(s[3], s[1])
atom %= expon + opar + exp + cpar, lambda h, s: ExponEulerNode(s[3], s[1])
atom %= log + opar + exp + comma + exp + cpar, lambda h, s: LogNode(s[3], s[5], s[1])
atom %= rand + opar + cpar, lambda h, s: RandNode(s[2])
atom %= PI, lambda h, s: ConstantNumNode(s[1])
atom %= E, lambda h, s: ConstantNumNode(s[1])

#boolean expressions as described in hulk
condition %= exp + leq + exp, lambda h, s: LeqNode(s[1], s[3], s[2])
condition %= exp + less + exp, lambda h, s: LessNode(s[1], s[3], s[2])
condition %= exp + equals + exp, lambda h, s: EqualNode(s[1], s[3], s[2])
condition %= exp + geq + exp, lambda h, s: LessNode(s[3], s[1], s[2])
condition %= exp + greater + exp, lambda h, s: LeqNode(s[3], s[1], s[2])
condition %= exp + neq + exp, lambda h, s: NotNode(EqualNode(s[1], s[3], s[2]), s[2])
condition %= true, lambda h, s: ConstantBoolNode(s[1])
condition %= false, lambda h, s: ConstantBoolNode(s[1])
condition %= exp + andx + exp, lambda h, s: AndNode(s[1], s[3], s[2])
condition %= exp + orx + exp, lambda h, s: OrNode(s[1], s[3], s[2])
condition %= opar + condition + cpar, lambda h, s: s[2]
condition %= notx + condition, lambda h, s: NotNode(s[2], s[1])

print_exp %= printx + opar + string_exp + cpar, lambda h, s: PrintNode(s[3], s[1])



# string_exp %= conditional + concat + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1]}{s[3]}')

# string_exp %= strx + concatenable + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1].lex[1:-1]}{s[3]}')
# # string_exp %= strx + concat_space + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1].lex[1:-1]} {s[3]}')
# string_exp %= term + concatenable + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1].lex[1:-1]}{s[3]}')
# # string_exp %= term + concat_space + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1].lex[1:-1]} {s[3]}')
# string_exp %= func_call + concatenable + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1]}{s[3]}')
# # string_exp %= func_call + concat_space + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1]} {s[3]}')
# string_exp %= attr_call + concatenable + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1]}{s[3]}')
# # string_exp %= attr_call + concat_space + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1]} {s[3]}')
# string_exp %= conditional + concatenable + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1]}{s[3]}')
# # string_exp %= conditional + concat_space + string_exp, lambda h, s: ConstantStringNode(s[1], f'{s[1]} {s[3]}')

# concatenable %= concat , lambda h, s: ""
# concatenable %= concat_space , lambda h, s: " "





#
# program %= type_list, lambda h, s: ProgramNode(s[1])
#
# type_list %= def_type, lambda h, s: [s[1]]
# type_list %= def_type + type_list, lambda h, s: [s[1]] + s[2]
#
# def_type %= (
#     typex + typeid + ocur + feature_list + ccur + semi,
#     lambda h, s: classDeclarationNode(s[2], s[4], s[1]),
# )
# def_type %= (
#     typex + typeid + inherits + typeid + ocur + feature_list + ccur + semi,
#     lambda h, s: classDeclarationNode(s[2], s[6], s[1], s[4]),
# )
#
# feature_list %= G.Epsilon, lambda h, s: []
# feature_list %= def_attr + feature_list, lambda h, s: [s[1]] + s[2]
# feature_list %= def_func + feature_list, lambda h, s: [s[1]] + s[2]
#
# def_attr %= objectid + colon + typeid + semi, lambda h, s: AttrDeclarationNode(
#     s[1], s[3]
# )
# def_attr %= (
#     objectid + colon + typeid + larrow + expr + semi,
#     lambda h, s: AttrDeclarationNode(s[1], s[3], s[5], s[4]),
# )
#
# def_func %= (
#     objectid + opar + cpar + colon + typeid + ocur + expr + ccur + semi,
#     lambda h, s: FuncDeclarationNode(s[1], [], s[5], s[7]),
# )
# def_func %= (
#     objectid + opar + param_list + cpar + colon + typeid + ocur + expr + ccur + semi,
#     lambda h, s: FuncDeclarationNode(s[1], s[3], s[6], s[8]),
# )
#
# param_list %= param, lambda h, s: [s[1]]
# param_list %= param + comma + param_list, lambda h, s: [s[1]] + s[3]
# param %= objectid + colon + typeid, lambda h, s: (s[1], s[3])
#
# expr %= comp, lambda h, s: s[1]
# expr %= s_comp, lambda h, s: s[1]
#
# comp %= arith, lambda h, s: s[1]
# comp %= arith + leq + arith, lambda h, s: LeqNode(s[1], s[3], s[2])
# comp %= arith + less + arith, lambda h, s: LessNode(s[1], s[3], s[2])
# comp %= arith + equal + arith, lambda h, s: EqualNode(s[1], s[3], s[2])
#
# arith %= term, lambda h, s: s[1]
# arith %= arith + plus + term, lambda h, s: PlusNode(s[1], s[3], s[2])
# arith %= arith + minus + term, lambda h, s: MinusNode(s[1], s[3], s[2])
#
# term %= factor, lambda h, s: s[1]
# term %= term + star + factor, lambda h, s: StarNode(s[1], s[3], s[2])
# term %= term + div + factor, lambda h, s: DivNode(s[1], s[3], s[2])
#
# factor %= atom, lambda h, s: s[1]
# factor %= opar + expr + cpar, lambda h, s: s[2]
# # factor %= isvoid + factor, lambda h, s: VoidNode(s[2], s[1])
# # factor %= neg + factor, lambda h, s: NegNode(s[2], s[1])
# factor %= func_call, lambda h, s: s[1]
# factor %= case_def, lambda h, s: s[1]
# factor %= block_def, lambda h, s: s[1]
# factor %= loop_def, lambda h, s: s[1]
# factor %= cond_def, lambda h, s: s[1]
#
# atom %= num, lambda h, s: ConstantNumNode(s[1])
# atom %= stringx, lambda h, s: ConstantStringNode(s[1])
# atom %= boolx, lambda h, s: ConstantBoolNode(s[1])
# atom %= objectid, lambda h, s: VariableNode(s[1])
# atom %= new + typeid, lambda h, s: InstantiateNode(s[2])
#
# func_call %= objectid + opar + arg_list + cpar, lambda h, s: CallNode(
#     VariableNode(selfToken), s[1], s[3]
# )
# func_call %= factor + dot + objectid + opar + arg_list + cpar, lambda h, s: CallNode(
#     s[1], s[3], s[5]
# )
# func_call %= (
#     factor + at + typeid + dot + objectid + opar + arg_list + cpar,
#     lambda h, s: CallNode(s[1], s[5], s[7], s[3]),
# )
#
# arg_list %= G.Epsilon, lambda h, s: []
# arg_list %= args, lambda h, s: s[1]
# args %= expr, lambda h, s: [s[1]]
# args %= expr + comma + args, lambda h, s: [s[1]] + s[3]
#
# case_def %= case + expr + of + branch_list + esac, lambda h, s: CaseNode(
#     s[2], s[4], s[1]
# )
# branch_list %= branch, lambda h, s: [s[1]]
# branch_list %= branch + branch_list, lambda h, s: [s[1]] + s[2]
# branch %= objectid + colon + typeid + rarrow + expr + semi, lambda h, s: CaseBranchNode(
#     s[4], s[1], s[3], s[5]
# )
#
# block_def %= ocur + expr_list + ccur, lambda h, s: BlockNode(s[2], s[1])
# expr_list %= expr + semi, lambda h, s: [s[1]]
# expr_list %= expr + semi + expr_list, lambda h, s: [s[1]] + s[3]
#
# loop_def %= whilex + expr + loop + expr + pool, lambda h, s: LoopNode(s[2], s[4], s[1])
#
# cond_def %= ifx + expr + then + expr + elsex + expr + fi, lambda h, s: ConditionalNode(
#     s[2], s[4], s[6], s[1]
# )
#
# s_comp %= s_arith, lambda h, s: s[1]
# s_comp %= arith + leq + s_arith, lambda h, s: LeqNode(s[1], s[3], s[2])
# s_comp %= arith + less + s_arith, lambda h, s: LessNode(s[1], s[3], s[2])
# s_comp %= arith + equal + s_arith, lambda h, s: EqualNode(s[1], s[3], s[2])
#
# s_arith %= s_term, lambda h, s: s[1]
# s_arith %= arith + plus + s_term, lambda h, s: PlusNode(s[1], s[3], s[2])
# s_arith %= arith + minus + s_term, lambda h, s: MinusNode(s[1], s[3], s[2])
#
# s_term %= s_factor, lambda h, s: s[1]
# s_term %= term + star + s_factor, lambda h, s: StarNode(s[1], s[3], s[2])
# s_term %= term + div + s_factor, lambda h, s: DivNode(s[1], s[3], s[2])
#
# s_factor %= notx + expr, lambda h, s: NotNode(s[2], s[1])
# s_factor %= let_def, lambda h, s: s[1]
# s_factor %= assign_def, lambda h, s: s[1]
# s_factor %= isvoid + s_factor, lambda h, s: VoidNode(s[2], s[1])
# s_factor %= neg + s_factor, lambda h, s: NegNode(s[2], s[1])
# s_factor %= factor, lambda h, s: s[1]
#
# let_def %= let + iden_list + inx + expr, lambda h, s: LetNode(s[2], s[4], s[1])
# iden_list %= iden, lambda h, s: [s[1]]
# iden_list %= iden + comma + iden_list, lambda h, s: [s[1]] + s[3]
# iden %= objectid + colon + typeid, lambda h, s: LetVarNode(s[1], s[3])
# iden %= objectid + colon + typeid + larrow + expr, lambda h, s: LetVarNode(
#     s[1], s[3], s[5], s[4]
# )
#
# assign_def %= objectid + larrow + expr, lambda h, s: AssignNode(s[1], s[3], s[2])