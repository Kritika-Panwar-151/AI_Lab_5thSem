import random

board=["_","_","_",
       "_","_","_",
       "_","_","_"]
winningCombinations=[(0,1,2),(3,4,5),(6,7,8),
                     (0,3,6),(1,4,7),(2,5,8),
                     (0,4,8),(2,4,6)]
c=0
completed=[]

def printBoard():
    for i in range(9):
        print(board[i],end=" ")
        if((i+1)%3==0): print()

def humanMove():
    global c
    
    pos=int(input("Enter position:"))
    pos=pos-1
    if(pos>=9 or pos<0 or pos in completed):
       print("Wrong position")
       humanMove()
    else:  
        board[pos]="X"
        completed.append(pos)
        c=c+1

def compMove():
    global c
    pos=-1
    for i in winningCombinations:
            if(board[i[0]]=="X" and board[i[1]]=="X" and i[2] not in completed):
                pos=i[2]
                break
            if(board[i[0]]=="X" and board[i[2]]=="X" and i[1] not in completed):
                pos=i[1]
                break
            if(board[i[1]]=="X" and board[i[2]]=="X" and i[0] not in completed):
                pos=i[0]
                break
    if(pos==-1):
        while(True):
            j=random.randint(0,8)
            if(j not in completed):
                pos=j
                break
    board[pos]="O"
    completed.append(pos)
    c=c+1

def isWin(s):
    for i in winningCombinations:
        if(board[i[0]]==s and board[i[1]]==s and board[i[2]]==s):
            return True
    return False

print("Board")
printBoard()
while(c<9):
    print("Your chance")
    humanMove()
    printBoard()
    if(isWin("X")):
        print("Human Wins")
        break
    print("Computers Move")
    compMove()
    printBoard()
    if(isWin("O")):
        print("Computer Wins")
        break
    isWin("O")
    
if(c==9 and not isWin("X") and not isWin("O")): 
    print("DRAW")














    
