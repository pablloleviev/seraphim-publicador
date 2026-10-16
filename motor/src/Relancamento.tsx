// Relançamento Seraphim (19–25/10/2026): cada vídeo tem linguagem PRÓPRIA (não reaproveita cenas do motor Cortes).
// V1 "Prazer, Seraphim": tipografia cinética sóbria, palavra a palavra, cortes secos no ritmo da fala.
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
  continueRender, delayRender, Easing} from 'remotion';

const OURO = '#F5A623', PRETO = '#0A0A0C', BRANCO = '#F5F5F7', CINZA = '#8E8E96';
export type Palavra = {w: string; s: number; e: number};
export type CenaR = {inicio: number; fim: number; tipo: string; texto?: string; itens?: string[]; icones?: string[]};
export type PropsR = {fps: number; duracao: number; arroba: string; audio: string | null; batida: string | null;
  palavras: Palavra[]; cenas: CenaR[]; peca: string; trilha_mix?: boolean};

const FONTES: [string, string, string?][] = [
  ['Fraunces', 'fraunces-900.woff2'], ['Space', 'space-grotesk-700.woff2'], ['Jet', 'jetbrains.ttf'],
  ['Manrope', 'manrope-800.woff2'], ['Instrument', 'instrument-serif-400.woff2'],
];
const useFontes = () => {
  const [h] = React.useState(() => delayRender('fontes'));
  React.useEffect(() => {
    const t = setTimeout(() => continueRender(h), 8000);
    Promise.all(FONTES.map(([n, f]) => new FontFace(n, `url(${staticFile('fontes/' + f)})`).load()
      .then((ff) => (document as any).fonts.add(ff)).catch(() => null))).finally(() => { clearTimeout(t); continueRender(h); });
  }, [h]);
};

// ícones em traço (Lucide, licença ISC), desenhados com animação de traço
const ICONES: Record<string, string> = {
  copiar: 'M8 8h12v12H8z M4 16V4h12',
  conferir: 'M9 11l3 3L22 4 M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11',
  repetir: 'M17 1l4 4-4 4 M3 11V9a4 4 0 0 1 4-4h14 M7 23l-4-4 4-4 M21 13v2a4 4 0 0 1-4 4H3',
};
const Icone: React.FC<{nome: string; p: number}> = ({nome, p}) => (
  <svg width={150} height={150} viewBox="0 0 24 24" fill="none" stroke={OURO} strokeWidth={1.4} strokeLinecap="round" strokeLinejoin="round">
    <path d={ICONES[nome]} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
  </svg>
);

const Grao: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{pointerEvents: 'none', opacity: 0.18, mixBlendMode: 'overlay',
    backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='${f % 8}'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")`}} />;
};

// cena 1: frase palavra a palavra (cada palavra entra exatamente quando é falada)
const PalavraAPalavra: React.FC<{c: CenaR; palavras: Palavra[]}> = ({c, palavras}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const t = c.inicio + f / fps;
  const ws = palavras.filter((p) => p.s >= c.inicio - 0.05 && p.s < c.fim);
  return (
    <AbsoluteFill style={{padding: '0 90px', justifyContent: 'center'}}>
      <div style={{fontFamily: 'Fraunces', fontSize: 118, lineHeight: 1.04, color: BRANCO}}>
        {ws.map((p, i) => {
          const vis = t >= p.s;
          const ult = i === ws.length - 1 || i === ws.length - 2;
          return <span key={i} style={{opacity: vis ? 1 : 0.07, color: ult && vis ? OURO : BRANCO}}>{p.w} </span>;
        })}
      </div>
    </AbsoluteFill>
  );
};

// cena 2: três ações curtas, cada uma com ícone desenhado; corte seco entre elas
const Tres: React.FC<{c: CenaR}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const dur = (c.fim - c.inicio) * fps; const k = Math.min(2, Math.floor(f / (dur / 3)));
  const local = f - k * (dur / 3);
  const p = interpolate(local, [0, 14], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 50}}>
      <Icone nome={(c.icones || ['copiar', 'conferir', 'repetir'])[k]} p={p} />
      <div style={{fontFamily: 'Space', fontSize: 120, color: BRANCO, letterSpacing: -2}}>{(c.itens || [])[k]}</div>
      <div style={{fontFamily: 'Jet', fontSize: 30, color: CINZA}}>0{k + 1} / 03</div>
    </AbsoluteFill>
  );
};

