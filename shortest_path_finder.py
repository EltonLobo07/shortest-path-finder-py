import pygame
from heapq import heappush,heappop
from random import randint
from math import sqrt

pygame.init()
WIN_SIZE=600
WIN=pygame.display.set_mode((WIN_SIZE,WIN_SIZE+50)) #+50 to the HEIGHT for the bottom menu
#pygame.display.set_mode((WIDTH,HEIGHT))

pygame.display.set_caption("Shortest path finder")
#This will be the display name of the window

#Defining the colors I will be using
#Color name=(R,G,B) 
ORANGE=(255,140,0)      #Start node 
GREY=(128,128,128)      #Grid lines
BLACK=(0,0,0)           #Barrier nodes
RED=(255,0,0)           #Open nodes (Nodes in heap)
GREEN=(0,255,0)         #Closed nodes (Nodes which are processed)
WHITE=(255,255,255)     #default node color
PURPLE=(128,0,128)      #Path nodes
LIGHT_BLUE=(135,206,235)#End node

class Node:
    def __init__(self,row,col,gap):
        self.row,self.col=row,col #The row and col value indicating where in the grid this node is present        
        self.x,self.y=col*gap,row*gap #The actual top left location of this node on the display
        self.color=WHITE
        self.neighbors=[] #Can have 4 nodes at max 
        self.gap=gap

    def getPos(self):
        '''
            Returns the row and column number of this node in grid 2D array
        '''
        return self.row,self.col

    def isClosed(self):
        return self.color==GREEN
    
    def isOpen(self):
        return self.color==RED

    def isBarrier(self):
        return self.color==BLACK

    def isPath(self):
        return self.color==PURPLE

    def isStart(self):
        return self.color==ORANGE

    def reset(self):
        self.color=WHITE

    def close(self):
        '''
            Sets the node to be a closed node
        '''
        self.color=GREEN

    def open(self):
        '''
            Sets the node to be an open node
        '''
        self.color=RED

    def barrier(self):
        '''
            Sets the node to be a barrier node
        '''
        self.color=BLACK

    def start(self):
        '''
            Sets the node to be the start node
        '''
        self.color=ORANGE

    def end(self):
        '''
            Sets the node to be the end node
        '''
        self.color=LIGHT_BLUE

    def path(self):
        '''
            The nodes on which this method is called will be in the path from start to end node
        '''
        self.color=PURPLE

    def draw(self,win):
        '''
            A node is represented using a rectangle. This rectangle is placed on the display starting at (self.x,self.y) when this method is called
        '''
        pygame.draw.rect(win,self.color,(self.x,self.y,self.gap,self.gap))
        #pygame.draw.rect(window_object,(R,G,B),(x,y,width,height))

    def updateNeighbors(self,grid):
        for nr,nc in [(self.row+1,self.col),(self.row-1,self.col),(self.row,self.col+1),(self.row,self.col-1)]:
            if (nr<0 or nr==len(grid) or nc<0 or nc==len(grid) or grid[nr][nc].isBarrier()):
                #Not a vald row or not a valid column or a barrier node
                continue
            self.neighbors.append(grid[nr][nc])

class Button:
    def __init__(self,color,x,y,width,height,text,text_color=(0,0,0)):
        self.color=color
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.text=text
        self.text_color=text_color #Default: Black color

    def draw(self,win):
        pygame.draw.rect(win,self.color,(self.x,self.y,self.width,self.height))
        font=pygame.font.SysFont('comicsans',20)
        #create a Font object from the system fonts
        #SysFont(name, size, bold=False, italic=False) -> Font
        #https://www.pygame.org/docs/ref/font.html#pygame.font.SysFont
        text=font.render(self.text,True,self.text_color)
        #This creates a new Surface with the specified text rendered on it. pygame provides no way to directly draw text on an existing Surface
        #instead you must use Font.render() to create an image (Surface) of the text, then blit this image onto another Surface.
        win.blit(text,(self.x+(self.width/2-text.get_width()/2),self.y+(self.height/2-text.get_height()/2)))

    def isOver(self,pos):
        x,y=pos
        if (x>self.x and x<self.x+self.width and y>self.y and y<self.y+self.height):
            return  True
        return False

def h(n1,n2):
    '''
        n1 and n2: Object of Node class, check Node class definition for more details
    '''
    x1,y1=n1.getPos()
    x2,y2=n2.getPos()
    #A heuristic function is said to be admissible if it never overestimates the cost of reaching the goal
    #Euclidean distance will under estimate the cost which makes the heuristic function admissible
    return sqrt((x1-x2)**2+(y1-y2)**2) 

def createGrid(total_rows,win_size):
    '''
        Creates a 2D array consisting of class Node objects.
        grid shape: total_rows x total_rows
    '''
    gap=win_size//total_rows
    return [[Node(r,c,gap) for c in range(total_rows)] for r in range(total_rows)]

