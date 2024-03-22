from src.lexer.utils.regex_ast import *
from src.lexer.utils.regex_grammar import StringChars, RegexChars
from src.cmp import visitor
from src.cmp.automaton_operations import *
from src.cmp.automaton import nfa_to_dfa
from src.cmp.automaton_operations import automata_minimization


class FormatVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ClosureNode)
    def visit(self, node):
        Child = self.visit(node.child)
        return automata_closure(Child)
    
    @visitor.when(UnionNode)
    def visit(self, node):
        Left = self.visit(node.left)
        Right = self.visit(node.right)
        return automata_union(Left, Right)
    
    @visitor.when(ConcatNode)
    def visit(self, node):
        Left = self.visit(node.left)
        Right = self.visit(node.right)
        return automata_concatenation(Left, Right)

    @visitor.when(SymbolNode)
    def visit(self, node):
        Symbol = node.value
        return self.SymbolAtm(Symbol)

    @visitor.when(AllCharsNode)
    def visit(self, node):
        Chars = StringChars.split()
        
        FinalAtm = automata_union(self.SymbolAtm(Chars[0]), self.SymbolAtm(Chars[1]))

        for char in Chars[2:]:
            FinalAtm = automata_union(FinalAtm, self.SymbolAtm(char))

        RgxChars = RegexChars.split()
        for char in RgxChars:
            FinalAtm = automata_union(FinalAtm, self.SymbolAtm(char))

        FinalAtm = automata_union(FinalAtm, self.SymbolAtm(' '))

        FinalAtm = nfa_to_dfa(FinalAtm)
        FinalAtm = automata_minimization(FinalAtm)
        return FinalAtm

    @visitor.when(PlusNode)
    def visit(self, node):
        Child = self.visit(node.child)
        return automata_concatenation(Child, automata_closure(Child))

    @visitor.when(InterrogationNode)
    def visit(self, node):
        Child = self.visit(node.child)
        E = NFA(states=1, finals=[0], transitions={})
        return automata_union(E, Child)

    @visitor.when(ScriptNode)
    def visit(self, node):
        Left = node.left.value
        Right = node.right.value

        Values = range(ord(Left) + 1, ord(Right))

        Chars = []
        for char in Values:
            Chars.append(chr(char))

        FinalAtm = automata_union(self.SymbolAtm(Left), self.SymbolAtm(Right))

        for char in Chars:
            FinalAtm = automata_union(FinalAtm, self.SymbolAtm(char))

        FinalAtm = nfa_to_dfa(FinalAtm)
        FinalAtm = automata_minimization(FinalAtm)
        return FinalAtm
    
    @staticmethod
    def SymbolAtm(lex):
        return NFA(states=2,finals=[1],transitions={(0, lex): [1]})