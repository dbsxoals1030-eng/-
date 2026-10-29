// All 16 MBTI mascots, minimal line style. Shared constants + mascot()/animFaces().
const K='#1F1F1F',F='#FBFAF7',AC='#D4573B';
const sw=`stroke="${K}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"`;
const star=(x,y,s,f)=>`<path transform="translate(${x} ${y}) scale(${s})" d="M0 -30 Q4 -4 30 0 Q4 4 0 30 Q-4 4 -30 0 Q-4 -4 0 -30Z" fill="${f}"/>`;
const heart=(x,y,s,f)=>`<path transform="translate(${x} ${y}) scale(${s})" d="M0 14 C-34 -8 -26 -38 0 -20 C26 -38 34 -8 0 14Z" fill="${f}" ${sw}/>`;
const feet=(y=356)=>`<path d="M128 ${y} h44 M228 ${y} h44" ${sw} fill="none"/>`;
const dots=(y,r=9,x1=148,x2=252)=>`<g class="eyes"><circle cx="${x1}" cy="${y}" r="${r}" fill="${K}"/><circle cx="${x2}" cy="${y}" r="${r}" fill="${K}"/></g>`;
const ringEye=(cx,cy,r,p)=>`<circle cx="${cx}" cy="${cy}" r="${r}" fill="#fff" ${sw}/><circle cx="${cx+4}" cy="${cy+4}" r="${p}" fill="${K}"/><circle cx="${cx+8}" cy="${cy-1}" r="${p*.35}" fill="#fff"/>`;
const blush=(y,x1=104,x2=296,r=16)=>`<ellipse cx="${x1}" cy="${y}" rx="${r}" ry="${r*.56}" fill="${AC}" opacity=".5"/><ellipse cx="${x2}" cy="${y}" rx="${r}" ry="${r*.56}" fill="${AC}" opacity=".5"/>`;
const bodyC=`<circle cx="200" cy="215" r="148" fill="${F}" ${sw}/>`;
const M={
ISTJ:()=>`${feet()}
<rect x="62" y="80" width="276" height="268" rx="86" fill="${F}" ${sw}/>
<path d="M66 128 Q62 66 150 62 L250 62 Q338 66 334 128 Q262 98 200 104 Q138 98 66 128Z" fill="${K}" ${sw}/>
<circle cx="147" cy="204" r="38" fill="none" ${sw}/><circle cx="253" cy="204" r="38" fill="none" ${sw}/><path d="M185 202 H215" ${sw} fill="none"/>
${dots(206,8,147,253)}<path d="M184 278 H216" ${sw} fill="none"/>
<path d="M200 306 l-14 12 l7 30 l7 8 l7 -8 l7 -30z" fill="${AC}" ${sw}/>`,
ISTP:()=>`<path d="M340 292 Q402 272 388 208" ${sw} fill="none"/>
<path d="M86 150 L96 52 L172 96" fill="${F}" ${sw}/><path d="M314 150 L304 52 L228 96" fill="${F}" ${sw}/>
<path d="M104 112 L107 80 L136 98Z" fill="${AC}"/><path d="M296 112 L293 80 L264 98Z" fill="${AC}"/>
<ellipse cx="200" cy="226" rx="150" ry="126" fill="${F}" ${sw}/>
<g class="eyes"><circle cx="145" cy="218" r="9" fill="${K}"/><circle cx="255" cy="218" r="9" fill="${K}"/><path d="M116 204 H174 M226 204 H284" ${sw} fill="none"/></g>
<path d="M184 264 Q192 274 200 264 Q208 274 216 264" ${sw} fill="none"/>
<circle cx="86" cy="248" r="12" fill="${AC}"/><path d="M86 260 Q74 306 116 334" stroke="${AC}" stroke-width="5" fill="none" stroke-linecap="round"/>${feet(350)}`,
INFJ:()=>`${feet(362)}${bodyC}
<g class="eyes"><path d="M120 210 Q148 240 176 210 M224 210 Q252 240 280 210" ${sw} fill="none"/></g>
<path d="M186 262 Q200 273 214 262" ${sw} fill="none"/>
<path d="M178 326 v-12 a22 22 0 0 1 44 0 v12" ${sw} fill="none"/><rect x="158" y="324" width="84" height="46" rx="14" fill="${AC}" ${sw}/><circle cx="200" cy="344" r="6" fill="${K}"/>
${star(334,70,.9,AC)}`,
INTP:()=>`${feet(358)}
<path d="M200 80 C310 70 355 170 345 250 C335 330 270 355 200 355 C120 355 55 330 58 245 C60 165 100 85 200 80Z" fill="${F}" ${sw}/>
<path d="M140 94 L120 36 L174 82Z M190 84 L198 22 L232 82Z M240 88 L274 38 L284 104Z" fill="${K}" ${sw}/>
<g class="eyes"><circle cx="140" cy="208" r="24" fill="#fff" ${sw}/><circle cx="145" cy="212" r="10" fill="${K}"/><circle cx="262" cy="210" r="17" fill="#fff" ${sw}/><circle cx="265" cy="213" r="7" fill="${K}"/></g>
<path d="M110 166 Q140 146 170 160 M240 182 L286 174" ${sw} fill="none"/>
<ellipse cx="205" cy="272" rx="10" ry="13" fill="${K}"/>
<circle cx="292" cy="96" r="8" fill="${F}" ${sw}/><circle cx="302" cy="72" r="12" fill="${F}" ${sw}/>
<circle cx="330" cy="22" r="50" fill="${F}" ${sw}/>
<g transform="translate(330 22)"><g class="gear"><circle r="20" fill="none" stroke="${AC}" stroke-width="8"/><circle r="29" fill="none" stroke="${AC}" stroke-width="10" stroke-dasharray="13 13"/></g></g>`,
INTJ:()=>`${feet(364)}
<path d="M200 74 L322 132 L322 292 Q322 350 262 354 L138 354 Q78 350 78 292 L78 132Z" fill="${F}" ${sw}/>
<path d="M140 70 L150 18 L178 50 L200 8 L222 50 L250 18 L260 70Z" fill="${AC}" ${sw}/>
<path d="M270 236 Q302 280 286 324" stroke="${K}" stroke-width="4" fill="none" stroke-linecap="round"/>
${dots(208)}<circle cx="252" cy="208" r="34" fill="none" ${sw}/>
<path d="M118 176 L176 192 M226 182 Q254 164 286 176" ${sw} fill="none"/>
<path d="M170 270 Q210 294 244 262" ${sw} fill="none"/>
<path d="M112 300 L292 344 M288 300 L108 344" ${sw} fill="none"/>`,
ENTJ:()=>`${feet()}
<rect x="66" y="84" width="268" height="266" rx="70" fill="${F}" ${sw}/>
<path d="M72 124 Q78 58 160 62 L206 26 L234 66 Q322 62 328 124 Q250 94 200 100 Q130 94 72 124Z" fill="${K}" ${sw}/>
${dots(212)}<path d="M114 184 L176 198 M224 198 L286 184" ${sw} fill="none"/>
<path d="M168 278 Q204 294 244 268" ${sw} fill="none"/>${star(200,322,.8,AC)}`,
ENTP:()=>`${feet()}${bodyC}
<path d="M150 80 Q136 40 166 28 M198 68 Q204 24 240 32 M250 82 Q278 50 300 66" ${sw} fill="none"/>
<path d="M326 24 l-30 52 h24 l-12 44 l44 -64 h-26 l16 -32z" fill="${AC}" ${sw}/>
${dots(206)}<path d="M118 178 L176 186 M226 168 Q254 148 284 168" ${sw} fill="none"/>
<path d="M156 252 Q200 316 244 252Z" fill="${K}" ${sw}/><path d="M178 288 Q200 272 222 288 Q200 306 178 288Z" fill="${AC}"/>`,
INFP:()=>`${feet()}${bodyC}
<path d="M54 204 Q50 70 200 66 Q350 70 346 204 Q330 142 268 126 Q230 160 150 132 Q90 150 54 204Z" fill="${K}" ${sw}/>
<g class="eyes">${ringEye(148,224,22,11)}${ringEye(252,224,22,11)}</g>
${blush(268)}<path d="M188 276 Q200 286 212 276" ${sw} fill="none"/>${heart(338,60,.9,AC)}`,
ENFJ:()=>`${feet()}${bodyC}
<path d="M62 244 Q26 224 22 182 M338 244 Q374 224 378 182" ${sw} fill="none"/>
<path d="M170 74 Q200 36 234 76" ${sw} fill="none"/>
<g class="eyes"><path d="M118 216 Q148 186 178 216 M222 216 Q252 186 282 216" ${sw} fill="none"/></g>
<path d="M160 252 Q200 304 240 252Z" fill="${K}" ${sw}/>${blush(250,98,302,14)}${heart(200,328,.9,AC)}`,
ENFP:()=>`${feet()}${bodyC}
<path d="M200 70 Q194 30 216 8" ${sw} fill="none"/><circle cx="220" cy="0" r="16" fill="${AC}" ${sw}/>
<g class="eyes">${ringEye(148,206,20,10)}${ringEye(252,206,20,10)}</g>
<path d="M150 248 Q200 318 250 248Z" fill="${K}" ${sw}/><path d="M176 288 Q200 272 224 288 Q200 308 176 288Z" fill="${AC}"/>
${blush(244,96,304)}${star(66,92,.6,AC)}${star(340,112,.5,AC)}`,
ISFJ:()=>`${feet(352)}
<ellipse cx="200" cy="226" rx="150" ry="130" fill="${F}" ${sw}/>
<path d="M62 192 Q58 70 200 70 Q342 70 338 192 Q320 122 200 122 Q80 122 62 192Z" fill="${K}" ${sw}/>
${dots(214)}${blush(250)}<path d="M186 262 Q200 274 214 262" ${sw} fill="none"/>
<path d="M92 300 Q200 340 308 300 L300 334 Q200 376 100 334Z" fill="${AC}" ${sw}/><path d="M248 338 L258 388 L284 372 L272 330Z" fill="${AC}" ${sw}/>`,
ESTJ:()=>`${feet()}
<rect x="62" y="84" width="276" height="266" rx="56" fill="${F}" ${sw}/>
<path d="M64 128 Q64 66 130 66 L270 66 Q336 66 336 128 L336 112 Q200 88 64 112Z" fill="${K}" ${sw}/>
${dots(216)}<path d="M110 186 L182 194 M218 194 L290 186" stroke="${K}" stroke-width="11" stroke-linecap="round" fill="none"/>
<path d="M172 280 H228" ${sw} fill="none"/>
<path d="M150 296 Q200 350 250 296" stroke="${AC}" stroke-width="6" fill="none" stroke-linecap="round"/><circle cx="200" cy="334" r="15" fill="${AC}" ${sw}/>`,
ESFJ:()=>`${feet()}${bodyC}
<path d="M200 76 L146 40 L148 106Z M200 76 L254 40 L252 106Z" fill="${AC}" ${sw}/><circle cx="200" cy="76" r="12" fill="${AC}" ${sw}/>
${dots(214)}<path d="M120 198 l-12 -9 M176 198 l12 -9 M224 198 l-12 -9 M280 198 l12 -9" ${sw} fill="none"/>
<path d="M156 250 Q200 306 244 250Z" fill="${K}" ${sw}/>${blush(250,96,304,20)}`,
ISFP:()=>`${feet(352)}
<ellipse cx="200" cy="226" rx="150" ry="128" fill="${F}" ${sw}/>
<path d="M60 224 Q54 160 90 140 M340 224 Q346 160 310 140" ${sw} fill="none"/>
<path d="M92 124 Q116 54 214 56 Q304 60 318 124 Q210 98 92 124Z" fill="${AC}" ${sw}/><circle cx="236" cy="50" r="9" fill="${AC}" ${sw}/>
${dots(216,8)}<path d="M186 266 Q200 278 214 266" ${sw} fill="none"/>${blush(252)}<circle cx="306" cy="304" r="15" fill="${AC}"/>`,
ESTP:()=>`${feet()}
<rect x="62" y="84" width="276" height="266" rx="96" fill="${F}" ${sw}/>
<path d="M66 144 Q200 96 334 144 L334 172 Q200 124 66 172Z" fill="${AC}" ${sw}/>
<rect x="102" y="192" width="84" height="54" rx="20" fill="${K}"/><rect x="214" y="192" width="84" height="54" rx="20" fill="${K}"/><path d="M186 210 H214" ${sw} fill="none"/>
<path d="M116 206 l14 -4 M228 206 l14 -4" stroke="#fff" stroke-width="5" stroke-linecap="round"/>
<path d="M154 276 Q212 312 256 266" ${sw} fill="none"/>`,
ESFP:()=>`${feet()}${bodyC}
<path d="M148 92 L200 -6 L252 92Z" fill="${AC}" ${sw}/><circle cx="200" cy="-8" r="11" fill="${F}" ${sw}/><circle cx="184" cy="56" r="5" fill="${F}"/><circle cx="214" cy="40" r="5" fill="${F}"/><circle cx="222" cy="72" r="5" fill="${F}"/>
${dots(210)}<path d="M150 250 Q200 316 250 250Z" fill="${K}" ${sw}/><path d="M176 286 Q200 270 224 286 Q200 306 176 286Z" fill="${AC}"/>
${blush(246,96,304)}${star(62,100,.6,AC)}${star(344,120,.5,AC)}`
};
function mascot(key,size){return `<svg viewBox="0 0 400 400" width="${size}" height="${size}" style="overflow:visible;display:block">${M[key]()}</svg>`}
function animFaces(root,t,off=0){
  root.querySelectorAll('.eyes').forEach(e=>{const p=(t+off)%3.6;const k=p<.14?1-Math.sin(p/.14*Math.PI)*.9:1;e.style.transform=`scaleY(${k})`});
  root.querySelectorAll('.gear').forEach(g=>g.style.transform=`rotate(${t*70}deg)`);
}