def drawGridLines(win,total_rows,win_size):
    '''
        Draws vertical and horizontal lines representing a grid on the display
    '''
    gap=win_size//total_rows
    for i in range(total_rows):
        cur=i*gap
        pygame.draw.line(win,GREY,(0,cur),(win_size,cur)) #draws vertical lines
        #pygame.draw.line(window_object,(R,G,B),(start_x,start_y),(end_x,end_y))
        pygame.draw.line(win,GREY,(cur,0),(cur,win_size)) #draws horizontal lines

def draw(win,grid,total_rows,win_size,b1,b2):
    '''
        Everything that is to be drawn on the window is written inside this function.
        After drawing, it updates the display so that all the changes are visible
    '''
    WIN.fill(WHITE)
    #Draw the nodes i.e. Place nodes and color nodes to default node color
    for nodes in grid:
        for node in nodes:
            node.draw(win)
    #Draw grid lines
    drawGridLines(win,total_rows,win_size)
    #Create the bottom menu
    pygame.draw.rect(win,BLACK,(0,win_size,win_size,50))
    b1.draw(win)
    b2.draw(win)
    #Update the window
    pygame.display.update()

def getClickedPos(pos,total_rows,win_size):
    '''
        pos: (x,y) position on the display
        
        Returns which grid cell is responsible for the current position on the display.
        It returns col,row of the grid cell
    '''
    gap=win_size//total_rows
    return pos[0]//gap,pos[1]//gap

def resetGrid(grid,keep_barriers=True):
    #Loop through all the nodes in the grid
    for nodes in grid:
        for node in nodes:
            if (node.isBarrier()):
                if (keep_barriers):
                    continue
            #Delete neighbor information from every node
            node.neighbors=[]
            #Reset all nodes to be default node
            node.reset()
    return None,None #start,end

def reconstruct(parent,end):
    node=end
    while (parent[node]):
        node.path()
        node=parent[node]
    end.end()

def locateCell(total_rows,win_size):
    return getClickedPos(pygame.mouse.get_pos(),total_rows,win_size)

def Astar(draw,grid,start,end):
    timestamp=0 #Will act as a tie breaker between tuples in the mnHeap, increments by 1 whenever a tuple is added to the heap
    mnHeap,parent=[],{}
    #Build g map
    g={node:float('inf') for nodes in grid for node in nodes} #g keeps track of the minimum distance from start node to the current node
    #Build f map
    f={node:float('inf') for nodes in grid for node in nodes} #f keeps track of g score + h score of a node
    #Update g, f and parent information for the start node
    g[start],f[start],parent[start]=0,h(start,end),None
    #Add a tuple of (f_score,cur_timestamp,start_node) to heap
    heappush(mnHeap,(f[start],timestamp,start))
    timestamp+=1
    #Loop until there is something in the heap
    while (mnHeap):
        #Add exit feature
        for event in pygame.event.get():
            if (event.type==pygame.QUIT):
                return True
        #Remove the node with smallest f score
        f_score,_,cur=heappop(mnHeap)
        if (f_score>f[cur]):
            #We have a better path in the mnHeap, the current tuple is outdated
            continue
        #Check if the removed node is the end node
        if (cur==end):
            reconstruct(parent,end)
            return False
        #Loop through the neighbors of the current node
        for node in cur.neighbors:
            if (node.isClosed() or node.isStart()):
                continue
            g_val=g[cur]+1
            if (g_val<g[node]):
                g[node]=g_val
                f[node]=g_val+h(node,end)
                parent[node]=cur
                heappush(mnHeap,(f[node],timestamp,node))
                timestamp+=1
                node.open() #To indicate the node is inside mnHeap
        if (cur!=start):
            cur.close() #If we closed start node, we lose color of the start node in the visualization
        draw()
    return False

def DijkstraSP(draw,grid,start,end):
    timestamp=0
    mnHeap,parent=[],{}
    #A map to record the minimum distance from the source to the node
    dist={node:float('inf') for nodes in grid for node in nodes}
    #Use the start node
    dist[start],parent[start]=0,None
    mnHeap.append((0,timestamp,start))
    timestamp+=1
    #Loop until there is something in the heap
    while (mnHeap):
        #Add exit feature
        for event in pygame.event.get():
            if (event.type==pygame.QUIT):
                return True
        #Remove the node with smallest distance from the mnHeap
        d,_,cur=heappop(mnHeap)
        if (d>dist[cur]):
            #We have a better path in the mnHeap, the current tuple is outdated
            continue
        #Check if the removed node is the end node
        if (cur==end):
            reconstruct(parent,end)
            return False
        for neighbor in cur.neighbors:
            if (neighbor.isClosed() or neighbor==start):
                continue
            nd=d+1
            if (nd<dist[neighbor]):
                dist[neighbor],parent[neighbor]=nd,cur
                heappush(mnHeap,(nd,timestamp,neighbor))
                timestamp+=1
                neighbor.open()
        if (cur!=start):
            cur.close()
        draw()
    return False

