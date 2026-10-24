// Reels da grade 26/10–01/11 ("Sinal Vivo"): composição própria, cenas guiadas por props (timeline em segundos).
// Cenas: foto | texto | colagem | janelas | notebook | flashes | fecho. Sem narração: texto em tela + som desenhado.
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
  continueRender, delayRender, Easing} from 'remotion';

const INK = '#0B0D12', AZUL = '#2F6BFF', ACIDO = '#C7FF3D', LAV = '#B8A6FF', MARFIM = '#F5F0E6', CINZA = '#7D8492', PAINEL = '#171B24';
export type CenaV = {inicio: number; fim: number; tipo: string; [k: string]: any};
export type PropsV = {fps: number; duracao: number; audio: string | null; cenas: CenaV[]; arroba: string};

const FONTES: [string, string, number][] = [['SH', 'stack-sans-headline-latin-700-normal.woff2', 700], ['ST', 'stack-sans-text-latin-500-normal.woff2', 500]];
const useFontes = () => {
  const [h] = React.useState(() => delayRender('fontes'));
  React.useEffect(() => {
    const t = setTimeout(() => continueRender(h), 8000);
    Promise.all(FONTES.map(([n, f, w]) => new FontFace(n, `url(${staticFile('fontes/' + f)})`, {weight: String(w)}).load()
      .then((ff) => (document as any).fonts.add(ff)).catch(() => null))).finally(() => { clearTimeout(t); continueRender(h); });
  }, [h]);
};

const cor = (t: string, acento: string) => t.split(/(\*[^*]+\*)/).map((p, i) => p.startsWith('*') ? <span key={i} style={{color: acento}}>{p.slice(1, -1)}</span> : <React.Fragment key={i}>{p}</React.Fragment>);

const Grao: React.FC<{o?: number}> = ({o = 0.16}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{pointerEvents: 'none', opacity: o, mixBlendMode: 'overlay',
    backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='${f % 9}'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")`}} />;
};

// texto palavra a palavra (spring), posição vertical em y
const Palavras: React.FC<{t: string; y: number; tam?: number; acento?: string; cl?: string; atraso?: number; entre?: number; alinha?: 'center' | 'left'; w?: number}> =
({t, y, tam = 96, acento = ACIDO, cl = MARFIM, atraso = 0, entre = 3, alinha = 'center', w = 900}) => {
  const f = useCurrentFrame();
  const palavras: {w: string; a: boolean}[] = [];
  let aberto = false;
  t.split(/(\*)/).forEach((p) => { if (p === '*') { aberto = !aberto; return; } p.split(' ').filter(Boolean).forEach((x) => palavras.push({w: x, a: aberto})); });
  return (
    <div style={{position: 'absolute', left: (1080 - w) / 2, width: w, top: y, display: 'flex', flexWrap: 'wrap', justifyContent: alinha === 'center' ? 'center' : 'flex-start', gap: `0 ${tam * 0.26}px`,
      font: `700 ${tam}px/1.04 SH`, letterSpacing: -tam * 0.025, color: cl, textShadow: '0 6px 0 rgba(0,0,0,.35)'}}>
      {palavras.map((p, i) => {
        const e = spring({frame: f - atraso - i * entre, fps: 30, config: {damping: 16, stiffness: 190}});
        return <span key={i} style={{display: 'inline-block', color: p.a ? acento : cl, opacity: Math.min(1, e * 1.6), transform: `translateY(${(1 - e) * 46}px) scale(${0.94 + 0.06 * e})`, filter: `blur(${(1 - e) * 10}px)`}}>{p.w}</span>;
      })}
    </div>
  );
};

const useCam = (tipo: string, dur: number) => {
  const f = useCurrentFrame();
  const t = Easing.out(Easing.cubic)(Math.min(1, f / Math.max(1, dur)));
  const l = Math.min(1, f / Math.max(1, dur));
  if (tipo === 'desacelera') return `scale(${1.28 - 0.22 * t}) translateY(${(1 - t) * -24}px)`;       // chega e desacelera
  if (tipo === 'empurra') return `scale(${1.04 + 0.16 * l})`;
  if (tipo === 'deriva-esq') return `scale(1.18) translateX(${40 - 80 * l}px)`;
  if (tipo === 'deriva-dir') return `scale(1.18) translateX(${-40 + 80 * l}px)`;
  if (tipo === 'sobe') return `scale(1.16) translateY(${50 - 100 * l}px)`;
  return `scale(1.08)`;
};

// ---------- cena: foto com grade azul-tinta ----------
const Foto: React.FC<{c: CenaV; dur: number}> = ({c, dur}) => {
  const cam = useCam(c.cam || 'empurra', dur);
  return (
    <AbsoluteFill style={{background: INK}}>
      <AbsoluteFill style={{transform: cam, transformOrigin: c.origem || '50% 50%'}}>
        <Img src={staticFile(c.img)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: c.pos || '50% 50%', filter: `saturate(${c.sat ?? 0.55}) contrast(1.08) brightness(${c.brilho ?? 0.9})`}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: AZUL, mixBlendMode: 'color', opacity: c.tinta ?? 0.55}} />
      <AbsoluteFill style={{background: `linear-gradient(180deg,rgba(11,13,18,.78) 0%,rgba(11,13,18,.05) 34%,rgba(11,13,18,.12) 58%,rgba(11,13,18,.9) 100%)`}} />
      <AbsoluteFill style={{background: 'radial-gradient(120% 90% at 50% 50%,transparent 55%,rgba(0,0,0,.55))'}} />
      {c.texto && <Palavras t={c.texto} y={c.y ?? 1180} tam={c.tam ?? 92} atraso={c.atraso ?? 6} acento={c.acento ?? ACIDO} />}
      {c.legenda && <div style={{position: 'absolute', left: 90, top: c.yl ?? 300, font: '700 30px SH', letterSpacing: 6, color: MARFIM, opacity: .85}}>{c.legenda}</div>}
    </AbsoluteFill>
  );
};

