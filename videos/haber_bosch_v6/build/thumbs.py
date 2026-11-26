from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
FD="/usr/share/fonts/opentype/inter/"; W,H=1280,720
wm=Image.open("/home/claude/orivanta/work/orivanta_watermark_v2.png").convert("RGBA"); wm=wm.resize((220,int(220*wm.height/wm.width)))
def base(p, dark=0.55):
    im=Image.open(p).convert("RGB").resize((W,H)); im=ImageEnhance.Brightness(im).enhance(dark); return im.convert("RGBA")
def txt(d,xy,s,size,fill,anchor="mm",font="InterDisplay-Black.otf",stroke=6):
    d.text(xy,s,font=ImageFont.truetype(FD+font,size),fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=(0,0,0))
G=(240,200,110)
# T1
im=base("/tmp/th_lf.png",0.7); d=ImageDraw.Draw(im)
txt(d,(W//2,250),"BREAD",190,(255,255,255)); txt(d,(W//2,440),"FROM AIR",170,G)
im.alpha_composite(wm,(W-250,H-wm.height-28)); im.convert("RGB").save("v6/thumbs/thumb_A_bread_from_air.jpg",quality=92)
# T2: Haber archival portrait + unknown partner
im=Image.new("RGBA",(W,H),(18,14,10,255)); d=ImageDraw.Draw(im)
hb=Image.open("/home/claude/orivanta/arc/ORV_extra_1.jpg").convert("L").convert("RGBA"); hb=hb.resize((int(500*hb.width/hb.height),500))
im.alpha_composite(hb,(70,90))
d.rectangle([70+hb.width+40,90,70+hb.width*2+40,590],fill=(40,34,26,255),outline=G,width=5)
txt(d,(70+hb.width*1.5+40,340),"?",280,G)
txt(d,(70+hb.width//2,640),"FAMOUS",44,(255,255,255),font="InterDisplay-Bold.otf",stroke=3)
txt(d,(70+int(hb.width*1.5)+40,640),"FORGOTTEN",44,G,font="InterDisplay-Bold.otf",stroke=3)
x=70+hb.width*2+90
txt(d,(x+(W-x)//2,280),"WHO",120,(255,255,255)); txt(d,(x+(W-x)//2,420),"BUILT IT?",74,G)
im.alpha_composite(wm,(W-250,30)); im.convert("RGB").save("v6/thumbs/thumb_B_who_built_it.jpg",quality=92)
# T3
im=base("/tmp/th_ga.png",0.6); d=ImageDraw.Draw(im)
txt(d,(W//2,260),"AIR",210,(255,255,255)); txt(d,(W//2,470),"→ FOOD",190,G)
im.alpha_composite(wm,(W-250,H-wm.height-28)); im.convert("RGB").save("v6/thumbs/thumb_C_air_to_food.jpg",quality=92)
s=Image.new("RGB",(W,H*3))
for i,f in enumerate(["A_bread_from_air","B_who_built_it","C_air_to_food"]): s.paste(Image.open(f"v6/thumbs/thumb_{f}.jpg"),(0,H*i))
s.resize((640,1080)).save("/tmp/thsheet.jpg")
