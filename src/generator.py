import sys
import os.path
import random as r
import copy
    
def initGrid():
    grid.clear()
    for i in range(N*N):
        grid.append(0)

def update():
    for c, cell in enumerate(grid):
        rows[int(c/N)][c%N] = cell
        cols[c%N][int(c/N)] = cell
        boxs[int(c/Q%P) + P*int(c/(P*N))][c%Q + Q*int(c/N) - N*int(c/(P*N))] = cell

def check(n):
    for row in rows:
        if row.count(n) > 1:
            return False
    for col in cols:
        if col.count(n) > 1:
            return False
    for box in boxs:
        if box.count(n) > 1:
            return False
    return True
            
def f():
    availTokens = copy.copy(T)

    index = r.choice(availCell)
    
    availCell.pop(availCell.index(index))

    #print(index)

    token = r.choice(availTokens)
    availTokens.pop(availTokens.index(token))
    grid[index] = token
    update()
    while True:
        if check(token):
            break
        else:
            if len(availTokens) > 0:
                #print(availTokens)
                token = r.choice(availTokens)
                availTokens.pop(availTokens.index(token))
                grid[index] = token
                update()
            else:
                initGrid()
                return "FAILED"

def gen():                
    for i in range(M):
        if f() == "FAILED":
            global availCell
            availCell = copy.copy(gridIndexList)
            return True
    return False

def convert(g):
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    string = ""
    header = str(N) + " " + str(P) + " " + str(Q) + "\n"
    for row in g:
        string += str(row)[1:-1] + "\n"
    for i in range (10, 36):
        if str(i) in string:
            string = string.replace(str(i), alphabet[i-10])
            print(i, "replaced with: ", alphabet[i-10])
    return header + string.replace(',', '')

def writeFile(txt):
    file = open(outputFileName, 'w')
    file.write(txt)
    file.close()

if __name__ == '__main__':
    inputFileName = sys.argv[1]

    if os.path.isfile(inputFileName) == False:
        print("Input file does not exist.")
        sys.exit()

    outputFileName = sys.argv[2]

    inputFile = open(inputFileName)
        
    inputText = inputFile.readline()

    inputFile.close()

    inputList = inputText.split()

    allTokens = []
    for i in range(1, 36):
        allTokens.append(i)

    M = int(inputList[0])
    N = int(inputList[1])
    P = int(inputList[2])
    Q = int(inputList[3])

    T = allTokens[:N]

    grid = []
    for i in range(N*N):
        grid.append(0)

    gridIndexList = []
    for i in range(N*N):
        gridIndexList.append(i)

    rows = []
    cols = []
    boxs = []
    for i in range(N):
        rows.append([])
        cols.append([])
        boxs.append([])
        for j in range(N):
            rows[i].append(0)
            cols[i].append(0)
            boxs[i].append(0)

    availCell = copy.copy(gridIndexList)

    while gen():
        pass

    writeFile(convert(rows))
