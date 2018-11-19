"""
An implementation of N.E.A.T. in Python
Created by Nicholas Julien
"""

import random, copy, math

def sigmoid(x):
    return 1 / (1+math.exp(-x))

class Population:
    genomes = []
    species = []
    innovation = 0
    innovations = []
    
    def __init__(self, populationSize, numInputs = 0, numOutputs = 0, speciationTreshold = 0.2):
        self.speciationTreshold = speciationTreshold
        for i in range(populationSize):
            self.genomes.append(Genome(self,numInputs, numOutputs))

    def addInnovation(self, inNodeID, outNodeID):
        for innov in self.innovations:
            if inNodeID==innov.inNodeID and outNodeID==innov.outNodeID:
                return innov.num
        self.innovation+=1
        self.innovations.append(Innovation(self.innovation, inNodeID, outNodeID))
        return -1

class Entity:

    def __init__(self, genome):
        

class Innovation:
    def __init__(self, num, inNodeID, outNodeID):
        self.num = num
        self.inNodeID=inNodeID
        self.outNodeID=outNodeID
class Species:
    def __init__(self, rep):
        self.rep = rep

class Genome:
    def __init__(self, population, numInputs=0, numOutputs=0):
        self.population = population
        self.nodeGenes = []
        self.connectionGenes = []
        self.nodeNum = 0
        for i in range(numInputs):
            self.nodeGenes.append(Node("input",self.nodeNum,0))
            self.nodeNum+=1
        for i in range(numOutputs):
            self.nodeGenes.append(Node("output",self.nodeNum,1))
            self.nodeNum+=1
        for node1 in self.nodeGenes:
            if node1.nodeType == "input":
                for node2 in self.nodeGenes:
                    if node2.nodeType == "output":
                        self.add_connection(node1.nodeID, node2.nodeID)

    #Testing functions
    def printOut(self):
        """print("Nodes:")
        for node in self.nodeGenes:
            print(node)
        for gene in self.connectionGenes:
            print(gene)"""
        print("====Genome====")
        for node in self.nodeGenes:
            print(node)
            for connection in self.connectionGenes:
                if connection.inNode==node.nodeID:
                    print("  ",connection)
        
            
    #Mutation functions
    def mutate(self, connectionChance, nodeChance, weightChance):
        if random.random() < connectionChance:
            inNode = random.choice(self.nodeGenes)
            outNode = random.choice(self.nodeGenes)
            if outNode.nodeType=="input" or inNode.nodeType=="output":
                tmp = outNode
                outNode = inNode
                inNode = tmp
            if outNode.nodeType!="input" and inNode.nodeType!="output" and not self.hasConnection(inNode.nodeID, outNode.nodeID):
                self.add_connection(inNode.nodeID, outNode.nodeID)
        if random.random() < nodeChance and len(self.connectionGenes)>0:
            self.add_node(random.choice(self.connectionGenes))
        if random.random() < weightChance:
            for connection in self.connectionGenes:
                self.modify_weight(connection)
    def add_connection(self, inNode, outNode):
        innovation = self.population.addInnovation(inNode, outNode)
        self.connectionGenes.append(Connection(inNode, outNode, random.random()*2.0-1.0, True, (self.getNodeFromID(inNode).splitY>self.getNodeFromID(outNode).splitY), self.population.innovation if innovation == -1 else innovation))
    def add_node(self, connection):
        if connection.recurrent:
            return
        startNode = self.getNodeFromID(connection.inNode)
        endNode = self.getNodeFromID(connection.outNode)
        newNode = Node("hidden",self.nodeNum,startNode.splitY+endNode.splitY/2)
        self.nodeNum+=1
        self.nodeGenes.append(newNode)
        connection.disable()
        innovation = self.population.addInnovation(startNode.nodeID, newNode.nodeID)
        startToNew = Connection(startNode.nodeID, newNode.nodeID, 1, True, False, self.population.innovation if innovation == -1 else innovation)
        innovation = self.population.addInnovation(newNode.nodeID, endNode.nodeID)
        newToEnd = Connection(newNode.nodeID, endNode.nodeID, connection.weight, True, False, self.population.innovation if innovation == -1 else innovation)
        self.connectionGenes.append(startToNew)
        self.connectionGenes.append(newToEnd)
    def modify_weight(self, connection):
        if random.random() < 0.1:
            connection.weight = random.random()*2.0-1.0
        else:
            connection.weight+=random.gauss(0,0.05)
    #Utility Functions
    def getNodeFromID(self, nodeID):
        for node in self.nodeGenes:
            if node.nodeID == nodeID:
                return node
        return False
    def getDistance(self, genome, c1=1, c2=1, c3=1):
        matched = []
        numMatching = 0
        numExcess = 0
        numDisjoint = 0
        n = len(self.nodeGenes) if len(self.nodeGenes) > len(genome.nodeGenes) else len(genome.nodeGenes)
        weightDifferenceSum=0
        for gene in self.connectionGenes:
            matching = False
            for gene2 in genome.connectionGenes:
                if gene.innovation == gene2.innovation:
                    weightDifferenceSum+=gene.weight-gene2.weight
                    numMatching+=1
                    matching = True
                    matched.append(gene2)
            if not matching:
                if gene.innovation<genome.connectionGenes[-1].innovation:
                    numDisjoint+=1
                else:
                    numExcess+=1
        for gene in genome.connectionGenes:
            if gene not in matched:
                if gene.innovation<self.connectionGenes[-1].innovation:
                    numDisjoint+=1
                else:
                    numExcess+=1
        delta = c1*(numExcess/n)+c2*(numDisjoint/n)+c3*((weightDifferenceSum/numMatching) if numMatching != 0 else 0)
        return delta

    def getDepth(self):
        seen = []
        for node in self.nodeGenes:
            if node.splitY not in seen:
                seen.append(node.splitY)
        return len(seen)
    
    def hasConnection(self, node1, node2):
        for connection in self.connectionGenes:
            if (connection.inNode == node1 and connection.outNode == node2) or (connection.inNode == node2 and connection.outNode == node1):
                return True
        return False
    
    def clone(self):
        ret = Genome(self.population)
        ret.nodeNum = self.nodeNum
        ret.nodeGenes = copy.deepcopy(self.nodeGenes)
        ret.connectionGenes = copy.deepcopy(self.connectionGenes)
        return ret
    
