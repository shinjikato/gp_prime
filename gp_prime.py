import operator
import math
import random
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt


class Tree(list):
    def __init__(self,content):
        list.__init__(self,content)
        self.fitness = None
    @property
    def height(self):
        stack = [0]
        max_depth = 0
        for elem in self:
            depth = stack.pop()
            max_depth = max(max_depth, depth)
            stack.extend([depth+1] * elem[2])
        return max_depth
    def searchSubtree(self, begin):
        end = begin + 1
        total = self[begin][2]
        while total > 0:
            total += self[end][2] - 1
            end += 1
        return slice(begin, end)
    def __str__(self):
        start = 0
        str_arr = [""]
        for node in self:
            for i in range(len(str_arr)):
                if str_arr[i] == "":
                    name,func,arity = node
                    if arity != 0:
                        tmp_arr = [name,"(",""]
                        for x in range(arity-1):
                            tmp_arr += [",",""]
                        tmp_arr.append(")")
                        str_arr = str_arr[:i] + tmp_arr + str_arr[i+1:]
                    else:
                        str_arr = str_arr[:i] + [name] + str_arr[i+1:]
                    break
        return "".join(str_arr)

def makePrimeNumbers(len_numbers):
    primes = [2, 3]
    n = 5
    while len(primes) < len_numbers:
        isprime = True
        for i in range(1, len(primes)):
            if primes[i] ** 2 > n:
                break
            if n % primes[i] == 0:
                isprime = False
                break
        if isprime:
            primes.append(n)
        n += 2
    return primes

def protectedDiv(left, right):
    with np.errstate(divide='ignore',invalid='ignore'):
        y = np.divide(left, right)
        if isinstance(y, np.ndarray):
            y[np.isinf(y)] = 1
            y[np.isnan(y)] = 1
        elif np.isinf(y) or np.isnan(y):
            y = 1
    return y

def protectedPower(left,right):
    with np.errstate(over='ignore',invalid='ignore'):
        y = np.power(left, right)
        if isinstance(y, np.ndarray):
            y[np.isinf(y)] = 1
            y[np.isnan(y)] = 1
        elif np.isinf(y) or np.isnan(y):
            y = 1
    return y

def makeNodeSet():
    nodeSet = []
    leafSet = []
    nodeSet.append(("add",np.add,2))
    nodeSet.append(("sub",np.subtract,2))
    nodeSet.append(("mul",np.multiply,2))
    nodeSet.append(("div",protectedDiv,2))
    #nodeSet.append(("pow",np.power,2))
    nodeSet.append(("sin",np.sin,1))
    nodeSet.append(("cos",np.cos,1))
    nodeSet.append(("tan",np.tan,1))
    nodeSet.append(("log",np.log,1))
    nodeSet.append(("exp",np.exp,1))
    nodeSet.append(("sqrt",np.sqrt,1))

    leafSet.append(("-1",1,0))
    leafSet.append(("0",0,0))
    leafSet.append(("1",1,0))
    leafSet.append(("0.5",0.5,0))
    leafSet.append(("0.1",0.1,0))
    leafSet.append(("pi",np.pi,0))
    leafSet.append(("e",np.e,0))
    leafSet.append(("x",None,0))

    return nodeSet,leafSet

def randomTreeMake(nodeSet,leafSet,_min,_max):
    height = random.randint(_min,_max)
    items = []
    stack = [0]
    while len(stack) != 0:
        depth = stack.pop()
        if depth == height:
            node = random.choice(leafSet)
        else:
            node = random.choice(nodeSet)
            stack.extend([depth+1]*node[2])
        items.append(node)
    tree = Tree(items)
    return tree

def get_y(tree,nodeSet,leafSet,x):
    stack = []
    for node in tree[::-1]:
        name,func,arity = node
        if name == "x":
            output = x
        else:
            if arity == 0:
                output = func*np.ones(x.shape[0])
            if arity == 1:
                outout = func(stack.pop())
            if arity == 2:
                output = func(stack.pop(),stack.pop())
        stack.append(output)
    return stack.pop()

