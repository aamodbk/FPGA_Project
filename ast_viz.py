from pycparser import c_ast, parse_file, c_parser
from anytree import Node, RenderTree, PreOrderIter
from anytree.exporter import DotExporter
import pycparser_fake_libc, anytree
import pandas as pd
import numpy as np

def get_children(root):
    if isinstance(root, c_ast.FileAST):
        children = root.children()
    elif isinstance(root[1], c_ast.Node):
        children = root[1].children()
    elif isinstance(root, set):
        children = list(root)
    else:
        children = []

    def expand(nested_list):
        for item in nested_list:
            if isinstance(item, list):
                for sub_item in expand(item):
                    yield sub_item
            elif item:
                yield item

    return list(expand(children))

def get_trees(current_node, parent_node, order):
    
    token, children = get_token(current_node), get_children(current_node)
    node = Node([order,token], parent=parent_node, order=order)

    for child_order in range(len(children)):
        get_trees(children[child_order], node, order+str(int(child_order)+1))

def get_token(node):
    token = ''
    if isinstance(node, c_ast.FileAST):
        token = node.__class__.__name__
        return token
    elif isinstance(node[1], str):
        token = node[1]
        return token
        #print(token)
    elif isinstance(node[1], c_ast.Node):
        token = node[1].__class__.__name__
    #print(token)
    
    if len(get_children(node))==0:
        attr_names = node[1].attr_names
        if attr_names:
            if 'names' in attr_names:
                token = node[1].names[0]
            elif 'name' in attr_names:
                token = node[1].name
            else:
                token = node[1].value
    else:
        if token == 'TypeDecl':
            token = node[1].declname
        if node[1].attr_names:
            attr_names = node[1].attr_names
            if 'op' in attr_names:
                if node[1].op[0] == 'p':
                    token = node[1].op[1:]
                else:
                    token = node[1].op
 
    if token == '':
        token = node[1].__class__.__name__
    return token

def get_edges_and_nodes(root):
    """Returns a list of edges and nodes from the given tree."""
    edges = []
    nodes = []

    def walker(node):
        """Recursive function to walk the tree and collect edges and nodes."""
        nodes.append(node)
        for child in node.children:
            edges.append((node, child))
            walker(child)

    walker(root)
    return edges, nodes

if __name__=="__main__":
    filename = './test.cpp'
    fake_libc_arg = "-I" + pycparser_fake_libc.directory

    ast = parse_file(filename, use_cpp=True,
            cpp_path='g++',
            cpp_args=['-E', fake_libc_arg, r'-IHLS_arbitrary_Precision_Types-master/include'])
    
    head = Node(["1",get_token(ast)])
    # Recursively construct AST tree.
    for child_order in range(len(get_children(ast))):
        get_trees(get_children(ast)[child_order], head, "1"+str(int(child_order)+1))

    lst = list(PreOrderIter(head, filter_=lambda node: node.is_leaf))
    f = [str(i)[7:-2].split(i.separator) for i in lst]
    # print(f)
    edges, nodes = get_edges_and_nodes(head)

    np.save('test_edges.npy', edges)

    # print(RenderTree(head))
    DotExporter(head).to_dotfile("./dotfiles/testcode.dot")


    # endnodes = anytree.findall(head, filter_=lambda node: len(node.children)==0)
    # members = []
    # tier = []
    # endcluster = []
    # for item in endnodes:
    #     members += item.members
    #     tier += [item.tier] * len(item.members)
    #     endcluster += [item.name] * len(item.members)
    # endf = pd.DataFrame(index=members)
    # endf['tier']=tier
    # endf['endcluster']=endcluster

    # print(endf.head())
