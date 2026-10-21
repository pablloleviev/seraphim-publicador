// V3 — "Um dia na oficina" (45 s, 9:16). Linguagem própria: relógio narrativo, luz que muda ao longo do dia
// (manhã fria -> meio-dia -> pôr do sol), inserts de interface real como "olhares" do gestor.
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {s, LAR, ease, io, css, lerp, Grao, Plano, Notebook, Celular} from './AutoFlowKit';

const Relogio: React.FC<{hora: string; dur: number}> = ({hora, dur}) => {
  const f = useCurrentFrame();
  const o = lerp(f, 2, 14, 0, 1) * lerp(f, dur - 8, dur, 1, 0);
  return (
    <div style={{position: 'absolute', left: 84, top: 290, opacity: o}}>
      <div style={{font: '800 150px/1 StackH', color: '#F4F2EC', letterSpacing: -6, textShadow: '0 6px 50px rgba(0,0,0,.6)'}}>
        {hora.split('').map((c, i) => <span key={i} style={{display: 'inline-block', transform: `translateY(${lerp(f, 2 + i * 2, 16 + i * 2, 40, 0)}px)`, opacity: lerp(f, 2 + i * 2, 14 + i * 2, 0, 1)}}>{c}</span>)}
      </div>
      <div style={{width: lerp(f, 6, 22, 0, 120), height: 4, background: LAR, marginTop: 18, borderRadius: 2}} />
    </div>
  );
};

const Texto: React.FC<{t: string; dur: number}> = ({t, dur}) => {
  const f = useCurrentFrame();
  return <div style={{position: 'absolute', left: 84, right: 110, top: 1420, font: '800 60px/1.12 StackH', color: '#F4F2EC', letterSpacing: -1.5,
    opacity: lerp(f, 6, 18, 0, 1) * lerp(f, dur - 10, dur, 1, 0), transform: `translateY(${lerp(f, 6, 20, 20, 0)}px)`, textShadow: '0 4px 36px rgba(0,0,0,.6)'}}>{t}</div>;
};

// fundo de estúdio com tom do horário
const Estudio: React.FC<{tom: string; children: React.ReactNode}> = ({tom, children}) => (
  <AbsoluteFill style={{background: `radial-gradient(85% 55% at 50% 48%, ${tom} 0%, #0E0E10 64%)`}}>{children}</AbsoluteFill>
);

const InsertPainel: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Estudio tom="#0f1a24">
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 2400}}>
        <div style={{transform: `translateY(${lerp(f, 0, s(1.4), 80, 0)}px) scale(${lerp(f, 0, s(5), 1.0, 1.12, io)}) rotateX(10deg) rotateY(${lerp(f, 0, s(5), 14, 6)}deg)`, opacity: lerp(f, 0, 10, 0, 1)}}>
          <Notebook f={f + 40} tela="af/painel_conteudo.png" />
        </div>
      </AbsoluteFill>
      <Texto t="O dia começa com o pátio na tela." dur={s(5)} />
    </Estudio>
  );
};

const InsertNovaOS: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Estudio tom="#24170c">
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        <div style={{width: 500, borderRadius: 26, overflow: 'hidden', boxShadow: `0 0 0 2px #2a2a30, 0 80px 140px rgba(0,0,0,.75), 0 0 120px rgba(255,106,19,${0.12 * lerp(f, 10, 40, 0, 1)})`,
          transform: `translateY(${lerp(f, 0, s(1.2), 60, -150)}px) scale(${lerp(f, 0, s(5), 0.96, 1.04, io)})`, opacity: lerp(f, 0, 10, 0, 1)}}>
          <Img src={staticFile('af/nova_os_painel.png')} style={{width: '100%', display: 'block'}} />
        </div>
      </AbsoluteFill>
      <Texto t="Nova ordem de serviço." dur={s(5)} />
    </Estudio>
  );
};

const InsertCelular: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Estudio tom="#1d1d12">
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 1800}}>
        <div style={{transform: `translateY(${lerp(f, 0, s(1.2), 200, -80)}px) rotateY(${lerp(f, 0, s(4), -24, -8)}deg) rotateX(6deg) scale(1.08)`, opacity: lerp(f, 0, 10, 0, 1)}}>
          <Celular tela="af/celular_ordens.png" />
        </div>
      </AbsoluteFill>
      <Texto t="Tudo acompanhado de onde você estiver." dur={s(4)} />
    </Estudio>
  );
};

