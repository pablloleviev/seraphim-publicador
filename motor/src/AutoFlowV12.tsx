// V12 — "Do caderno ao sistema" (39 s, 9:16). MESMA LINGUAGEM DO V1 APROVADO:
// cenas de oficina com movimento de câmera e cortes motivados (dois ângulos do mesmo plano),
// batida de preto antes da revelação, bloco de produto com a tela real no notebook 3D saindo do
// escuro (exposição, poça de luz laranja, linha de luz, sombra de contato), grão, poeira e vinheta.
// Texto: Stack Sans, revelação palavra a palavra. Áudio: só trilha e efeitos (sem narração).
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {s, LAR, ease, io, css, lerp, Grao, Plano, Frase, Notebook} from './AutoFlowKit';

// bloco do produto: 13 s -> 31 s (18 s) — quadro de ordens e, depois, histórico por placa
const Produto: React.FC = () => {
  const f = useCurrentFrame();
  const ry = lerp(f, 0, s(3.4), -26, -12), rx = lerp(f, 0, s(3.4), 28, 10);
  const ty = lerp(f, 0, s(2.8), 320, 0), op = lerp(f, 0, s(0.5), 0, 1);
  const luz = lerp(f, 0, s(1.6), 0, 1);
  const exp = lerp(f, s(0.2), s(1.8), 0.15, 1);
  // 4,5-8 s: aproxima nas colunas do quadro | 9,2 s: troca para o histórico | 10-16 s: caminha até a placa
  const zoom = f < s(4.5) ? 1 : f < s(9) ? lerp(f, s(4.5), s(6.4), 1, 1.7)
    : f < s(12) ? lerp(f, s(9.4), s(11), 1.7, 1.5) : lerp(f, s(12), s(15.5), 1.5, 1.95, io);
  const px = f < s(9) ? lerp(f, s(4.5), s(6.4), 0, 300) : lerp(f, s(9.6), s(15.5), -140, 260, io);
  const py = f < s(9) ? lerp(f, s(4.5), s(6.4), 0, 150) : lerp(f, s(9.6), s(15.5), 60, -150, io);
  const sai = lerp(f, s(16.6), s(18), 0, 1);
  return (
    <AbsoluteFill style={{background: '#050506'}}>
      <AbsoluteFill style={{background: 'radial-gradient(80% 50% at 50% 50%, #2a1508 0%, #0E0E10 62%)', opacity: luz}} />
      <div style={{position: 'absolute', left: 120, top: 620, width: 840, height: 660, borderRadius: '50%',
        background: `radial-gradient(closest-side, ${LAR}, transparent)`, opacity: luz * (0.26 + 0.08 * Math.sin(f / 30)), transform: `scale(${0.6 + 0.4 * luz})`}} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 1180, height: 2, background: `linear-gradient(90deg, transparent, ${LAR}, transparent)`,
        opacity: lerp(f, 0, s(0.3), 0, 1) * lerp(f, s(0.6), s(1.4), 1, 0), transform: `scaleX(${lerp(f, 0, s(0.7), 0.05, 1)})`, boxShadow: `0 0 40px ${LAR}`}} />
      <div style={{position: 'absolute', left: 190, right: 190, top: 1235, height: 90, borderRadius: '50%',
        background: 'radial-gradient(closest-side, rgba(0,0,0,.75), transparent)', opacity: op * (1 - sai)}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 2400}}>
        <div style={{transform: `translate(${px * (1 - sai)}px, ${ty + py * (1 - sai) - 160 * sai}px) scale(${zoom * (1 - 0.28 * sai)}) rotateX(${rx}deg) rotateY(${ry + 6 * sai}deg)`,
          opacity: op * (1 - 0.5 * sai), filter: `blur(${3 * sai}px) brightness(${exp})`, transformStyle: 'preserve-3d'}}>
          <Notebook f={f} tela="af/ordens_conteudo.png" tela2="af/historico_conteudo.png" troca={s(9.2)} />
        </div>
      </AbsoluteFill>
      <Sequence from={s(1.1)} durationInFrames={s(5.2)}><Frase texto="Cada ordem no seu lugar." destaque="lugar." dur={s(5.2)} top={300} tam={88} /></Sequence>
      <Sequence from={s(6.6)} durationInFrames={s(5.0)}><Frase texto="Do pendente à entrega." dur={s(5.0)} top={300} tam={84} /></Sequence>
      <Sequence from={s(12.2)} durationInFrames={s(5.4)}><Frase texto="E o histórico de cada carro, pela placa." destaque="placa." dur={s(5.4)} top={300} tam={66} /></Sequence>
    </AbsoluteFill>
  );
};

