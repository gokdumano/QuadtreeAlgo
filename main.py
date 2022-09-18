from utils import *

XMAX, YMAX = 512, 512
N_POINTS   = 32

points   = Point.sample( xMax=XMAX, yMax=YMAX, n_sample=N_POINTS )
bbox     = Rectangle( x=0, y=512, width=512, height=512 )
bbox.addPoint(*points)

quadTree = QTree(bbox)
VisualizeQTree(points, quadTree)