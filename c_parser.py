from pycparser import parse_file, c_parser, c_ast
import re, ctree
import pycparser_fake_libc

class CVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.loop_depth = 0
        self.loop_count = 0
        self.nested_loop_count = 0
        self.arithmetic_operators = {}
        self.logical_operators = {}
        self.input_bit_width = 0
        self.output_bit_width = 0
        self.input_ports = 0
        self.output_ports = 0
        self.loop_operations = []

    def visit_FuncDef(self, node):
        self.output_ports += 1
        # print(node.decl.type.args.params)
        self.input_ports += len(node.decl.type.args.params) if node.decl.type.args else 0
        self.generic_visit(node)

    def visit_For(self, node):
        self.loop_count += 1
        # print('For: '+str({type(n) for n in node.stmt.block_items}))
        if(isinstance(node.stmt, c_ast.Compound)):
            self.nested_loop_count += any(isinstance(n, c_ast.Label) for n in node.stmt.block_items)
            self.nested_loop_count += any(isinstance(n, c_ast.For) for n in node.stmt.block_items)
            self.nested_loop_count += any(isinstance(n, c_ast.While) for n in node.stmt.block_items)
        self.generic_visit(node)

    def visit_While(self, node):
        self.loop_count += 1
        # print('While: '+str(type(node)))
        # print('Nested While: '+str({type(n[1]) for n in node.children()}))
        if(isinstance(node.stmt, c_ast.Compound)):
            self.nested_loop_count += any(isinstance(n, c_ast.Label) for n in node.stmt.block_items)
            self.nested_loop_count += any(isinstance(n, c_ast.For) for n in node.stmt.block_items)
            self.nested_loop_count += any(isinstance(n, c_ast.While) for n in node.stmt.block_items)
        self.generic_visit(node)

    def visit_DoWhile(self, node):
        self.loop_count += 1
        if(isinstance(node.stmt, c_ast.Compound)):
            self.nested_loop_count += any(isinstance(n, c_ast.Label) for n in node.stmt.block_items)
            self.nested_loop_count += any(isinstance(n, c_ast.While) for n in node.stmt.block_items)
            self.nested_loop_count += any(isinstance(n, c_ast.For) for n in node.stmt.block_items)
        self.generic_visit(node)

    def visit_BinaryOp(self, node):
        if node.op in ['+', '-', '*', '/', '%']:
            self.arithmetic_operators.setdefault(str(node.op), 0)
            self.arithmetic_operators[str(node.op)] += 1
        elif node.op in ['&&', '||', '!', '&', '|', '^']:
            self.logical_operators.setdefault(str(node.op), 0)
            self.logical_operators[str(node.op)] += 1
        self.generic_visit(node)

    def visit_Decl(self, node):
        if isinstance(node.type, c_ast.TypeDecl):
            if isinstance(node.type.type, c_ast.IdentifierType):
                if 'int' in node.type.type.names:
                    self.input_bit_width += 32

    def print_results(self):
        print(f"Number of loops: {self.loop_count}")
        print(f"Number of nested loops: {self.nested_loop_count}")
        print(f"Number of arithmetic operators: {self.arithmetic_operators}")
        print(f"Number of logical operators: {self.logical_operators}")
        # print(f"Input bit-width: {self.input_bit_width}")
        # print(f"Output bit-width: {self.output_bit_width}")
        print(f"Number of input ports: {self.input_ports}")
        print(f"Number of output ports: {self.output_ports}")
        # print(f"Loop operations: {self.loop_operations}")
        f.write(f"Number of loops: {self.loop_count}\n")
        f.write(f"Number of nested loops: {self.nested_loop_count}\n")
        f.write(f"Number of arithmetic operators: {self.arithmetic_operators}\n")
        f.write(f"Number of logical operators: {self.logical_operators}\n")
        # f.write(f"Input bit-width: {self.input_bit_width}")
        # f.write(f"Output bit-width: {self.output_bit_width}")
        f.write(f"Number of input ports: {self.input_ports}\n")
        f.write(f"Number of output ports: {self.output_ports}\n")

if __name__ == "__main__":
    filename = './MachSuite/bfs/queue/bfs.c'
    fake_libc_arg = "-I" + pycparser_fake_libc.directory

    ast = parse_file(filename, use_cpp=True,
            cpp_path='g++',
            cpp_args=['-E', fake_libc_arg, r'-IHLS_arbitrary_Precision_Types-master/include'])
    
    # ast.show()
    f = open('./paramouts/bfsqueue.txt', "a")
    f.truncate(0)
    visitor = CVisitor()
    visitor.visit(ast)
    visitor.print_results()

    f.close()