const Fecho: React.FC = () => {
  const f = useCurrentFrame();
  const sc = lerp(f, 0, s(1.2), 0.82, 1), op = lerp(f, 0, s(0.8), 0, 1);
  const brilho = lerp(f, s(0.3), s(1.6), 0, 1) * lerp(f, s(1.6), s(3), 1, 0.35);
  return (
    <AbsoluteFill style={{background: '#0E0E10', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{position: 'absolute', width: 600, height: 600, borderRadius: '50%', background: `radial-gradient(closest-side, ${LAR}, transparent)`, opacity: 0.35 * brilho}} />
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: op, transform: `scale(${sc})`, marginTop: -120}}>
        <Img src={staticFile('af/logo-icone.png')} style={{width: 210}} />
        <div style={{font: '800 112px/1 StackH', color: '#F4F2EC', letterSpacing: -4, marginTop: 46}}>AutoFlow</div>
        <div style={{font: '500 30px StackT', color: 'rgba(244,242,236,.55)', marginTop: 16, letterSpacing: 1}}>by Seraphim</div>
      </div>
      <div style={{position: 'absolute', left: 80, right: 80, top: 1330, textAlign: 'center', font: '800 54px/1.2 StackH', color: LAR, letterSpacing: -1,
        opacity: lerp(f, s(1.3), s(2.2), 0, 1), transform: `translateY(${lerp(f, s(1.3), s(2.3), 20, 0)}px)`}}>Sua oficina merece uma gestão mais simples.</div>
    </AbsoluteFill>
  );
};

export type PropsAF12 = {trilha: string | null};

export const AutoFlowV12: React.FC<PropsAF12> = ({trilha}) => (
  <AbsoluteFill style={{background: '#000'}}>
    <style>{css}</style>
    {/* 0-12 s: o que a oficina anota hoje — cortes motivados, dois ângulos do mesmo plano */}
    <Sequence from={0} durationInFrames={s(2.1)}>
      <Plano src="af/n-caderno-notebook.png" dur={s(2.1)} ent={8} mov={{z0: 1.3, z1: 1.1, x0: -12, x1: 8, e: ease}} poeira />
    </Sequence>
    <Sequence from={s(2.1)} durationInFrames={s(1.0)}>
      <Plano src="af/n-caderno-notebook.png" dur={s(1.0)} mov={{z0: 1.95, z1: 2.1, ox: 40, oy: 70, x0: 8, x1: -6}} poeira />
    </Sequence>
    <Sequence from={s(3.1)} durationInFrames={s(2.6)}>
      <Plano src="af/n-recepcionista-folheando.png" dur={s(2.6)} mov={{z0: 1.18, z1: 1.08, x0: 60, x1: -30, e: ease}} />
    </Sequence>
    <Sequence from={s(5.7)} durationInFrames={s(1.0)}>
      <Plano src="af/n-recepcionista-folheando.png" dur={s(1.0)} mov={{z0: 1.85, z1: 2.0, ox: 55, oy: 75, x0: -6, x1: 8}} />
    </Sequence>
    <Sequence from={s(6.7)} durationInFrames={s(2.3)}>
      <Plano src="af/n-celular-tocando.png" dur={s(2.3)} mov={{z0: 1.1, z1: 1.22, ox: 45, oy: 50, e: ease}} />
    </Sequence>
    <Sequence from={s(9.0)} durationInFrames={s(1.2)}>
      <Plano src="af/n-celular-tocando.png" dur={s(1.2)} mov={{z0: 1.9, z1: 2.0, ox: 25, oy: 60}} />
    </Sequence>
    <Sequence from={s(10.2)} durationInFrames={s(1.8)}>
      <Plano src="af/n-mural.png" dur={s(1.8)} sai={14} mov={{z0: 1.26, z1: 1.55, ox: 60, oy: 45, e: io}} />
    </Sequence>
    <Sequence from={s(3.1)} durationInFrames={s(3.4)}><Frase texto="Toda oficina anota." dur={s(3.4)} /></Sequence>
    <Sequence from={s(6.9)} durationInFrames={s(4.9)}><Frase texto="Depois, precisa achar." destaque="achar." dur={s(4.9)} /></Sequence>
    {/* 12-13 s: preto e silêncio */}
    <Sequence from={s(13)} durationInFrames={s(18)}><Produto /></Sequence>
    <Sequence from={s(31)} durationInFrames={s(3.4)}>
      <Plano src="af/n-digitando.png" dur={s(3.4)} ent={6} mov={{z0: 1.06, z1: 1.2, ox: 55, oy: 45, e: ease}} />
    </Sequence>
    <Sequence from={s(34.2)} durationInFrames={s(4.8)}><Fecho /></Sequence>
    <Grao />
    {trilha && <Audio src={staticFile(trilha)} />}
  </AbsoluteFill>
);
