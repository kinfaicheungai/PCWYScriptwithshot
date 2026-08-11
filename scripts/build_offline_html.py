from pathlib import Path
from io import BytesIO
import base64
import html
import json

from PIL import Image

SITE = Path(__file__).resolve().parents[1]
OUT = SITE.parent / "PaintingChristmas_Interactive_Offline.html"
scenes = json.loads((SITE / "app/scenes.json").read_text(encoding="utf-8"))

for scene in scenes:
    embedded = []
    for url in scene["images"]:
        source = SITE / "public" / url.lstrip("/")
        with Image.open(source) as image:
            image = image.convert("RGB")
            if image.width > 1600:
                height = round(image.height * 1600 / image.width)
                image = image.resize((1600, height), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            image.save(buffer, "JPEG", quality=76, optimize=True, progressive=True)
        embedded.append("data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii"))
    scene["images"] = embedded

data = json.dumps(scenes, ensure_ascii=False, separators=(",", ":"))

document = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Painting Christmas With You — Offline Storyboard</title>
<style>
:root{--paper:#f4f0e7;--red:#a92324;--line:#d2c9b9}*{box-sizing:border-box}html,body{margin:0;height:100%;overflow:hidden;background:#191a1c;color:#1a1d21;font-family:Arial,sans-serif}button,input{font:inherit}.app{height:100%;display:grid;grid-template-rows:58px 54px minmax(0,1fr) minmax(220px,36vh);background:var(--paper)}header{display:grid;grid-template-columns:1fr minmax(230px,420px) 1fr;gap:14px;align-items:center;padding:0 18px;background:#17191c;color:white}.brand{font-weight:700}.brand small{display:block;color:#92969f;font-size:10px;letter-spacing:.12em}.search{position:relative}.search input{width:100%;padding:10px 13px;border:1px solid #41444b;border-radius:4px;background:#24272c;color:white;outline:0}.results{position:absolute;z-index:20;top:43px;left:0;right:0;background:#24272c;border:1px solid #444;max-height:260px;overflow:auto}.results button{display:block;width:100%;padding:9px 12px;text-align:left;background:none;border:0;color:white}.results button:hover{background:#383b42}.modes{justify-self:end;display:flex;background:#282b30;padding:3px}.modes button{padding:8px 11px;border:0;background:none;color:#aaa;font-size:11px}.modes .on{background:#eee9df;color:#222}.sceneBar{display:grid;grid-template-columns:45px 1fr 45px;gap:12px;align-items:center;padding:0 16px;border-bottom:1px solid var(--line)}.sceneBar button{width:36px;height:36px;border:1px solid #b9b09f;border-radius:50%;background:none;font-size:20px}.identity b{color:var(--red);letter-spacing:.1em;margin-right:16px}.identity span{font-weight:700}.boards{position:relative;min-height:0;padding:14px 48px 8px;background:#292a2d;display:flex;flex-direction:column;align-items:center}.frame{position:relative;min-height:0;flex:1;width:100%;display:flex;justify-content:center}.frame>img{width:100%;height:100%;object-fit:contain}.boardArrow{position:absolute;top:50%;transform:translateY(-50%);width:42px;height:62px;border:0;background:#111b;color:white;font-size:38px}.boardArrow.left{left:-44px}.boardArrow.right{right:-44px}.count{position:absolute;right:8px;bottom:8px;background:#111c;color:#fff;padding:6px 9px;font-size:11px}.strip{height:47px;display:flex;gap:5px;margin-top:6px}.strip button{width:75px;height:47px;padding:2px;background:#111;border:2px solid transparent;opacity:.55}.strip button.on{border-color:#d54b46;opacity:1}.strip img{width:100%;height:100%;object-fit:cover}.script{min-height:0;overflow-y:auto;background:#d9d2c5;border-top:4px solid var(--red)}.page{width:min(980px,calc(100% - 28px));margin:auto;padding:20px 62px 48px;background:#faf6ec}.sceneText{padding:10px 0 30px;border-bottom:1px solid #ddd4c5;opacity:.58}.sceneText.current{opacity:1}.heading{display:grid;grid-template-columns:42px 1fr 42px;gap:16px;font:700 15px Courier New,monospace}.heading span:last-child{text-align:right}.copy{margin:18px 58px 0;font:15px/1.35 Courier New,monospace}.action{white-space:pre-wrap;margin:0 0 1.25em}.character{width:52%;margin:1.25em 0 0 38%;white-space:pre-wrap}.parenthetical{width:38%;margin:.1em 0 0 31%;white-space:pre-wrap}.dialogue{width:58%;margin:.1em 0 1.25em 23%;white-space:pre-wrap}.end{text-align:center;color:#aaa;font-size:9px;letter-spacing:.16em}.boardsOnly{grid-template-rows:58px 54px minmax(0,1fr)}.scriptOnly{grid-template-rows:58px 54px minmax(0,1fr)}.hidden{display:none!important}
@media(max-width:760px){header{grid-template-columns:1fr auto;padding:0 9px}.brand small,.search{display:none}.app{grid-template-rows:54px 50px minmax(0,1fr) minmax(250px,43vh)}.sceneBar{padding:0 7px;gap:5px}.identity b{font-size:12px;margin-right:6px}.identity span{font-size:11px}.boards{padding:7px}.boardArrow.left{left:1px}.boardArrow.right{right:1px}.strip{display:none}.page{width:100%;padding:15px 11px 40px}.copy{margin:12px 0;font-size:clamp(11px,3vw,13px)}.heading{grid-template-columns:28px 1fr 28px;gap:5px;font-size:12px}.character{width:62%;margin-left:32%}.parenthetical{width:58%;margin-left:25%}.dialogue{width:76%;margin-left:12%}}
</style></head><body>
<div class="app" id="app"><header><div class="brand">Painting Christmas With You<small>OFFLINE STORYBOARD READER</small></div><div class="search"><input id="search" placeholder="Jump to scene…"><div class="results hidden" id="results"></div></div><div class="modes"><button data-mode="split" class="on">Split</button><button data-mode="boards">Boards</button><button data-mode="script">Script</button></div></header>
<div class="sceneBar"><button id="prevScene">←</button><div class="identity"><b id="sceneNo"></b><span id="sceneTitle"></span></div><button id="nextScene">→</button></div>
<section class="boards" id="boards"><div class="frame"><img id="board"><button class="boardArrow left" id="prevBoard">‹</button><button class="boardArrow right" id="nextBoard">›</button><div class="count" id="count"></div></div><div class="strip" id="strip"></div></section>
<section class="script" id="script"><div class="page" id="page"></div></section></div>
<script>const scenes=__SCENES__;let si=0,bi=0,suppress=false,timer;const $=id=>document.getElementById(id),script=$('script'),page=$('page');
const esc=s=>s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
page.innerHTML=scenes.map(s=>`<article class="sceneText" data-scene="${s.number}"><div class="heading"><span>${s.number}</span><span>${esc(s.title)}</span><span>${s.number}</span></div><div class="copy">${s.blocks.map(b=>`<div class="${b.type}">${esc(b.text)}</div>`).join('')}</div><div class="end">END SCENE ${s.number}</div></article>`).join('');
const articles=[...document.querySelectorAll('.sceneText')];
function render(){const s=scenes[si];$('sceneNo').textContent=`SCENE ${s.number}`;$('sceneTitle').textContent=s.title;articles.forEach((a,i)=>a.classList.toggle('current',i===si));const image=s.images[bi];$('board').src=image||'';$('board').style.display=image?'block':'none';$('count').textContent=s.images.length>1?`${bi+1} / ${s.images.length}`:'';$('strip').innerHTML=s.images.map((im,i)=>`<button class="${i===bi?'on':''}" data-i="${i}"><img src="${im}"></button>`).join('');$('strip').querySelectorAll('button').forEach(b=>b.onclick=()=>{bi=+b.dataset.i;render()});$('prevScene').disabled=si===0;$('nextScene').disabled=si===scenes.length-1}
function jump(i,board=0){si=Math.max(0,Math.min(scenes.length-1,i));bi=Math.max(0,Math.min(board,scenes[si].images.length-1));render();suppress=true;clearTimeout(timer);script.scrollTop+=articles[si].getBoundingClientRect().top-script.getBoundingClientRect().top;timer=setTimeout(()=>suppress=false,50)}
function stepBoard(d){let n=bi+d;if(n>=0&&n<scenes[si].images.length){bi=n;render();return}let s=si+d;while(s>=0&&s<scenes.length&&!scenes[s].images.length)s+=d;if(s>=0&&s<scenes.length)jump(s,d>0?0:scenes[s].images.length-1)}
$('prevScene').onclick=()=>jump(si-1);$('nextScene').onclick=()=>jump(si+1);$('prevBoard').onclick=()=>stepBoard(-1);$('nextBoard').onclick=()=>stepBoard(1);
script.onscroll=()=>{if(suppress)return;const marker=script.scrollTop+3;let active=0;for(let i=0;i<articles.length;i++){if(articles[i].offsetTop<=marker)active=i;else break}if(active!==si){si=active;bi=0;render()}};
document.querySelectorAll('[data-mode]').forEach(btn=>btn.onclick=()=>{document.querySelectorAll('[data-mode]').forEach(b=>b.classList.remove('on'));btn.classList.add('on');const m=btn.dataset.mode;$('app').className='app '+(m==='boards'?'boardsOnly':m==='script'?'scriptOnly':'');$('boards').classList.toggle('hidden',m==='script');$('script').classList.toggle('hidden',m==='boards')});
const input=$('search'),results=$('results');input.oninput=()=>{const q=input.value.toLowerCase().replace(/^s(?:cene)?\s*/,'').trim();if(!q){results.classList.add('hidden');return}const found=scenes.map((s,i)=>[s,i]).filter(([s])=>String(s.number).startsWith(q)||s.title.toLowerCase().includes(q)).slice(0,8);results.innerHTML=found.map(([s,i])=>`<button data-i="${i}"><b>S${s.number}</b> ${esc(s.title)}</button>`).join('');results.classList.toggle('hidden',!found.length);results.querySelectorAll('button').forEach(b=>b.onclick=()=>{jump(+b.dataset.i);input.value='';results.classList.add('hidden')})};input.onkeydown=e=>{if(e.key==='Enter'){const n=parseInt(input.value.replace(/\D/g,''));const i=scenes.findIndex(s=>s.number===n);if(i>=0)jump(i);input.value='';results.classList.add('hidden')}};
document.onkeydown=e=>{if(e.target===input)return;if(e.key==='ArrowUp')jump(si-1);if(e.key==='ArrowDown')jump(si+1);if(e.key==='ArrowLeft')stepBoard(-1);if(e.key==='ArrowRight')stepBoard(1)};render();</script></body></html>'''

OUT.write_text(document.replace("__SCENES__", data), encoding="utf-8")
print(f"Created {OUT.name}: {OUT.stat().st_size / 1048576:.1f} MB")
