// V1 — "Apresentamos o AutoFlow" (lançamento cinematográfico, 38 s, 9:16)
// Cenas de oficina = imagens-chave (Higgsfield Soul Cinema) com movimento de câmera feito aqui.
// Interface = SOMENTE recortes das capturas reais (sem banner/plano), compostos em dispositivos 3D.
import React from 'react';
import {AbsoluteFill, Audio, Img, interpolate, Easing, Sequence, staticFile, useCurrentFrame, random} from 'remotion';

const FPS = 30;
const s = (t: number) => Math.round(t * FPS);
const LAR = '#FF6A13';
const ease = Easing.bezier(0.22, 1, 0.36, 1);
const io = Easing.bezier(0.65, 0, 0.35, 1);

const css = `
@font-face{font-family:StackH;font-weight:800;src:url(${staticFile('fontes/stack-sans-headline-latin-700-normal.woff2')})}
@font-face{font-family:StackT;font-weight:500;src:url(${staticFile('fontes/stack-sans-text-latin-500-normal.woff2')})}
`;

const lerp = (f: number, a: number, b: number, v0: number, v1: number, e = ease) =>
  interpolate(f, [a, b], [v0, v1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});

// grão de filme + vinheta
const Grao: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <svg width="1080" height="1920" style={{position: 'absolute', opacity: 0.09, mixBlendMode: 'overlay'}}>
        <filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 12} /></filter>
        <rect width="1080" height="1920" filter="url(#g)" />
      </svg>
      <AbsoluteFill style={{background: 'radial-gradient(120% 80% at 50% 45%, transparent 55%, rgba(0,0,0,.65) 100%)'}} />
    </AbsoluteFill>
  );
};

// partículas de poeira no feixe de luz
const Poeira: React.FC<{n?: number; cor?: string; dur: number}> = ({n = 40, cor = '255,190,140', dur}) => {
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
          background: `rgba(${cor},${a})`, filter: `blur(${r > 4 ? 2 : 0.6}px)`, opacity: lerp(f, 0, 12, 0, 1) * lerp(f, dur - 10, dur, 1, 0)}} />;
      })}
    </AbsoluteFill>
  );
};

type Mov = {z0: number; z1: number; x0?: number; x1?: number; y0?: number; y1?: number};
const Plano: React.FC<{src: string; dur: number; mov: Mov; grade?: string; poeira?: boolean}> = ({src, dur, mov, grade, poeira}) => {
  const f = useCurrentFrame();
  const z = lerp(f, 0, dur, mov.z0, mov.z1, io);
  const x = lerp(f, 0, dur, mov.x0 || 0, mov.x1 || 0, io);
  const y = lerp(f, 0, dur, mov.y0 || 0, mov.y1 || 0, io);
  const op = lerp(f, 0, 9, 0, 1) * lerp(f, dur - 9, dur, 1, 0);
  return (
    <AbsoluteFill style={{background: '#000', opacity: op}}>
      <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover',
        transform: `scale(${z}) translate(${x}px, ${y}px)`, filter: grade || 'contrast(1.08) saturate(.92) brightness(.95)'}} />
      {/* varredura de luz quente */}
      <AbsoluteFill style={{background: `linear-gradient(105deg, transparent ${lerp(f, 0, dur, -30, 90)}%, rgba(255,140,60,.10) ${lerp(f, 0, dur, -20, 100)}%, transparent ${lerp(f, 0, dur, -10, 110)}%)`, mixBlendMode: 'screen'}} />
      {poeira && <Poeira dur={dur} />}
    </AbsoluteFill>
  );
};

