def cross_product(p1,p2,p3) :
    x1 , y1 = p1
    x2 , y2 = p2
    x3 , y3 = p3

    x1 -= x3
    y1 -= y3
    x2 -= x3
    y2 -= y3

    return x1*y2 - x2*y1 == 0

def centre_cercle_circonscrit(p1,p2,p3) :
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    D = 2 * (x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))

    Ux = ((x1**2 + y1**2)*(y2 - y3) + (x2**2 + y2**2)*(y3 - y1) + (x3**2 + y3**2)*(y1 - y2)) / D
    Uy = ((x1**2 + y1**2)*(x3 - x2) + (x2**2 + y2**2)*(x1 - x3) + (x3**2 + y3**2)*(x2 - x1)) / D

    return (Ux, Uy)

def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    
    return (x1 - x2)**2 + (y1 - y2)**2

with open("data/data.txt", "r") as f:
    content = f.read()  
    liste = content.split() 
    points = []
    for i in range(len(liste)) :
        x,y = liste[i].split(",")
        points.append((float(x) , float(y)))

n = len(points)
centres = []
triangles = []
#print(n)
for i in range (n-2) :
    for j in range (i+1,n-1) :
        for k in range (j+1,n) :
            p1 = points[i]
            p2 = points[j]
            p3 = points[k]
            if(cross_product(p1,p2,p3)) :
                continue
            centre_cercle = centre_cercle_circonscrit(p1,p2,p3)
            rayon_cercle = distance(centre_cercle, p1)
            point_dans_cercle = False
            for l in range (n) :
                if l == i or l == j or l == k :
                    continue
                if distance(centre_cercle,points[l]) < rayon_cercle :
                    point_dans_cercle = True
                    break
            if point_dans_cercle == False :
                centres.append(centre_cercle)
                triangles.append({
                    "p1" : p1,
                    "p2" : p2,
                    "p3" : p3,
                })



#print(centres)
#print(triangles)

lt=len(triangles)

axe_voronoi=[]

for i in range(lt-1):
    for j in range (i+1,lt):
        t1= {triangles[i]["p1"] , triangles[i]["p2"] , triangles[i]["p3"]}
        t2= {triangles[j]["p1"] , triangles[j]["p2"] , triangles[j]["p3"]}
        
        t3 = t1.intersection(t2)
        if len(t3)==2:
            axe_voronoi.append({centres[i], centres[j]})

cote={}
for i in range (lt):
    t=triangles[i] #{'p1': (2.0, 1.0), 'p2': (6.0, 1.0), 'p3': (3.0, 4.0)}
    p1=t["p1"]
    p2=t["p2"]
    p3=t["p3"]
    if (p1,p2) in cote:
        cote[(p1,p2)]+=1
    else:
        cote[(p1,p2)]=1

    if (p1,p3) in cote:
        cote[(p1,p3)]+=1
    else:
        cote[(p1,p3)]=1

    if (p2,p3) in cote:
        cote[(p2,p3)]+=1
    else:
        cote[(p2,p3)]=1
#print(cote)
cote_seul=[]

for key,value in cote.items():
    print(key,value)
    
    if value ==1:
        cote_seul.append(key)

        
#print(axe_voronoi)
print(cote_seul)