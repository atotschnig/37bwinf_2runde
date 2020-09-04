import numpy as np
import math

dateiname = input("Dateiname : ")
datei = open(dateiname+".txt").read().split('\n')

# Überprüfung ob Eckpunkte rechtsherum angegeben werden
def rechtsherum(polygon) :
    summe = 0
    seiten = len(polygon)
    for i in range(seiten) :
        p1, p2 = knoten[polygon[i]], knoten[polygon[(i+1)%seiten]]
        summe += p1[0]*p2[1] - p2[0]*p1[1]
    if summe > 0 : # linksherum
        polygon.reverse()
    return polygon

# Einlesen der Polygone und der Koordinaten des Haus
anzahlPolygone = int(datei[0])
polygone = [0] * anzahlPolygone
knoten, kanten = [], []
bereits = 0 
for i in range(anzahlPolygone) :
    eingabe = list(map(int, datei[i+1].split(" ")))
    seiten = eingabe[0]
    for j in range(seiten) :
        knoten.append([eingabe[2*j+1],eingabe[2*j+2],i])
        p1 = bereits + j
        p2 = bereits + (j+1) % seiten
        kanten.append(sorted([p1,p2]))
    polygone[i] = rechtsherum(list(range(bereits, bereits+seiten)))
    bereits += seiten
haus = list(map(int, datei[-1].split(" ")))
knoten.append(haus + [-1])
anzahlKnoten = len(knoten)
maxx = max(knoten, key=lambda x: x[0])[0]


# gibt zwei Nachbar-Eckpunkte auf dem selben Polygon zurück
def verbunden(k) :
    nachbar = []
    if k == anzahlKnoten-1 : # Haus hat keinen Nachbarn
        return nachbar
    polygon = polygone[knoten[k][2]]
    for i in range(len(polygon)) :
        if polygon[i] == k :
            nachbar = [polygon[i-1],polygon[(i+1)%len(polygon)]]
    return nachbar

# berechnet Winkel zwischen zwei Punkten zur horizontalen Gerade
def winkel(k1, k2) : 
    if k1[0] == k2[0] :
        w = np.sign(k2[1]-k1[1]) * math.pi / 2 
    else :
        w = math.atan((k2[1]-k1[1])/(k2[0]-k1[0]))
    if k1[0] > k2[0] :
        w += math.pi
    elif k1[1] > k2[1] :
        w += 2*math.pi 
    return w

# brechnet mathematisches Kreuzprodukt
def kreuzprodukt(a,b,c,d) :
    return (b[0]-a[0])*(d[1]-c[1])-(d[0]-c[0])*(b[1]-a[1])

# überprüft ob zwei Strecken sich schneiden
def schneidet(a,b,c,d) : 
    if np.sign(kreuzprodukt(c,a,c,d)) != np.sign(kreuzprodukt(c,b,c,d)) :
        if np.sign(kreuzprodukt(a,c,a,b)) != np.sign(kreuzprodukt(a,d,a,b)) :
            return True
    return False

# überprüft ob zwei Punkte für einander sichtbar sind
def sichtbar(k1,k2,kanten) : 
    for kante in kanten :
        if not(k2 in kante) and schneidet(knoten[k1],knoten[k2],knoten[kante[0]],knoten[kante[1]]) :
            return False
    return True

# initialisiert die horizontal schneidenden Kanten
def horizontal(k) : 
    horizontaleKanten = []
    for kante in kanten :
        if knoten[kante[0]][1] != knoten[k][1] and knoten[kante[1]][1] != knoten[k][1] :
            if schneidet(knoten[k],[maxx+1,knoten[k][1]],knoten[kante[0]],knoten[kante[1]]) :
                horizontaleKanten.append(kante)
    return horizontaleKanten

# berechnet die Distanz zwische zwei Punkten
def distanz(k1,k2) : 
    d = math.sqrt((k2[0]-k1[0])**2 + (k2[1]-k1[1])**2)
    return d

# Überprüfung zwischen den eigenen kanten
def überprüfung(w,hindernis) :
    if len(hindernis) == 0 : # Haus hat keine Kanten
        return True
    if hindernis[0] > hindernis[1] :
        if hindernis[0] < w or w < hindernis[1] :
            return False
    if hindernis[0] < w and w < hindernis[1] : 
        return False
    return True

# sucht optimalen Winkel zur Landstrasse
def optimalerWinkel(k,w1,w2) : 
    haltestelle = winkel(k,[0,0])
    if w2 <= math.pi/2 or w1 > haltestelle : # kein Blick zur Landstrasse
        return [False, 0, 0]
    if w1 > 5*math.pi/6 :
        optimal = w1
    elif w2 < 5*math.pi/6 :
        optimal = w2
    else :
        optimal = 5*math.pi/6
    weg = -math.tan(optimal) * k[0]
    d = -k[0] / math.cos(optimal)
    zeit = 3.6 * (d/15 - (k[1]+weg)/30)
    return [True, zeit, k[1]+weg] # falls Weg zur Strasse, kürzeste Distanz zur Strasse

    
### Graph aller möglichen Verbindungen zwischen Eckpunkten #####################

