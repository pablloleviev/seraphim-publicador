// Peças compartilhadas dos vídeos AutoFlow (V2, V3). O V1 aprovado fica intocado no próprio arquivo.
import React from 'react';
import {AbsoluteFill, Img, interpolate, Easing, staticFile, useCurrentFrame, random} from 'remotion';

export const FPS = 30;
export const s = (t: number) => Math.round(t * FPS);
export const LAR = '#FF6A13';
export const ease = Easing.bezier(0.22, 1, 0.36, 1);
export const io = Easing.bezier(0.65, 0, 0.35, 1);

export const css = `
@font-face{font-family:StackH;font-weight:800;src:url(${staticFile('fontes/stack-sans-headline-latin-700-normal.woff2')})}
@font-face{font-family:StackT;font-weight:500;src:url(${staticFile('fontes/stack-sans-text-latin-500-normal.woff2')})}
`;

export const lerp = (f: number, a: number, b: number, v0: number, v1: number, e = ease) =>
  interpolate(f, [a, b], [v0, v1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});

// grão de filme + vinheta
export const Grao: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', inset: -64, backgroundImage: `url(${staticFile('af/grao.png')})`, backgroundSize: '512px 512px',
        transform: `translate(${(random(`gx${f % 8}`) * 64) | 0}px, ${(random(`gy${f % 8}`) * 64) | 0}px)`, opacity: 0.07, mixBlendMode: 'overlay'}} />
      <AbsoluteFill style={{background: 'radial-gradient(120% 80% at 50% 45%, transparent 55%, rgba(0,0,0,.65) 100%)'}} />
    </AbsoluteFill>
  );
};

// partículas de poeira no feixe de luz
export const Poeira: React.FC<{n?: number; cor?: string; dur: number}> = ({n = 40, cor = '255,190,140', dur}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {Array.from({length: n}).map((_, i) => {
        const x = random(`x${i}`) * 1080, y0 = random(`y${i}`) * 1920, r = 1.5 + random(`r${i}`) * 4;
        const v = 0.2 + random(`v${i}`) * 0.6;
        const y = (y0 - f * v * 1.6 + 1920) % 1920;
        const xx = x + Math.sin((f + i * 20) / 40) * 18;
        const a = 0.15 + 0.5 * random(`a${i}`);
        return <div key={i} style={{position: 'absolute', left: xx, top: y, width: r, height: r, borderRadius: '50%',
          background: `rgba(${cor},${a})`, opacity: lerp(f, 0, 12, 0, 1) * lerp(f, dur - 10, dur, 1, 0)}} />;
      })}
    </AbsoluteFill>
  );
};

export type Mov = {z0: number; z1: number; x0?: number; x1?: number; y0?: number; y1?: number; ox?: number; oy?: number; e?: (n: number) => number};
export const Plano: React.FC<{src: string; dur: number; mov: Mov; grade?: string; poeira?: boolean; ent?: number; sai?: number}> = ({src, dur, mov, grade, poeira, ent = 3, sai = 0}) => {
  const f = useCurrentFrame();
  const em = mov.e || io;
  const z = lerp(f, 0, dur, mov.z0, mov.z1, em);
  const x = lerp(f, 0, dur, mov.x0 || 0, mov.x1 || 0, em);
  const y = lerp(f, 0, dur, mov.y0 || 0, mov.y1 || 0, em);
  const op = (ent ? lerp(f, 0, ent, 0, 1) : 1) * (sai ? lerp(f, dur - sai, dur, 1, 0) : 1);
  return (
    <AbsoluteFill style={{background: '#000', opacity: op}}>
      <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover',
        transformOrigin: `${mov.ox ?? 50}% ${mov.oy ?? 50}%`, transform: `scale(${z}) translate(${x}px, ${y}px)`, filter: grade || 'contrast(1.08) saturate(.92) brightness(.95)'}} />
      {/* varredura de luz quente */}
      <AbsoluteFill style={{background: `linear-gradient(105deg, transparent ${lerp(f, 0, dur, -30, 90)}%, rgba(255,140,60,.10) ${lerp(f, 0, dur, -20, 100)}%, transparent ${lerp(f, 0, dur, -10, 110)}%)`, mixBlendMode: 'screen'}} />
      {poeira && <Poeira dur={dur} />}
    </AbsoluteFill>
  );
};