const Fecho: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: 'linear-gradient(180deg, #1b0f07 0%, #0E0E10 55%)', alignItems: 'center'}}>
      <div style={{position: 'absolute', top: 470, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: lerp(f, 0, 18, 0, 1), transform: `scale(${lerp(f, 0, 30, 0.9, 1)})`}}>
        <Img src={staticFile('af/logo-icone.png')} style={{width: 170}} />
        <div style={{font: '800 100px/1 StackH', color: '#F4F2EC', letterSpacing: -3, marginTop: 36}}>AutoFlow</div>
        <div style={{font: '500 28px StackT', color: 'rgba(244,242,236,.55)', marginTop: 12}}>by Seraphim</div>
      </div>
      <div style={{position: 'absolute', left: 90, right: 90, top: 1150, textAlign: 'center', opacity: lerp(f, 24, 44, 0, 1)}}>
        <div style={{font: '800 52px/1.15 StackH', color: '#F4F2EC', letterSpacing: -1.2}}>Teste gratuito para oficinas selecionadas.</div>
        <div style={{font: '500 38px StackT', color: LAR, marginTop: 22}}>Solicite acesso pelo direct.</div>
      </div>
    </AbsoluteFill>
  );
};

export type PropsAF3 = {trilha: string | null};

export const AutoFlowV3: React.FC<PropsAF3> = ({trilha}) => (
  <AbsoluteFill style={{background: '#000'}}>
    <style>{css}</style>
    <Sequence from={0} durationInFrames={s(2.7)}>
      <Plano src="af/n-cadeado.png" dur={s(2.7)} ent={12} mov={{z0: 1.2, z1: 1.1, ox: 70, oy: 45, e: ease}} grade="contrast(1.06) saturate(.9) brightness(.96)" />
    </Sequence>
    <Sequence from={s(2.6)} durationInFrames={s(2.7)}>
      <Plano src="af/cena-09.png" dur={s(2.7)} ent={4} mov={{z0: 1.1, z1: 1.22, oy: 60, e: io}} poeira grade="contrast(1.06) saturate(.9) brightness(.96)" />
    </Sequence>
    <Sequence from={s(5.2)} durationInFrames={s(2.5)}>
      <Plano src="af/n-luzes.png" dur={s(2.5)} ent={3} mov={{z0: 1.08, z1: 1.16, ox: 45, oy: 40, e: io}} grade="contrast(1.06) saturate(.88) brightness(.98)" />
    </Sequence>
    <Sequence from={s(7.6)} durationInFrames={s(2.6)}>
      <Plano src="af/cena-10.png" dur={s(2.6)} ent={3} mov={{z0: 1.16, z1: 1.06, x0: 20, x1: -6, e: ease}} grade="contrast(1.06) saturate(.88) brightness(.96)" />
    </Sequence>
    <Sequence from={0} durationInFrames={s(5.2)}><Relogio hora="07:42" dur={s(5.2)} /></Sequence>
    <Sequence from={s(10)} durationInFrames={s(5)}><InsertPainel /></Sequence>
    <Sequence from={s(15)} durationInFrames={s(2.7)}>
      <Plano src="af/n-carro-entrando.png" dur={s(2.7)} ent={6} mov={{z0: 1.12, z1: 1.2, ox: 50, oy: 55, e: io}} />
    </Sequence>
    <Sequence from={s(17.6)} durationInFrames={s(2.6)}>
      <Plano src="af/n-digitando.png" dur={s(2.6)} ent={3} mov={{z0: 1.06, z1: 1.14, ox: 35, oy: 40, e: io}} />
    </Sequence>
    <Sequence from={s(15)} durationInFrames={s(5.2)}><Relogio hora="09:15" dur={s(5.2)} /></Sequence>
    <Sequence from={s(20)} durationInFrames={s(5)}><InsertNovaOS /></Sequence>
    <Sequence from={s(25)} durationInFrames={s(3.1)}>
      <Plano src="af/n-elevador.png" dur={s(3.1)} ent={6} mov={{z0: 1.2, z1: 1.08, oy: 35, e: ease}} grade="contrast(1.08) saturate(1) brightness(1.02)" />
    </Sequence>
    <Sequence from={s(28)} durationInFrames={s(3.2)}>
      <Plano src="af/n-celular-maos.png" dur={s(3.2)} ent={3} mov={{z0: 1.1, z1: 1.2, ox: 30, oy: 30, e: io}} grade="contrast(1.08) saturate(1) brightness(1.02)" />
    </Sequence>
    <Sequence from={s(25)} durationInFrames={s(6.2)}><Relogio hora="13:40" dur={s(6.2)} /></Sequence>
    <Sequence from={s(31)} durationInFrames={s(4)}><InsertCelular /></Sequence>
    <Sequence from={s(35)} durationInFrames={s(5.2)}>
      <Plano src="af/n-silhueta-portao.png" dur={s(5.2)} ent={10} sai={10} mov={{z0: 1.04, z1: 1.12, e: io}} grade="contrast(1.06) saturate(1.05) brightness(1)" />
      <Relogio hora="18:20" dur={s(5.2)} />
    </Sequence>
    <Sequence from={s(40)} durationInFrames={s(5)}><Fecho /></Sequence>
    <Grao />
    {trilha && <Audio src={staticFile(trilha)} />}
  </AbsoluteFill>
);