class Connection:
    def __init__(self, inNode, outNode, weight, expressed, recurrent, innovation):
        self.inNode = inNode
        self.outNode = outNode
        self.weight = weight
        self.expressed = expressed
        self.recurrent = recurrent
        self.innovation = innovation

    def __str__(self):
        return '%s: %s -(%s)-> %s' % (self.innovation, self.inNode, self.weight if self.expressed else "disabled", self.outNode)
        
    def disable(self):
        self.expressed = False

class Node:
    def __init__(self,nodeType,nodeID,splitY):
        self.nodeType = nodeType
        self.nodeID = nodeID
        self.splitY = splitY
    def __str__(self):
        return '%s(%s at %s)' % (self.nodeID, self.nodeType,self.splitY)

def crossover_genomes(g1,g2,sameFit=False):
    child = Genome(g1.population)
    child.nodeNum = g1.nodeNum
    child.nodeGenes = copy.deepcopy(g1.nodeGenes)
    for connection in g1.connectionGenes:
        matching = False
        for connection2 in g2.connectionGenes:
            if connection.innovation == connection2.innovation:
                matching = True
                if random.random() < .5:
                    child.connectionGenes.append(copy.deepcopy(connection))
                else:
                    child.connectionGenes.append(copy.deepcopy(connection2))
        if not matching:
            #We can calculate if this is excess or disjoint later
            child.connectionGenes.append(copy.deepcopy(connection))
    return child

"""Neural Network"""
def genomeToNN(genome):
    neurons = []
    for node in genome.nodeGenes:
        neurons.append(Neuron(node.nodeType, node.nodeID))
    for connection in genome.connectionGenes:
        if connection.expressed:
            startNeuron = 0
            endNeuron = 0
            for neuron in neurons:
                if neuron.neuronID==connection.inNode:
                    startNeuron = neuron
                if neuron.neuronID==connection.outNode:
                    endNeuron = neuron
                if startNeuron!=0 and endNeuron!=0:
                    break
            syn = Synapse(startNeuron, endNeuron, connection.weight, connection.recurrent)
            startNeuron.outputSynapses.append(syn)
            endNeuron.inputSynapses.append(syn)
    return NeuralNetwork(neurons, genome.getDepth())
                    

class NeuralNetwork:
    def __init__(self, neurons, depth):
        self.neurons = neurons
        self.depth = depth
    def update(self, inputs):
        outputs = []
        for i in range(self.depth):
            outputs = []
            j=0
            for neuron in self.neurons:
               if neuron.neuronType == "input":
                   neuron.value = inputs[j]
                   j+=1
               else:
                   neuron.activate()
               if neuron.neuronType == "output":
                   outputs.append(neuron.value)
        return outputs
        
class Neuron:
    def __init__(self, neuronType, neuronID):
        self.inputSynapses = []
        self.outputSynapses = []
        self.value = 0
        self.neuronType = neuronType
        self.neuronID = neuronID
    def activate(self):
        sumWeighted=0
        for synapse in self.inputSynapses:
            sumWeighted+=synapse.weight*synapse.startNeuron.value
        self.value = sigmoid(sumWeighted)

class Synapse:
    def __init__(self, startNeuron, endNeuron, weight, recurrent):
        self.startNeuron = startNeuron
        self.endNeuron = endNeuron
        self.weight = weight
        self.recurrent = recurrent

