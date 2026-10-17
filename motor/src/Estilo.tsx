// Motor "estilo": mesma linguagem visual dos carrosséis aprovados (preto + dourado, vidro 3D, moedas 3D, fumaça, desfoque).
// Cenas: capa | frase | moedas | cartao | fecho. Cada cena entra com transição de desfoque + deslize e um "whoosh".
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
  continueRender, delayRender, Easing} from 'remotion';

const OURO = '#F5A623', OURO2 = '#FFD27A', BRANCO = '#F5F5F7';
export type Palavra = {w: string; s: number; e: number};
export type CenaE = {inicio: number; fim: number; tipo: string; linha?: string; titulo?: string; rotulo?: string;
  numero?: string; icones?: string[]; cartoes?: string[]; fundo?: string; foto?: string;
  transicao?: string; camera?: string; itens?: string[]; antes?: string; depois?: string; icone?: string};
export type PropsE = {fps: number; duracao: number; arroba: string; audio: string | null; batida: string | null;
  palavras: Palavra[]; cenas: CenaE[]; trilha_mix?: boolean; sfx?: boolean;
  personalidade?: string; legenda?: string; tarja?: boolean; semente?: number};

const FONTES: [string, string][] = [['Anton', 'anton.ttf'], ['Sora', 'sora-700.woff2'], ['Man5', 'manrope-500.woff2'], ['Man8', 'manrope-800.woff2']];
const useFontes = () => {
  const [h] = React.useState(() => delayRender('fontes'));
  React.useEffect(() => {
    const t = setTimeout(() => continueRender(h), 8000);
    Promise.all(FONTES.map(([n, f]) => new FontFace(n, `url(${staticFile('fontes/' + f)})`).load()
      .then((ff) => (document as any).fonts.add(ff)).catch(() => null))).finally(() => { clearTimeout(t); continueRender(h); });
  }, [h]);
};

// título com *destaque* em dourado
const Tit: React.FC<{t: string; cor?: string}> = ({t, cor = OURO}) => (
  <>{t.split('<br>').map((l, j) => <React.Fragment key={j}>{j > 0 && <br />}<TitL t={l} cor={cor} /></React.Fragment>)}</>
);
const TitL: React.FC<{t: string; cor: string}> = ({t, cor}) => (
  <>{t.split(/(\*[^*]+\*)/).map((p, i) => p.startsWith('*') ? <span key={i} style={{color: cor}}>{p.slice(1, -1)}</span> : <span key={i}>{p}</span>)}</>
);

const useIcone = (nome: string) => {
  const [svg, setSvg] = React.useState('');
  const [h] = React.useState(() => delayRender('icone ' + nome));
  React.useEffect(() => {
    fetch(staticFile('icones/' + nome + '.svg')).then((r) => r.text()).then(setSvg).catch(() => setSvg('')).finally(() => continueRender(h));
  }, [nome, h]);
  return svg;
};
const Icone: React.FC<{nome: string; cor: string; tam: number}> = ({nome, cor, tam}) => {
  const s = useIcone(nome).replace(/width="24"/, `width="${tam}"`).replace(/height="24"/, `height="${tam}"`)
    .replace(/stroke="currentColor"/, `stroke="${cor}"`).replace(/stroke-width="2"/, 'stroke-width="1.7"');
  return <div style={{width: tam, height: tam, filter: 'drop-shadow(0 4px 2px rgba(255,255,255,.35)) drop-shadow(0 -3px 2px rgba(0,0,0,.4))'}} dangerouslySetInnerHTML={{__html: s}} />;
};

