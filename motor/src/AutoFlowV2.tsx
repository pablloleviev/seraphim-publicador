// V2 — "Do caderno ao sistema" (40 s, 9:16). Linguagem própria: luz de janela, papel, match-cut da
// anotação para o cartão da OS, monitor frontal (não notebook), texto alinhado à esquerda.
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {s, LAR, ease, io, css, lerp, Grao, Plano} from './AutoFlowKit';

const CREME = '#F4F2EC';

// texto à esquerda, linha a linha, com traço laranja
const Legenda: React.FC<{texto: string; dur: number; top?: number; tam?: number; claro?: boolean}> = ({texto, dur, top = 1240, tam = 62, claro}) => {
  const f = useCurrentFrame();
  const o = lerp(f, 4, 18, 0, 1) * lerp(f, dur - 10, dur, 1, 0);
  return (
    <div style={{position: 'absolute', left: 88, right: 120, top, opacity: o}}>
      <div style={{width: lerp(f, 0, 16, 0, 64), height: 4, background: LAR, marginBottom: 26, borderRadius: 2}} />
      <div style={{font: `800 ${tam}px/1.1 StackH`, color: claro ? '#141414' : CREME, letterSpacing: -1.6, textShadow: claro ? 'none' : '0 4px 36px rgba(0,0,0,.55)',
        transform: `translateY(${lerp(f, 4, 20, 22, 0)}px)`, clipPath: `inset(0 ${lerp(f, 4, 22, 100, 0)}% 0 0)`}}>{texto}</div>
    </div>
  );
};

// monitor frontal (tipo estúdio), com tela real
const Monitor: React.FC<{tela: string; zoom: number; px: number; py: number; ox?: number; oy?: number}> = ({tela, zoom, px, py, ox = 50, oy = 50}) => (
  <div style={{width: 960}}>
    <div style={{background: '#0b0b0d', borderRadius: 22, padding: 16, boxShadow: '0 0 0 2px #2a2a30, 0 80px 140px rgba(0,0,0,.7)'}}>
      <div style={{borderRadius: 8, overflow: 'hidden', aspectRatio: '16/10.6', background: '#0E0E10', position: 'relative'}}>
        <Img src={staticFile(tela)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top left',
          transformOrigin: `${ox}% ${oy}%`, transform: `translate(${px}px, ${py}px) scale(${zoom})`}} />
        <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,0) 40%)'}} />
      </div>
    </div>
    <div style={{width: 120, height: 150, margin: '0 auto', background: 'linear-gradient(90deg,#1a1a1e,#2c2c32,#1a1a1e)'}} />
    <div style={{width: 360, height: 18, margin: '0 auto', borderRadius: 10, background: '#232328', boxShadow: '0 30px 60px rgba(0,0,0,.6)'}} />
  </div>
);

// 15-18 s: match-cut — o papel vira o cartão da OS
const Match: React.FC = () => {
  const f = useCurrentFrame();
  const D = s(4.4);
  const t = lerp(f, s(1.6), s(2.8), 0, 1, io);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Img src={staticFile('af/cena-05.png')} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover',
        transformOrigin: '56% 44%', transform: `scale(${lerp(f, 0, D, 1.5, 3.2, io)})`, opacity: 1 - t, filter: 'contrast(1.05) saturate(.9)'}} />
      <AbsoluteFill style={{background: '#0E0E10', opacity: t}}>
        <Img src={staticFile('af/ordens_conteudo.png')} style={{position: 'absolute', width: 2728, left: -492, top: 207,
          transformOrigin: '1032px 553px', transform: `scale(${lerp(f, s(1.6), D, 1.7, 1.15, ease)})`}} />
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(14,14,16,0) 55%, rgba(14,14,16,.92) 72%)'}} />
      </AbsoluteFill>
      <Legenda texto="E se cada anotação tivesse um lugar?" dur={D} top={1300} />
    </AbsoluteFill>
  );
};

