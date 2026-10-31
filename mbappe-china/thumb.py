"""Thumbnail EN: Mbappé (meme da túnica de Mao) × Xi Jinping, fundo com os memes, "MBAPPÉ LOST €7 MILLION".
Recortes (rembg) em build/cut_*.png. Valor: ~50 mi de yuans ≈ €6,7–7 mi (Le Monde / L'Équipe)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np, glob
W,H=1280,720
memes=sorted(glob.glob('assets/memes/MEME_0[2-6]_*'))+sorted(glob.glob('assets/_extras/MEME_0[1-7]*'))
bg=Image.new('RGB',(W,H)); cols,rows=5,3; cw,ch=W//cols+1,H//rows+1; k=0
for r in range(rows):
    for c in range(cols):
        im=Image.open(memes[k%len(memes)]).convert('RGB'); k+=1
        s=max(cw/im.width,ch/im.height); im=im.resize((int(im.width*s)+1,int(im.height*s)+1))
        im=im.crop(((im.width-cw)//2,(im.height-ch)//2,(im.width-cw)//2+cw,(im.height-ch)//2+ch))
        bg.paste(im,(c*(W//cols),r*(H//rows)))
a=np.asarray(bg).astype(np.float32)/255; lum=(a@np.array([.3,.59,.11],np.float32))[...,None]
a=(lum+(a-lum)*0.35)*0.42; a[...,0]+=0.06*(1-lum[...,0])
bg=Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
yy,xx=np.mgrid[0:H,0:W]; v=np.clip(1-0.55*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2),0.25,1)[...,None]
bg=Image.fromarray((np.asarray(bg)*v).astype(np.uint8))
def place(cut,height,x,glow):
    cut=cut.crop(cut.getbbox()); s=height/cut.height; cut=cut.resize((int(cut.width*s),height),Image.LANCZOS)
    al=cut.split()[3]; halo=Image.new('RGBA',cut.size,glow+(0,)); halo.putalpha(al.filter(ImageFilter.GaussianBlur(14)).point(lambda p:min(255,int(p*1.6))))
    bg.paste(halo,(x-8,H-height),halo); bg.paste(cut,(x,H-height),cut); return cut.width
mb=ImageEnhance.Contrast(Image.open('build/cut_mbappe.png').convert('RGBA')).enhance(1.1)
place(mb,650,-40,(255,40,40))
xi=Image.open('build/cut_xi.png'); xc=xi.crop(xi.getbbox()); xw=int(xc.width*660/xc.height)
place(xi,660,W-xw+60,(255,200,0))
ga=np.zeros((300,W,4),np.uint8); ga[...,3]=(np.linspace(0,1,300)**1.3*230)[:,None].astype(np.uint8)
g=Image.fromarray(ga); bg.paste(g,(0,H-300),g)
d=ImageDraw.Draw(bg); A=lambda n: ImageFont.truetype('fonts/Anton-Regular.ttf',n)
f2,f1=A(150),A(80)
b2=d.textbbox((0,0),"€7 MILLION",font=f2,stroke_width=10); h2=b2[3]-b2[1]
y2=H-22-h2-b2[1]
d.text((W/2,y2),"€7 MILLION",font=f2,fill=(255,214,0),anchor="ma",stroke_width=10,stroke_fill=(0,0,0))
b1=d.textbbox((0,0),"MBAPPÉ LOST",font=f1,stroke_width=7); h1=b1[3]-b1[1]
y1=y2+b2[1]-12-h1-b1[1]
d.text((W/2,y1),"MBAPPÉ LOST",font=f1,fill=(255,255,255),anchor="ma",stroke_width=7,stroke_fill=(0,0,0))
bg.save('saida/thumbnail_en.png'); bg.save('saida/thumbnail_en.jpg',quality=92)