// fundo escuro com brilho dourado + fumaça que se move devagar
const Fundo: React.FC<{claro?: boolean}> = ({claro}) => {
  const f = useCurrentFrame();
  if (claro) return <AbsoluteFill style={{background: 'radial-gradient(80% 60% at 50% 40%,#fbfaf7,#e8e6df)'}} />;
  const blob = (x: number, y: number, s: number, v: number, o: number) => (
    <div style={{position: 'absolute', left: x + Math.sin(f / v) * 60, top: y + Math.cos(f / (v * 1.3)) * 50, width: s, height: s,
      borderRadius: '50%', background: OURO, filter: 'blur(110px)', opacity: o}} />);
  return (
    <AbsoluteFill style={{background: 'radial-gradient(90% 60% at 0% 0%,#1c1c22 0%,#08080a 70%)'}}>
      {blob(600, 1400, 700, 40, 0.22)}{blob(-200, 300, 600, 55, 0.10)}{blob(500, 700, 400, 30, 0.08)}
    </AbsoluteFill>
  );
};

const Particulas: React.FC<{n?: number}> = ({n = 26}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{pointerEvents: 'none'}}>{Array.from({length: n}).map((_, i) => {
    const x = (i * 397) % 1080, v = 0.6 + (i % 5) * 0.35, y = 1920 - ((f * v * 3 + i * 211) % 2100);
    const s = 3 + (i % 4) * 2;
    return <div key={i} style={{position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: OURO2,
      opacity: 0.25 + (i % 3) * 0.15, filter: i % 2 ? 'blur(2px)' : 'none', boxShadow: `0 0 ${s * 3}px ${OURO}`}} />;
  })}</AbsoluteFill>;
};

