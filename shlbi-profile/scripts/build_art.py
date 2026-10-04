#!/usr/bin/env python3
"""Build original, script-free SVG artwork. Uses Python's standard library only.
No font files, external images, JavaScript, trackers, or live services are embedded.
"""
from pathlib import Path
from html import escape
import math

ROOT = Path(__file__).resolve().parents[1]
BG = '#10120f'
PANEL = '#151812'
BONE = '#eeeade'
MUTED = '#9bA18f'
LIME = '#c6f36b'
LINE = '#343c2c'
DARK = '#21281b'
FONT = 'Arial, Helvetica, sans-serif'
MONO = "'Courier New', monospace"

CSS = '''
text{font-family:Arial,Helvetica,sans-serif}
.mono{font-family:'Courier New',monospace}
.float-a{animation:assemble-a 11s ease-in-out infinite}
.float-b{animation:assemble-b 11s ease-in-out infinite}
.float-c{animation:assemble-c 11s ease-in-out infinite}
@keyframes assemble-a{0%,12%,78%,100%{transform:translate(0,0)}35%,50%{transform:translate(20px,-24px)}}
@keyframes assemble-b{0%,16%,82%,100%{transform:translate(0,0)}38%,56%{transform:translate(-20px,14px)}}
@keyframes assemble-c{0%,20%,88%,100%{transform:translate(0,0)}42%,60%{transform:translate(16px,22px)}}
.signal{stroke-dasharray:7 180;animation:signal 7s linear infinite}
@keyframes signal{to{stroke-dashoffset:-374}}
.orbit{transform-origin:240px 139px;animation:orbit 26s linear infinite}
.orbit-slow{transform-origin:240px 139px;animation:orbit 36s linear infinite reverse}
@keyframes orbit{to{transform:rotate(360deg)}}
.transfer{animation:transfer 12s ease-in-out infinite}
@keyframes transfer{0%,12%{transform:translate(0,0);opacity:1}45%{transform:translate(124px,-54px);opacity:1}72%,84%{transform:translate(250px,18px);opacity:1}88%,92%{transform:translate(250px,18px);opacity:0}94%{transform:translate(0,0);opacity:0}100%{transform:translate(0,0);opacity:1}}
.curve{stroke-dasharray:700;animation:curve 10s ease-in-out infinite}
@keyframes curve{0%,100%{stroke-dashoffset:0;opacity:1}45%{stroke-dashoffset:0;opacity:1}65%{stroke-dashoffset:700;opacity:.2}80%{stroke-dashoffset:0;opacity:1}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
'''

def txt(x,y,s,size=14,fill=BONE,weight=400,mono=False,spacing=None,anchor=None,extra=''):
    attrs=f'x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}"'
    if mono: attrs+=' class="mono"'
    if spacing is not None: attrs+=f' letter-spacing="{spacing}"'
    if anchor: attrs+=f' text-anchor="{anchor}"'
    return f'<text {attrs} {extra}>{escape(str(s))}</text>'

def line(x1,y1,x2,y2,color=LINE,width=1,extra=''):
    return f'<path d="M{x1} {y1}H{x2}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>' if y1==y2 else f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>'

