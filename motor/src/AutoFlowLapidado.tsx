// AutoFlow V2/V3 "lapidados": mesma imagem filmada, agora com edição de cinema da Seraphim por cima —
// câmera viva (punch-in, deriva, tremor), transições motivadas (chicote, zoom, flash, vazamento de luz),
// legendas Anton palavra a palavra, partículas, vinheta e grão. O áudio vem pronto (mixado no ffmpeg).
import React from 'react';
import {AbsoluteFill, Audio, Easing, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig} from 'remotion';

const LAR = '#FF6A13';
const BRANCO = '#F5F5F7';
const FPS = 30;

export type Shot = {a: number; b: number; o: number; kind: 'foot' | 'ui' | 'card' | 'fim'; trans?: 'whip' | 'zoom' | 'flash' | 'luz' | 'corte'; dir?: 1 | -1; deriva?: number};
export type Cap = {w: string; s: number; e: number; hi?: boolean; fim?: boolean};
export type PropsLap = {video: string; audio: string | null; dur: number; shots: Shot[]; caps: Cap[]; hits: number[]; fimCard: number;
  nome: string};

const f2 = (t: number) => Math.round(t * FPS);
const ease = Easing.bezier(0.22, 1, 0.36, 1);
const io = Easing.bezier(0.65, 0, 0.35, 1);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const L = (f: number, a: number, b: number, v0: number, v1: number, e: (n: number) => number = ease) =>
  interpolate(f, [a, b], [v0, v1], {...clamp, easing: e});

const useFontes = () => {
  const [h] = React.useState(() => delayRender('fontes-lap'));
  React.useEffect(() => {
    const t = setTimeout(() => continueRender(h), 8000);
    Promise.all([['Anton', 'anton.ttf'], ['StackH', 'stack-sans-headline-latin-700-normal.woff2'], ['StackT', 'stack-sans-text-latin-500-normal.woff2']]
      .map(([n, f]) => new FontFace(n, `url(${staticFile('fontes/' + f)})`).load().then((ff) => (document as any).fonts.add(ff)).catch(() => null)))
      .finally(() => { clearTimeout(t); continueRender(h); });
  }, [h]);
};

// ---- um plano do vídeo com câmera + transição de entrada/saída ----
const Plano: React.FC<{sh: Shot; dur: number; src: string; idx: number; nxt?: Shot}> = ({sh, dur, src, idx, nxt}) => {
  const f = useCurrentFrame();
  const speed = (sh.b - sh.a) / (dur / FPS);
  const t = f / Math.max(1, dur);
  const foot = sh.kind === 'foot';
  const dir = sh.dir || 1;
  const tipo = sh.trans || 'whip';
  const IN = 7, OUT = 5;
  const ein = L(f, 0, IN, 1, 0);               // 1 -> 0 ao entrar
  const eout = L(f, dur - OUT, dur, 0, 1, io);  // 0 -> 1 ao sair
  // câmera base
  let sc = 1, tx = 0, ty = 0, rot = 0;
  if (sh.kind === 'fim') { sc = 1 + 0.045 * L(f, 0, dur, 0, 1, io); }
  else if (foot) {
    const d = sh.deriva ?? (idx % 2 ? 1 : -1);
    sc = 1.07 + 0.05 * t;                       // empurra devagar
    tx = d * L(f, 0, dur, -14, 14, io); ty = -10 * t;
    // tremor leve de câmera na mão
    tx += Math.sin(f * 0.9 + idx) * 2.2; ty += Math.cos(f * 1.3 + idx * 2) * 2;
    rot = Math.sin(f / 22 + idx) * 0.18;
  } else if (sh.kind === 'ui') {
    sc = 1.0 + 0.03 * L(f, 0, dur, 0, 1, io);   // UI respira, sem cortar títulos
  } else { sc = 1.0 + 0.04 * L(f, 0, dur, 0, 1, io); }
  // transição de entrada
  let blur = 0, flash = 0, op = 1;
  if (tipo === 'whip') { tx += dir * 170 * ein * ein; blur += 22 * ein; sc *= 1 + 0.05 * ein; }
  else if (tipo === 'zoom') { sc *= 1 + 0.32 * ein * ein; blur += 18 * ein; }
  else if (tipo === 'flash') { flash = Math.max(0, 1 - f / 6); sc *= 1 + 0.05 * ein; }
  else if (tipo === 'luz') { flash = Math.max(0, 1 - f / 10) * 0.7; blur += 8 * ein; }
  // saída: prepara o próximo corte, continuando o movimento
  if (nxt && sh.kind !== 'fim') {
    const nt = nxt.trans || 'whip';
    if (nt === 'whip') { tx -= (nxt.dir || 1) * 90 * eout * eout; blur += 12 * eout; }
    else if (nt === 'zoom') { sc *= 1 - 0.08 * eout * eout; blur += 6 * eout; }
  }
  return (
    <AbsoluteFill style={{background: '#050507'}}>
      <AbsoluteFill style={{transform: `translate(${tx}px, ${ty}px) rotate(${rot}deg) scale(${sc})`, filter: blur > 0.3 ? `blur(${blur}px)` : undefined, opacity: op}}>
        <OffthreadVideo src={staticFile(src)} startFrom={f2(sh.a)} playbackRate={speed} muted style={{width: 1080, height: 1920}} />
      </AbsoluteFill>
      {flash > 0.01 && <AbsoluteFill style={{background: tipo === 'luz' ? `radial-gradient(70% 50% at 70% 30%, rgba(255,170,90,${flash}), rgba(255,106,19,${flash * 0.5}) 60%, transparent)` : `rgba(255,255,255,${flash * 0.85})`}} />}
    </AbsoluteFill>
  );
};

