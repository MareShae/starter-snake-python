g = [1, 2, 3, 4]

def gg(z=6):
    p = g[0]
    g.pop(0)
    return p * z


p = gg()

print(p)
print(g)