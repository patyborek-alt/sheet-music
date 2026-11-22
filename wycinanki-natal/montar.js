// Monta os PDFs para impressão a partir de paths.json (gerado por gerar.py)
//  - wycinanki-natal-<modo>.pdf : tudo junto, com página de instruções
//  - pdf/<modo>/<desenho>.pdf    : cada desenho em arquivo separado
const fs = require('fs'); const { chromium } = require('playwright');
const [,, json, outDir] = process.argv;
const P = JSON.parse(fs.readFileSync(json));
const order = ['choinka','rozeta','sniezynka','bombka','dzwonek','betlejemska','faixa',
               'ptaszki','aniol','anioly','wesolych','swiat','wesolych_esp','swiat_esp'];
function svg(k, mode, cls = '') {
  const d = P[k].d, b = P[k].bounds, pad = 2;
  const vb = `${b[0]-pad} ${b[1]-pad} ${b[2]-b[0]+2*pad} ${b[3]-b[1]+2*pad}`;
  const st = mode === 'preto' ? 'fill="#000"' : 'fill="#d6d6d6" stroke="#000" stroke-width="0.35"';
  return `<svg class="${cls}" xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" width="${b[2]-b[0]+2*pad}mm" height="${b[3]-b[1]+2*pad}mm"><path fill-rule="evenodd" ${st} d="${d}"/></svg>`;
}
const RULER = '<span class="ruler">├──────── 5 cm ────────┤</span>';
function page(k, mode, n) {
  const inner = k === 'faixa' ? svg(k, mode) + svg(k, mode) : svg(k, mode);
  const land = P[k].land ? ' land' : '';
  const hint = mode === 'preto' ? 'preto' : 'cinza';
  return `<section class="pg${land}"><div class="art">${inner}</div>
  <footer><b>${P[k].title}</b><span>${hint} = fica pintado · branco = fica coberto${n ? ' · pág. ' + n : ''}</span>${RULER}</footer></section>`;
}
const css = `@page{size:A4;margin:0} @page land{size:A4 landscape;margin:0}
*{box-sizing:border-box} body{margin:0;font-family:Georgia,serif}
.pg{width:210mm;height:297mm;padding:12mm;display:flex;flex-direction:column;page-break-after:always;overflow:hidden}
.pg.land{page:land;width:297mm;height:210mm}
.art{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly}
footer{display:flex;justify-content:space-between;align-items:center;gap:4mm;font-size:8.5pt;color:#444;border-top:.3mm solid #999;padding-top:2mm}
.ruler{display:inline-block;width:50mm;flex:none;text-align:center;font-family:monospace;font-size:8pt;white-space:nowrap;overflow:hidden}
h1{font-size:24pt;margin:0 0 2mm;color:#b3001b} h2{font-size:12.5pt;margin:4.5mm 0 1.5mm;color:#1d5c2e}
.intro{flex:1;font-size:9.6pt;line-height:1.4} .intro li{margin:.8mm 0} .intro ul,.intro ol{margin:0;padding-left:6mm}
.leg{display:flex;gap:8mm;margin:3mm 0} .leg div{display:flex;align-items:center;gap:2mm}
.sw{width:8mm;height:8mm;border:.3mm solid #000;flex:none}
.thumbs{display:flex;flex-wrap:wrap;gap:3mm 4mm;margin-top:4mm;align-items:center;justify-content:center}
.thumbs svg{height:19mm;width:auto;max-width:34mm}`;
function capa(mode) {
  const dark = mode === 'preto' ? '#000' : '#d6d6d6';
  return `<section class="pg"><div class="intro">
<h1>Wycinanki de Natal</h1>
<div>Moldes de recorte folclórico polonês para pintar a vitrine com spray (neve artificial ou tinta spray para vidro).
O desenho que você vê na folha é <b>exatamente o que fica pintado</b> no vidro.</div>
<div class="leg"><div><span class="sw" style="background:${dark}"></span> <b>fica pintado</b> no vidro (você tira esta peça antes do spray)</div>
<div><span class="sw" style="background:#fff"></span> <b>fica coberto</b> — o vidro continua transparente</div></div>
<h2>Material</h2><ul>
<li><b>Papel adesivo A4 para impressora</b> (vinil fosco ou papel contact imprimível) — ele gruda no vidro e segura todas as pecinhas brancas no lugar. Alternativa: imprima em papel comum e cole sobre papel contact transparente.</li>
<li>Estilete afiado, base de corte, spray, fita crepe e jornal para proteger em volta.</li></ul>
<h2>Passo a passo</h2><ol>
<li>Imprima a <b>100 % / tamanho real</b> (confira a régua de 5 cm). Para vitrine grande, amplie em A3 (141 %).</li>
<li>Com o estilete, corte <b>todas as linhas</b>: o contorno do desenho e o contorno de cada furinho branco. Não corte a folha em volta — ela é a proteção.</li>
<li>Limpe o vidro com álcool. Tire o verso do adesivo e cole <b>a folha inteira</b> no vidro, alisando do centro para fora com um pano.</li>
<li><b>Descole e jogue fora a parte ${mode === 'preto' ? 'preta' : 'cinza'}.</b> Nos desenhos ela é uma peça só e sai inteira (no texto, cada letra sai separada); os furinhos brancos e a moldura da folha continuam colados no vidro.</li>
<li>Aperte bem as bordas de tudo que ficou. Proteja em volta da folha com jornal e fita crepe.</li>
<li>Agite o spray e aplique a ~30 cm, em camadas finas, só sobre a área aberta. Espere 1–2 min.</li>
<li>Retire a moldura e as pecinhas brancas (a ponta do estilete ajuda). Pronto: o desenho aparece pintado no vidro, com a renda transparente por dentro.</li></ol>
<h2>Dicas</h2><ul>
<li>Os desenhos são simétricos e funcionam dos dois lados do vidro. <b>O texto Wesołych Świąt não</b>: para quem lê da rua, use a versão normal se pintar <b>por fora</b> e a versão <b>ESPELHADA</b> se pintar <b>por dentro</b>.</li>
<li>Para emendar os textos, cole „Wesołych” em cima e „Świąt” embaixo.</li>
<li>Neve spray sai com pano úmido; tinta spray para vidro sai com raspador.</li></ul>
<div class="thumbs">${order.filter(k => !k.endsWith('_esp')).map(k => svg(k, mode)).join('')}</div>
</div><footer><b>Wycinanki de Natal — instruções</b><span>versão ${mode === 'preto' ? 'preenchida' : 'econômica (contorno)'}</span>${RULER}</footer></section>`;
}
const doc = body => `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${body}</body></html>`;
(async () => {
  const browser = await chromium.launch();
  const p = await browser.newPage();
  async function pdf(html, path) {
    await p.setContent(html);
    await p.pdf({ path, printBackground: true, preferCSSPageSize: true });
  }
  for (const mode of ['preto', 'economico']) {
    let pages = [capa(mode)], n = 1;
    for (const k of order) pages.push(page(k, mode, ++n));
    await pdf(doc(pages.join('')), `${outDir}/wycinanki-natal-${mode}.pdf`);
    fs.mkdirSync(`${outDir}/pdf/${mode}`, { recursive: true });
    for (const [i, k] of order.entries())
      await pdf(doc(page(k, mode, 0)), `${outDir}/pdf/${mode}/${String(i + 1).padStart(2, '0')}-${k}.pdf`);
    await pdf(doc(capa(mode)), `${outDir}/pdf/${mode}/00-instrucoes.pdf`);
  }
  await browser.close();
})();