// ---- vazamento de luz laranja (passa varrendo a tela) ----
const VazaLuz: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame() - at;
  if (f < 0 || f > 22) return null;
  const x = L(f, 0, 22, -40, 130, io);
  const o = Math.sin((f / 22) * Math.PI) * 0.75;
  return <AbsoluteFill style={{mixBlendMode: 'screen', opacity: o, pointerEvents: 'none',
    background: `linear-gradient(100deg, transparent ${x - 28}%, rgba(255,106,19,.55) ${x - 10}%, rgba(255,196,120,.9) ${x}%, rgba(255,106,19,.35) ${x + 12}%, transparent ${x + 30}%)`}} />;
};

// ---- impacto: tremida + clarão curto nos momentos fortes ----
const Impacto: React.FC<{hits: number[]; children: React.ReactNode}> = ({hits, children}) => {
  const f = useCurrentFrame();
  let sh = 0, fl = 0;
  for (const h of hits) { const d = f - f2(h); if (d >= 0 && d < 14) { sh = Math.max(sh, 1 - d / 14); if (d < 4) fl = Math.max(fl, 1 - d / 4); } }
  const a = sh * 16;
  return (
    <AbsoluteFill style={{transform: `translate(${Math.sin(f * 2.7) * a}px, ${Math.cos(f * 3.1) * a}px) scale(${1 + 0.03 * sh})`}}>
      {children}
      {fl > 0 && <AbsoluteFill style={{background: `rgba(255,236,214,${fl * 0.5})`, mixBlendMode: 'screen'}} />}
    </AbsoluteFill>
  );
};

// ---- poeira em suspensão no feixe de luz ----
const Particulas: React.FC<{n?: number}> = ({n = 30}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'screen'}}>{Array.from({length: n}).map((_, i) => {
    const x = (i * 397 + Math.sin(f / 50 + i) * 30) % 1080, v = 0.35 + (i % 5) * 0.22, y = 1920 - ((f * v * 2.2 + i * 211) % 2100);
    const s = 2 + (i % 4) * 1.6;
    return <div key={i} style={{position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: i % 3 ? 'rgba(255,200,150,.9)' : LAR,
      opacity: 0.12 + (i % 3) * 0.1, filter: i % 2 ? 'blur(1.5px)' : 'none', boxShadow: `0 0 ${s * 3}px rgba(255,140,60,.8)`}} />;
  })}</AbsoluteFill>;
};

