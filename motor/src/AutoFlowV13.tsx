// V13 — "Um dia na oficina" (39,5 s, 9:16). MESMA LINGUAGEM DO V1 APROVADO:
// montagem cinematográfica com cortes motivados, batidas de preto antes de cada revelação,
// blocos de produto com telas reais em notebook e celular 3D saindo do escuro, grão, poeira e vinheta.
// A hora é o fio narrativo (07:42 -> 18:20), em Stack Sans, com a mesma revelação do texto do V1.
// Áudio: só trilha e efeitos (sem narração).
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {s, LAR, ease, io, css, lerp, Grao, Plano, Frase, Notebook, Celular} from './AutoFlowKit';

// hora do dia: mesma revelação do texto (desfoque -> nítido), com o fio de luz laranja
const Hora: React.FC<{hora: string; dur: number}> = ({hora, dur}) => {
  const f = useCurrentFrame();
  const sai = lerp(f, dur - 10, dur, 1, 0);
  return (
    <div style={{position: 'absolute', left: 90, top: 250, opacity: sai}}>
      <div style={{font: '800 136px/1 StackH', color: '#F4F2EC', letterSpacing: -5, textShadow: '0 4px 40px rgba(0,0,0,.65)'}}>
        {hora.split('').map((c, i) => {
          const t0 = 4 + i * 3;
          return <span key={i} style={{display: 'inline-block', opacity: lerp(f, t0, t0 + 12, 0, 1),
            filter: `blur(${lerp(f, t0, t0 + 12, 12, 0)}px)`, transform: `translateY(${lerp(f, t0, t0 + 14, 16, 0)}px)`}}>{c}</span>;
        })}
      </div>
      <div style={{width: lerp(f, 8, 24, 0, 130), height: 4, background: LAR, marginTop: 16, borderRadius: 2, boxShadow: `0 0 24px ${LAR}`}} />
    </div>
  );
};

// bloco de produto (notebook): o painel do dia
const ProdutoPainel: React.FC = () => {
  const f = useCurrentFrame();
  const ry = lerp(f, 0, s(3.2), -28, -12), rx = lerp(f, 0, s(3.2), 26, 10);
  const ty = lerp(f, 0, s(2.6), 320, 0), op = lerp(f, 0, s(0.5), 0, 1);
  const luz = lerp(f, 0, s(1.6), 0, 1);
  const exp = lerp(f, s(0.2), s(1.8), 0.15, 1);
  const zoom = f < s(4.2) ? 1 : f < s(7) ? lerp(f, s(4.2), s(6), 1, 1.65) : lerp(f, s(7), s(8.6), 1.65, 1.8, io);
  const px = f < s(7) ? lerp(f, s(4.2), s(6), 0, 250) : lerp(f, s(7), s(8.6), 250, -120, io);
  const py = f < s(7) ? lerp(f, s(4.2), s(6), 0, -90) : lerp(f, s(7), s(8.6), -90, 120, io);
  const sai = lerp(f, s(7.8), s(9), 0, 1);
  return (
    <AbsoluteFill style={{background: '#050506'}}>
      <AbsoluteFill style={{background: 'radial-gradient(80% 50% at 50% 50%, #0f1a24 0%, #0E0E10 64%)', opacity: luz}} />
      <div style={{position: 'absolute', left: 140, top: 620, width: 820, height: 640, borderRadius: '50%',
        background: `radial-gradient(closest-side, ${LAR}, transparent)`, opacity: luz * 0.2, transform: `scale(${0.6 + 0.4 * luz})`}} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 1180, height: 2, background: `linear-gradient(90deg, transparent, ${LAR}, transparent)`,
        opacity: lerp(f, 0, s(0.3), 0, 1) * lerp(f, s(0.6), s(1.4), 1, 0), transform: `scaleX(${lerp(f, 0, s(0.7), 0.05, 1)})`, boxShadow: `0 0 40px ${LAR}`}} />
      <div style={{position: 'absolute', left: 190, right: 190, top: 1235, height: 90, borderRadius: '50%',
        background: 'radial-gradient(closest-side, rgba(0,0,0,.75), transparent)', opacity: op * (1 - sai)}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 2400}}>
        <div style={{transform: `translate(${px * (1 - sai)}px, ${ty + py * (1 - sai) - 150 * sai}px) scale(${zoom * (1 - 0.26 * sai)}) rotateX(${rx}deg) rotateY(${ry + 6 * sai}deg)`,
          opacity: op * (1 - 0.5 * sai), filter: `blur(${3 * sai}px) brightness(${exp})`, transformStyle: 'preserve-3d'}}>
          <Notebook f={f} tela="af/painel_conteudo.png" />
        </div>
      </AbsoluteFill>
      <Sequence from={s(1.0)} durationInFrames={s(5.0)}><Frase texto="O dia começa com o pátio na tela." destaque="tela." dur={s(5.0)} top={300} tam={72} /></Sequence>
      <Sequence from={s(6.3)} durationInFrames={s(3.0)}><Frase texto="O que entrou, o que está em andamento." dur={s(3.0)} top={300} tam={60} /></Sequence>
    </AbsoluteFill>
  );
};

