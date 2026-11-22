// Monta o PDF para impressão a partir de paths.json (gerado por gerar.py)
const fs = require('fs'); const { chromium } = require('playwright');
const [,, json, outDir] = process.argv;
const P = JSON.parse(fs.readFileSync(json));
const order = ['choinka','rozeta','sniezynka','bombka','dzwonek','betlejemska','faixa'];
function svg(k, mode, w, h) {
  const d = P[k].d, b = P[k].bounds;
  const pad = 2, vb = `${b[0]-pad} ${b[1]-pad} ${b[2]-b[0]+2*pad} ${b[3]-b[1]+2*pad}`;
  const st = mode === 'preto' ? 'fill="#000"' : 'fill="#e4e4e4" stroke="#000" stroke-width="0.35"';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" width="${b[2]-b[0]+2*pad}mm" height="${b[3]-b[1]+2*pad}mm"><path fill-rule="evenodd" ${st} d="${d}"/></svg>`;
}
function page(inner, title, n) {
  return `<section class="pg"><div class="art">${inner}</div>
  <footer><b>${title}</b><span>${n}</span><span class="ruler">├──────── 5 cm ────────┤</span></footer></section>`;
}
const css = `@page{size:A4;margin:0} *{box-sizing:border-box} body{margin:0;font-family:Georgia,serif}
.pg{width:210mm;height:297mm;padding:12mm;display:flex;flex-direction:column;page-break-after:always}
.art{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly}
footer{display:flex;justify-content:space-between;align-items:center;font-size:9pt;color:#444;border-top:.3mm solid #999;padding-top:2mm}
.ruler{display:inline-block;width:50mm;text-align:center;font-family:monospace;font-size:8pt;white-space:nowrap;overflow:hidden}
h1{font-size:26pt;margin:0 0 2mm;color:#b3001b} h2{font-size:13pt;margin:6mm 0 2mm;color:#1d5c2e}
.intro{flex:1;font-size:10pt;line-height:1.45} .intro li{margin:1mm 0}
.leg{display:flex;gap:8mm;margin:4mm 0} .leg div{display:flex;align-items:center;gap:2mm}
.sw{width:9mm;height:9mm;border:.3mm solid #000}
.thumbs{display:flex;gap:3mm;margin-top:5mm;align-items:center;justify-content:space-between}
.thumbs svg{width:23mm;height:auto;max-height:28mm}
.pg{overflow:hidden}`;
function capa(mode) {
  const dark = mode === 'preto' ? '#000' : '#e4e4e4';
  return `<section class="pg"><div class="intro">
<h1>Wycinanki de Natal</h1>
<div>Stencils de recorte folclórico polonês para pintar vitrine de vidro com spray (neve artificial ou tinta spray para vidro).</div>
<div class="leg"><div><span class="sw" style="background:${dark}"></span> papel que <b>fica</b> (máscara)</div>
<div><span class="sw" style="background:#fff"></span> <b>recortar e jogar fora</b> — o spray passa por aqui</div></div>
<h2>Impressão</h2><ul>
<li>Imprimir em A4 a <b>100 % / tamanho real</b> (desmarque "ajustar à página"). Confira a régua de 5 cm no rodapé.</li>
<li>Para vitrines grandes: imprima ampliado em A3 (141 %) ou em gráfica — as pontes ficam ainda mais firmes.</li>
<li>Papel ideal: sulfite 120–180 g, cartolina fina ou papel-contact (adesivo). Contact gruda sozinho no vidro e não deixa o spray vazar por baixo.</li></ul>
<h2>Recorte</h2><ul>
<li>Use estilete bem afiado sobre base de corte. Comece pelos furos pequenos do centro e termine pelo contorno externo.</li>
<li>Cada desenho foi verificado: é <b>uma peça só</b>, nenhuma parte solta, e todas as pontes de papel têm no mínimo 2 mm.</li>
<li>Furadores de papel redondos de 3–6 mm agilizam os furinhos.</li></ul>
<h2>Aplicação no vidro</h2><ol>
<li>Limpe e seque bem o vidro (álcool).</li>
<li>Borrife levemente água com 1 gota de detergente no vidro, assente o papel e alise com pano — ele adere sem fita. Ou use fita crepe enrolada atrás / cola spray reposicionável.</li>
<li>Pressione bem todas as pontinhas e pontes contra o vidro.</li>
<li>Agite o spray e aplique a ~30 cm, em camadas finas, primeiro sobre os furos e depois esfumando em volta do contorno.</li>
<li>Espere 1–2 min e retire o papel puxando por uma ponta, devagar. Resultado: o desenho aparece <b>transparente</b>, com a renda de neve nos furos.</li></ol>
<h2>Dicas</h2><ul>
<li>Todos os desenhos são simétricos — funcionam por dentro ou por fora do vidro sem espelhar.</li>
<li>Quer o efeito inverso (desenho branco em vidro limpo)? Guarde as peças recortadas dos furos e use o "rodapé" e a roseta como molde de contorno.</li>
<li>Neve spray sai com pano úmido; tinta spray para vidro sai com raspador/estilete.</li></ul>
<div class="thumbs">${order.map(k => svg(k, mode)).join('')}</div>
</div><footer><b>Wycinanki de Natal — instruções</b><span>versão ${mode === 'preto' ? 'preenchida' : 'econômica (contorno)'}</span><span class="ruler">├──────── 5 cm ────────┤</span></footer></section>`;
}
(async () => {
  const browser = await chromium.launch();
  for (const mode of ['preto', 'economico']) {
    let pages = [capa(mode)]; let n = 1;
    for (const k of order) {
      const inner = k === 'faixa' ? svg(k, mode) + svg(k, mode) : svg(k, mode);
      pages.push(page(inner, P[k].title, `pág. ${++n}`));
    }
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${pages.join('')}</body></html>`;
    fs.writeFileSync(`${outDir}/wycinanki-natal-${mode}.html`, html);
    const p = await browser.newPage();
    await p.setContent(html);
    await p.pdf({ path: `${outDir}/wycinanki-natal-${mode}.pdf`, format: 'A4', printBackground: true, preferCSSPageSize: true });
    if (process.env.PREVIEW) { await p.setViewportSize({width: 794, height: 1123}); await p.screenshot({path: `${process.env.PREVIEW}/prev-${mode}.png`, fullPage: true}); }
    await p.close();
  }
  await browser.close();
})();
