// Motor "estilo": mesma linguagem visual dos carrosséis aprovados (preto + dourado, vidro 3D, moedas 3D, fumaça, desfoque).
// Cenas: capa | frase | moedas | cartao | fecho. Cada cena entra com transição de desfoque + deslize e um "whoosh".
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
  continueRender, delayRender, Easing} from 'remotion';

const OURO = '#F5A623', OURO2 = '#FFD27A', BRANCO = '#F5F5F7';
export type Palavra = {w: string; s: number; e: number};
export type CenaE = {inicio: number; fim: number; tipo: string; linha?: string; titulo?: string; rotulo?: string;
  numero?: string; icones?: string[]; cartoes?: string[]; fundo?: string; foto?: string};
export type PropsE = {fps: number; duracao: number; arroba: string; audio: string | null; batida: string | null;
  palavras: Palavra[]; cenas: CenaE[]; trilha_mix?: boolean; sfx?: boolean};

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

const Particulas: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{pointerEvents: 'none'}}>{Array.from({length: 26}).map((_, i) => {
    const x = (i * 397) % 1080, v = 0.6 + (i % 5) * 0.35, y = 1920 - ((f * v * 3 + i * 211) % 2100);
    const s = 3 + (i % 4) * 2;
    return <div key={i} style={{position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: OURO2,
      opacity: 0.25 + (i % 3) * 0.15, filter: i % 2 ? 'blur(2px)' : 'none', boxShadow: `0 0 ${s * 3}px ${OURO}`}} />;
  })}</AbsoluteFill>;
};

const Grao: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{pointerEvents: 'none', opacity: 0.14, mixBlendMode: 'overlay',
    backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='${f % 8}'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")`}} />;
};

// entrada: desfoque + deslize + escala; saída curta com desfoque
const Transicao: React.FC<{dur: number; children: React.ReactNode}> = ({dur, children}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const e = spring({frame: f, fps, config: {damping: 18, mass: 0.7}});
  const sai = interpolate(f, [dur - 6, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const zoom = interpolate(f, [0, dur], [1, 1.06]);
  return <AbsoluteFill style={{transform: `translateY(${(1 - e) * 120}px) scale(${zoom * (0.94 + 0.06 * e)})`,
    filter: `blur(${(1 - e) * 24 + sai * 18}px)`, opacity: Math.min(e * 1.4, 1 - sai * 0.6)}}>{children}</AbsoluteFill>;
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

// legenda palavra a palavra, 3 por vez, a falada em dourado e maior
const Legenda: React.FC<{palavras: Palavra[]; claro: (t: number) => boolean}> = ({palavras, claro}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const t = f / fps;
  const i = palavras.findIndex((p) => t >= p.s && t < p.e + 0.2);
  if (i < 0) return null;
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
  const ehClaro = (t: number) => props.cenas.some((c) => c.fundo === 'claro' && t >= c.inicio && t < c.fim);
  return (
    <AbsoluteFill style={{background: '#08080a'}}>
      {props.cenas.map((c, i) => {
        const from = Math.round(c.inicio * fps); const dur = Math.max(1, Math.round((c.fim - c.inicio) * fps));
        const claro = c.fundo === 'claro';
        const C = c.tipo === 'capa' ? <Capa c={c} /> : c.tipo === 'moedas' ? <Moedas c={c} /> : c.tipo === 'cartao' ? <Cartao c={c} claro={claro} />
          : c.tipo === 'fecho' ? <Fecho c={c} arroba={props.arroba} /> : <Frase c={c} claro={claro} />;
        return <Sequence key={i} from={from} durationInFrames={dur}>
          <Fundo claro={claro} />
          <Transicao dur={dur}>{C}</Transicao>
          {!claro && <Particulas />}
          {props.sfx !== false && i > 0 && <Audio src={staticFile('sfx/whoosh.wav')} volume={0.35} />}
        </Sequence>;
      })}
      <Legenda palavras={props.palavras} claro={ehClaro} />
      <div style={{position: 'absolute', left: 70, top: 110, fontFamily: 'Man8', fontSize: 30, lineHeight: 0.95, color: BRANCO, mixBlendMode: 'difference'}}>SERA<br />PHIM</div>
      <Grao />
      {props.audio && <Audio src={staticFile(props.audio)} />}
      {props.batida && <Audio src={staticFile(props.batida)} volume={props.trilha_mix ? 1 : 0.14} />}
    </AbsoluteFill>
  );
};
