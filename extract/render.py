import numpy as np, sys
from PIL import Image
hd=np.load('h1024.npy'); SEA=float(sys.argv[1]) if len(sys.argv)>1 else 6
cell=4000/1024
gy,gx=np.gradient(hd,cell)
az,alt=np.radians(315),np.radians(40)
slope=np.arctan(np.hypot(gx,gy)); aspect=np.arctan2(-gx,gy)  # rows already north-up
shade=np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-aspect)
shade=np.clip(shade,0,1)
# hypsometric ramp (muted forest/snow)
stops=[(SEA,(196,190,160)),(20,(150,160,118)),(120,(98,122,86)),(300,(84,104,78)),(450,(128,128,116)),(560,(200,202,200)),(700,(244,246,248))]
def ramp(v):
    out=np.zeros(v.shape+(3,))
    xs=[s[0] for s in stops]; 
    for c in range(3): out[...,c]=np.interp(v,xs,[s[1][c] for s in stops])
    return out
land=ramp(hd)*(0.55+0.6*shade[...,None])
depth=np.clip((SEA-hd)/30,0,1)[...,None]
water=(1-depth)*np.array([150,185,196])+depth*np.array([86,126,146])
img=np.where((hd<SEA)[...,None],water,land)
Image.fromarray(np.clip(img,0,255).astype(np.uint8)).save('map.png')
Image.fromarray(np.clip(img,0,255).astype(np.uint8)).resize((512,512)).save('map_small.png')
