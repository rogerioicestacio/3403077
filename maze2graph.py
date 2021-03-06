import numpy as np
from PIL import Image
import time

def load_image( infilename ) :
    img = Image.open( infilename )
    impixels = img.load()
    #img.show()
    #print(impixels[0,0])
    print(img.getbands())
    data = np.asarray( img, dtype="int32" )
    print("Image shape: ",data.shape)
    return data

def save_image( npdata, outfilename ) :
    print("Saved image shape: ",npdata.shape)
    #img = Image.fromarray(npdata,"RGBA")
    img = Image.fromarray( np.asarray( np.clip(npdata,0,255), dtype="uint8"), "RGBA" )
    img.save( outfilename )
    
def find_entry(data):
    #for i in data[0]:
    #print data[0].shape
    for index, x in enumerate(data[0]):
        if x[0] == 0:
            #print(index)
            #print(data[2][index][0])
            return 0,index

def find_exit(data):
    wd,hd,sd = data.shape
    for index, x in enumerate(data[-1]):
        if x[0] == 0:
            return wd-2,index
            
            
def find_dir(data,l,c,block=2):
    right=0
    left=0
    top=0
    down=0
    wd,hd,sd = data.shape
    #right
    if c < wd-block and data[l][c+block][0] == 0:
        right=block
    #left        
    if c > block and (data[l][c-block][0] == 0 or data[l+1][c-block][0] == 0):
        left=block        
    #down        
    if l < hd-block and data[l+block][c][0] == 0:
        down=block
    #top        
    if l > block and (data[l-block][c][0] == 0 or data[l-block][c+1][0] == 0):
        top=block
    return right,down,left,top
    
class Graph_state:
    def __init__(self,line,column,start=False):
        self.line = line
        self.column = column
        self.start = start
        self.children = []
        self.parent = None
        self.goal = False
    def isgoal(self, objective):
        if (objective[0] == self.line) and (objective[1] == self.column):
            self.goal = True
    def add(self,child):
        child.parent = self
        self.children.append(child)
    def __str__(self):
        repre = "(%d,%d)"%(self.line,self.column)
        return repre
        
def find_next_intersection(data, act_state, vector, objective):
    wd,hd,sd = data.shape
    if vector[0] != 0:
        #go right
        for x in range(act_state.column+vector[0],wd,vector[0]):
            right,down,left,top = find_dir(data,act_state.line,x)
            if right == 0: #found an edge
                new_state = Graph_state(act_state.line,x)
                new_state.isgoal(objective)
                act_state.add(new_state)
                #print("intersection right at: ",act_state.line,x)
                #print(" -> can go: ",(0,down,0,top))
                find_next_intersection(data, new_state, (0,down,0,top), objective)   
                break
            if down != 0 or top != 0:    
                new_state = Graph_state(act_state.line,x)
                new_state.isgoal(objective)
                act_state.add(new_state)
                #print("intersection right at: ",act_state.line,x)
                #print(" -> can go: ",(0,down,0,top))
                find_next_intersection(data, new_state, (0,down,0,top), objective)   
    if vector[1] != 0:
        #go down
        for y in range(act_state.line+vector[1],hd,vector[1]):
            right,down,left,top = find_dir(data,y,act_state.column)
            if down == 0: #found an edge
                new_state = Graph_state(y,act_state.column)
                new_state.isgoal(objective)
                act_state.add(new_state)
                #print("intersection down at: ",y,act_state.column)
                #print(" -> can go: ",(right,0,left,0))
                find_next_intersection(data, new_state, (right,0,left,0), objective)
                break
            if right != 0 or left != 0:    
                new_state = Graph_state(y,act_state.column)
                new_state.isgoal(objective)
                act_state.add(new_state)
                #print("intersection down at: %d,%d -> can go: %r"%(y,act_state.column,(right,0,left,0)))
                find_next_intersection(data, new_state, (right,0,left,0), objective)
    if vector[2] != 0:
        #go left
        for x in range(act_state.column-vector[2],0,-vector[2]):
            right,down,left,top = find_dir(data,act_state.line,x)
            if left == 0: #found an edge
                new_state = Graph_state(act_state.line,x)
                new_state.isgoal(objective)
                act_state.add(new_state)
                #print("intersection left at: ",act_state.line,x)
                #print(" -> can go: ",(0,down,0,top))
                find_next_intersection(data, new_state, (0,down,0,top), objective)   
                break
            if down != 0 or top != 0:    
                new_state = Graph_state(act_state.line,x)
                new_state.isgoal(objective)
                act_state.add(new_state)
                #print("intersection left at: %d,%d  -> can go: %r"%(act_state.line,x,(0,down,0,top)))
                find_next_intersection(data, new_state, (0,down,0,top), objective)   
    if vector[3] != 0:
        #go up
        for y in range(act_state.line-vector[3],0,-vector[3]):
            right,down,left,top = find_dir(data,y,act_state.column)
            if top == 0: #found an edge
                new_state = Graph_state(y,act_state.column)
                new_state.isgoal(objective)
                act_state.add(new_state)
                #print("intersection up at: ",y,act_state.column)
                #print(" -> can go: ",(right,0,left,0))
                find_next_intersection(data, new_state, (right,0,left,0), objective)
                break
            if right != 0 or left != 0:    
                new_state = Graph_state(y,act_state.column)
                new_state.isgoal(objective)
                act_state.add(new_state)
                #print("intersection up at: %d,%d -> can go: %r"%(y,act_state.column,(right,0,left,0)))
                find_next_intersection(data, new_state, (right,0,left,0), objective)
    
def count_state(root_state, count):
    for s in root_state.children:
        count += 1
        count += count_state(s,0)
    return count    

def print_states(root_state, output):
    if root_state.start:
        output += "R:"+str(root_state) + ";"
    elif root_state.goal:
        output += "**"+str(root_state) + "**;"
    else:
        output += str(root_state) + ";"
    for s in root_state.children:
        output += print_states(s,"")
    return output    
    
def draw_path(data,root_state):
    if root_state.start:
        data[root_state.line][root_state.column] = [0,255,0,255]    
    elif root_state.goal:
        data[root_state.line][root_state.column] = [255,0,0,255]
    else:
        data[root_state.line][root_state.column] = [255,255,0,255]
    for s in root_state.children:   
        draw_path(data,s)
    
t0 = time.time()    
#img_data = load_image('4 by 4 orthogonal maze.png')
img_data = load_image('10 by 10 orthogonal maze.png')
#img_data = load_image('100 by 100 orthogonal maze.png')

l_entrada,c_entrada = find_entry(img_data)
lex,cex = find_exit(img_data)
objective = (lex,cex)
print("entrada: ",l_entrada,c_entrada)
print("saida: ",objective)
start_point = Graph_state(l_entrada,c_entrada,True)
start_point.isgoal(objective)
find_next_intersection(img_data,start_point,find_dir(img_data,l_entrada,c_entrada),objective)
total_state = count_state(start_point,1)

print("total states: %d"%total_state)
if total_state < 500:
    print(print_states(start_point,"-> "))
else:
    print("muitos estados para imprimir...")
print("tempo de pre-processamento: %2.5f sec"%(time.time()-t0))

draw_path(img_data,start_point)
save_image( img_data, 'solve.png' )
