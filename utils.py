from collections import defaultdict, deque

from networkx.drawing.nx_pydot import graphviz_layout
from matplotlib import pyplot as plt
import networkx as nx

from operator import attrgetter, itemgetter
from math import degrees, atan2
from random import uniform

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __repr__(self):
        return f'POINT<x:{self.x}, y:{self.y}>'        
    def __iter__(self):
        return (_ for _ in (self.x, self.y))    
    @staticmethod
    def sample(xMax, yMax, xMin=0, yMin=0, n_sample=16):
        return { Point(uniform(xMin, xMax), uniform(yMin, yMax)) for _ in range(n_sample) }   
        
class Rectangle:
    def __init__(self, x, y, width, height, name='Main', parent=None):
        self.xy     = Point(x, y)
        self.width  = width
        self.height = height
        
        self.points   = set()
        self.name     = name
        self.parent   = parent
        
    def __repr__(self):
        return f'RECTANGLE<UpperLeftCoord:{self.xy}, Width:{self.width}, Height:{self.height}, Name:{self.name}> ({len(self.points)} points)'
    
    def __hash__(self):
        return hash((*self.xy, self.width, self.height))
    
    def __contains__(self, point):
        xMin, yMax = self.xy
        xMax, yMin = xMin + self.width, yMax - self.height
        return (xMin <= point.x < xMax) and (yMin <= point.y < yMax)
    
    def addPoint(self, *points):
        for point in points:
            if point in self:
                self.points.add(point)                
    
    def divide(self):
        xMin, yMax = self.xy
        xMax, yMin = xMin + self.width, yMax - self.height
        xMid, yMid = (xMax + xMin) / 2, (yMax + yMin) / 2
        dw, dh     = self.width / 2, self.height / 2
        
        UpperRight = Rectangle(xMid, yMax, dw, dh, name=f'{self.name}_UR', parent=self.name)
        UpperLeft  = Rectangle(xMin, yMax, dw, dh, name=f'{self.name}_UL', parent=self.name)
        LowerRight = Rectangle(xMid, yMid, dw, dh, name=f'{self.name}_LR', parent=self.name)
        LowerLeft  = Rectangle(xMin, yMid, dw, dh, name=f'{self.name}_LL', parent=self.name)
        
        UpperRight.addPoint(*self.points)
        UpperLeft.addPoint(*self.points)
        LowerRight.addPoint(*self.points)
        LowerLeft.addPoint(*self.points)
    
        return UpperRight, UpperLeft, LowerRight, LowerLeft

def QTree(bbox):
    quadTree = { bbox }
    queue    = deque([ bbox ])
    
    while queue:
        div     = queue.pop()
        subdivs = div.divide()
        
        for subdiv in subdivs:
            if len(subdiv.points) > 1:
                queue.append(subdiv)
            quadTree.add(subdiv)
            
    return quadTree

def VisualizeQTree(points, quadTree):
    fig, axs = plt.subplots(1, 2, figsize=(21,18))
    axs[0].set_axis_off()
    axs[1].set_axis_off()

    #create simple line plot
    xs, ys  = [], []
    for point in points:
        xs.append(point.x)
        ys.append(point.y)
    axs[0].scatter(xs, ys, c='r', marker='+')

    for rect in quadTree:
        x1, y2 = rect.xy
        x2, y1 = x1 + rect.width, y2 - rect.height
        axs[0].plot([x1,x2,x2,x1,x1], [y1,y1,y2,y2,y1], c='k')        

    nodes = [ (q.name, { 'n_points': len(q.points) }) for q in quadTree    ]
    edges = [ (q.name, q.parent) for q in quadTree if q.parent is not None ]

    G   = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    empties = set()
    leaves  = set()
    parents = set()

    for name, data in G.nodes(data=True):
        n_points = data['n_points']
        if   n_points == 0: empties.add(name)
        elif n_points == 1: leaves.add(name)
        else              : parents.add(name)
        
    pos = graphviz_layout(G, prog='twopi')
    nx.draw_networkx_edges(G, pos, width=.5, edge_color='k')
    nx.draw_networkx_nodes(G, pos, nodelist=empties , node_color='w', node_size=20, edgecolors='k', ax=axs[1])
    nx.draw_networkx_nodes(G, pos, nodelist=leaves  , node_color='g', node_size=20, edgecolors='k', ax=axs[1])
    nx.draw_networkx_nodes(G, pos, nodelist=parents , node_color='b', node_size=20, edgecolors='k', ax=axs[1])
    nx.draw_networkx_nodes(G, pos, nodelist=['Main'], node_color='r', node_size=50, edgecolors='k', ax=axs[1])
    
    plt.tight_layout()
    plt.show()