// cena 3: as três palavras são riscadas por um filete dourado; surgem as três frentes
const Risca: React.FC<{c: CenaR}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const velhos = ['copiar', 'conferir', 'repetir'];
  const novos = c.itens || ['sistemas', 'automação', 'integração'];
  return (
    <AbsoluteFill style={{padding: '0 110px', justifyContent: 'center', gap: 34}}>
      {velhos.map((w, i) => {
        const r = interpolate(f, [8 + i * 6, 22 + i * 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const sai = interpolate(f, [fps * 1.6, fps * 2.1], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return <div key={w} style={{position: 'relative', fontFamily: 'Space', fontSize: 96, color: CINZA, opacity: sai, height: 110}}>
          {w}<div style={{position: 'absolute', left: 0, top: 58, height: 8, width: `${r * 100}%`, background: OURO}} /></div>;
      })}
      <div style={{position: 'absolute', left: 110, right: 110, top: 760}}>
        {novos.map((w, i) => {
          const e = spring({frame: f - fps * 2.1 - i * 7, fps, config: {damping: 16}});
          return <div key={w} style={{fontFamily: 'Fraunces', fontSize: 122, lineHeight: 1.1, color: BRANCO,
            opacity: e, transform: `translateY(${(1 - e) * 40}px)`}}>{w}<span style={{color: OURO}}>.</span></div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

// cena 4: "com método" cresce até ocupar a tela
const Cresce: React.FC<{c: CenaR}> = ({c}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const dur = (c.fim - c.inicio) * fps;
  const s = interpolate(f, [0, dur], [1, 1.5], {easing: Easing.inOut(Easing.quad)});
  const [a, b] = (c.texto || 'Sem promessa mágica.|Com método.').split('|');
  const eb = spring({frame: f - fps * 1.0, fps, config: {damping: 20}});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{fontFamily: 'Instrument', fontStyle: 'italic', fontSize: 70, color: CINZA, marginBottom: 30}}>{a}</div>
      <div style={{fontFamily: 'Fraunces', fontSize: 170, color: OURO, transform: `scale(${s * eb})`, whiteSpace: 'nowrap'}}>{b}</div>
    </AbsoluteFill>
  );
};

// cena 5: assinatura — logo oficial + @
const Assina: React.FC<{c: CenaR; arroba: string}> = ({c, arroba}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const e = spring({frame: f, fps, config: {damping: 18}});
  const linha = interpolate(f, [6, 26], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 46}}>
      <Img src={staticFile('marca/logo-original.png')} style={{width: 300, borderRadius: 30, opacity: e, transform: `scale(${0.9 + 0.1 * e})`}} />
      <div style={{fontFamily: 'Fraunces', fontSize: 110, color: BRANCO, opacity: e}}>{c.texto || 'Prazer, Seraphim.'}</div>
      <div style={{width: 120 * linha, height: 5, background: OURO}} />
      <div style={{fontFamily: 'Space', fontSize: 40, color: CINZA, opacity: linha}}>{arroba}</div>
    </AbsoluteFill>
  );
};

const Legenda: React.FC<{palavras: Palavra[]; ocultar: [number, number][]}> = ({palavras, ocultar}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const t = f / fps;
  if (ocultar.some(([a, b]) => t >= a && t < b)) return null;
  const i = palavras.findIndex((p) => t >= p.s && t < p.e + 0.25);
  if (i < 0) return null;
  const ini = Math.floor(i / 4) * 4;
  return <div style={{position: 'absolute', left: 90, right: 90, bottom: 330, textAlign: 'center', fontFamily: 'Manrope', fontSize: 46, color: BRANCO}}>
    {palavras.slice(ini, ini + 4).map((p, k) => <span key={k} style={{color: ini + k === i ? OURO : 'rgba(245,245,247,.75)'}}>{p.w} </span>)}</div>;
};

export const Relancamento: React.FC<PropsR> = (props) => {
  useFontes();
  const {fps} = useVideoConfig();
  // cenas onde o texto na tela JÁ é a fala não levam legenda (evita texto duplicado)
  const ocultar = props.cenas.filter((c) => ['palavra', 'cresce', 'assina'].includes(c.tipo)).map((c) => [c.inicio, c.fim] as [number, number]);
  return (
    <AbsoluteFill style={{background: PRETO}}>
      {props.cenas.map((c, i) => {
        const from = Math.round(c.inicio * fps); const dur = Math.max(1, Math.round((c.fim - c.inicio) * fps));
        const C = c.tipo === 'palavra' ? <PalavraAPalavra c={c} palavras={props.palavras} /> : c.tipo === 'tres' ? <Tres c={c} />
          : c.tipo === 'risca' ? <Risca c={c} /> : c.tipo === 'cresce' ? <Cresce c={c} /> : <Assina c={c} arroba={props.arroba} />;
        return <Sequence key={i} from={from} durationInFrames={dur}>{C}</Sequence>;
      })}
      <Legenda palavras={props.palavras} ocultar={ocultar} />
      <Grao />
      {props.audio && <Audio src={staticFile(props.audio)} />}
      {props.batida && <Audio src={staticFile(props.batida)} volume={props.trilha_mix ? 1 : 0.14} />}
    </AbsoluteFill>
  );
};