def rect(x,y,w,h,fill='none',stroke=LINE,r=0,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" {extra}/>'

def svg(w,h,title,body,description='',css=CSS):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description or title)}</desc>
<defs><pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".75" fill="{LINE}" opacity=".6"/></pattern><linearGradient id="fade" x2="1" y2="1"><stop stop-color="#25331a"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>
<style>{css}</style>
{rect(.5,.5,w-1,h-1,BG,LINE,8)}
{body}
</svg>\n'''

def cube(x,y,s=30,accent=False,outline=False,anim=None):
    dx,dy=s*.43,-s*.28
    fill=LIME if accent else '#20271a'
    top='#e0ffa7' if accent else '#2d3723'
    side='#819f48' if accent else '#161d12'
    edge='#d0f692' if accent else '#62734c'
    if outline: fill=BG; top='#151a12'; side='#10170c'; edge=LINE
    body=f'<path d="M0 0L{dx} {dy}H{s+dx}L{s} 0Z" fill="{top}" stroke="{edge}" stroke-width=".8"/>'
    body+=f'<path d="M{s} 0L{s+dx} {dy}V{s+dy}L{s} {s}Z" fill="{side}" stroke="{edge}" stroke-width=".8"/>'
    body+=rect(0,0,s,s,fill,edge,0,extra='stroke-width=".8"')
    if not outline:
        body+=line(5,s-6,s-5,s-6,'#161e0d' if accent else '#465337',.7)
    if anim: body=f'<g class="{anim}">{body}</g>'
    return f'<g transform="translate({x},{y})">{body}</g>'

def monogram():
    b=''
    # A constructed S. These blocks are artwork, not a contribution graph.
    rows=['11111','11000','11000','11111','00011','00011','11111']
    for r,row in enumerate(rows):
        for c,on in enumerate(row):
            if on=='1':
                accent=(r==3 or (r==0 and c==4) or (r==6 and c==0))
                anim={(0,4):'float-a',(3,0):'float-b',(6,4):'float-c'}.get((r,c))
                b+=cube(c*34,r*34,29,accent,anim=anim)
    return b

def hero(mobile=False):
    w,h=(480,630) if mobile else (960,486)
    b=rect(w*.57,64,w*.43-1,h-128,'url(#dots)','none')
    b+=line(32,65,w-32,65)
    b+=rect(32,27,10,10,LIME,LIME)
    b+=txt(54,37,'SHLBI / BUILD LAB',12,LIME,mono=True,spacing=1.5)
    if not mobile:b+=txt(w-32,37,'CHARLOTTE, NC',11,MUTED,mono=True,anchor='end',spacing=1.2)
    if mobile:
        b+=txt(30,134,'SAIF',65,BONE,700,spacing=-2)
        b+=txt(30,198,'ALSHALABI',55,BONE,700,spacing=-2)
        b+=txt(32,243,'Developer tools. Applied AI.',21,BONE)
        b+=txt(32,274,'Things that should exist.',21,MUTED)
        b+=f'<g transform="translate(173,325) scale(.84)">{monogram()}</g>'
        b+=line(38,460,144,460,LINE,1,extra='stroke-dasharray="3 5"')
        b+=txt(38,450,'S / 01',11,MUTED,mono=True)
        b+=line(340,355,425,355,LINE,1,extra='stroke-dasharray="3 5"')
        b+=line(32,553,448,553)
        b+=txt(32,580,'CS @ UNC CHARLOTTE',12,BONE,mono=True)
        b+=txt(32,603,'CURRENT BUILD',11,MUTED,mono=True)
        b+=txt(158,603,'REPOT ↗',12,LIME,700,mono=True)
    else:
        b+=txt(38,165,'SAIF',87,BONE,700,spacing=-4)
        b+=txt(38,255,'ALSHALABI',76,BONE,700,spacing=-3)
        b+=rect(499,237,12,12,LIME,LIME)
        b+=txt(40,318,'Developer tools. Applied AI.',26,BONE)
        b+=txt(40,353,'Things that should exist.',26,MUTED)
        b+=f'<g transform="translate(702,120) scale(.98)">{monogram()}</g>'
        b+=line(621,155,681,155,LINE,1,extra='stroke-dasharray="3 5"')
        b+=txt(620,141,'S / 01',11,MUTED,mono=True)
        b+=line(868,374,915,374)
        b+=txt(916,400,'REASSEMBLY STUDY',10,MUTED,mono=True,anchor='end',spacing=1)
        b+=line(32,425,928,425)
        b+=txt(40,456,'CS @ UNC CHARLOTTE',12,BONE,mono=True,spacing=1)
        b+=txt(640,456,'CURRENT BUILD',11,MUTED,mono=True,spacing=1)
        b+=txt(928,456,'REPOT ↗',14,LIME,700,mono=True,anchor='end')
    return svg(w,h,'Saif Alshalabi — SHLBI / Build Lab',b,'Developer tools. Applied AI. Things that should exist. Computer science at UNC Charlotte; currently building REPOT. A modular S slowly disassembles and reconnects.')

def transfer_art():
    b=''
    b+='<path d="M22 104C122 -60 252 -66 329 55" fill="none" stroke="#4b6033" stroke-width="1" stroke-dasharray="3 5"/>'
    b+='<path d="M22 104C122 -60 252 -66 329 55" fill="none" stroke="#c6f36b" stroke-width="2" class="signal"/>'
    for origin,outline in [(0,False),(250,True)]:
        for r in range(3):
            for c in range(3):
                if (r,c)==(1,1):continue
                b+=cube(origin+c*29,70+r*29+(18 if origin else 0),25,outline=outline)
    b+=f'<g transform="translate(29,99)"><g class="transfer">{cube(0,0,25,True)}</g></g>'
    b+=txt(0,194,'SOURCE',12,MUTED,mono=True,spacing=1)
    b+=txt(250,212,'DESTINATION',12,MUTED,mono=True,spacing=1)
    return b

def repot(mobile=False):
    w,h=(480,492) if mobile else (960,340)
    b=rect(w*.48,58,w*.52-1,h-104,'url(#dots)','none')
    b+=txt(32,38,'01 / CURRENT BUILD',12,LIME,mono=True,spacing=1.5)
    if mobile:
        b+=txt(30,112,'REPOT',66,BONE,700,spacing=-2.5)
        b+=txt(32,157,'Move features,',27,BONE)
        b+=txt(32,191,'not entire codebases.',27,BONE)
        b+=f'<g transform="translate(44,223) scale(1.03)">{transfer_art()}</g>'
        b+=line(32,463,448,463)
        b+=txt(32,483,'DEVELOPER TOOLS',10,MUTED,mono=True,spacing=1)
        b+=txt(448,483,'MCP / BETA',10,LIME,mono=True,anchor='end',spacing=1)
    else:
        b+=txt(30,132,'REPOT',86,BONE,700,spacing=-3)
        b+=txt(34,184,'Move features,',29,BONE)
        b+=txt(34,222,'not entire codebases.',29,BONE)
        b+=f'<g transform="translate(548,49)">{transfer_art()}</g>'
        b+=line(32,282,928,282)
        b+=txt(34,313,'DEVELOPER TOOLS',12,MUTED,mono=True,spacing=1)
        b+=txt(309,313,'SOURCE → FEATURE → YOUR CODEBASE',11,MUTED,mono=True)
        b+=txt(928,313,'MCP / BETA',12,LIME,mono=True,anchor='end',spacing=1)
    return svg(w,h,'REPOT — Move features, not entire codebases.',b,'Concept illustration: a highlighted feature module moves between two codebases. Not a product recording or a verified transfer.')

def kinetic():
    b=rect(1,1,478,244,'url(#dots)','none')
    b+=txt(24,32,'02 / KINETIC',12,LIME,mono=True,spacing=1)
    for r in (54,78,102):
        b+=f'<ellipse cx="240" cy="139" rx="{r*1.55}" ry="{r*.7}" fill="none" stroke="{LINE}" stroke-width="1"/>'
    b+='<path d="M83 139H397M240 65V213" fill="none" stroke="#283020" stroke-dasharray="2 6"/>'
    b+='<g transform="translate(240,139) scale(1.55,.7) translate(-240,-139)"><g class="orbit">'
    for i in range(15):
        a=i*2*math.pi/15
        x=240+78*math.cos(a);y=139+78*math.sin(a)
        # All coordinates are illustration geometry, not actual simulator outputs.
        b+=f'<rect x="{x-3:.2f}" y="{y-3:.2f}" width="6" height="6" fill="{LIME if i<5 else "#758364"}" transform="rotate({i*24+90},{x:.2f},{y:.2f})"/>'
    b+='</g></g>'
    b+=f'<circle cx="240" cy="139" r="38" fill="{BG}" stroke="{LINE}"/>'
    b+=txt(240,144,'t →',21,BONE,mono=True,anchor='middle')
    b+=txt(24,233,'ONE TIMELINE. EVERY OUTPUT.',11,MUTED,mono=True,spacing=.6)
    return svg(480,255,'Kinetic — deterministic timelines',b,'An abstract animated traffic-ring illustration, not a recording of the simulator.')

def osmo():
    b=rect(1,1,478,244,'url(#dots)','none')
    b+=txt(24,32,'03 / OSMO',12,LIME,mono=True,spacing=1)
    for y in range(70,190,30):b+=line(35,y,445,y,'#283021',1)
    for x in range(35,446,41):b+=line(x, 60,x,193,'#283021',1)
    b+='<path d="M35 193H445M35 193V54" fill="none" stroke="#556446" stroke-width="1.2"/>'
    for k,color in enumerate((LIME,'#9ca98d','#60734b')):
        pts=[]
        for t in range(110):
            x=35+t*3.72
            y=192-((t/13)*math.exp(-t/(13+k*9)))*(230-k*35)
            pts.append(f'{x:.1f},{y:.1f}')
        b+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{2.5 if k==0 else 1.5}" class="curve" style="animation-delay:{k*.4}s"/>'
    b+=txt(24,233,'MODELS. MEASUREMENTS. LIMITATIONS.',11,MUTED,mono=True,spacing=.2)
    return svg(480,255,'OSMO — pharmacokinetic research',b,'Stylized synthetic curves illustrate the research theme. These are decorative curves, not measured data or scientific results.')

def footer(mobile=False):
    w,h=(480,165) if mobile else (960,160)
    b=txt(32,37,'END OF PAGE / START OF A CONVERSATION',10,LIME,mono=True,spacing=.7)
    if mobile:
        b+=txt(31,84,'Have something',30,BONE,700,spacing=-.5)
        b+=txt(31,122,'worth building?',30,BONE,700,spacing=-.5)
        b+=txt(448,129,'↗',40,LIME,anchor='end')
    else:
        b+=txt(30,104,'Have something worth building?',39,BONE,700,spacing=-1)
        b+=txt(918,111,'↗',55,LIME,anchor='end')
    return svg(w,h,'Have something worth building?',b)

def button(label,width=168,accent=False):
    bg=LIME if accent else PANEL; fg=BG if accent else BONE
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="42" viewBox="0 0 {width} 42" role="img"><title>{escape(label)}</title>{rect(.5,.5,width-1,41,bg,LIME if accent else LINE,5)}{txt(width/2,26,label,12,fg,700,mono=True,anchor="middle",spacing=.7)}</svg>\n'

def build():
    assets=ROOT/'assets'
    for mobile in (False,True):
        directory=assets/'mobile' if mobile else assets
        directory.mkdir(parents=True,exist_ok=True)
        for name,fn in [('hero',hero),('repot',repot),('footer',footer)]:
            (directory/f'{name}.svg').write_text(fn(mobile),encoding='utf-8')
    for name,fn in [('kinetic',kinetic),('osmo',osmo)]:
        (assets/f'{name}.svg').write_text(fn(),encoding='utf-8')
    (assets/'linkedin.svg').write_text(button('LINKEDIN ↗',150,True),encoding='utf-8')
    (assets/'repot-link.svg').write_text(button('EXPLORE REPOT ↗',174),encoding='utf-8')
    # Explicit static variants for <picture> reduced-motion selection. Some
    # browsers do not propagate media changes into an already cached SVG image.
    for relative in ('hero.svg','mobile/hero.svg','repot.svg','mobile/repot.svg','kinetic.svg','osmo.svg'):
        source=(assets/relative).read_text(encoding='utf-8')
        static=source.replace('</style>','*{animation:none!important}</style>')
        target=assets/'static'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(static,encoding='utf-8')
    print('Built 10 original SVG assets and 6 reduced-motion variants.')

if __name__=='__main__':build()