const Grao: React.FC<{o?: number}> = ({o = 0.14}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{pointerEvents: 'none', opacity: o, mixBlendMode: 'overlay',
    backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='${f % 8}'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")`}} />;
};

// PERSONALIDADES: cada vídeo escolhe uma (ritmo, molas, câmera, transições, densidade de efeitos)
const PERS: Record<string, {damp: number; trans: string[]; cam: string[]; part: number; grao: number}> = {
  impacto:   {damp: 11, trans: ['chicote', 'zoom', 'corte', 'flash'], cam: ['empurra', 'tremor', 'empurra'], part: 34, grao: 0.16},
  elegante:  {damp: 22, trans: ['desfoque', 'mascara', 'dissolve'], cam: ['deriva', 'inclina', 'afasta'], part: 18, grao: 0.12},
  minimal:   {damp: 26, trans: ['dissolve', 'corte', 'desfoque'], cam: ['parada', 'deriva'], part: 6, grao: 0.08},
  emocional: {damp: 20, trans: ['dissolve', 'luz', 'desfoque'], cam: ['afasta', 'deriva', 'empurra'], part: 22, grao: 0.2},
  dinamico:  {damp: 14, trans: ['deslize', 'chicote', 'zoom', 'mascara'], cam: ['empurra', 'inclina', 'deriva'], part: 28, grao: 0.14},
};
const P = (n?: string) => PERS[n || 'dinamico'] || PERS.dinamico;

const Camera: React.FC<{tipo: string; dur: number; children: React.ReactNode}> = ({tipo, dur, children}) => {
  const f = useCurrentFrame(); const t = f / Math.max(1, dur);
  let tr = '';
  if (tipo === 'empurra') tr = `scale(${1 + 0.08 * t})`;
  else if (tipo === 'afasta') tr = `scale(${1.1 - 0.1 * t})`;
  else if (tipo === 'deriva') tr = `translate(${Math.sin(f / 40) * 18}px, ${-30 * t}px) scale(1.04)`;
  else if (tipo === 'inclina') tr = `perspective(1600px) rotateY(${-4 + 8 * t}deg) rotateX(${2 - 3 * t}deg) scale(1.05)`;
  else if (tipo === 'tremor') tr = `translate(${Math.sin(f * 2.3) * (f < 8 ? 10 : 2)}px, ${Math.cos(f * 1.7) * (f < 8 ? 10 : 2)}px) scale(${1.02 + 0.05 * t})`;
  return <AbsoluteFill style={{transform: tr}}>{children}</AbsoluteFill>;
};

const Transicao: React.FC<{dur: number; tipo: string; damp: number; children: React.ReactNode}> = ({dur, tipo, damp, children}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const e = spring({frame: f, fps, config: {damping: damp, mass: 0.7}});
  const sai = interpolate(f, [dur - 6, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  let st: React.CSSProperties = {};
  if (tipo === 'chicote') st = {transform: `translateX(${(1 - e) * 1100}px) skewX(${(1 - e) * -12}deg)`, filter: `blur(${(1 - e) * 30}px)`};
  else if (tipo === 'zoom') st = {transform: `scale(${2.2 - 1.2 * e})`, filter: `blur(${(1 - e) * 26}px)`, opacity: e};
  else if (tipo === 'corte') st = {};
  else if (tipo === 'flash') st = {filter: `brightness(${1 + Math.max(0, 1 - f / 5) * 2.5})`};
  else if (tipo === 'mascara') st = {clipPath: `circle(${e * 140}% at 50% 55%)`};
  else if (tipo === 'dissolve') st = {opacity: interpolate(f, [0, 14], [0, 1], {extrapolateRight: 'clamp'})};
  else if (tipo === 'luz') st = {opacity: interpolate(f, [0, 16], [0, 1], {extrapolateRight: 'clamp'}), filter: `brightness(${1 + Math.max(0, 1 - f / 18) * 1.4}) blur(${Math.max(0, 1 - f / 14) * 12}px)`};
  else if (tipo === 'deslize') st = {transform: `translateY(${(1 - e) * 160}px)`, opacity: Math.min(1, e * 1.5)};
  else st = {transform: `translateY(${(1 - e) * 120}px) scale(${0.94 + 0.06 * e})`, filter: `blur(${(1 - e) * 24}px)`, opacity: Math.min(e * 1.4, 1)};
  const saida = tipo === 'corte' ? {} : {filter: `${st.filter || ''} blur(${sai * 14}px)`};
  return <AbsoluteFill style={{...st, ...saida}}>{children}</AbsoluteFill>;
};

const Vidro: React.FC<{style?: React.CSSProperties; children?: React.ReactNode; claro?: boolean}> = ({style, children, claro}) => (
  <div style={{position: 'relative', borderRadius: 40, overflow: 'hidden',
    background: 'linear-gradient(135deg,#2b2b31 0%,#141418 55%,#24180a 100%)', border: '2px solid rgba(255,210,122,.38)',
    boxShadow: claro ? '0 50px 90px rgba(80,60,20,.35), inset 0 2px 0 rgba(255,255,255,.25)' : '0 50px 100px rgba(0,0,0,.6), 0 0 80px rgba(245,166,35,.15), inset 0 2px 0 rgba(255,255,255,.18)',
    ...style}}>
    <div style={{position: 'absolute', left: '-10%', right: '-10%', top: '-45%', height: '75%', transform: 'rotate(-8deg)',
      background: 'linear-gradient(180deg,rgba(255,255,255,.22),rgba(255,255,255,0))'}} />
    {children}
  </div>
);

const Capa: React.FC<{c: CenaE}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const tiles: [string, number, number, number, number][] = [[c.icones?.[0] || 'workflow', 50, 420, -14, 260], [c.icones?.[1] || 'message-circle', 770, 330, 12, 240], [c.icones?.[2] || 'bar-chart-3', 790, 880, -8, 200]];
  const linha2 = spring({frame: f - 10, fps, config: {damping: 12}});
  return (
    <AbsoluteFill>
      <Img src={staticFile(c.foto || 'pessoas/pabllo_recorte.png')} style={{position: 'absolute', left: '50%', bottom: 560, height: 1150,
        transform: `translateX(-50%) scale(${interpolate(f, [0, 90], [1.08, 1])})`}} />
      {tiles.map(([ic, x, y, r, s], i) => {
        const e = spring({frame: f - 4 - i * 5, fps, config: {damping: 11}});
        const fl = Math.sin((f + i * 20) / 18) * 14;
        return <div key={i} style={{position: 'absolute', left: x, top: y + fl, transform: `perspective(900px) rotate(${r}deg) rotateY(${-r * 2}deg) scale(${e})`}}>
          <Vidro style={{width: s, height: s, display: 'flex', alignItems: 'center', justifyContent: 'center'}}><Icone nome={ic} cor={OURO2} tam={s * 0.5} /></Vidro></div>;
      })}
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 900, background: 'linear-gradient(180deg,rgba(8,8,10,0),#08080a 55%)'}} />
      <div style={{position: 'absolute', left: 50, right: 50, bottom: 430, textAlign: 'center', color: BRANCO}}>
        <div style={{fontFamily: 'Man8', fontSize: 44, letterSpacing: 3, marginBottom: 18}}>{c.linha}</div>
        <div style={{fontFamily: 'Anton', fontSize: 150, lineHeight: 0.98, textTransform: 'uppercase', transform: `scale(${0.85 + 0.15 * linha2})`}}><Tit t={c.titulo || ''} /></div>
      </div>
    </AbsoluteFill>
  );
};