graph = np.zeros((anzahlKnoten+1,anzahlKnoten+1))
strasse = [0] * anzahlKnoten
for k in range(anzahlKnoten) :
    andereKnoten = [[i,winkel(knoten[k],knoten[i])] for i in range(anzahlKnoten) if i != k]
    andereKnoten.sort(key=lambda x: x[1])
    relevanteKanten = horizontal(k)
    # überprüft ob Blick raus aus dem Feld an Hindernissen
    if len(relevanteKanten) == 0 : 
        moeglich, zeit, weg = optimalerWinkel(knoten[k],0,andereKnoten[0][1])
        if moeglich :
            graph[k,anzahlKnoten] = zeit
            strasse[k] = weg
    hindernis = [winkel(knoten[k],knoten[i]) for i in verbunden(k)]
    for j in range(anzahlKnoten-1) :
        ki, wi = andereKnoten[j]
        if überprüfung(wi,hindernis) and sichtbar(k,ki,relevanteKanten) :
            graph[k,ki] = distanz(knoten[k],knoten[ki])
        # relevante Kanten aktualisieren
        eigeneKanten = [sorted([i,ki]) for i in verbunden(ki) if i!=k]
        for kante in eigeneKanten :
            if kante in relevanteKanten :
                relevanteKanten.remove(kante)
            else :
                relevanteKanten.append(kante)
        
        # überprüft ob Blick raus aus dem Feld an Hindernissen
        if len(relevanteKanten) == 0 :
            if j+1 < anzahlKnoten-1 :
                wmax = andereKnoten[j+1][1]
            else :
                wmax = 2* math.pi
            moeglich, zeit, weg = optimalerWinkel(knoten[k],wi,wmax)
            if moeglich and (graph[k,anzahlKnoten]>zeit or graph[k,anzahlKnoten]==0) :
                graph[k,anzahlKnoten] = zeit
                strasse[k] = weg


### Schnellster Weg mit Dijkstra ###############################################

# wählt unbesuchten Knoten mit kleinster Distanz
def naechste(distanzen, besucht) :
    minimum = math.inf
    for i in range(anzahlKnoten+1) :
        if distanzen[i] < minimum and besucht[i] == 0 :
            minimum = distanzen[i]
            index = i
    return index

# baut den optimalen Weg zu einem Punkt rekursiv wieder auf
def weg(i) :
    if ursprung[i] == -1 :
        return [i]
    return weg(ursprung[i])+[i]
    
besucht = [0] * (anzahlKnoten+1)
distanzen = [math.inf] * (anzahlKnoten+1)
distanzen[anzahlKnoten-1] = 0
ursprung = [-1] * (anzahlKnoten+1)
for i in range(anzahlKnoten+1) :
    punkt = naechste(distanzen, besucht)
    besucht[punkt] = 1
    for j in range(anzahlKnoten+1) :
        if graph[punkt,j]>0 and besucht[j]==0 and distanzen[j]>distanzen[punkt]+graph[punkt,j] :
            distanzen[j] = distanzen[punkt]+graph[punkt,j]
            ursprung[j] = punkt

index = min([i for i in range(anzahlKnoten-1) if graph[i,-1] != 0], key=lambda x: 3.6*distanzen[x]/15 + graph[x,-1])
optimalerWeg = weg(index) + [anzahlKnoten]


### Ausgabe und Schreiben der svg Datei ########################################
with open(dateiname+".svg", 'r') as datei :
    graphik = datei.readlines()

polyline = '<polyline id = "R" points="'
for i in optimalerWeg[:-1] :
    polyline += str(knoten[i][0]) + ' ' + str(knoten[i][1]) + ' '
polyline += '0 '+ str(strasse[optimalerWeg[-2]]) + '" fill="none" stroke="#000080" stroke-width="4"/>' + '\n'
graphik[-4] = polyline

with open(dateiname+".svg", 'w') as datei :
    datei.writelines(graphik)

def zeitangabe(name, zeit) :
    stunden = int((30*60 + zeit) // 3600)
    minuten = int((zeit - stunden*3600) // 60)
    sekunden = round(zeit - stunden*3600 - minuten*60)
    print(name, ":", 7+stunden, ":", 30+minuten, ":", int(sekunden)) 
    
letzter = optimalerWeg[-2]
laenge = distanzen[letzter] + distanz(knoten[letzter],[0,strasse[letzter]])
dauer = 3.6/15 * laenge
treffpunkt = strasse[letzter]
zielzeit = 3.6 * treffpunkt / 30
startzeit = zielzeit - dauer
zeitangabe("Startzeit", startzeit)
zeitangabe("Zielzeit", zielzeit)
print("y-Koordinate von Lisas Treffen auf den Bus :", round(treffpunkt))
print("Dauer : ", round(dauer)/60, "Minuten")
print("Länge : ", str(int(round(laenge))), "Meter")
print("Koordinaten aller Eckpunkte der berechneten Route :")
print(haus[0], ",", haus[1], "Lisas Haus")
for punkt in optimalerWeg[1:-1] :
    print(knoten[punkt][0], ",", knoten[punkt][1], "von Polygon P" + str(knoten[punkt][2]+1))
print("0 ,", round(treffpunkt), "Landstraße")
