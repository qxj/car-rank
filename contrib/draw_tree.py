#!/usr/bin/python
#
# Copyright (C) 2016 Julian Qian
#
# @file      draw_tree.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-07-11 20:33:56
#

"""
Draw heatmap of the LambdaMART model generated from RankLib.

Inspired by https://wellecks.wordpress.com/2015/02/21/peering-into-the-black-box-visualizing-lambdamart/

Usage:
./draw_tree.py model.xml | dot -Tpng > model_heatmap.png
"""

import xml.etree.ElementTree
import sys

xmlFile = sys.argv[1]
ensemble = xml.etree.ElementTree.parse(xmlFile).getroot()


class Node(object):

    def __init__(self):
        self.feat = None
        self.thre = None
        self.output = None
        self.left = None
        self.right = None

    def __str__(self):
        if self.is_leaf():
            return """<output:%.2f>""" % (self.output)
        else:
            return """<feat:%d/%.2f, %s, %s>""" % (
                self.feat, self.thre, self.left, self.right
            )

    def __repr__(self):
        return self.__str__()

    def is_leaf(self):
        return self.output is not None


def build_tree(split):
    root = Node()
    for elem in list(split):
        if elem.tag == 'output':  # leaf
            root.output = float(elem.text)
            return root
        elif elem.tag == 'feature':
            root.feat = int(elem.text)
        elif elem.tag == 'threshold':
            root.thre = float(elem.text)
        elif elem.tag == 'split':
            pos = elem.attrib['pos']
            if pos == 'left':
                root.left = build_tree(elem)
            elif pos == 'right':
                root.right = build_tree(elem)
    return root

trees = []
for tree in list(ensemble)[:100]:
    eroot = list(tree)[0]
    trees.append(build_tree(eroot))

# print len(trees)

import collections


class HNode(object):

    def __init__(self):
        self.feats = collections.defaultdict(lambda: 0)
        self.left = None
        self.right = None

    def __str__(self):
        out = ['%s:%s' % (k, v) for k, v in self.feats.items()]
        return """<%s, %s, %s>""" % ('|'.join(out),
                                     self.left, self.right)

    def __repr__(self):
        return self.__str__()

g_HeatMap = HNode()


def build_heatmap(tree, root):
    if tree.is_leaf():
        root.feats['N'] += 1
        return
    root.feats[tree.feat] += 1
    if tree.left:
        if root.left is None:
            root.left = HNode()
        build_heatmap(tree.left, root.left)
    if tree.right:
        if root.right is None:
            root.right = HNode()
        build_heatmap(tree.right, root.right)


for tree in trees:
    build_heatmap(tree, g_HeatMap)


def draw_node(node, n=0):
    items = sorted(node.feats.items(), key=lambda x: x[1], reverse=True)
    feats = ['%s:%d' % (feat, num) for feat, num in items]
    print """n{} [label="{}"]; """.format(n, '|'.join(feats))
    if node.left:
        print """n{} -> n{}; """.format(n, 2 * n + 1)
        draw_node(node.left, 2 * n + 1)
    if node.right:
        print """n{} -> n{}; """.format(n, 2 * n + 2)
        draw_node(node.right, 2 * n + 2)

print "digraph G {"
print "node [shape=record];"
draw_node(g_HeatMap)
print "}"