const Frase: React.FC<{c: CenaE; claro: boolean}> = ({c, claro}) => {
  const f = useCurrentFrame();
  const ws = (c.titulo || '').split(' ');
  return (
    <AbsoluteFill style={{padding: '0 90px', justifyContent: 'center'}}>
      <div style={{fontFamily: 'Sora', fontSize: 112, lineHeight: 1.08, letterSpacing: -2, color: claro ? '#111' : BRANCO}}>
        {ws.map((w, i) => {
          const op = interpolate(f, [i * 3, i * 3 + 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const d = w.startsWith('*') || w.endsWith('*') || w.endsWith('*.') || w.endsWith('*,');
          return <span key={i} style={{opacity: op, display: 'inline-block', marginRight: 26, filter: `blur(${(1 - op) * 10}px)`,
            transform: `translateY(${(1 - op) * 30}px)`, color: d ? (claro ? '#C77F00' : OURO) : undefined}}>{w.replace(/\*/g, '')}</span>;
        })}
      </div>
    </AbsoluteFill>
  );
};

const Moedas: React.FC<{c: CenaE}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const pos = [[140, 1050], [430, 1120], [720, 1050], [290, 1330], [580, 1330]];
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 80, right: 80, top: 330, fontFamily: 'Sora', fontSize: 100, lineHeight: 1.08, letterSpacing: -2, color: BRANCO}}><Tit t={c.titulo || ''} /></div>
      {(c.icones || []).slice(0, 5).map((ic, i) => {
        const e = spring({frame: f - 8 - i * 6, fps, config: {damping: 9, mass: 0.8}});
        const [x, y] = pos[i]; const fl = Math.sin((f + i * 15) / 16) * 10;
        return <div key={i} style={{position: 'absolute', left: x, top: y - (1 - e) * 900 + fl, width: 250, height: 250, borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `perspective(700px) rotateX(18deg) rotate(${[-10, 6, 12, -4, 8][i]}deg) rotateY(${(1 - e) * 180}deg)`,
          background: `radial-gradient(circle at 32% 28%,#fff3cf 0%,${OURO2} 18%,${OURO} 45%,#8a5300 80%,#4a2c00 100%)`,
          boxShadow: '0 40px 70px rgba(0,0,0,.6), 0 0 60px rgba(245,166,35,.3), inset -10px -14px 30px rgba(0,0,0,.45), inset 10px 12px 26px rgba(255,255,255,.5)'}}>
          <Icone nome={ic} cor="#3a2300" tam={120} /></div>;
      })}
    </AbsoluteFill>
  );
};

