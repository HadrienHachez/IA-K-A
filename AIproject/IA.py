        #   The possible actions are:
        #   ('move', x, y, dir): moves person at position (x,y) of one cell in direction dir
        #   ('arrest', x, y, dir): arrests the villager in direction dir with knight at position (x, y)
        #   ('kill', x, y, dir): kills the assassin/knight in direction dir with knight/assassin at position (x, y)
        #   ('attack', x, y, dir): attacks the king in direction dir with assassin at position (x, y)
        #   ('reveal', x, y): reveals villager at position (x,y) as an assassin

        #   state['people'] == liste de liste pour localisation personnages
        #   state['board'] == liste de liste pour plateau de jeu
        #   state['card'] == [2,7,false,5]

import random
import copy

                #   ----------------------
                #         ASSASSINS
                #   ----------------------
        
#   assassins par défaults
        # fonction qui me permet de choisir des assassins aléatoirement parmis mes citoyens en début de jeu
def choicekillers(state):
    MyPop=[]
    for i in range(10):
        for j in range(10):
            if state['people'][i][j] not in {"knight","king",None}:
                MyPop.append(state['people'][i][j])
    MyKillers=[]
    while len(MyKillers)!=3:
        Killer=random.choice(MyPop)
        if Killer not in MyKillers:
            MyKillers.append(Killer)
    return MyKillers

#   Time or not time yet?
        # determine la distance en case entre deux pions (indépendamment du terrain et de son occupation)
        # réccupère tout ceux qui sont assez proche de l'objectif par rapport aux points d'action
def able2kill(group,pa,king,myactions):
    d=[]
    for guy in group:
        d.append(abs(guy[1]-king[1])+abs(guy[2]-king[2]))
    Distance=copy.copy(d)
    D=0
    I=[]
    while D<=pa:
        try:
            I.append(group[d.index(D)])
            d[I[end]]=-1
        except:
            D+=1
    return I 

#   calcul abilité à tuer ou non
        # Mon petit chef-d'oeuvre, cette série de 3 fonctions (dont 2 récursives) me donne au final toute les possibilités de trajet
        # indépendamment du terrain et de son occupation qu'un peyon peut prendre pour aller d'un point à un autre
        # cette fonction
def findway(x,y,MOVE=[]):
    A=copy.copy(x)
    B=copy.copy(y)
    move=copy.copy(MOVE)
    try:
        A[1],A[2]=A[1]+move[-1][0],A[2]+move[-1][1]
    except:
        pass
    if A[1]==B[1] and A[2]==B[2]:
        return move
    elif A[2]-B[2]==0:
        move.append(((B[1]-A[1])/abs(A[1]-B[1]),0))
        return findway(A,B,move)
    elif A[1]-B[1]==0:
        move.append((0,(B[2]-A[2])/abs(A[2]-B[2])))
        return findway(A,B,move)            
    else:
        movx=((B[1]-A[1])/abs(A[1]-B[1]),0)
        move1=[copy.copy(move),movx]
        movy=(0,(B[2]-A[2])/abs(A[2]-B[2]))
        move2=[copy.copy(move),movy]
        return [findway(A,B,move1),findway(A,B,move2)]
        # me sort un truc très moche, c'est à dire tout les itinéraires (GENIAL!), mais dans des listes de listes de listes... Avec chaque itinéraire écrit différemment du précédent quasiment   
def extracttuple(move,e=[]):
    for ordre in move:
        if type(ordre)==tuple:
            e.append(ordre)
        else:
            extracttuple(ordre,e)
    return e
        # m'extrait touts les tuples (càd commande) pour me les mettre dans une belle liste unique            
def giveway(start,end,move):
    way=[move[i:i+abs(start[2]-end[2])+abs(start[1]-end[1])] for i in range(0,len(move), abs(start[2]-end[2])+abs(start[1]-end[1]))]
    return way
        # me sépare enfin chaque itinéraire sachant que ce dernier comprend toujours le même nombre de case