// texto com revelação palavra a palavra (desfoque -> nítido)
const Frase: React.FC<{texto: string; dur: number; top?: number; tam?: number; destaque?: string}> = ({texto, dur, top = 1340, tam = 64, destaque}) => {
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
const Notebook: React.FC<{f: number; tela: string; tela2?: string; troca?: number}> = ({f, tela, tela2, troca = 99999}) => {
  const liga = lerp(f, s(1.2), s(2.2), 0, 1);
  const t2 = tela2 ? lerp(f, troca, troca + 12, 0, 1) : 0;
  return (
    <div style={{width: 900, transformStyle: 'preserve-3d'}}>
      <div style={{position: 'relative', background: '#0c0c0e', borderRadius: '26px 26px 6px 6px', padding: 18, boxShadow: '0 0 0 2px #2a2a30, 0 90px 140px rgba(0,0,0,.75)'}}>
        <div style={{position: 'relative', borderRadius: 8, overflow: 'hidden', aspectRatio: '2690/1861', background: '#050506'}}>
          <Img src={staticFile(tela)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: liga * (1 - t2), filter: `brightness(${0.4 + 0.6 * liga})`}} />
          {tela2 && <Img src={staticFile(tela2)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: t2}} />}
          <div style={{position: 'absolute', inset: 0, background: `linear-gradient(115deg, rgba(255,255,255,0) ${lerp(f, s(1.4), s(3.4), -40, 120)}%, rgba(255,255,255,.16) ${lerp(f, s(1.4), s(3.4), -25, 135)}%, rgba(255,255,255,0) ${lerp(f, s(1.4), s(3.4), -10, 150)}%)`}} />
        </div>
      </div>
      <div style={{height: 34, margin: '0 -64px', background: 'linear-gradient(180deg,#3c3c44,#16161a)', borderRadius: '0 0 30px 30px', boxShadow: '0 40px 80px rgba(0,0,0,.6)'}} />
    </div>
  );
};

const Celular: React.FC<{tela: string}> = ({tela}) => (
  <div style={{width: 420, borderRadius: 60, background: '#0a0a0c', padding: 13, boxShadow: '0 0 0 3px #2b2b31, 0 70px 120px rgba(0,0,0,.85)', position: 'relative'}}>
    <Img src={staticFile(tela)} style={{width: '100%', borderRadius: 40, display: 'block'}} />
    <div style={{position: 'absolute', inset: 13, borderRadius: 40, background: 'linear-gradient(120deg, rgba(255,255,255,.14), rgba(255,255,255,0) 45%)'}} />
  </div>
);

// bloco do produto: 13 s -> 31 s (18 s)
const Produto: React.FC = () => {
  const f = useCurrentFrame();
  const D = s(18);
  // entrada do notebook
  const ry = lerp(f, 0, s(4), -38, -14), rx = lerp(f, 0, s(4), 24, 12), ty = lerp(f, 0, s(3.5), 260, 0), op = lerp(f, 0, s(1.2), 0, 1);
  // zoom nos cards (7-10 s) e no quadro de Ordens (10-13 s)
  const zoom = f < s(7) ? 1 : f < s(10) ? lerp(f, s(7), s(8.5), 1, 1.75) : lerp(f, s(10), s(11), 1.75, 1.55);
  const px = f < s(10) ? lerp(f, s(7), s(8.5), 0, 260) : lerp(f, s(10.3), s(13), 300, -260, io);
  const py = f < s(10) ? lerp(f, s(7), s(8.5), 0, 120) : lerp(f, s(10), s(11), 120, 40);
  // celular entra (13-18 s) e notebook recua
  const cel = lerp(f, s(13), s(14.6), 0, 1);
  const recua = lerp(f, s(12.6), s(14), 0, 1);
  const z = zoom * (1 - 0.32 * recua);
  return (
    <AbsoluteFill style={{background: 'radial-gradient(80% 50% at 50% 50%, #2a1508 0%, #0E0E10 62%)'}}>
      <div style={{position: 'absolute', left: 140, top: 640, width: 800, height: 640, borderRadius: '50%', background: LAR, filter: 'blur(170px)', opacity: 0.26 + 0.1 * Math.sin(f / 30)}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 2400}}>
        <div style={{transform: `translate(${px * (1 - recua)}px, ${ty + py * (1 - recua) - 180 * recua}px) scale(${z}) rotateX(${rx}deg) rotateY(${ry + 8 * recua}deg)`,
          opacity: op * (1 - 0.45 * recua), filter: `blur(${5 * recua}px)`, transformStyle: 'preserve-3d'}}>
          <Notebook f={f} tela="af/painel_conteudo.png" tela2="af/ordens_conteudo.png" troca={s(10)} />
        </div>
      </AbsoluteFill>
      {cel > 0 && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 1800}}>
          <div style={{transform: `translate(${lerp(f, s(13), s(14.8), 560, 90)}px, ${lerp(f, s(13), s(18), 160, 110)}px) rotateY(${lerp(f, s(13), s(18), -34, -16)}deg) rotateX(6deg)`, opacity: cel}}>
            <Celular tela="af/celular_painel.png" />
          </div>
        </AbsoluteFill>
      )}
      <Sequence from={0} durationInFrames={s(6.6)}><Frase texto="Apresentamos o AutoFlow." destaque="AutoFlow" dur={s(6.6)} top={300} tam={96} /></Sequence>
      <Sequence from={s(7.2)} durationInFrames={s(5.6)}><Frase texto="Cada ordem de serviço, da entrada à entrega." dur={s(5.6)} top={300} tam={66} /></Sequence>
      <Sequence from={s(13.4)} durationInFrames={s(4.6)}><Frase texto="Na mesa ou no bolso." dur={s(4.6)} top={300} tam={80} /></Sequence>
      {/* nota de rodapé honesta: interface real */}
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 360, textAlign: 'center', font: '500 24px StackT', color: 'rgba(244,242,236,.45)', letterSpacing: 2,
        opacity: lerp(f, s(2), s(3), 0, 1) * lerp(f, D - 15, D, 1, 0) * (f > s(6.8) && f < s(13.2) ? 0 : 1)}}>INTERFACE REAL DO SISTEMA</div>
    </AbsoluteFill>
  );
};