const Cartao: React.FC<{c: CenaE; claro: boolean}> = ({c, claro}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const e = spring({frame: f - 6, fps, config: {damping: 14}});
  const linha = interpolate(f, [14, 40], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const num = spring({frame: f - 24, fps, config: {damping: 8}});
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 80, right: 80, top: 360, fontFamily: 'Sora', fontSize: 104, lineHeight: 1.08, letterSpacing: -2, color: claro ? '#111' : BRANCO}}>
        <Tit t={c.titulo || ''} cor={claro ? '#C77F00' : OURO} /></div>
      <div style={{position: 'absolute', left: 110, top: 800, transform: `perspective(1300px) rotateX(${12 - 2 * e}deg) rotateY(${-10 + (1 - e) * 40}deg) scale(${0.8 + 0.2 * e})`, opacity: e}}>
        <Vidro claro={claro} style={{width: 860, height: 360, padding: '44px 52px'}}>
          <div style={{position: 'relative', fontFamily: 'Man8', fontSize: 30, letterSpacing: 4, color: OURO2}}>{c.rotulo}</div>
          <div style={{position: 'relative', fontFamily: 'Anton', fontSize: 150, lineHeight: 1, marginTop: 18, transform: `scale(${0.6 + 0.4 * num})`, transformOrigin: 'left',
            background: `linear-gradient(180deg,#fff 30%,${OURO2})`, WebkitBackgroundClip: 'text', color: 'transparent'}}>{c.numero}</div>
          <svg width="400" height="200" viewBox="0 0 300 150" style={{position: 'absolute', right: 30, bottom: 30}}>
            <path d="M0 130 C70 128 110 110 150 80 S240 20 280 18" fill="none" stroke="#fff" strokeWidth={5} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - linha} />
            <circle cx={280} cy={18} r={13 * linha} fill="#111" stroke="#fff" strokeWidth={5} />
          </svg>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

const Fecho: React.FC<{c: CenaE; arroba: string}> = ({c, arroba}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 80, right: 80, top: 420, fontFamily: 'Sora', fontSize: 96, lineHeight: 1.1, letterSpacing: -2, color: BRANCO}}><Tit t={c.titulo || ''} /></div>
      <div style={{position: 'absolute', left: 80, right: 80, top: 1000, display: 'flex', gap: 34}}>
        {(c.cartoes || []).map((t, i) => {
          const e = spring({frame: f - 10 - i * 8, fps, config: {damping: 14}});
          return <div key={i} style={{flex: 1, border: `3px solid ${OURO}`, borderRadius: 26, padding: 36, background: 'rgba(245,166,35,.06)', opacity: e,
            transform: `translateY(${(1 - e) * 60}px)`, boxShadow: `0 0 ${40 + Math.sin(f / 8) * 15}px rgba(245,166,35,.25)`,
            fontFamily: 'Man5', fontSize: 40, lineHeight: 1.3, color: BRANCO}}>
            <div style={{width: 34, height: 34, borderRadius: '50%', border: `3px solid ${OURO}`, marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <div style={{width: 16, height: 16, borderRadius: '50%', background: OURO}} /></div>{t}</div>;
        })}
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1460, textAlign: 'center', fontFamily: 'Man8', fontSize: 46, color: OURO2,
        opacity: interpolate(f, [30, 45], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>SIGA {arroba.toUpperCase()}</div>
    </AbsoluteFill>
  );
};


// número gigante contando, tela cheia
const Numero: React.FC<{c: CenaE}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const alvo = parseFloat((c.numero || '0').replace(/[^\d.,]/g, '').replace(',', '.')) || 0;
  const pre = (c.numero || '').match(/^[^\d]*/)?.[0] || ''; const suf = (c.numero || '').replace(/^[^\d]*[\d.,]+/, '');
  const p = interpolate(f, [4, fps * 1.2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.exp)});
  const v = Number.isInteger(alvo) ? Math.round(alvo * p) : (alvo * p).toFixed(1);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{fontFamily: 'Man8', fontSize: 40, letterSpacing: 6, color: OURO2, marginBottom: 10}}>{c.rotulo}</div>
      <div style={{fontFamily: 'Anton', fontSize: 400, lineHeight: 0.9, background: `linear-gradient(180deg,#fff 20%,${OURO2} 60%,${OURO})`,
        WebkitBackgroundClip: 'text', color: 'transparent', filter: `drop-shadow(0 0 60px rgba(245,166,35,${0.2 + 0.3 * p}))`}}>{pre}{v}{suf}</div>
      <div style={{fontFamily: 'Sora', fontSize: 76, color: BRANCO, textAlign: 'center', padding: '0 90px', marginTop: 30}}><Tit t={c.titulo || ''} /></div>
    </AbsoluteFill>
  );
};

