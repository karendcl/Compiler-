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
conditional, condition = G.NonTerminals("<conditional> <condition>")
then_exp =  G.NonTerminal("<then-exp>")
elif_block = G.NonTerminal("<elif-block>")
while_block = G.NonTerminal("<while-block>")


curly_o , curly_c = G.Terminals("{ }")
semi_colon , colon = G.Terminals("; :")
opar, cpar = G.Terminals("( )")
rarrow = G.Terminal("=>")
func_id, func_type = G.Terminals("func_id func_type")
comma = G.Terminal(",")
let, inx = G.Terminals("let in")
var_id = G.Terminal("var_id")
equal = G.Terminal("=")
ifx, elsex, elifx, whilex = G.Terminals("if else elif while")

exp_block %= curly_o + exp_list + curly_c + end_extended, lambda h, s: s[2]

end_extended %= semi_colon, lambda h, s: [s[1]]
end_extended %= G.Epsilon, lambda h, s: []


exp_list %= exp + semi_colon + exp_list, lambda h, s: [s[1]] + s[3]
exp_list %= G.Epsilon, lambda h, s: []

def_func %= func_id + opar + param_list + cpar + rarrow + exp + semi_colon, lambda h, s: FuncDeclarationNode(s[1], s[3], s[6], s[5])
def_func %= func_id + opar + param_list + cpar + exp_block, lambda h, s: FuncDeclarationNode(s[1], s[3], s[5], s[4])

param_list %= param, lambda h, s: [s[1]]
param_list %= param + comma + param_list, lambda h, s: [s[1]] + s[3]

arg_declaration %= func_id + colon + func_type, lambda h, s: (s[1], s[3])
arg_declaration %= func_id, lambda h, s: (s[1], None)

param %= arg_declaration, lambda h, s: s[1]

let_exp %= let + assign_list + inx + exp, lambda h, s: LetNode(s[2], s[4], s[1])

assign_list %= assign_var, lambda h, s: [s[1]]
assign_list %= assign_var + comma + assign_list, lambda h, s: [s[1]] + s[3]

assign_var %= var_id + equal + exp, lambda h, s: AssignNode(s[1], s[3], s[2])

elif_block %= elifx + condition + then_exp, lambda h, s: (s[2], s[3])
elif_block %= elifx + condition + then_exp + elif_block, lambda h, s: (s[2], s[3]) + s[4]
elif_block %= G.Epsilon, lambda h, s: []

condition %= exp, lambda h, s: s[1]

then_exp %= exp, lambda h, s: s[1]
then_exp %= exp_block, lambda h, s: s[1]

conditional %= ifx + condition + then_exp + elif_block + elsex + then_exp, lambda h, s: ConditionalNode(s[2], s[3], s[4], s[6], s[1])

while_block %= whilex + condition + then_exp, lambda h, s: LoopNode(s[2], s[3], s[1])



exp %= let_exp, lambda h, s: s[1]
exp %= conditional, lambda h, s: s[1]
exp %= def_func, lambda h, s: s[1]











# type_list, def_type = G.NonTerminals("<type-list> <def-type>")
#
# feature_list, def_attr, def_func = G.NonTerminals(
#     "<feature-list> <def-attr> <def-func>"
# )
# param_list, param, expr_list = G.NonTerminals("<param-list> <param> <expr-list>")
# expr, comp, arith, term, factor, atom = G.NonTerminals(
#     "<expr> <comp> <arith> <term> <factor> <atom>"
# )
# s_comp, s_arith, s_term, s_factor = G.NonTerminals(
#     "<special_comp> <special_arith> <special_term> <special_factor>"
# )
# func_call, arg_list, args = G.NonTerminals("<func-call> <arg-list> <args>")
# case_def, block_def, loop_def, cond_def, let_def, assign_def = G.NonTerminals(
#     "<case_def> <block_def> <loop_def> <cond_def> <let_def> <assign_def>"
# )
# branch_list, branch = G.NonTerminals("<branch_list> <branch>")
# iden_list, iden = G.NonTerminals("<iden_list> <iden>")
#

# terminals
# typex, inherits = G.Terminals("type inherits")
# let, inx = G.Terminals("let in")
# case, of, esac = G.Terminals("case of esac")
# whilex, loop, pool = G.Terminals("while loop pool")
# ifx, then, elsex, fi = G.Terminals("if then else fi")
# isvoid, notx = G.Terminals("isvoid not")
# semi, colon, comma, dot, opar, cpar, ocur, ccur, larrow, rarrow, at = G.Terminals(
#     "; : , . ( ) { } <- => @"
# )
# equal, plus, minus, star, div, less, leq, neg, powx = G.Terminals("= + - * / < <= ~ ^")
# typeid, objectid, num, stringx, boolx, new = G.Terminals(
#     "typeid objectid int string bool new"
# )
#
#
# # productions
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