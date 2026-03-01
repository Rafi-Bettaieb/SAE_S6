import drawsvg as draw
from matplotlib import pyplot as plt

def cross_product(p1,p2,p3) :
    x1 , y1 = p1
    x2 , y2 = p2
    x3 , y3 = p3

    x1 -= x3
    y1 -= y3
    x2 -= x3
    y2 -= y3

    return (x1*y2 - x2*y1)

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
if __name__ == "__main__":
    with open("phase1/data/data.txt", "r") as f:
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
                if(cross_product(p1,p2,p3)==0) :
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

    axe_voronoi_ext=[]

    for cote in cote_seul:
        A=cote[0]
        B=cote[1]
        centre=None
        P=None
        for i in range(len(triangles)):
            t=triangles[i]
            if A in (t["p1"],t["p2"],t["p3"]) and B in (t["p1"],t["p2"],t["p3"]):
                centre=centres[i]
                if t["p1"]!=A and t["p1"]!=B:
                    P=t["p1"]
                if t["p2"]!=A and t["p2"]!=B:
                    P=t["p2"]
                if t["p3"]!=A and t["p3"]!=B:
                    P=t["p3"]

        dx=B[0]-A[0]
        dy=B[1]-A[1]
        perp_x=-dy
        perp_y=dx

        if cross_product(A,B,P)>0:
            perp_x=dy
            perp_y=-dx

        longueur=200
        point_fin=(centre[0]+perp_x*longueur,centre[1]+perp_y*longueur)
        axe_voronoi_ext.append((centre,point_fin))
    #print(axe_voronoi_ext)

    fig, ax = plt.subplots(figsize=(8, 8))

    xs=[p[0] for p in points]
    ys=[p[1] for p in points]

    xmin,xmax=min(xs)-1, max(xs)+1
    ymin,ymax=min(ys)-1, max(ys)+1

    for p in points:
        ax.plot(p[0], p[1], 'ro', markersize=6)

    for axe in axe_voronoi:
        c1,c2=list(axe)
        ax.plot([c1[0],c2[0]], [c1[1],c2[1]], 'g-', linewidth=2)

    for axe in axe_voronoi_ext:
        c1,c2=axe
        ax.plot([c1[0],c2[0]], [c1[1],c2[1]], 'g-', linewidth=2)

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    plt.savefig("phase1/results/resultat.png")
    plt.savefig("phase1/results/resultat.svg")
    plt.show()