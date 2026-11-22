import UnityPy, struct, glob, os, json
D=r"C:\Program Files (x86)\Steam\steamapps\common\Sons Of The Forest\SonsOfTheForest_Data"
def rstr(b,p):
    n=struct.unpack_from('<i',b,p)[0]; s=b[p+4:p+4+n].decode('utf8','replace'); p+=4+n; p=(p+3)&~3; return s,p
files=[os.path.join(D,'resources.assets')]+sorted(glob.glob(D+r'sharedassets*.assets'))+sorted(glob.glob(D+r'evel*'))
files=[x for x in files if not x.endswith('.resS')]
items={}; raws={}
for fp in files:
    env=UnityPy.load(os.path.join(D,"globalgamemanagers.assets"), fp)
    for f in env.files.values():
        ext=[e.path for e in getattr(f,'externals',[])]
        gi=[i+1 for i,p in enumerate(ext) if p.lower().endswith('globalgamemanagers.assets')]
        if not gi: continue
        for pid,o in f.objects.items():
            if o.type.name!='MonoBehaviour': continue
            b=o.get_raw_data()
            if len(b)<64: continue
            fid,spid=struct.unpack_from('<iq',b,16)
            if (fid,spid)!=(gi[0],4766): continue
            p=28; mname,p=rstr(b,p); p+=4; name,p=rstr(b,p); iid=struct.unpack_from('<i',b,p)[0]
            if iid not in items: items[iid]=name; raws[iid]=b.hex()
json.dump(items,open('items.json','w'),indent=0,sort_keys=True)
json.dump(raws,open('items_raw.json','w'))
print(len(items))
