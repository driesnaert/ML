import copy
import sys

'''
preprocess(data[string],delimeter[list of chars],strIndicator[list of chars],emptyValues[list],ignoreLines[list],ignoreColumns[list],x)
--> returnt een NumpyArray

Elke lijn van de file 'data' wordt ingelezen en gesplitst volgens de delimeterkarakters (tenzij een delimeter tussen 2 strIndicators staat).
Van elke lijn wordt eerst uitgemaakt of die numeriek (alle waarden uitgezonder de missing waarden zijn getallen) of categorisch is.
opm.: als een numerieke waarde minder dan x procent unieke waarden heeft wordt die toch behandeld als een categorische variabele.
opm.: lijnen met index in ignoreLines worden 'weggegooid'.
opm.: na splitsen worden de kolommen in ignoreColumns gewist

Voor een categorische variabele met n waarden, wordt er n-1 binaire kolommen gemaakt.
Vb.: y neemt waarden A,B of C aan.
Als y = A --> [1,0], als y = B --> [0,1], als y = C --> [0,0]
Voor een numerieke variabele wordt 1 kolom gemaakt en de waarde gekopieerd.

Vervolgens wordt de data zonder missing values gebruikt om de missing values te voorspellen met een regressiemodel.
Opm.: bij categorische data wordt de output van het regressiemodel herschaald zodat de getallen een probabilistische interpretatie krijgen
'''

'''
    readData(data[string],delimeter[list of chars],strIndicator[list of chars],ignoreLines[list],ignoreColumns[list])
    leest het bestand 'data' in en returnt een tabel van strings
    doel: lees de data in, splits de lijnen en vergeet de kolommen en lijnen die niet nodig zijn

    hulpfuncties: 
        1. splitLijn(string,d,s,[],"",False): recursieve functie die een string splitst en een lijst van strings returnt
        2. removeIndices(lijst,indices[lijst van ints]) verwijdert alle elementen met een index die voorkomt in de lijst 'indices'
'''


def readData(data,delimeter,strIndicator,ignoreLines,ignoreColumns):
    f = open(data,'r')
    ret = []
    for i, lijn in enumerate(f):
        if i in ignoreLines:
            continue
        else:
            temp = splitLijn(lijn,delimeter,strIndicator,[],"",False)
            temp = removeIndices(temp,ignoreColumns)
            ret.append(temp)
    return ret

def removeIndices(lijst,indices):
    ret = []
    for i, item in enumerate(lijst):
        if i in indices:
            continue
        else:
            ret.append(item)
    return ret
   
           
def splitLijn(string,d,s,lijnArray,entry,inString):
    if not '\n' in d:
        temp1 = copy.deepcopy(d)
        temp1.append('\n')
        return splitLijn(string,temp1,s,lijnArray,entry,inString)
    if len(string) == 0:
        return lijnArray
    if string[0] in s:
        return splitLijn(string[1:],d,s,lijnArray,entry,not inString)
    if string[0] in d:
        temp1 = copy.deepcopy(lijnArray)
        temp2 = copy.deepcopy(entry)
        if inString:
            temp2 = temp2 + string[0]
            return splitLijn(string[1:],d,s,temp1,temp2,inString)
        else:
            temp1.append(entry)
            return splitLijn(string[1:],d,s,temp1,"",inString)
    else:
        temp1 = copy.deepcopy(lijnArray)
        temp2 = copy.deepcopy(entry)
        temp2 = temp2 + string[0]
        return splitLijn(string[1:],d,s,temp1,temp2,inString)
 