def mate(tree1,tree2,limit,limMode):
    save1 = deepcopy(tree1)
    save2 = deepcopy(tree2)
    while True:
        index1 = random.randint(1,len(tree1)-1)
        index2 = random.randint(1,len(tree2)-1)
        slice1 = tree1.searchSubtree(index1)
        slice2 = tree2.searchSubtree(index2)
        tree1[slice1],tree2[slice2] = tree2[slice2],tree1[slice1]
        if limMode == "LENGTH":
            if len(tree1) <= limit and len(tree2) <= limit:
                return tree1,tree2
        elif limMode == "HEIGHT":
            if tree1.height <= limit and tree2.height <= limit:
                return tree1,tree2
        else:
            return tree1,tree2
        tree1,tree2 = deepcopy(save1),deepcopy(save2)

def mutate(tree,NodeSet,leafSet,limit,limMode):
    save = deepcopy(tree)
    while True:
        index = random.randrange(len(tree))
        slice_ = tree.searchSubtree(index)
        tree[slice_] = randomTreeMake(NodeSet,leafSet,1,2)
        if limMode == "LENGTH":
            if len(tree) <= limit:
                return tree
        elif limMode == "HEIGHT":
            if tree.height <= limit:
                return tree
        else:
            return tree
        tree = deepcopy(save)

def initial_population(N,nodeSet,leafSet,_min,_max):
    population = []
    for n in range(N):
        tree = randomTreeMake(nodeSet,leafSet,_min,_max)
        population.append(tree)
    return population

def evaluate(population,nodeSet,leafSet,x,y):
    for tree in population:
        if tree.fitness == None:
            _y = get_y(tree,nodeSet,leafSet,x)
            fitness = np.sum(np.abs(_y - y))
            tree.fitness = fitness

def select(population,M):
    new_population = []
    for i in range(len(population)):
        sub_population = random.sample(population,M)
        best = min(sub_population,key=lambda tree:tree.fitness)
        new_population.append(deepcopy(best))
    return new_population

def crossover(population,Pcx):
    random.shuffle(population)
    for i in range(int(len(population)/2)):
        if random.random() < Pcx:
            childA = population[2*i]
            childB = population[2*i+1]
            childA,childB = mate(childA,childB,17,"HEIGHT")
            population[2*i] = deepcopy(childA)
            population[2*i+1] = deepcopy(childB)
            population[2*i].fitness = None
            population[2*i+1].fitness = None
    return population

def mutation(population,Pmut,nodeSet,leafSet):
    random.shuffle(population)
    for i in range(len(population)):
        if random.random() < Pmut:
            child = population[i]
            child = mutate(child,nodeSet,leafSet,17,"HEIGHT")
            population[i] = deepcopy(child)
            population[i].fitness = None

    return population

def printLog(population,g):
    key=lambda tree:tree.fitness
    worst = max(population,key=key)
    best = min(population,key=key)
    ave = sum([tree.fitness for tree in population])/len(population)
    key=lambda tree:len(tree)
    max_node = len(max(population,key=key))
    min_node = len(min(population,key=key))
    ave_node = sum([len(tree) for tree in population])/len(population)
    print("===========",g,"genelation===========")
    print("worst fitness : ",worst.fitness,"  max nodes : ",max_node)
    print("ave   fitness : ",ave          ,"  ave nodes : ",ave_node)
    print("best  fitness : ",best.fitness, "  min nodes : ",min_node)

def makeGraph(tree,x,y,nodeSet,leafSet):
    _y = get_y(tree,nodeSet,leafSet,x)
    plt.plot(x,y,label="true prime number")
    plt.plot(x,_y,label="gp prime number")
    plt.legend(loc="upper left")
    plt.savefig("test.pdf")

def main():
    N = 1000
    M = 7
    maxG = 500
    Pcx = 0.5
    Pmut = 0.1
    nodeSet,leafSet = makeNodeSet()
    x = np.array(range(1,10))
    y = np.array(makePrimeNumbers(x.shape[0]))

    population = initial_population(N,nodeSet,leafSet,1,2)
    g = 0
    while True:
        evaluate(population,nodeSet,leafSet,x,y)
        printLog(population,g)
        if g == maxG:
            break
        population = select(population,M)
        population = crossover(population,Pcx)
        population = mutation(population,Pmut,nodeSet,leafSet)
        g+=1
    best = min(population,key=lambda tree:tree.fitness)
    print(best)
    makeGraph(best,x,y,nodeSet,leafSet)

main()