// ---------- cena: texto sobre cor ----------
const Texto: React.FC<{c: CenaV; dur: number}> = ({c, dur}) => {
  const f = useCurrentFrame();
  const fundo = c.fundo || INK;
  const claro = fundo === MARFIM;
  const virada = c.virada ? interpolate(f, [c.virada, c.virada + 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  return (
    <AbsoluteFill style={{background: fundo}}>
      {c.virada != null && <AbsoluteFill style={{background: AZUL, clipPath: `inset(0 ${(1 - virada) * 100}% 0 0)`}} />}
      {!c.virada && <AbsoluteFill style={{background: `radial-gradient(70% 45% at 50% 60%,${c.brilho || 'rgba(47,107,255,.16)'},transparent 70%)`}} />}
      {c.linhas.map((l: any, i: number) => (
        <Palavras key={i} t={l.t} y={l.y} tam={l.tam ?? 104} acento={l.acento ?? ACIDO} cl={l.cl ?? (claro ? INK : MARFIM)} atraso={(l.atraso ?? 0)} entre={l.entre ?? 4} w={l.w ?? 900} />
      ))}
      {c.regua && <div style={{position: 'absolute', left: 90, top: c.regua, width: interpolate(f, [4, 20], [0, 220], {extrapolateRight: 'clamp'}), height: 10, background: c.reguaCor || ACIDO}} />}
    </AbsoluteFill>
  );
};

// ---------- itens gráficos (sem dados reais) ----------
const Item: React.FC<{k: string; seed?: number; fundo?: string}> = ({k, seed = 0, fundo}) => {
  const r = (n: number) => ((Math.sin(seed * 12.9898 + n * 78.233) * 43758.5453) % 1 + 1) % 1;
  const base: React.CSSProperties = {position: 'absolute', inset: 0, overflow: 'hidden'};
  if (k === 'planilha') {
    const cols = 6, lin = 14;
    return <div style={{...base, background: '#E9ECEF'}}><div style={{position: 'absolute', left: -60, top: 160, width: 1300, transform: `rotate(${-4 + r(1) * 8}deg)`, background: '#fff', boxShadow: '0 40px 0 rgba(0,0,0,.25)'}}>
      {Array.from({length: lin}).map((_, y) => <div key={y} style={{display: 'flex', height: 96, background: y === 0 ? '#D9DEE5' : '#fff'}}>{Array.from({length: cols}).map((_, x) => <div key={x} style={{flex: 1, borderRight: '3px solid #C5CBD3', borderBottom: '3px solid #C5CBD3', position: 'relative'}}>{y > 0 && r(x * 7 + y) > 0.55 && <div style={{position: 'absolute', left: 14, top: 36, width: `${30 + r(x + y) * 50}%`, height: 20, background: '#D1D6DD', borderRadius: 10}} />}</div>)}</div>)}
    </div></div>;
  }
  if (k === 'agenda') {
    return <div style={{...base, background: MARFIM}}>
      <div style={{position: 'absolute', left: 110, top: 300, right: 110, height: 1160, background: '#fff', boxShadow: '0 36px 0 rgba(0,0,0,.2)', transform: `rotate(${-2 + r(2) * 4}deg)`}}>
        <div style={{height: 150, background: INK}} />
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(7,1fr)', height: 1010}}>{Array.from({length: 35}).map((_, i) => <div key={i} style={{border: '2px solid #E1DDD2', background: i === 17 + (seed % 5) ? ACIDO : 'transparent', position: 'relative'}}>{i % 4 === 0 && <div style={{position: 'absolute', left: 8, bottom: 14, width: '55%', height: 10, background: '#D6D1C5', borderRadius: 5}} />}</div>)}</div>
      </div></div>;
  }
  if (k === 'postits') {
    const cs = [ACIDO, LAV, MARFIM, '#7FA2FF', ACIDO, LAV, MARFIM, '#7FA2FF'];
    return <div style={{...base, background: '#1a1d26'}}>{cs.map((c, i) => <div key={i} style={{position: 'absolute', left: 60 + (i % 3) * 340 + r(i) * 40, top: 280 + Math.floor(i / 3) * 420 + r(i + 9) * 50, width: 320, height: 320, background: c, transform: `rotate(${-14 + r(i + 3) * 28}deg)`, boxShadow: '0 22px 0 rgba(0,0,0,.35)'}}>
      {[0, 1, 2].map((j) => <div key={j} style={{position: 'absolute', left: 30, top: 60 + j * 56, width: `${50 + r(i + j) * 40}%`, height: 16, background: INK, opacity: .25, borderRadius: 8}} />)}</div>)}</div>;
  }
  if (k === 'notifs') {
    return <div style={{...base, background: INK}}>{Array.from({length: 7}).map((_, i) => <div key={i} style={{position: 'absolute', left: 70 + r(i) * 60, top: 280 + i * 170, width: 860 - r(i + 4) * 120, height: 140, borderRadius: 40, background: i % 3 === 0 ? ACIDO : 'rgba(245,240,230,.92)', boxShadow: '0 16px 0 rgba(0,0,0,.4)', display: 'flex', alignItems: 'center', padding: '0 34px', gap: 26}}>
      <div style={{width: 70, height: 70, borderRadius: 22, background: i % 3 === 0 ? INK : AZUL}} />
      <div style={{flex: 1}}><div style={{width: '55%', height: 20, background: INK, opacity: .75, borderRadius: 10}} /><div style={{width: '85%', height: 16, background: INK, opacity: .28, borderRadius: 8, marginTop: 18}} /></div></div>)}</div>;
  }
  if (k === 'celular' || k === 'celular-desfoque') {
    return <div style={{...base, background: INK}}><div style={{position: 'absolute', left: 190, top: 250, width: 700, height: 1320, borderRadius: 90, background: '#222733', border: '14px solid #2c3140', boxShadow: '0 40px 0 rgba(0,0,0,.45)', overflow: 'hidden'}}>
      <div style={{filter: 'blur(14px)', padding: 50}}>{Array.from({length: 9}).map((_, i) => <div key={i} style={{height: 110, borderRadius: 30, background: i % 4 === 1 ? AZUL : 'rgba(245,240,230,.9)', marginBottom: 28, width: `${60 + r(i) * 40}%`, marginLeft: i % 2 ? 'auto' : 0}} />)}</div>
    </div></div>;
  }
  if (k === 'papel') {
    return <div style={{...base, background: '#12151c'}}><div style={{position: 'absolute', left: 150, top: 330, width: 780, height: 1060, background: MARFIM, transform: `rotate(${-5 + r(3) * 8}deg)`, boxShadow: '26px 30px 0 rgba(0,0,0,.55)', clipPath: 'polygon(0 0,100% 0,100% 92%,86% 100%,0 100%)'}}>
      {Array.from({length: 11}).map((_, i) => <div key={i} style={{position: 'absolute', left: 60, top: 150 + i * 78, width: i % 4 === 3 ? '40%' : '78%', height: 14, background: INK, opacity: .22, borderRadius: 7}} />)}
      <div style={{position: 'absolute', left: 60, top: 70, width: 260, height: 26, background: INK, opacity: .5, borderRadius: 13}} />
    </div></div>;
  }
  if (k === 'mensagem') {
    return <div style={{...base, background: '#0f1218'}}>
      <div style={{position: 'absolute', right: 120, top: 520, width: 700, borderRadius: 50, borderBottomRightRadius: 12, background: AZUL, padding: '46px 52px', boxShadow: '0 18px 0 rgba(0,0,0,.5)'}}>
        <div style={{width: '90%', height: 22, background: MARFIM, borderRadius: 11, opacity: .9}} /><div style={{width: '64%', height: 22, background: MARFIM, borderRadius: 11, opacity: .9, marginTop: 24}} />
        <div style={{position: 'absolute', right: 34, bottom: -64, font: '500 34px ST', color: CINZA, letterSpacing: 2}}>✓✓ visto</div></div>
      <div style={{position: 'absolute', left: 120, top: 920, width: 220, height: 90, borderRadius: 45, background: PAINEL, border: '3px dashed #3b4252', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16}}>{[0, 1, 2].map((i) => <div key={i} style={{width: 16, height: 16, borderRadius: 8, background: CINZA, opacity: .5}} />)}</div>
    </div>;
  }
  if (k === 'caderno') {
    return <div style={{...base}}><Img src={staticFile('af/n-caneta.png')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'saturate(.5) contrast(1.1)'}} /><AbsoluteFill style={{background: AZUL, mixBlendMode: 'color', opacity: .45}} /></div>;
  }
  return <div style={{...base, background: fundo || INK}} />;
};

// ---------- cena: colagem acelerada ----------
const Colagem: React.FC<{c: CenaV}> = ({c}) => {
  const f = useCurrentFrame();
  const its: {k: string; d: number}[] = c.itens;
  let acc = 0, idx = its.length - 1, local = 0;
  for (let i = 0; i < its.length; i++) { if (f < acc + its[i].d) { idx = i; local = f - acc; break; } acc += its[i].d; }
  const it = its[idx];
  const sh = local < 2 ? 1 : 0;
  return (
    <AbsoluteFill style={{background: INK}}>
      <AbsoluteFill style={{transform: `scale(${1.04 + local * 0.012}) translateX(${Math.sin(f * 1.7) * 6}px)`}}><Item k={it.k} seed={idx + 1} /></AbsoluteFill>
      <AbsoluteFill style={{background: ACIDO, opacity: sh * 0.28, mixBlendMode: 'screen'}} />
      <AbsoluteFill style={{boxShadow: `inset 0 0 0 ${local % 6 < 1 ? 12 : 0}px ${ACIDO}`}} />
      {c.texto && <Palavras t={c.texto} y={c.y ?? 1240} tam={74} acento={ACIDO} atraso={4} />}
    </AbsoluteFill>
  );
};

// ---------- cena: flashes (Sáb) ----------
const Flashes: React.FC<{c: CenaV}> = ({c}) => {
  const f = useCurrentFrame();
  const its: {k: string; d: number; l?: string}[] = c.itens;
  let acc = 0, idx = its.length - 1, local = 0;
  for (let i = 0; i < its.length; i++) { if (f < acc + its[i].d) { idx = i; local = f - acc; break; } acc += its[i].d; }
  const it = its[idx];
  return (
    <AbsoluteFill style={{background: INK}}>
      <AbsoluteFill style={{transform: `scale(${1.02 + local * 0.006})`}}><Item k={it.k} seed={idx + 3} /></AbsoluteFill>
      <AbsoluteFill style={{background: ACIDO, opacity: interpolate(local, [0, 3, 6], [0.85, 0.2, 0], {extrapolateRight: 'clamp'}), mixBlendMode: 'hard-light'}} />
      <AbsoluteFill style={{background: 'radial-gradient(90% 70% at 50% 50%,transparent 45%,rgba(0,0,0,.65))'}} />
      {it.l && <div style={{position: 'absolute', left: 90, bottom: 380, font: '700 44px SH', letterSpacing: 6, color: ACIDO, textShadow: '0 5px 0 rgba(0,0,0,.6)'}}>{it.l}</div>}
    </AbsoluteFill>
  );
};

// ---------- cena: janelas abstratas que se alinham ----------
const Janelas: React.FC<{c: CenaV; dur: number}> = ({c, dur}) => {
  const f = useCurrentFrame();
  const n = 8, alinha = c.alinhaEm ?? 60;
  const e = spring({frame: f - alinha, fps: 30, config: {damping: 15, stiffness: 140}});
  const r = (i: number, k: number) => ((Math.sin(i * 91.7 + k * 17.3) * 43758.5453) % 1 + 1) % 1;
  return (
    <AbsoluteFill style={{background: INK}}>
      <AbsoluteFill style={{background: 'radial-gradient(70% 40% at 50% 55%,rgba(199,255,61,.10),transparent 70%)'}} />
      {Array.from({length: n}).map((_, i) => {
        const w = 470, h = 300;
        const cx0 = 140 + r(i, 1) * 800, cy0 = 330 + r(i, 2) * 1050, rot0 = -22 + r(i, 3) * 44;
        const ent = interpolate(f, [i * 3, i * 3 + 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const dx = Math.sin(f / 9 + i) * 14 * (1 - e), dy = Math.cos(f / 11 + i * 2) * 12 * (1 - e);
        const cx1 = 285 + (i % 2) * 510, cy1 = 420 + Math.floor(i / 2) * 340;
        const cx = cx0 + (cx1 - cx0) * e + dx, cy = cy0 + (cy1 - cy0) * e + dy, rot = rot0 * (1 - e);
        return (
          <div key={i} style={{position: 'absolute', left: cx - w / 2, top: cy - h / 2, width: w, height: h, borderRadius: 26, background: i % 3 === 0 ? MARFIM : '#1d222e', transform: `rotate(${rot}deg) scale(${ent * (1 + (1 - e) * 0.12)})`,
            boxShadow: `0 ${18 + (1 - e) * 20}px 0 rgba(0,0,0,.45)`, border: i % 3 === 0 ? 'none' : '2px solid #313848', overflow: 'hidden'}}>
            <div style={{height: 58, background: i % 3 === 0 ? '#DDD7C8' : '#262c3a', display: 'flex', alignItems: 'center', gap: 12, padding: '0 22px'}}>
              {[0, 1, 2].map((j) => <div key={j} style={{width: 16, height: 16, borderRadius: 8, background: j === 0 && i === 2 ? ACIDO : (i % 3 === 0 ? '#B9B2A1' : '#3a4153')}} />)}
            </div>
            <div style={{padding: 30}}>
              {[0, 1, 2].map((j) => <div key={j} style={{height: 20, borderRadius: 10, marginBottom: 24, width: `${[88, 66, 78][j] - r(i, j) * 20}%`, background: i % 3 === 0 ? INK : MARFIM, opacity: .16 + j * 0.05}} />)}
            </div>
          </div>);
      })}
      {c.texto && <Palavras t={c.texto} y={c.y ?? 1500} tam={60} acento={ACIDO} atraso={alinha + 10} />}
    </AbsoluteFill>
  );
};

// ---------- cena: notebook com tela real ----------
const Notebook: React.FC<{c: CenaV; dur: number}> = ({c, dur}) => {
  const f = useCurrentFrame();
  const l = Math.min(1, f / Math.max(1, dur));
  const rotY = -22 + 14 * l, rotX = 10 - 4 * l;
  const brilho = interpolate(l, [0, 1], [-60, 160]);
  return (
    <AbsoluteFill style={{background: INK}}>
      <AbsoluteFill style={{background: `radial-gradient(60% 35% at 50% 62%,rgba(47,107,255,.40),transparent 70%)`}} />
      <AbsoluteFill style={{transform: `scale(${1.0 + 0.08 * l})`, perspective: 2100, perspectiveOrigin: '50% 45%'}}>
        <div style={{position: 'absolute', left: 40, top: 560, width: 1000, transformStyle: 'preserve-3d', transform: `rotateX(${rotX}deg) rotateY(${rotY}deg)`}}>
          <div style={{width: 1000, height: 631, borderRadius: 32, background: '#0a0b0e', padding: 22, boxShadow: '0 60px 80px rgba(0,0,0,.6),0 0 0 3px #2a2e38', position: 'relative'}}>
            <div style={{width: '100%', height: '100%', borderRadius: 12, overflow: 'hidden', position: 'relative'}}>
              <Img src={staticFile(c.tela)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 0%', filter: 'brightness(.82) blur(0.6px)'}} />
              <div style={{position: 'absolute', inset: 0, background: `linear-gradient(115deg,transparent ${brilho - 25}%,rgba(255,255,255,.20) ${brilho}%,transparent ${brilho + 22}%)`}} />
              <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg,rgba(255,255,255,.07),transparent 35%)'}} />
            </div>
          </div>
          <div style={{width: 1150, height: 36, marginLeft: -75, marginTop: 6, borderRadius: '0 0 40px 40px', background: 'linear-gradient(180deg,#e3e6ec,#8c919c 70%,#5c616b)', boxShadow: '0 40px 60px rgba(0,0,0,.65)', position: 'relative'}}>
            <div style={{position: 'absolute', left: '50%', top: 0, width: 180, height: 10, marginLeft: -90, borderRadius: '0 0 12px 12px', background: '#6b707b'}} />
          </div>
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg,rgba(11,13,18,.7),transparent 30%,transparent 70%,rgba(11,13,18,.7))'}} />
      {c.texto && <Palavras t={c.texto} y={c.y ?? 300} tam={c.tam ?? 78} acento={c.acento ?? ACIDO} atraso={c.atraso ?? 10} />}
    </AbsoluteFill>
  );
};

// ---------- cena: fecho com marca ----------
const Fecho: React.FC<{c: CenaV; arroba: string}> = ({c, arroba}) => {
  const f = useCurrentFrame();
  const e = spring({frame: f - 4, fps: 30, config: {damping: 18, stiffness: 120}});
  return (
    <AbsoluteFill style={{background: INK}}>
      <AbsoluteFill style={{background: `radial-gradient(70% 40% at 50% 46%,${c.brilho || 'rgba(47,107,255,.38)'},transparent 70%)`}} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 560, display: 'flex', flexDirection: 'column', alignItems: 'center', transform: `translateY(${(1 - e) * 40}px) scale(${0.94 + 0.06 * e})`, opacity: e}}>
        <Img src={staticFile('af/logo-icone.png')} style={{width: 190, height: 190, borderRadius: 44, boxShadow: '0 28px 70px rgba(255,106,19,.35)'}} />
        <div style={{font: '700 76px SH', letterSpacing: -1.5, marginTop: 34, color: MARFIM}}>AutoFlow</div>
      </div>
      <Palavras t={c.texto} y={c.y ?? 960} tam={c.tam ?? 74} acento={c.acento ?? ACIDO} atraso={14} w={880} />
      {c.sub && <div style={{position: 'absolute', left: 0, right: 0, top: c.ysub ?? 1250, textAlign: 'center', font: '500 38px ST', color: CINZA, letterSpacing: 1, opacity: interpolate(f, [30, 46], [0, 1], {extrapolateRight: 'clamp'})}}>{c.sub}</div>}
      <div style={{position: 'absolute', left: 0, right: 0, top: 1480, textAlign: 'center', font: '500 28px ST', color: CINZA, letterSpacing: 2}}>por {arroba}</div>
    </AbsoluteFill>
  );
};

export const SinalVivo: React.FC<PropsV> = (props) => {
  useFontes();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: INK}}>
      {props.cenas.map((c, i) => {
        const from = Math.round(c.inicio * fps), dur = Math.max(1, Math.round((c.fim - c.inicio) * fps));
        const C = c.tipo === 'foto' ? <Foto c={c} dur={dur} /> : c.tipo === 'texto' ? <Texto c={c} dur={dur} /> : c.tipo === 'colagem' ? <Colagem c={c} />
          : c.tipo === 'flashes' ? <Flashes c={c} /> : c.tipo === 'janelas' ? <Janelas c={c} dur={dur} /> : c.tipo === 'notebook' ? <Notebook c={c} dur={dur} />
          : <Fecho c={c} arroba={props.arroba} />;
        return <Sequence key={i} from={from} durationInFrames={dur} layout="none">{C}</Sequence>;
      })}
      <Grao />
      {props.audio && <Audio src={staticFile(props.audio)} />}
    </AbsoluteFill>
  );
};
