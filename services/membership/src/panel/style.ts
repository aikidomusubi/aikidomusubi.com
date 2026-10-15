// The panel's styles, as approved in docs/mockups/panel-cuotas.html. Inline in
// every page: one stylesheet, no build step, nothing to cache-bust.
//
// The site's palette (Sanzo Wada), system faces: Futura where the machine has
// it for headings, the system sans for the rest. The chip colours are darker
// than the mockup's so that 12px bold text clears 4.5:1 on its own tint.
export const CSS = `
:root{
  --black:#111314;--ink:#3D4A50;--mute:#56636A;--line:rgba(17,19,20,.14);--line2:rgba(17,19,20,.08);
  --paper:#F6F5F1;--card:#fff;--yellow:#FFF200;
  --green:#155c36;--greenbg:#E8F2EC;--rust:#8a3a12;--rustbg:#FBEFE8;--blue:#064F6E;--bluebg:#E6EFF3;
  --red:#82241f;--redbg:#F7E9E8;--olive:#474400;--olivebg:#FFFBC2;--grey:#4d5a60;--greybg:#EDECE8;
  --display:Futura,"Century Gothic","Trebuchet MS",sans-serif;
}
*{box-sizing:border-box}
html{background:var(--paper)}
body{margin:0;background:var(--paper);color:var(--black);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans",Arial,sans-serif;-webkit-text-size-adjust:100%}
a{color:inherit}
:focus-visible{outline:3px solid var(--blue);outline-offset:2px}
.skip{position:absolute;left:-9999px;top:0;background:var(--yellow);color:var(--black);padding:.6rem 1rem;z-index:10;font-weight:700}
.skip:focus{left:.5rem;top:.5rem}
.sr{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

.top{display:flex;align-items:center;gap:.8rem;background:var(--black);color:#fff;padding:.8rem clamp(1rem,3vw,1.6rem)}
.mark{width:32px;height:32px;flex:none;display:block;border-radius:7px;box-shadow:0 0 0 1px rgba(255,255,255,.22)}
.mark svg{width:32px;height:32px;display:block}
.top .name{font:700 1rem/1 var(--display);letter-spacing:.06em;text-transform:uppercase;text-decoration:none;color:#fff}
.mode{font:700 .68rem/1 var(--display);letter-spacing:.1em;text-transform:uppercase;background:var(--yellow);color:var(--black);border-radius:1rem;padding:.25rem .5rem}
.top .sp{flex:1}
.top .who{font-size:.82rem;color:rgba(255,255,255,.78);max-width:40vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.top form{margin:0}
.top .out{background:none;border:0;color:#fff;font:inherit;font-size:.82rem;text-decoration:underline;cursor:pointer;padding:.5rem .2rem;min-height:40px}

.nav{display:flex;gap:.2rem;padding:0 clamp(1rem,3vw,1.6rem);background:var(--black)}
.nav a{color:rgba(255,255,255,.78);text-decoration:none;font-size:.92rem;padding:.6rem .85rem .75rem;border-bottom:3px solid transparent;display:flex;gap:.45rem;align-items:center;min-height:44px}
.nav a[aria-current=page]{color:#fff;font-weight:700;border-bottom-color:var(--yellow)}
.nav svg{width:18px;height:18px}
.nav .n{font:700 .74rem/1 var(--display);background:rgba(255,255,255,.2);color:#fff;border-radius:1rem;padding:.22rem .45rem}
.nav a[aria-current=page] .n{background:var(--yellow);color:var(--black)}

main{max-width:1240px;margin:0 auto;padding:1.5rem clamp(1rem,3vw,1.6rem) 3rem}
main:focus{outline:none}
h1.hello{font:700 1.6rem/1.2 var(--display);margin:0 0 .25rem}
.sub{color:var(--ink);margin:0 0 1.3rem;font-size:.95rem}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:.8rem;margin:0 0 1.6rem;padding:0;list-style:none}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.8rem 1rem}
.stat b{display:block;font:700 1.6rem/1.1 var(--display)}
.stat span{font-size:.82rem;color:var(--mute)}
.cols{columns:2 26rem;column-gap:1.1rem}
.group{break-inside:avoid;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:0 0 1.1rem}
.gh{display:flex;align-items:flex-start;gap:.75rem;padding:.85rem 1.1rem;border-bottom:1px solid var(--line2)}
.ic{width:34px;height:34px;border-radius:9px;display:grid;place-items:center;flex:none}
.ic svg{width:19px;height:19px}
.ic.paper{background:var(--rustbg);color:var(--rust)}.ic.keikogi{background:var(--bluebg);color:var(--blue)}
.ic.sc{background:var(--greenbg);color:var(--green)}.ic.age{background:var(--olivebg);color:var(--olive)}.ic.money{background:var(--redbg);color:var(--red)}
.gh h2{margin:0;font:700 1rem/1.3 var(--display);letter-spacing:.02em}
.gh p{margin:.1rem 0 0;font-size:.82rem;color:var(--mute)}
.gh .cnt{margin-left:auto;font:700 .82rem/1 var(--display);border-radius:1rem;padding:.3rem .55rem;background:var(--rustbg);color:var(--rust)}
.tasks{list-style:none;margin:0;padding:0}
.task{display:flex;align-items:center;gap:.9rem;padding:.8rem 1.1rem;border-bottom:1px solid var(--line2)}
.task:last-child{border-bottom:0}
.av{width:38px;height:38px;border-radius:50%;flex:none;display:grid;place-items:center;font:700 .85rem/1 var(--display);background:#ECEAE3}
.tx{flex:1;min-width:0}
.tx b{display:block;font-size:.97rem}
.tx b a{text-decoration:none}.tx b a:hover{text-decoration:underline}
.tx span{display:block;font-size:.84rem;color:var(--mute)}
.btns{display:flex;gap:.45rem;flex-wrap:wrap;justify-content:flex-end}
.btns form{margin:0}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.4rem;min-height:44px;padding:.5rem 1rem;border-radius:8px;font-family:inherit;font-weight:700;font-size:.9rem;line-height:1.1;white-space:nowrap;border:1.5px solid var(--black);background:var(--black);color:#fff;text-decoration:none;cursor:pointer}
.btn:hover{background:#2a2e30}
.btn.alt{background:#fff;color:var(--black)}.btn.alt:hover{background:var(--paper)}
.btn.warn{background:#fff;color:var(--red);border-color:var(--red)}.btn.warn:hover{background:var(--redbg)}
.btn.big{min-height:50px;font-size:1rem;width:100%}
.btn svg{width:17px;height:17px;flex:none}
.chip{display:inline-flex;align-items:center;gap:.35rem;font-size:.78rem;font-weight:700;border-radius:1rem;padding:.2rem .6rem;white-space:nowrap}
.chip::before{content:"";width:.5rem;height:.5rem;border-radius:50%;background:currentColor}
.chip.ok{background:var(--greenbg);color:var(--green)}.chip.todo{background:var(--rustbg);color:var(--rust)}
.chip.wait{background:var(--greybg);color:var(--grey)}.chip.info{background:var(--bluebg);color:var(--blue)}
.chip.bad{background:var(--redbg);color:var(--red)}
.chips{display:flex;gap:.35rem;flex-wrap:wrap;margin:.3rem 0 0;padding:0;list-style:none}

.toast{display:flex;align-items:center;gap:.8rem;flex-wrap:wrap;background:var(--black);color:#fff;border-radius:12px;padding:.7rem 1rem;margin:0 0 1.2rem;font-size:.95rem}
.toast svg{width:20px;height:20px;color:var(--yellow);flex:none}
.toast span{flex:1;min-width:12rem}
.toast form{margin:0}
.toast button{background:none;border:0;color:var(--yellow);font-family:inherit;font-weight:700;font-size:.95rem;text-decoration:underline;cursor:pointer;min-height:40px;padding:0 .3rem}
.toast.err{background:var(--redbg);color:var(--red);border:1.5px solid var(--red)}
.toast.err svg{color:var(--red)}

.empty{text-align:center;padding:2.4rem 1rem;background:var(--card);border:1px solid var(--line);border-radius:12px;margin:0 0 1.1rem}
.empty .okc{width:64px;height:64px;border-radius:50%;background:var(--greenbg);color:var(--green);display:grid;place-items:center;margin:0 auto .9rem}
.empty .okc svg{width:30px;height:30px}
.empty h2{font:700 1.3rem/1.2 var(--display);margin:0 0 .3rem}
.empty p{color:var(--mute);font-size:.95rem;margin:0 auto;max-width:28rem}
.banner{display:flex;gap:.6rem;align-items:flex-start;margin:0;padding:.75rem 1.3rem;font-size:.92rem;border-bottom:1px solid var(--line2)}
.banner svg{flex:none;width:18px;height:18px;margin-top:.15rem}
.banner.info{background:var(--bluebg);color:var(--blue)}
.banner.bad{background:var(--redbg);color:var(--red);font-weight:700}
.banner.done{background:var(--greybg);color:var(--grey)}
.ic.withdrawal{background:var(--redbg);color:var(--red)}
.stat a{display:block;text-decoration:none;color:inherit;margin:-.8rem -1rem;padding:.8rem 1rem;border-radius:10px}
.stat a:hover{background:#FCFBF8}
.sheet .sum .tot{border-top:1px solid var(--line);margin-top:.3rem;padding-top:.45rem;font-weight:700}
.sheet .note{font-size:.88rem;color:var(--mute)}
.help{display:flex;gap:.6rem;align-items:flex-start;background:var(--bluebg);color:var(--blue);border-radius:10px;padding:.75rem .95rem;font-size:.88rem;margin:0 0 1rem}
.help svg{flex:none;width:18px;height:18px;margin-top:.15rem}

.search{display:flex;gap:.5rem;margin:0 0 .9rem}
.search label{flex:1;display:flex;align-items:center;gap:.6rem;background:#fff;border:1.5px solid #7b878c;border-radius:10px;padding:0 .9rem;min-height:48px}
.search label:focus-within{outline:3px solid var(--blue);outline-offset:1px}
.search svg{width:18px;height:18px;color:var(--mute);flex:none}
.search input{flex:1;border:0;font:inherit;font-size:1rem;background:none;min-width:0;padding:.6rem 0}
.search input:focus{outline:none}
.filters{display:flex;gap:.4rem;flex-wrap:wrap;margin:0 0 1.1rem;padding:0;list-style:none}
.filters a{display:inline-flex;align-items:center;min-height:40px;font-size:.88rem;border:1px solid var(--line);background:#fff;border-radius:2rem;padding:.35rem .9rem;text-decoration:none}
.filters a[aria-current=true]{background:var(--black);color:#fff;border-color:var(--black);font-weight:700}
.split{display:grid;grid-template-columns:minmax(0,1fr) 30rem;gap:1.2rem;align-items:start}
.split.solo{grid-template-columns:minmax(0,1fr)}
.fams{list-style:none;margin:0;padding:0}
.fam{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:0 0 .7rem;position:relative}
.fam a.open{display:block;padding:.95rem 1.1rem;text-decoration:none;border-radius:12px}
.fam a.open:hover{background:#FCFBF8}
.fam[aria-current=true]{outline:2px solid var(--black)}
.fam h3{margin:0;font-size:1.02rem}
.fam .meta{font-size:.85rem;color:var(--mute)}
.fam .ppl{font-size:.88rem;color:var(--ink);margin:.15rem 0 0}
.none{color:var(--mute);padding:1rem 0}

.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;position:sticky;top:1rem}
.back{display:inline-flex;align-items:center;gap:.3rem;margin:0 0 .8rem;font-weight:700;min-height:40px}
.back svg{width:18px;height:18px;flex:none}
.ph{padding:1.1rem 1.3rem;border-bottom:1px solid var(--line2)}
.ph h2{margin:0 0 .2rem;font:700 1.35rem/1.2 var(--display)}
.ph p{margin:0;font-size:.88rem;color:var(--mute);overflow-wrap:anywhere}
.ph .tel{white-space:nowrap}
.person .fee{font-size:.86rem;color:var(--ink)}
.pb{padding:1rem 1.3rem}
.pb h3{font:700 .74rem/1 var(--display);letter-spacing:.12em;text-transform:uppercase;color:var(--mute);margin:1.1rem 0 .6rem}
.pb h3:first-child{margin-top:0}
.people{list-style:none;margin:0;padding:0}
.person{display:grid;grid-template-columns:auto 1fr;gap:.15rem .8rem;padding:.75rem 0;border-bottom:1px solid var(--line2)}
.person:last-child{border-bottom:0}
.person .av{grid-row:span 4}
.person b{font-size:.98rem}
.person .do{display:flex;gap:.4rem;flex-wrap:wrap;margin:.45rem 0 0}
.person .do form{margin:0}
.person .do .btn{min-height:40px;padding:.4rem .8rem;font-size:.84rem}
.kv{display:grid;grid-template-columns:auto 1fr;gap:.35rem 1rem;font-size:.92rem;margin:0}
.kv dt{color:var(--mute)}
.kv dd{margin:0;font-weight:700;text-align:right}
.tl{list-style:none;margin:0;padding:0;border-left:2px solid var(--line);font-size:.88rem}
.tl li{position:relative;padding:0 0 .6rem .9rem;color:var(--ink)}
.tl li::before{content:"";position:absolute;left:-.4rem;top:.45rem;width:.6rem;height:.6rem;border-radius:50%;background:#fff;border:2px solid var(--black)}
.tl li.g::before{background:var(--green);border-color:var(--green)}
.tl li.r::before{background:var(--red);border-color:var(--red)}
.tl time{color:var(--mute);margin-right:.35rem;font-size:.8rem}
.actions{display:grid;gap:.5rem;padding:1rem 1.3rem;border-top:1px solid var(--line2);background:#FBFAF7}
.actions .btn{width:100%;justify-content:flex-start}
.actions p{margin:.2rem 0 0;font-size:.84rem;color:var(--mute)}

.sheet{max-width:34rem;margin:1rem auto;background:#fff;border:1px solid var(--line);border-radius:16px;padding:1.4rem 1.3rem 1.3rem;box-shadow:0 14px 40px rgba(17,19,20,.08)}
.sheet h1{margin:0 0 .6rem;font:700 1.35rem/1.25 var(--display)}
.sheet p{margin:0 0 .9rem;color:var(--ink)}
.sheet .sum{background:var(--paper);border-radius:10px;padding:.7rem .95rem;margin:0 0 1.1rem}
.sheet .sum div{display:flex;justify-content:space-between;gap:1rem;padding:.2rem 0}
.sheet .sum b{white-space:nowrap}
.sheet form{margin:0 0 .55rem}
.sheet .btn.alt{width:100%}

.login{max-width:26rem;margin:2rem auto}
.login .card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:1.4rem}
.login h1{font:700 1.3rem/1.25 var(--display);margin:0 0 .4rem}
.login p{font-size:.95rem;color:var(--ink);margin:0 0 1rem}
.login label{display:block;font-weight:700;font-size:.92rem;margin:0 0 .3rem}
.login input{display:block;width:100%;border:1.5px solid #7b878c;border-radius:8px;padding:.7rem .8rem;margin:0 0 1rem;font:inherit;font-size:1.05rem}
.login input.code{font:700 1.6rem/1 ui-monospace,Menlo,monospace;letter-spacing:.35em;text-align:center}
.login .note{font-size:.84rem;color:var(--mute);text-align:center;margin:1rem 0 0}
.login .again{display:block;text-align:center;margin:1rem 0 0;font-size:.9rem}
.login .err{color:var(--red);font-weight:700}

.faq{max-width:46rem}
.faq details{background:#fff;border:1px solid var(--line);border-radius:12px;margin:0 0 .6rem}
.faq summary{cursor:pointer;padding:.9rem 1.1rem;font-weight:700;min-height:44px}
.faq details>div{padding:0 1.1rem 1rem;color:var(--ink)}
.faq details>div p{margin:0 0 .6rem}
h1.page{font:700 1.5rem/1.2 var(--display);margin:0 0 1rem}

@media (max-width:1099px){
  .split{grid-template-columns:minmax(0,1fr)}
  .split.detail .list{display:none}
  .panel{position:static}
}
@media (min-width:1100px){ .back{display:none} }
@media (max-width:899px){
  body{padding-bottom:76px}
  .nav{position:fixed;left:0;right:0;bottom:0;z-index:5;background:#fff;border-top:1px solid var(--line);display:grid;grid-template-columns:repeat(3,1fr);padding:.3rem 0 calc(.4rem + env(safe-area-inset-bottom))}
  .nav a{flex-direction:column;gap:.1rem;color:var(--mute);font-size:.76rem;border:0;padding:.3rem 0;position:relative}
  .nav a[aria-current=page]{color:var(--black);border:0}
  .nav svg{width:22px;height:22px}
  .nav .n{position:absolute;top:0;left:calc(50% + 6px);font-size:.68rem;padding:.15rem .35rem;background:var(--black);color:#fff}
  .nav a[aria-current=page] .n{background:var(--black);color:var(--yellow)}
  .stats{grid-template-columns:repeat(2,1fr)}
  .top .who{display:none}
}
@media (max-width:599px){
  .task{flex-wrap:wrap;row-gap:.55rem}
  .task .btns{flex-basis:100%;justify-content:flex-start;padding-left:calc(38px + .9rem)}
  h1.hello{font-size:1.35rem}
  .cols{columns:1}
}
@media (prefers-reduced-motion:no-preference){ .btn,.fam a.open{transition:background .15s} }
`;