def generateRandom(draw,grid):
    '''
        Iterative DFS but the order of appending neighbors to stack is random
    '''
    stack,added=[grid[0][0]],{(0,0)}
    for r in range(0,len(grid)):
        for c in range(len(grid)):
            grid[r][c].barrier()
    for c in range(0,len(grid)):
        for r in range(len(grid)):
            grid[r][c].barrier()
    while (stack):
        for event in pygame.event.get():
            if (event.type==pygame.QUIT):
                return True
        cur,tmp=stack.pop(),[]
        for nr,nc in [(cur.row+1,cur.col),(cur.row-1,cur.col),(cur.row,cur.col+1),(cur.row,cur.col-1)]:
            if (nr<0 or nr==len(grid) or nc<0 or nc==len(grid) or (nr,nc) in added):
                continue
            tmp.append(grid[nr][nc])
            added.add((nr,nc))
        if (len(tmp)==0):
            continue
        cur.reset()
        nxt=tmp[randint(0,len(tmp)-1)]
        for node in tmp:
            if (node!=nxt):
                stack.append(node)
        stack.append(nxt)
        draw()
    return False

def main(win,win_size):
    total_rows=50 #Path finding takes decent amount of time with value set to 50
    start,end,grid,run=None,None,createGrid(total_rows,WIN_SIZE),True
    #start represents the start node
    #end represents the end node
    #grid represents the grid which holds all of the displayed nodes
    #run represents boolean value. When set to False, the control comes out of the main while loop 
    dButton=Button(WHITE,2,win_size+2,win_size//2-3,46,"Dijkstra's shortest path",BLACK) #Button to the bottom left for Dijkstra's shortest path
    aButton=Button(BLACK,win_size//2+1,win_size+2,win_size//2-2,46,"A star",WHITE) #Button to the bottom right for A star
    while (run):
        #Draw everything on the display
        draw(WIN,grid,total_rows,WIN_SIZE,dButton,aButton)
        
        #Add exit feature. When user clicks on the 'X' button on the top right of the window, the program ends
        for event in pygame.event.get():
            if (event.type==pygame.QUIT):
                run=False
                
            #Check if left mouse button is pressed
            #left mouse button is dedicated to add barrier, start and end nodes or to select an option on the menu bar
            if (pygame.mouse.get_pressed()[0]):
                #Get the position of the mouse of the display
                c,r=locateCell(total_rows,win_size)
                if (r>=total_rows):
                    pos=pygame.mouse.get_pos()
                    if (dButton.isOver(pos)):
                        dButton.color,dButton.text_color=WHITE,BLACK
                        aButton.color,aButton.text_color=BLACK,WHITE
                    elif (aButton.isOver(pos)):
                        aButton.color,aButton.text_color=WHITE,BLACK
                        dButton.color,dButton.text_color=BLACK,WHITE
                    continue
                node=grid[r][c]
                if (not start and node!=end):
                    start=node
                    start.start()
                elif (not end and node!=start):
                    end=node
                    end.end()
                elif (node!=start and node!=end):
                    node.barrier()
                    
            #Check if right mouse button is clicked
            #right mouse button is dedicated to delete barrier, start and end nodes from the display
            elif (pygame.mouse.get_pressed()[2]):
                #Get the position of the mouse of the display
                c,r=locateCell(total_rows,win_size)
                if (r>=total_rows):
                    continue
                node=grid[r][c]
                #Don't allow user to remove open, closed and path nodes
                if (node.isOpen() or node.isClosed() or node.isPath()):
                    continue
                node.reset()
                if (start==node):
                    start=None
                elif (end==node):
                    end=None
                    
            #Check if any key is pressed 
            if (event.type==pygame.KEYDOWN):
                #Check if g is pressed
                #'g' key is dedicated to generating a random graph using DFS
                if (event.key==pygame.K_g):
                    resetGrid(grid)
                    start,end=None,None
                    if (generateRandom(lambda: draw(win,grid,total_rows,win_size,dButton,aButton),grid)):
                        run=False
                    
                #Check the key is equal to the SPACEBAR
                #'SPACEBAR' key is dedicated to start Dijkstra's shortest path or A star algorithm depending on the user's choice
                elif (event.key==pygame.K_SPACE and start and end):
                    resetGrid(grid)
                    #Intentional overwrites
                    start.start()
                    end.end()
                    #Update the adjacency list of every node on the display
                    for nodes in grid:
                        for node in nodes:
                            node.updateNeighbors(grid)
                    if (dButton.color==WHITE):
                        if (DijkstraSP(lambda: draw(win,grid,total_rows,win_size,dButton,aButton),grid,start,end)):
                            run=False
                    else:
                        if (Astar(lambda: draw(win,grid,total_rows,win_size,dButton,aButton),grid,start,end)):
                            run=False

                #'LCTRL' key is dedicated to resetting the display
                elif (event.key==pygame.K_LCTRL):
                    start,end=resetGrid(grid,False)
    pygame.quit()

if (__name__=='__main__'):
    main(WIN,WIN_SIZE)