// lista: cartões de vidro empilhados em profundidade, câmera passa por eles
const Lista: React.FC<{c: CenaE}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const it = c.itens || [];
  return (
    <AbsoluteFill style={{perspective: 1400}}>
      <div style={{position: 'absolute', left: 80, right: 80, top: 260, fontFamily: 'Sora', fontSize: 92, lineHeight: 1.08, letterSpacing: -2, color: BRANCO}}><Tit t={c.titulo || ''} /></div>
      {it.map((t, i) => {
        const e = spring({frame: f - 8 - i * 9, fps, config: {damping: 15}});
        return <div key={i} style={{position: 'absolute', left: 90, right: 90, top: 700 + i * 250,
          transform: `translateZ(${(1 - e) * -900}px) rotateX(${(1 - e) * 40}deg) rotateY(${(i % 2 ? 1 : -1) * 4}deg)`, opacity: e}}>
          <Vidro style={{padding: '40px 50px', display: 'flex', alignItems: 'center', gap: 36}}>
            <div style={{position: 'relative', fontFamily: 'Anton', fontSize: 90, color: OURO, width: 90}}>{i + 1}</div>
            <div style={{position: 'relative', fontFamily: 'Man8', fontSize: 50, color: BRANCO, lineHeight: 1.15}}>{t}</div></Vidro></div>;
      })}
    </AbsoluteFill>
  );
};

// contraste: antes x depois, tela dividida com linha dourada que corta
const Contraste: React.FC<{c: CenaE}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const l = interpolate(f, [0, 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const d = spring({frame: f - 12, fps, config: {damping: 14}});
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 960, background: '#ecebe6', clipPath: `inset(0 ${100 - l * 100}% 0 0)`}}>
        <div style={{position: 'absolute', left: 90, top: 330, fontFamily: 'Man8', fontSize: 34, letterSpacing: 5, color: '#777'}}>ANTES</div>
        <div style={{position: 'absolute', left: 90, right: 90, top: 400, fontFamily: 'Sora', fontSize: 84, lineHeight: 1.1, color: '#222', textDecoration: f > 24 ? 'line-through' : 'none', textDecorationColor: OURO}}>{c.antes}</div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 955, height: 10, background: OURO, transform: `scaleX(${l})`, boxShadow: `0 0 40px ${OURO}`}} />
      <div style={{position: 'absolute', left: 90, right: 90, top: 1060, opacity: d, transform: `translateY(${(1 - d) * 50}px)`}}>
        <div style={{fontFamily: 'Man8', fontSize: 34, letterSpacing: 5, color: OURO2}}>DEPOIS</div>
        <div style={{fontFamily: 'Sora', fontSize: 90, lineHeight: 1.1, color: BRANCO, marginTop: 20}}><Tit t={c.depois || ''} /></div>
      </div>
    </AbsoluteFill>
  );
};

// objeto: um ícone 3D enorme girando no centro, com fumaça e anel de luz
const Objeto: React.FC<{c: CenaE}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const e = spring({frame: f, fps, config: {damping: 13}});
  return (
    <AbsoluteFill style={{alignItems: 'center'}}>
      <div style={{position: 'absolute', top: 420, width: 700, height: 700, borderRadius: '50%', border: `3px solid rgba(245,166,35,.4)`,
        boxShadow: `0 0 120px rgba(245,166,35,.35), inset 0 0 80px rgba(245,166,35,.2)`, transform: `rotateX(70deg) scale(${e})`}} />
      <div style={{position: 'absolute', top: 470, transform: `perspective(900px) rotateY(${Math.sin(f / 30) * 25}deg) rotateX(${8 + Math.cos(f / 40) * 6}deg) scale(${e}) translateY(${Math.sin(f / 20) * 14}px)`}}>
        <Vidro style={{width: 520, height: 520, borderRadius: 110, display: 'flex', alignItems: 'center', justifyContent: 'center'}}><Icone nome={c.icone || 'zap'} cor={OURO2} tam={280} /></Vidro></div>
      <div style={{position: 'absolute', left: 80, right: 80, top: 1180, textAlign: 'center', fontFamily: 'Anton', fontSize: 130, lineHeight: 1, textTransform: 'uppercase', color: BRANCO}}><Tit t={c.titulo || ''} /></div>
    </AbsoluteFill>
  );
};