// bloco de produto (nova OS + celular): a tarde da oficina
const ProdutoOS: React.FC = () => {
  const f = useCurrentFrame();
  const op = lerp(f, 0, s(0.5), 0, 1);
  const luz = lerp(f, 0, s(1.4), 0, 1);
  const exp = lerp(f, s(0.2), s(1.6), 0.2, 1);
  const sobe = lerp(f, 0, s(2.4), 260, 0);
  const zoom = f < s(3.4) ? lerp(f, s(1.4), s(3.4), 1, 1.18) : lerp(f, s(3.4), s(6), 1.18, 1.05, io);
  const cel = lerp(f, s(6.2), s(7.8), 0, 1);
  const recua = lerp(f, s(6), s(7.4), 0, 1);
  return (
    <AbsoluteFill style={{background: '#050506'}}>
      <AbsoluteFill style={{background: 'radial-gradient(80% 50% at 50% 48%, #24170c 0%, #0E0E10 64%)', opacity: luz}} />
      <div style={{position: 'absolute', left: 180, top: 560, width: 760, height: 700, borderRadius: '50%',
        background: `radial-gradient(closest-side, ${LAR}, transparent)`, opacity: luz * (0.24 + 0.06 * Math.sin(f / 26))}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 2000}}>
        <div style={{width: 560, borderRadius: 30, overflow: 'hidden', boxShadow: `0 0 0 2px #2a2a30, 0 80px 150px rgba(0,0,0,.8), 0 0 140px rgba(255,106,19,${0.14 * luz})`,
          transform: `translate(${-60 * recua}px, ${sobe - 120 * recua}px) scale(${zoom * (1 - 0.18 * recua)}) rotateY(${lerp(f, 0, s(6), 10, -4)}deg) rotateX(4deg)`,
          opacity: op * (1 - 0.45 * recua), filter: `blur(${3 * recua}px) brightness(${exp})`}}>
          <Img src={staticFile('af/nova_os_painel.png')} style={{width: '100%', display: 'block'}} />
        </div>
      </AbsoluteFill>
      {cel > 0 && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 1800}}>
          <div style={{transform: `translate(${lerp(f, s(6.2), s(8), 520, 120)}px, ${lerp(f, s(6.2), s(10), 170, 120)}px) rotateY(${lerp(f, s(6.2), s(10), -32, -14)}deg) rotateX(6deg)`, opacity: cel}}>
            <Celular tela="af/celular_ordens.png" />
          </div>
        </AbsoluteFill>
      )}
      <Sequence from={s(0.9)} durationInFrames={s(4.6)}><Frase texto="Uma ordem nova, em poucos campos." destaque="campos." dur={s(4.6)} top={300} tam={70} /></Sequence>
      <Sequence from={s(6.4)} durationInFrames={s(4.0)}><Frase texto="E o quadro vai junto." destaque="junto." dur={s(4.0)} top={300} tam={80} /></Sequence>
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
      <div style={{position: 'absolute', left: 80, right: 80, top: 1310, textAlign: 'center',
        opacity: lerp(f, s(1.3), s(2.2), 0, 1), transform: `translateY(${lerp(f, s(1.3), s(2.3), 20, 0)}px)`}}>
        <div style={{font: '800 52px/1.2 StackH', color: '#F4F2EC', letterSpacing: -1}}>Teste gratuito para oficinas selecionadas.</div>
        <div style={{font: '800 44px StackH', color: LAR, marginTop: 20, letterSpacing: -0.5}}>Solicite acesso pelo direct.</div>
      </div>
    </AbsoluteFill>
  );
};

