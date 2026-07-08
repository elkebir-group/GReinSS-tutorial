import numpy as np, matplotlib.pyplot as plt

BLUE='#13294B'; ORANGE='#FF5F05'; NODE='#d9e2ec'; GREY='#7a8697'; GREEN='#1c7c3a'; RED='#cf2f1c'

n=6
ang=np.linspace(0.5*np.pi, 0.5*np.pi+2*np.pi, n, endpoint=False)  # node 0 at top, clockwise
xy=np.c_[np.cos(ang), np.sin(ang)]

edges=[(0,1),(1,2),(2,3),(3,4),(4,0),(0,2),(5,0),(3,5)]        # latent graph S*
walks=[(5,3),(4,1),(0,3),(2,4)]                                # observed (start,end) endpoints

def nodes(ax):
    ax.scatter(xy[:,0],xy[:,1], s=430, color=NODE, edgecolor='#33415a', zorder=3, linewidths=1.3)
    for i,(x,y) in enumerate(xy): ax.text(x,y,str(i),ha='center',va='center',zorder=4,fontsize=11)
    ax.set_aspect('equal'); ax.axis('off'); ax.set_xlim(-1.32,1.32); ax.set_ylim(-1.30,1.32)

def dedges(ax, es, color, ls='-'):
    for i,j in es:
        ax.annotate('', xy=xy[j], xytext=xy[i],
                    arrowprops=dict(arrowstyle='-|>', color=color, alpha=.85, lw=1.7,
                                    linestyle=ls, shrinkA=13, shrinkB=13,
                                    mutation_scale=14))

fig,ax=plt.subplots(1,3,figsize=(9.8,2.65))

# 1 — latent graph S*
dedges(ax[0], edges, BLUE); nodes(ax[0])
ax[0].set_title(r'latent graph  $S^*_i$', color=BLUE, fontsize=12, pad=1)

# 2 — observation: only start->end points of k absorbing walks
for s,e in walks:
    ax[1].annotate('', xy=xy[e], xytext=xy[s],
                   arrowprops=dict(arrowstyle='-|>', color=GREY, alpha=.9, lw=1.5,
                                   linestyle=(0,(4,3)), shrinkA=15, shrinkB=15,
                                   mutation_scale=13, connectionstyle='arc3,rad=0.28'))
nodes(ax[1])
ax[1].set_title(r'observe: start$\to$end of $k$ walks', fontsize=11.5, pad=1)

# 3 — GReinSS reconstruction
dedges(ax[2], edges, ORANGE); nodes(ax[2])
ax[2].set_title(r'GReinSS  $\hat S_i$', color=ORANGE, fontsize=12, pad=1)

plt.tight_layout(w_pad=1.0)
out='assets/graph-cartoon.png'
plt.savefig(out, dpi=220, bbox_inches='tight', facecolor='white')
print('saved', out)