// pessoa: texto gigante ATRÁS da pessoa, parallax
const Pessoa: React.FC<{c: CenaE}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const e = spring({frame: f, fps, config: {damping: 18}});
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: -40, right: -40, top: 360, textAlign: 'center', fontFamily: 'Anton', fontSize: 330, lineHeight: 0.86,
        textTransform: 'uppercase', color: 'transparent', WebkitTextStroke: `4px ${OURO}`, transform: `translateX(${(1 - e) * -200 + f * 0.6}px)`, opacity: 0.9}}>{(c.linha || '').replace(/\*/g, '')}</div>
      <Img src={staticFile(c.foto || 'pessoas/pabllo_recorte.png')} style={{position: 'absolute', left: '50%', bottom: 420, height: 1250, transform: `translateX(calc(-50% + ${(1 - e) * 120 - f * 0.25}px))`}} />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 700, background: 'linear-gradient(180deg,rgba(8,8,10,0),#08080a 60%)'}} />
      <div style={{position: 'absolute', left: 80, right: 80, bottom: 470, textAlign: 'center', fontFamily: 'Sora', fontSize: 84, lineHeight: 1.08, color: BRANCO}}><Tit t={c.titulo || ''} /></div>
    </AbsoluteFill>
  );
};

// citação elegante: serif grande, aspas de luz, revelação lenta
const Citacao: React.FC<{c: CenaE}> = ({c}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 30], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{padding: '0 100px', justifyContent: 'center'}}>
      <div style={{fontFamily: 'Anton', fontSize: 300, color: OURO, opacity: 0.35 * o, lineHeight: 0.6, filter: 'blur(1px)'}}>“</div>
      <div style={{fontFamily: 'Sora', fontSize: 92, lineHeight: 1.15, color: BRANCO, opacity: o, letterSpacing: -1, filter: `blur(${(1 - o) * 8}px)`}}><Tit t={c.titulo || ''} /></div>
      <div style={{width: 160 * o, height: 4, background: OURO, marginTop: 50}} />
    </AbsoluteFill>
  );
};

// legenda palavra a palavra, 3 por vez, a falada em dourado e maior
const Legenda: React.FC<{palavras: Palavra[]; claro: (t: number) => boolean; estilo?: string; ocultar?: [number, number][]}> = ({palavras, claro, estilo, ocultar = []}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const t = f / fps;
  if (ocultar.some(([a, b]) => t >= a && t < b)) return null;
  const i = palavras.findIndex((p) => t >= p.s && t < p.e + 0.2);
  if (i < 0 || estilo === 'nenhuma') return null;
  if (estilo === 'palavra') {
    const p = palavras[i]; const k = (t - p.s) / Math.max(0.05, p.e - p.s);
    return <div style={{position: 'absolute', left: 0, right: 0, bottom: 300, textAlign: 'center', fontFamily: 'Anton', fontSize: 120, textTransform: 'uppercase',
      color: claro(t) ? '#111' : BRANCO, transform: `scale(${1.15 - 0.15 * Math.min(1, k * 3)})`, textShadow: claro(t) ? 'none' : `0 0 40px rgba(245,166,35,.45)`}}>{p.w}</div>;
  }
  if (estilo === 'sutil') {
    const ini2 = Math.floor(i / 6) * 6;
    return <div style={{position: 'absolute', left: 120, right: 120, bottom: 240, textAlign: 'center', fontFamily: 'Man5', fontSize: 40, lineHeight: 1.35,
      color: claro(t) ? '#333' : 'rgba(245,245,247,.85)'}}>{palavras.slice(ini2, ini2 + 6).map((p) => p.w).join(' ')}</div>;
  }
  const ini = Math.floor(i / 3) * 3; const cl = claro(t);
  return <div style={{position: 'absolute', left: 60, right: 60, bottom: 250, textAlign: 'center', fontFamily: 'Man8', fontSize: 58, textTransform: 'uppercase',
    textShadow: cl ? 'none' : '0 4px 20px rgba(0,0,0,.8)'}}>
    {palavras.slice(ini, ini + 3).map((p, k) => <span key={k} style={{display: 'inline-block', margin: '0 14px',
      color: ini + k === i ? (cl ? '#C77F00' : OURO) : (cl ? '#222' : BRANCO), transform: `scale(${ini + k === i ? 1.12 : 1})`}}>{p.w}</span>)
      .reduce((a: React.ReactNode[], el, k) => k ? [...a, ' ', el] : [el], [])}</div>;
};