export type PropsAF13 = {trilha: string | null};

export const AutoFlowV13: React.FC<PropsAF13> = ({trilha}) => (
  <AbsoluteFill style={{background: '#000'}}>
    <style>{css}</style>
    {/* 07:42 — a oficina abre */}
    <Sequence from={0} durationInFrames={s(2.3)}>
      <Plano src="af/n-cadeado.png" dur={s(2.3)} ent={8} mov={{z0: 1.28, z1: 1.1, ox: 65, oy: 45, e: ease}} grade="contrast(1.08) saturate(.86) brightness(.92)" poeira />
    </Sequence>
    <Sequence from={s(2.3)} durationInFrames={s(1.0)}>
      <Plano src="af/n-cadeado.png" dur={s(1.0)} mov={{z0: 1.95, z1: 2.1, ox: 70, oy: 50, x0: 6, x1: -8}} grade="contrast(1.08) saturate(.86) brightness(.92)" />
    </Sequence>
    <Sequence from={s(3.3)} durationInFrames={s(2.4)}>
      <Plano src="af/n-luzes.png" dur={s(2.4)} mov={{z0: 1.08, z1: 1.2, ox: 45, oy: 35, e: io}} grade="contrast(1.07) saturate(.88) brightness(.96)" />
    </Sequence>
    <Sequence from={s(5.7)} durationInFrames={s(2.6)}>
      <Plano src="af/cena-09.png" dur={s(2.6)} mov={{z0: 1.14, z1: 1.04, x0: 30, x1: -14, e: ease}} poeira />
    </Sequence>
    <Sequence from={s(8.3)} durationInFrames={s(1.6)}>
      <Plano src="af/cena-09.png" dur={s(1.6)} sai={12} mov={{z0: 1.8, z1: 2.0, ox: 30, oy: 40}} />
    </Sequence>
    <Sequence from={0} durationInFrames={s(3.3)}><Hora hora="07:42" dur={s(3.3)} /></Sequence>
    <Sequence from={s(5.9)} durationInFrames={s(3.6)}><Frase texto="O dia começa antes do primeiro cliente." dur={s(3.6)} tam={60} /></Sequence>
    {/* preto curto e revelação do painel */}
    <Sequence from={s(10.8)} durationInFrames={s(9.4)}><ProdutoPainel /></Sequence>
    {/* 13:40 — a oficina em ritmo */}
    <Sequence from={s(20.2)} durationInFrames={s(2.4)}>
      <Plano src="af/n-carro-entrando.png" dur={s(2.4)} ent={6} mov={{z0: 1.1, z1: 1.22, ox: 50, oy: 55, e: io}} />
    </Sequence>
    <Sequence from={s(22.6)} durationInFrames={s(1.9)}>
      <Plano src="af/n-elevador.png" dur={s(1.9)} sai={12} mov={{z0: 1.2, z1: 1.06, oy: 35, e: ease}} grade="contrast(1.08) saturate(1) brightness(1.02)" />
    </Sequence>
    <Sequence from={s(20.2)} durationInFrames={s(3.2)}><Hora hora="13:40" dur={s(3.2)} /></Sequence>
    <Sequence from={s(25)} durationInFrames={s(10.4)}><ProdutoOS /></Sequence>
    {/* 18:20 — o portão desce */}
    <Sequence from={s(35.4)} durationInFrames={s(3.6)}>
      <Plano src="af/n-silhueta-portao.png" dur={s(3.6)} ent={10} sai={12} mov={{z0: 1.04, z1: 1.16, e: io}} grade="contrast(1.06) saturate(1.05) brightness(1)" poeira />
    </Sequence>
    <Sequence from={s(35.4)} durationInFrames={s(3.4)}><Hora hora="18:20" dur={s(3.4)} /></Sequence>
    <Sequence from={s(39)} durationInFrames={s(5)}><Fecho /></Sequence>
    <Grao />
    {trilha && <Audio src={staticFile(trilha)} />}
  </AbsoluteFill>
);