'''
    masterData(data[tabel van strings],delimeter[list of chars],strIndicator[list of chars],emptyValues[list],ignoreLines[list],ignoreColumns[list])
    is de tweede functie die opgeroepen wordt en het resultaat wordt doorgegeven aan elke functie die verder wordt opgeroepen.

    returnt in een lijst met als elementen:
        return[0]: een tabel (woordenboek) met op de rijen alle unieke elementen per kolom in data.
        return[1]: een binaire lijst, als return[1][n] True is, wil dit zeggen dat de n-de kolom enkel numerieke waarden heeft (missing niet meegerekend)
    return[2]: een lijst met fracties, op de n-de plaats staat het percentage unieke waarden de n-de kolom heeft.
     opm.: percentage unieke waarden --> als een kolom 100 entries heeft en 12 unieke waarden, is het percentage unieke waarden 12
    return[3]: lijst van lijnen die empty waarden heeft

    hulpfuncties:
        1. isNumeric(entry[string],emptyList[lijst met chars]): True als entry can geconverteerd worden naar een float of entry in emptyList zit
'''
def isNumeric(s,e):
    if s in e:
        return True
    else:
        try:
            float(s)
            return True
        except ValueError:
            return False

def masterData(tabel, delimeter, strIndicator, emptyValues, ignoreLines, ignoreColumns):
    
    woordenboek = [[] for j in range(len(tabel[0]))] 
    for row in tabel:
        for i, entry in enumerate(row):
            if (not (entry in woordenboek[i])) and (not (entry in emptyValues)):
                woordenboek[i].append(entry)

    aantalUnieke = []
                
    numericColumns = [True] * len(tabel[0])
    legeLijnen = []
    for j,rij in enumerate(tabel):
        for i, entry in enumerate(rij):
            if not isNumeric(entry,emptyValues):
                numericColumns[i] = False
            if ((entry in emptyValues) and (j not in legeLijnen)):
                legeLijnen.append(j)
        
    return [woordenboek,numericColumns,aantalUnieke,legeLijnen]
        
'''
    splitData(tabel,masterdata): tabel is een tabel van strings, masterdata is de return van de functie masterdata opgeroepen in de 2e functie.
    returnt 2 tabellen met numerieke waarden. De tabel van strings wordt gesplitst in 2 tabellen met enkel numerieke waarden:
    1 met missing values en 1 zonder.
    Missing values worden op False gezet (alle kolommen voor categorische missings)
    Voor  categorische variabelen worden extra binaire kolommen gemaak
    !!!voor een categorische variabele die n waarden kan aannemen, worden er hier nog n kolommen aangemaakt,
       dit terwijl de output van de main functie maar n-1 kolommen zal hebben voor n mogelijke waarden!!!
    numerieke waarden met een lager dan 'x' percentage aan unieke waarden worden behandeld als categorische variabelen

    hulpfuncties:
        1. maakEntryNumeriek(entry,kolom,masterdata): als entry missing --> False
                                                          entry numeriek --> getal
                                                          entry categorisch --> lijst met nullen en 1.
'''
def splitData(tabel,masterdata,emptyValues):
    cleanData = []
    nonCleanData = []
    for i, rij in enumerate(tabel):
        rijToAdd = []
        for j, entry in enumerate(rij):
            ent = maakEntryNumeriek(entry,j,masterdata,emptyValues)
            for item in ent:
                rijToAdd.append(item)
            
        if i in masterdata[3]:
        # rij heeft empty
            nonCleanData.append(rijToAdd)
        else:
            cleanData.append(rijToAdd)
    print 'clean data:'
    print cleanData
    print 'niet clean:'
    print nonCleanData
    return [cleanData,nonCleanData]    

                
            
def maakEntryNumeriek(entry,kolom,masterdata,emptyValues):
    if masterdata[1][kolom]:
        if entry in emptyValues:
            return [False]
        else:
            return [float(entry)]
    else:
        ret = [0]*len(masterdata[0][kolom])
        if entry in emptyValues:
            return [False]*len(masterdata[0][kolom])
        else:
            index = masterdata[0][kolom].index(entry)
            ret[index] = 1
            return ret
                
        
        
        


tabel = readData('test.csv',[','],['"'],[0],[2])
masterdata = masterData(tabel,[],[],[''],[],[])
print 'woordenboek:'
print masterdata[0]
splitData(tabel,masterdata,[''])
