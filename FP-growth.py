from _collections import defaultdict
from audioop import reverse
from itertools import combinations

''' Read the data.txt and then set the data format like:
    items = [{A,B,C},{B,C,D},...]
'''
def readData(fileName):
    TDB = dict();
    items = [];
    with open(fileName, "r") as file:
        for line in file.readlines():
            data = line.strip().split();
            for i in range(len(data)):
                data[i] = int(data[i]);
            if(TDB.get(data[1])):
                TDB[data[1]].append(data[2]);
            else:
                TDB[data[1]] = [data[2]];
    for value in TDB.values():
        items.append(set(value));
    return items;

''' sortFreqSup { item:freq, item:freq,....}
    left the item whose frequence is bigger than minimumSup
'''
def cleanNsort(items, minimumSup):
    # count each item's frequence
    itemFreq = defaultdict(int);
    for trans in items:
        for item in trans:
            itemFreq[item] += 1;
    freqSup = dict();
    for item, sup in itemFreq.items():
        if(sup >= minimumSup):
            freqSup[item] = sup;
    sortFreqSup = dict(sorted(freqSup.items(),
                              key=lambda item: item[1],
                              reverse=True));
    return sortFreqSup;

''' orderItems [ item, item, item, ....]
    eliminate items which not in the sortedFreqSup
    and order each items as sortedFreqSup's order
    See details P.51
'''
def orderItemByFreq(items, sortFreqSup):
    orderItems = [];

    for trans in items:
        tmpItem = [];
        for item in sortFreqSup.keys():
            if(item in trans):
                tmpItem.append(item);
        if(len(tmpItem) > 0):
            orderItems.append(tmpItem);
    return orderItems;

''' headerTable 
    { item:[freq, treeNode], 
      item:[freq, treeNode],
      ....
    }
'''
def createHeaderTable(sortFreqSup):
    headerTable = dict();
    for item, freq in sortFreqSup.items():
        headerTable[item] = [freq, None];
    return headerTable;


def constructTree(orderedItems, headerTable):
    root = TreeNode("NULL", 0, None);
    
    for items in orderedItems:
        # a pointer for pointing current node
        pointer = root;
        for item in items:
            if(item not in pointer.children.keys()):
                childNode = TreeNode(item, 0, pointer);
                pointer.addChild(childNode);
                pointer = childNode;
                # refresh headerTable if the node hasn't defined
                if(headerTable[item][1] is None):
                    headerTable[item][1] = childNode;
                # if the node has already defined, trace down the next same item node
                else:
                    updateNextSame(headerTable[item][1], childNode);
            else:
                pointer = pointer.children[item];
            pointer.addFreq();
    return root;


def updateNextSame(treeNode, nextSameNode):
    while treeNode.nextSame is not None:
        treeNode = treeNode.nextSame;
    treeNode.nextSame = nextSameNode;


def mineFPTree(headerTable):
    freqPatterns = dict();
    
    for item, value in headerTable.items():
        # print(item, value[0], value[1]);
        # get each item's node independently ex: [node(f),node(f),...]
        sameNodeList = getSameNodeList(value[1]);
        
        condPatternBase = [];
        patternFreq = 0;
        for treeNode in sameNodeList:
            path = traceUpTree(treeNode);
            if(len(path) > 0):
                patternBase = fromPath2PatternBase(path)
                condPatternBase.append(patternBase);
                patternFreq += treeNode.freq;
        
        condFPTrees = set();
        if(len(condPatternBase) > 0):
            condFPTrees.update(condPatternBase[0]);
            for patternBase in condPatternBase:
                condFPTrees = condFPTrees.intersection(patternBase);
        
        # for all sub-set of condFPTrees
        for el in range(len(condFPTrees)):
            for freEl in combinations(condFPTrees, el):
                freEl = set(freEl);
                freqPattern = freEl.union(set([item]));
                freqPatterns[frozenset(freqPattern)] = patternFreq;
        # for condFPTrees
        freqPattern = condFPTrees.union(set([item]));
        freqPatterns[frozenset(freqPattern)] = patternFreq;
    return freqPatterns;


def getSameNodeList(treeNode):
    nodeList = [treeNode];
    while(treeNode.nextSame is not None):
        nodeList.append(treeNode.nextSame);
        treeNode = treeNode.nextSame;
    return nodeList;


def traceUpTree(treeNode):
    path = [];
    while treeNode.parent is not None:
        path.append(treeNode);
        treeNode = treeNode.parent;
    return path;


def fromPath2PatternBase(path):
    patternBase = set();
    for node in path:
        patternBase.add(node.item);
    return patternBase;


def generateRules(freqPatterns, minConfidence):
    rules = [];
    for pattern, freq in freqPatterns.items():
        if(len(pattern) > 1):
            for i in range(1, len(pattern)):
                for j in combinations(pattern, i):
                    if(freqPatterns.get(frozenset(j))):
                        confidence = freq / freqPatterns.get(frozenset(j));
                        rule = (frozenset(j), pattern - frozenset(j), confidence);
                        if(confidence >= minConfidence):
                            rules.append(rule);
    return rules;


class TreeNode:

    def __init__(self, item, freq, parent):
        self.item = item;
        self.freq = freq;
        self.parent = parent;  # parent node
        self.nextSame = None;  # the next same item node
        self.children = dict();  # children's dict
        
    def addFreq(self):
        self.freq += 1;
        
    def addChild(self, treeNode):
        self.children[treeNode.item] = treeNode;

    
if __name__ == '__main__':
    # init
    dataFile = "data.txt";
    # dataFile = "winequalityN.txt";
    minimumSup = 50;
    minConfidence = 0.8;

    items = readData(dataFile);

    sortFreqSup = cleanNsort(items, minimumSup);

    orderItems = orderItemByFreq(items, sortFreqSup);
    
    headerTable = createHeaderTable(sortFreqSup);
    fpTree = constructTree(orderItems, headerTable);
    freqPatterns = mineFPTree(headerTable);
    
    print("Frequent patterns:");
    for pattern, freq in freqPatterns.items():
        if(len(pattern) > 1):
            print(list(pattern), freq);
    
    print("Association rules:");
    for rule in generateRules(freqPatterns, minConfidence):
        print(list(rule[0]), "=>", list(rule[1]), "confidence", rule[2]);
