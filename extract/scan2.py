import UnityPy, struct, glob, os, collections, sys
D=r"C:\Program Files (x86)\Steam\steamapps\common\Sons Of The Forest\SonsOfTheForest_Data"
gg=UnityPy.load(D+r"\globalgamemanagers.assets")
scripts={}
for o in gg.objects:
    if o.type.name=='MonoScript':
        s=o.read(); scripts[o.path_id]=s.m_ClassName
want={pid:n for pid,n in scripts.items() if 'Achievement' in n or n in('ItemData','ItemDatabase','ItemDatabaseManager','BlueprintBookPageData','BlueprintBookPages')}
print(want)
files=[D+'\resources.assets']+sorted(glob.glob(D+r"\sharedassets*.assets"))+sorted(glob.glob(D+r"\level*"))
files=[x for x in files if not x.endswith('.resS')]
for fp in files:
    try: env=UnityPy.load(fp)
    except Exception as e: print('ERR',fp,e); continue
    for f in env.files.values():
        ext=[e.path for e in getattr(f,'externals',[])]
        # find index of globalgamemanagers.assets among externals (fileID = idx+1)
        gi=[i+1 for i,p in enumerate(ext) if p.lower().endswith('globalgamemanagers.assets')]
        if not gi: continue
        gi=gi[0]; c=collections.Counter()
        for pid,o in f.objects.items():
            if o.type.name!='MonoBehaviour': continue
            b=o.get_raw_data()
            if len(b)<28: continue
            fid,spid=struct.unpack_from('<iq',b,16)
            if fid==gi and spid in want: c[want[spid]]+=1; 
            if fid==gi and spid in want and 'Achievement' in want[spid]+'Database' : print(os.path.basename(fp),want[spid],pid,len(b))
        if c: print(os.path.basename(fp),dict(c)); sys.stdout.flush()