const Grao: React.FC<{o?: number}> = ({o = 0.13}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{pointerEvents: 'none', opacity: o, mixBlendMode: 'overlay',
    backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='${f % 8}'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")`}} />;
};

const Vinheta: React.FC = () => <AbsoluteFill style={{pointerEvents: 'none', background: 'radial-gradient(120% 90% at 50% 45%, transparent 55%, rgba(0,0,0,.5) 100%)'}} />;

// ---- legendas Anton: palavra a palavra, chunk de até 3 palavras, destaque laranja ----
const Legendas: React.FC<{caps: Cap[]; fimCard: number}> = ({caps, fimCard}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const t = f / fps;
  // monta chunks: quebra em pontuação ou 3 palavras
  const chunks: Cap[][] = []; let cur: Cap[] = [];
  caps.forEach((c, i) => {
    cur.push(c);
    const fimFrase = /[.!?,;:]$/.test(c.w) || cur.length >= 3 || (caps[i + 1] && caps[i + 1].s - c.e > 0.45);
    if (fimFrase) { chunks.push(cur); cur = []; }
  });
  if (cur.length) chunks.push(cur);
  const ch = chunks.find((c) => t >= c[0].s - 0.02 && t < c[c.length - 1].e + 0.16);
  if (!ch) return null;
  const sombra = '0 6px 0 rgba(0,0,0,.55), 0 0 42px rgba(0,0,0,.85), 0 0 90px rgba(0,0,0,.6)';
  const fim = ch[0].fim;
  if (fim) return null; // o cartão final já traz o texto na tela
  const letras = ch.reduce((n, c) => n + c.w.replace(/[.,;:!?]+$/, '').length, 0);
  const tam = Math.max(70, Math.min(128, Math.floor(940 / (letras * 0.5 + (ch.length - 1) * 0.55 + 0.2))));
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1180, height: 520, background: 'linear-gradient(180deg, transparent, rgba(0,0,0,.42) 55%, transparent)'}} />
      <div style={{position: 'absolute', left: 50, right: 50, top: 1395, height: 170, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: Math.round(tam * 0.24),
        flexWrap: 'nowrap', whiteSpace: 'nowrap'}}>
        {ch.map((c, k) => {
          const d = t - c.s; if (d < -0.02) return null;
          const e = spring({frame: Math.max(0, Math.round(d * fps)), fps, config: {damping: 9, mass: 0.55, stiffness: 190}});
          const ativo = t >= c.s && t < c.e + 0.04;
          return <span key={k} style={{display: 'inline-block', flexShrink: 0, fontFamily: 'Anton', fontSize: tam, lineHeight: 1, textTransform: 'uppercase', letterSpacing: 2,
            color: c.hi ? LAR : BRANCO, textShadow: sombra, transform: `scale(${0.55 + 0.45 * e + (ativo ? 0.06 : 0)}) translateY(${(1 - e) * 24}px) rotate(${(1 - e) * (k % 2 ? 3 : -3)}deg)`,
            opacity: Math.min(1, e * 1.6)}}>{c.w.replace(/[.,;:!?]+$/, '')}</span>;
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---- brilho na logo do cartão final ----
const BrilhoFim: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame() - at;
  if (f < 0 || f > 60) return null;
  const x = L(f, 4, 40, -30, 130, io);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <AbsoluteFill style={{mixBlendMode: 'screen', opacity: L(f, 0, 6, 0, 1) * L(f, 30, 60, 1, 0),
        background: `linear-gradient(105deg, transparent ${x - 14}%, rgba(255,210,160,.55) ${x}%, transparent ${x + 14}%)`, clipPath: 'inset(300px 0 1200px 0)'}} />
      <AbsoluteFill style={{background: `radial-gradient(40% 24% at 50% 30%, rgba(255,106,19,${0.35 * L(f, 0, 10, 1, 0)}), transparent)`}} />
    </AbsoluteFill>
  );
};

export const AutoFlowLapidado: React.FC<PropsLap> = (p) => {
  useFontes();
  return (
    <AbsoluteFill style={{background: '#050507'}}>
      <Impacto hits={p.hits}>
        <AbsoluteFill style={{filter: 'contrast(1.06) saturate(1.06)'}}>
          {p.shots.map((sh, i) => {
            const prox = p.shots[i + 1];
            const dur = Math.max(2, (prox ? f2(prox.o) : p.dur) - f2(sh.o));
            return <Sequence key={i} from={f2(sh.o)} durationInFrames={dur}><Plano sh={sh} dur={dur} src={p.video} idx={i} nxt={prox} /></Sequence>;
          })}
        </AbsoluteFill>
        {p.shots.filter((s) => s.trans === 'luz').map((s, i) => <VazaLuz key={i} at={f2(s.o) - 2} />)}
        <Sequence from={0} durationInFrames={f2(p.fimCard)}><Particulas n={22} /></Sequence>
        <Sequence from={f2(p.fimCard)}><Particulas n={14} /></Sequence>
        <BrilhoFim at={f2(p.fimCard)} />
      </Impacto>
      <Legendas caps={p.caps} fimCard={p.fimCard} />
      <Vinheta />
      <Grao />
      {p.audio && <Audio src={staticFile(p.audio)} />}
    </AbsoluteFill>
  );
};