export const Estilo: React.FC<PropsE> = (props) => {
  useFontes();
  const {fps} = useVideoConfig();
  const ocultas = props.cenas.filter((c) => ['frase', 'citacao'].includes(c.tipo));
  const ehClaro = (t: number) => props.cenas.some((c) => c.fundo === 'claro' && t >= c.inicio && t < c.fim);
  return (
    <AbsoluteFill style={{background: '#08080a'}}>
      {props.cenas.map((c, i) => {
        const from = Math.round(c.inicio * fps); const dur = Math.max(1, Math.round((c.fim - c.inicio) * fps));
        const claro = c.fundo === 'claro';
        const C = c.tipo === 'capa' ? <Capa c={c} /> : c.tipo === 'moedas' ? <Moedas c={c} /> : c.tipo === 'cartao' ? <Cartao c={c} claro={claro} />
          : c.tipo === 'fecho' ? <Fecho c={c} arroba={props.arroba} /> : c.tipo === 'numero' ? <Numero c={c} /> : c.tipo === 'lista' ? <Lista c={c} />
          : c.tipo === 'contraste' ? <Contraste c={c} /> : c.tipo === 'objeto' ? <Objeto c={c} /> : c.tipo === 'pessoa' ? <Pessoa c={c} />
          : c.tipo === 'citacao' ? <Citacao c={c} /> : <Frase c={c} claro={claro} />;
        const pp = P(props.personalidade); const sd = (props.semente || 0) + i * 7;
        const tr = i === 0 ? (c.transicao || 'desfoque') : (c.transicao || pp.trans[sd % pp.trans.length]);
        const cam = c.camera || pp.cam[(sd >> 1) % pp.cam.length];
        return <Sequence key={i} from={from} durationInFrames={dur}>
          <Fundo claro={claro} />
          <Transicao dur={dur} tipo={tr} damp={pp.damp}><Camera tipo={cam} dur={dur}>{C}</Camera></Transicao>
          {!claro && <Particulas n={pp.part} />}
          {props.sfx !== false && i > 0 && <Audio src={staticFile('sfx/whoosh.wav')} volume={0.35} />}
        </Sequence>;
      })}
      <Legenda palavras={props.palavras} claro={ehClaro} estilo={props.legenda} ocultar={ocultas.map((c) => [c.inicio, c.fim] as [number, number])} />
      <div style={{position: 'absolute', left: 70, top: 110, fontFamily: 'Man8', fontSize: 30, lineHeight: 0.95, color: BRANCO, mixBlendMode: 'difference'}}>SERA<br />PHIM</div>
      <Grao o={P(props.personalidade).grao} />
      {props.tarja && <><div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 150, background: '#000'}} /><div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 150, background: '#000'}} /></>}
      {props.audio && <Audio src={staticFile(props.audio)} />}
      {props.batida && <Audio src={staticFile(props.batida)} volume={props.trilha_mix ? 1 : 0.14} />}
    </AbsoluteFill>
  );
};