#   calcul meilleur action pour un assassin
def bestkill(killer,ways,state,pa):
    cost,health,knight,command=[],[],[],[]    
    for way in ways:
        x0,y0,z0=killer[1],killer[2],killer[3]
        knight.append(0)
        cost.append(0)
        health.append(0)
        command.append([('reveal', x0, y0)])
        for ordre in way:
            x1,y1=int(x0+ordre[0]),int(y0+ordre[1])
            z1,people=state['board'][x1][y1],state['people'][x1][y1]
            if people not in {'knight','king',None}:
                cost[-1]=1000
                break
            elif people=='king':
                cost[-1]+=2
                health[-1]+=1
                command[-1].append(('attack', x0, y0, direction(ordre)))
                if pa-cost[-1]>1:
                    cost[-1]+=2
                    health[-1]+=1
                    command[-1].append(('attack', x0, y0, direction(ordre)))
            elif people=='knight':
                if z1=='R' and z0=='G':
                    cost[-1]=1000
                else:
                    cost[-1]+=2+knight[-1]
                    knight[-1]+=1
                    command[-1].append(('kill', x0, y0, direction(ordre)))
                    command[-1].append(('move', x0, y0, direction(ordre)))
            elif people==None:
                if not(z1=='G' and z0=='R'):
                    cost[-1]+=1
                    command[-1].append(('move', x0, y0, direction(ordre)))
                else:
                    command[-1].append(('move', x0, y0, direction(ordre)))
            x0,y0,z0=x1,y1,z1
    while max(cost)>pa:
        i=cost.index(max(cost))
        del cost[i]
        del ways[i]
        del health[i]
        del knight[i]
        del command[i]
        if len(cost)==0:
            break
    if len(cost)==0:
        return -1,-1,-1,-1,-1
    if max(health)>0:
        while min(health)!=max(health):
            i=health.index(min(health))
            del cost[i]
            del ways[i]
            del health[i]
            del knight[i]
            del command[i]
        while min(knight)!=max(knight):
            i=knight.index(min(knight))
            del cost[i]
            del ways[i]
            del health[i]
            del knight[i]
            del command[i]
        command,ways,cost,health,knight=command[0],ways[0],cost[0],health[0],knight[0]
    else:
        return -1,-1,-1,-1,-1
    return command,ways,cost,health,knight

#   détermine quelle assassin choisir pour attaquer le roi
def time2kill(maybekiller,king,state,paV):
    actions,way,cost,health,knight=[],[],[],[],[]
    for killer in maybekiller:
        ways=giveway(killer,king,extracttuple(findway(killer,king),[]))
        a,w,c,h,k=bestkill(killer,ways,state,paV)
        way.append(w)
        cost.append(c)
        health.append(h)
        knight.append(k)
        actions.append(a)
    while min(health)!=max(health):
        i=health.index(min(health))
        del maybekiller[i]
        del cost[i]
        del way[i]
        del health[i]
        del knight[i]
        del actions[i]
    while min(knight)!=max(knight):
        i=knight.index(min(knight))
        del maybekiller[i]
        del cost[i]
        del way[i]
        del health[i]
        del knight[i]
        del actions[i]
    Killer,Way,cost,Health,Knight,actions=maybekiller[0],way[0],cost[0],health[0],knight[0],actions[0]
    return actions,cost

                #   ----------------------
                #           KING
                #   ----------------------

                #   ----------------------
                #           BOTH
                #   ----------------------

#   trouve mes pions
def findtroops(state,troops):
    mytroops=[]
    for i in range(10):
        for j in range(10):
            if state['people'][i][j] in troops:
                mytroops.append([state['people'][i][j],i,j,state['board'][i][j]])
            elif state['people'][i][j]=='king':
                king=[state['people'][i][j],i,j]
    return mytroops,king

#   déplacements aléatoires 
def randommove(group,pa,obj,state,myactions,opp,imax):
    
    it=0
    d=['N','W','S','E']
    z=[1,1,-1,-1]
    i=[1,2,1,2]
    x=[-1,0,1,0]
    y=[0,-1,0,1]
    while pa>0 and it<imax:
        g=random.choice(range(len(group)))
        for j in range(4):
            if z[j]*group[g][i[j]]>z[j]*obj[i[j]]:
                if state['people'][group[g][1]+x[j]][group[g][2]+y[j]] in opp:                    
                    if group[g][3]=='R':
                        myactions.append(('move',group[g][1],group[g][2],d[j]))                        
                        state['people'][group[g][1]][group[g][2]]=None
                        state['people'][group[g][1]+x[j]][group[g][2]+y[j]]=group[g][0]
                        group[g][i[j]]+=x[j]+y[j]
                        pa+=-1
                    elif group[g][3]=='G' and state['board'][group[g][1]+x[j]][group[g][2]+y[j]]=='G':
                        myactions.append(('move',group[g][1],group[g][2],d[j]))                        
                        state['people'][group[g][1]][group[g][2]]=None
                        state['people'][group[g][1]+x[j]][group[g][2]+y[j]]=group[g][0]
                        group[g][i[j]]+=x[j]+y[j]
                        pa+=-1
                    elif pa>1:
                        myactions.append(('move',group[g][1],group[g][2],d[j]))                        
                        state['people'][group[g][1]][group[g][2]]=None
                        state['people'][group[g][1]+x[j]][group[g][2]+y[j]]=group[g][0]
                        group[g][i[j]]+=x[j]+y[j]
                        pa+=-2
        it+=1
    return state,myactions

#   transforme vecteur xy en une direction cartographique
def direction(v):
    if v==(1,0):
        return 'S'
    elif v==(-1,0):
        return 'N'
    elif v==(0,1):
        return 'E'
    else:
        return 'W'