// texto com revelação palavra a palavra (desfoque -> nítido)
export const Frase: React.FC<{texto: string; dur: number; top?: number; tam?: number; destaque?: string}> = ({texto, dur, top = 1340, tam = 64, destaque}) => {
  const f = useCurrentFrame();
  const pal = texto.split(' ');
  const sai = lerp(f, dur - 10, dur, 1, 0);
  return (
    <div style={{position: 'absolute', left: 90, right: 90, top, textAlign: 'center', font: `800 ${tam}px/1.12 StackH`, color: '#F4F2EC', letterSpacing: -1.5, opacity: sai,
      textShadow: '0 4px 40px rgba(0,0,0,.6)'}}>
      {pal.map((p, i) => {
        const t0 = 6 + i * 4;
        const o = lerp(f, t0, t0 + 14, 0, 1), b = lerp(f, t0, t0 + 14, 14, 0), yy = lerp(f, t0, t0 + 16, 18, 0);
        const cor = destaque && p.replace(/[.,]/g, '') === destaque ? LAR : undefined;
        return <span key={i} style={{display: 'inline-block', marginRight: '0.26em', opacity: o, filter: `blur(${b}px)`, transform: `translateY(${yy}px)`, color: cor}}>{p}</span>;
      })}
    </div>
  );
};

// notebook 3D com tela real
export const Notebook: React.FC<{f: number; tela: string; tela2?: string; troca?: number}> = ({f, tela, tela2, troca = 99999}) => {
  const liga = lerp(f, s(0.9), s(1.7), 0, 1);
  const t2 = tela2 ? lerp(f, troca, troca + 12, 0, 1) : 0;
  return (
    <div style={{width: 900, transformStyle: 'preserve-3d'}}>
      <div style={{position: 'relative', background: '#0c0c0e', borderRadius: '26px 26px 6px 6px', padding: 18, boxShadow: '0 0 0 2px #2a2a30, 0 90px 140px rgba(0,0,0,.75)'}}>
        <div style={{position: 'relative', borderRadius: 8, overflow: 'hidden', aspectRatio: '2690/1861', background: '#050506'}}>
          <Img src={staticFile(tela)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: liga * (1 - t2), filter: `brightness(${0.4 + 0.6 * liga})`}} />
          {tela2 && <Img src={staticFile(tela2)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: t2}} />}
          <div style={{position: 'absolute', inset: 0, background: `linear-gradient(115deg, rgba(255,255,255,0) ${lerp(f, s(1.0), s(2.8), -40, 120)}%, rgba(255,255,255,.16) ${lerp(f, s(1.0), s(2.8), -25, 135)}%, rgba(255,255,255,0) ${lerp(f, s(1.0), s(2.8), -10, 150)}%)`}} />
        </div>
      </div>
      <div style={{height: 34, margin: '0 -64px', background: 'linear-gradient(180deg,#3c3c44,#16161a)', borderRadius: '0 0 30px 30px', boxShadow: '0 40px 80px rgba(0,0,0,.6)'}} />
    </div>
  );
};

export const Celular: React.FC<{tela: string}> = ({tela}) => (
  <div style={{width: 420, borderRadius: 60, background: '#0a0a0c', padding: 13, boxShadow: '0 0 0 3px #2b2b31, 0 70px 120px rgba(0,0,0,.85)', position: 'relative'}}>
    <Img src={staticFile(tela)} style={{width: '100%', borderRadius: 40, display: 'block'}} />
    <div style={{position: 'absolute', inset: 13, borderRadius: 40, background: 'linear-gradient(120deg, rgba(255,255,255,.14), rgba(255,255,255,0) 45%)'}} />
  </div>
);

