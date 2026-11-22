import dnfile, sys
G=r"C:\Program Files (x86)\Steam\steamapps\common\Sons Of The Forest\_RedLoader\Game"
pe=dnfile.dnPE(G+"\\"+sys.argv[1])
td=pe.net.mdtables.TypeDef
for t in td:
    if str(t.TypeName) in sys.argv[2:]:
        print('==',t.TypeNamespace,t.TypeName)
        for f in t.FieldList:
            r=f.row
            if not str(r.Name).startswith('NativeFieldInfoPtr'): print('  F',r.Name)
        for m in t.MethodList:
            n=str(m.row.Name)
            if not n.startswith(('get_','set_','.c')): print('  M',n)