const Fecho: React.FC = () => {
  const f = useCurrentFrame();
  const sc = lerp(f, 0, s(1.2), 0.82, 1), op = lerp(f, 0, s(0.8), 0, 1);
  const brilho = lerp(f, s(0.3), s(1.6), 0, 1) * lerp(f, s(1.6), s(3), 1, 0.35);
  return (
    <AbsoluteFill style={{background: '#0E0E10', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{position: 'absolute', width: 600, height: 600, borderRadius: '50%', background: LAR, filter: 'blur(200px)', opacity: 0.35 * brilho}} />
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: op, transform: `scale(${sc})`, marginTop: -120}}>
        <Img src={staticFile('af/logo-icone.png')} style={{width: 210}} />
        <div style={{font: '800 112px/1 StackH', color: '#F4F2EC', letterSpacing: -4, marginTop: 46}}>AutoFlow</div>
        <div style={{font: '500 30px StackT', color: 'rgba(244,242,236,.55)', marginTop: 16, letterSpacing: 1}}>by Seraphim</div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1360, textAlign: 'center', font: '800 54px StackH', color: LAR, letterSpacing: -1,
        opacity: lerp(f, s(1.3), s(2.2), 0, 1), transform: `translateY(${lerp(f, s(1.3), s(2.3), 20, 0)}px)`}}>Conheça o AutoFlow.</div>
    </AbsoluteFill>
  );
};

export type PropsAF = {trilha: string | null};

export const AutoFlowV1: React.FC<PropsAF> = ({trilha}) => (
  <AbsoluteFill style={{background: '#000'}}>
    <style>{css}</style>
    <Sequence from={0} durationInFrames={s(4.3)}>
      <Plano src="af/cena-01.png" dur={s(4.3)} mov={{z0: 1.22, z1: 1.04, x0: -10, x1: 8}} poeira />
    </Sequence>
    <Sequence from={s(4)} durationInFrames={s(4.3)}>
      <Plano src="af/cena-02.png" dur={s(4.3)} mov={{z0: 1.14, z1: 1.14, x0: 50, x1: -50}} />
      <Frase texto="Toda oficina tem um ritmo." dur={s(4.3)} />
    </Sequence>
    <Sequence from={s(8)} durationInFrames={s(4)}>
      <Plano src="af/cena-03.png" dur={s(4)} mov={{z0: 1.02, z1: 1.2, y0: 0, y1: -30}} />
      <Frase texto="E toda gestão merece clareza." destaque="clareza" dur={s(4)} />
    </Sequence>
    {/* 12-13 s: preto e silêncio */}
    <Sequence from={s(13)} durationInFrames={s(18)}><Produto /></Sequence>
    <Sequence from={s(31)} durationInFrames={s(3.2)}>
      <Plano src="af/cena-04.png" dur={s(3.2)} mov={{z0: 1.06, z1: 1.16, x0: 0, x1: -20}} />
    </Sequence>
    <Sequence from={s(34)} durationInFrames={s(4)}><Fecho /></Sequence>
    <Grao />
    {trilha && <Audio src={staticFile(trilha)} />}
  </AbsoluteFill>
);