// 18-31 s: sistema real no monitor
const Sistema: React.FC = () => {
  const f = useCurrentFrame();
  const ent = lerp(f, 0, s(1.2), 0, 1);
  const fase2 = f >= s(7);
  const z = fase2 ? lerp(f, s(7), s(9), 1.0, 1.35, io) : lerp(f, 0, s(7), 1.12, 1.0, io);
  const px = fase2 ? lerp(f, s(7), s(9), 0, -40, io) : lerp(f, s(0.5), s(6.5), 0, -420, io);
  const troca = lerp(f, s(6.6), s(7.2), 0, 1);
  return (
    <AbsoluteFill style={{background: 'radial-gradient(90% 55% at 50% 42%, #22140b 0%, #0E0E10 65%)'}}>
      <div style={{position: 'absolute', left: 90, top: 520, width: 900, height: 700, borderRadius: '50%', background: `radial-gradient(closest-side, ${LAR}, transparent)`, opacity: 0.18}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        <div style={{transform: `translateY(${lerp(f, 0, s(1.4), 120, -40)}px) scale(${lerp(f, 0, s(1.4), 0.94, 1)})`, opacity: ent}}>
          <div style={{position: 'relative'}}>
            <div style={{opacity: 1 - troca}}><Monitor tela="af/ordens_conteudo.png" zoom={z * 1.5} px={px} py={0} ox={0} oy={0} /></div>
            <div style={{position: 'absolute', inset: 0, opacity: troca}}><Monitor tela="af/historico_conteudo.png" zoom={fase2 ? z : 1} px={fase2 ? px : 0} py={0} ox={10} oy={18} /></div>
          </div>
        </div>
      </AbsoluteFill>
      <Sequence from={s(0.5)} durationInFrames={s(6.1)}><Legenda texto="Cada ordem de serviço no quadro, do pendente à entrega." dur={s(6.1)} top={1500} tam={54} /></Sequence>
      <Sequence from={s(6.8)} durationInFrames={s(5.4)}><Legenda texto="E o histórico de cada carro, pela placa." dur={s(5.4)} top={1500} tam={58} /></Sequence>
    </AbsoluteFill>
  );
};

const Fecho: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: CREME, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 34, opacity: lerp(f, 0, 18, 0, 1), transform: `translateY(${lerp(f, 0, 24, 30, 0)}px)`, marginTop: -160}}>
        <Img src={staticFile('af/logo-icone.png')} style={{width: 150, filter: 'drop-shadow(0 10px 30px rgba(0,0,0,.15))'}} />
        <div>
          <div style={{font: '800 96px/1 StackH', color: '#121214', letterSpacing: -3}}>AutoFlow</div>
          <div style={{font: '500 28px StackT', color: 'rgba(18,18,20,.5)', marginTop: 10}}>by Seraphim</div>
        </div>
      </div>
      <div style={{position: 'absolute', left: 100, right: 100, top: 1180, textAlign: 'center', font: '800 58px/1.15 StackH', color: '#121214', letterSpacing: -1.5,
        opacity: lerp(f, 20, 40, 0, 1)}}>Sua oficina merece uma gestão <span style={{color: LAR}}>mais simples.</span></div>
    </AbsoluteFill>
  );
};

export type PropsAF2 = {trilha: string | null};

export const AutoFlowV2: React.FC<PropsAF2> = ({trilha}) => (
  <AbsoluteFill style={{background: '#000'}}>
    <style>{css}</style>
    <Sequence from={0} durationInFrames={s(5.2)}>
      <Plano src="af/cena-05.png" dur={s(5.2)} ent={10} mov={{z0: 1.12, z1: 1.28, ox: 55, oy: 45, e: io}} grade="contrast(1.04) saturate(.95) brightness(1.02)" />
      <Legenda texto="Esse caderno já sabe muita coisa da sua oficina." dur={s(5.2)} top={1300} />
    </Sequence>
    <Sequence from={s(5)} durationInFrames={s(5.2)}>
      <Plano src="af/cena-06.png" dur={s(5.2)} ent={8} mov={{z0: 1.16, z1: 1.06, x0: -20, x1: 10, e: ease}} />
      <Legenda texto="Só que nem sempre ele te encontra na hora certa." dur={s(5.2)} top={1300} />
    </Sequence>
    <Sequence from={s(10)} durationInFrames={s(5.2)}>
      <Plano src="af/cena-07.png" dur={s(5.2)} ent={8} mov={{z0: 1.18, z1: 1.18, x0: 60, x1: -60, e: io}} />
    </Sequence>
    <Sequence from={s(15)} durationInFrames={s(4.4)}><Match /></Sequence>
    <Sequence from={s(19.4)} durationInFrames={s(12.2)}><Sistema /></Sequence>
    <Sequence from={s(31.4)} durationInFrames={s(5.2)}>
      <Plano src="af/cena-08.png" dur={s(5.2)} ent={12} sai={10} mov={{z0: 1.04, z1: 1.1, e: io}} />
      <Legenda texto="O caderno pode descansar." dur={s(5.2)} top={1300} />
    </Sequence>
    <Sequence from={s(36.4)} durationInFrames={s(5.6)}><Fecho /></Sequence>
    <Grao />
    {trilha && <Audio src={staticFile(trilha)} />}
  </AbsoluteFill>
);
