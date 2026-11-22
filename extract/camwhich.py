import UnityPy, os, re
D=r"C:\Program Files (x86)\Steam\steamapps\common\Sons Of The Forest\SonsOfTheForest_Data"
gg=UnityPy.load(os.path.join(D,'globalgamemanagers'))
scenes=[o.read().scenes for o in gg.objects if o.type.name=='BuildSettings'][0]
names=[b'Cultists1',b'CultistsArrival',b'Sahara',b'Estate']
for i,s in enumerate(scenes):
    if not re.search(r'SonsStorySpots|BunkerResidential|BunkerLuxury',s): continue
    f=list(UnityPy.load(os.path.join(D,'level%d'%i)).files.values())[0]
    for pid,o in f.objects.items():
        if o.type.name!='GameObject': continue
        go=o.read()
        if not go.m_Name.startswith('ActionCameraPickup'): continue
        found=[]
        for c in go.m_Component:
            ptr=c.component if hasattr(c,'component') else c
            ob=f.objects.get(ptr.path_id)
            if ob and ob.type.name=='MonoBehaviour':
                b=ob.get_raw_data()
                found+= [n.decode() for n in names if n in b]
                found+= re.findall(rb'[\x20-\x7e]{5,}',b)[:6]
        print(s.split('/')[-1],pid,found)
