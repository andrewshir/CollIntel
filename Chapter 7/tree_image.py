import numpy as np
from PIL import Image,ImageDraw

class decisionnde(object):
    def __init__(self, node_depth=0, is_leaf=False, lb=None, rb=None, feature=None, threshold=None):
        self.lb = lb
        self.rb = rb
        self.feature = feature
        self.threshold = threshold
        self.is_leaf = is_leaf
        self.node_depth = node_depth


def getwidth(node):
    if node.lb==None and node.rb==None: return 1
    return getwidth(node.lb) + getwidth(node.rb)

def getdepth(node):
    if node.lb==None and node.rb==None: return 0
    return max(getdepth(node.lb), getdepth(node.rb)) + 1


def drawtree(root_node, jpeg):
    w = getwidth(root_node) * 100
    h = getdepth(root_node) * 100 + 120
    img = Image.new('RGB',(w,h),(255,255,255))
    draw = ImageDraw.Draw(img)
    drawnode(draw, root_node, w / 2, 20)
    img.save(jpeg, 'JPEG')


def drawnode(draw, node, x, y):
    if not node.is_leaf:
        # Get the width of each branch
        w1= getwidth(node.rb) * 100
        w2= getwidth(node.lb) * 100
        # Determine the total space required by this node
        left=x-(w1+w2)/2
        right=x+(w1+w2)/2
        # Draw the condition string
        draw.text((x-20,y-10), "feature %s <= %s" % (node.feature, node.threshold), (0, 0, 0))
        # Draw links to the branches
        draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
        draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))
        # Draw the branch nodes
        drawnode(draw, node.rb, left + w1 / 2, y + 100)
        drawnode(draw, node.lb, right - w2 / 2, y + 100)
    else:
        txt= "depth: %s" % str(node.node_depth)
        draw.text((x-20,y),txt,(0,0,0))

def draw_tree(tree, jpeg='tree.jpg'):
    n_nodes = tree.node_count
    children_left = tree.children_left
    children_right = tree.children_right
    feature = tree.feature
    threshold = tree.threshold

    node_depth = np.zeros(shape=n_nodes)
    is_leaves = np.zeros(shape=n_nodes, dtype=bool)
    stack = [(0, -1)]  # seed is the root node id and its parent depth
    while len(stack) > 0:
        node_id, parent_depth = stack.pop()
        node_depth[node_id] = parent_depth + 1

        # If we have a test node
        if (children_left[node_id] != children_right[node_id]):
            stack.append((children_left[node_id], parent_depth + 1))
            stack.append((children_right[node_id], parent_depth + 1))
        else:
            is_leaves[node_id] = True

    nodes = []
    for i in xrange(n_nodes):
        new_node = decisionnde(node_depth[i], is_leaves[i])
        nodes.append(new_node)
        if is_leaves[i]:
            pass
            # print("%snode=%s leaf node." % (node_depth[i] * "\t", i))
        else:
            new_node.feature = feature[i]
            new_node.threshold = threshold[i]
            # print("%snode=%s test node: go to node %s if X[:, %s] <= %ss else to "
            #       "node %s."
            #       % (node_depth[i] * "\t",
            #          i,
            #          children_left[i],
            #          feature[i],
            #          threshold[i],
            #          children_right[i],
            #          ))

    for i in xrange(n_nodes):
        if not is_leaves[i]:
            nodes[i].lb = nodes[children_left[i]]
            nodes[i].rb = nodes[children_right[i]]

    root = nodes[0]
    w=getwidth(root)*100
    h=getdepth(root)*100+120
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)
    drawnode(draw, root,w/2,20)
    img.save(jpeg,'JPEG')
