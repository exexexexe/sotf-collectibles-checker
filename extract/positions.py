import UnityPy, glob, os, re, json, sys
D=r"C:\Program Files (x86)\Steam\steamapps\common\Sons Of The Forest\SonsOfTheForest_Data"
items=json.load(open('items.json')); L=json.load(open('lists.json'))
want={items[str(i)]:i for i in L['notes']+L['blueprints']+L['plated']}
rx=re.compile(r'^(%s)(Pickup)?( \(\d+\))?$'%'|'.join(sorted(want,key=len,reverse=True)))
# scene names
gg=UnityPy.load(os.path.join(D,'globalgamemanagers'))
scenes=[]
for o in gg.objects:
    if o.type.name=='BuildSettings':
        scenes=o.read().scenes; break
print('scenes',len(scenes))
def qrot(q,v):
    x,y,z,w=q.x,q.y,q.z,q.w; vx,vy,vz=v
    tx=2*(y*vz-z*vy); ty=2*(z*vx-x*vz); tz=2*(x*vy-y*vx)
    return (vx+w*tx+(y*tz-z*ty), vy+w*ty+(z*tx-x*tz), vz+w*tz+(x*ty-y*tx))
def qmul(a,b):
    class Q: pass
    q=Q(); q.w=a.w*b.w-a.x*b.x-a.y*b.y-a.z*b.z; q.x=a.w*b.x+a.x*b.w+a.y*b.z-a.z*b.y
    q.y=a.w*b.y-a.x*b.z+a.y*b.w+a.z*b.x; q.z=a.w*b.z+a.x*b.y-a.y*b.x+a.z*b.w; return q
out=[]
for fp in sorted(glob.glob(os.path.join(D,'level*')), key=lambda p:int(re.sub(r'\D','',os.path.basename(p)) or 0)):
    lvl=int(re.sub(r'\D','',os.path.basename(fp)))
    env=UnityPy.load(fp)
    f=list(env.files.values())[0]
    tr={}
    for pid,o in f.objects.items():
        if o.type.name=='Transform' or o.type.name=='RectTransform':
            try: tr[pid]=o.read()
            except Exception: pass
    for pid,o in f.objects.items():
        if o.type.name!='GameObject': continue
        go=o.read(); m=rx.match(go.m_Name)
        if not m: continue
        t=None
        for c in go.m_Component:
            ptr=c.component if hasattr(c,'component') else c
            if ptr.path_id in tr: t=tr[ptr.path_id]; break
        if t is None: continue
        # world position
        p=(t.m_LocalPosition.x,t.m_LocalPosition.y,t.m_LocalPosition.z); cur=t
        while cur.m_Father.path_id and cur.m_Father.path_id in tr:
            par=tr[cur.m_Father.path_id]
            s=par.m_LocalScale; p=(p[0]*s.x,p[1]*s.y,p[2]*s.z); p=qrot(par.m_LocalRotation,p)
            lp=par.m_LocalPosition; p=(p[0]+lp.x,p[1]+lp.y,p[2]+lp.z); cur=par
        # path of parent names
        names=[]; cur=t
        while cur.m_Father.path_id and cur.m_Father.path_id in tr:
            cur=tr[cur.m_Father.path_id]
            try: names.append(cur.m_GameObject.read().m_Name)
            except Exception: pass
        out.append(dict(id=want[m.group(1)],obj=go.m_Name,level=lvl,scene=scenes[lvl] if lvl<len(scenes) else '?',pos=[round(v,1) for v in p],parents=names[:6],active=go.m_IsActive))
    print(lvl, scenes[lvl] if lvl<len(scenes) else '?', sum(1 for x in out if x['level']==lvl)); sys.stdout.flush()
json.dump(out,open('positions.json','w'),indent=1)
