import React from 'react';
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing, continueRender, delayRender,
} from 'remotion';

// ---------- tipos ----------
export type Palavra = {w: string; s: number; e: number};
export type Cena = {
  inicio: number; fim: number;
  modelo: 'impacto' | 'numero' | 'imagem' | 'lista' | 'cta' | 'gravacao';
  linhas?: string[]; numero?: string; apoio?: string; itens?: string[];
  sera?: string; imagem?: string; fundo?: 'escuro' | 'branco'; raios?: boolean;
};
export type Props = {
  fps: number; duracao: number; arroba: string;
  audio: string | null; batida: string | null; sfx: boolean;
  palavras: Palavra[]; cenas: Cena[];
  video?: string | null; video_som?: boolean;   // gravação já tratada (cinema.py) — som vem dela
};

// ---------- marca ----------
const C = {preto: '#0A0A0C', ouro: '#F5A623', ouro2: '#FFC94D', branco: '#F5F5F7', prata: '#A1A1AA'};
const W = 1080, H = 1920;

// ---------- fontes ----------
const fontesCSS = `
@font-face{font-family:'Anton';src:url('${staticFile('fontes/anton.ttf')}')}
@font-face{font-family:'InterX';font-weight:800;src:url('${staticFile('fontes/inter800.ttf')}')}
@font-face{font-family:'InterM';font-weight:500;src:url('${staticFile('fontes/inter500.ttf')}')}
`;
const useFontes = () => {
  const [h] = React.useState(() => delayRender('fontes'));
  React.useEffect(() => {
    const fontes = [
      new FontFace('Anton', `url(${staticFile('fontes/anton.ttf')})`),
      new FontFace('InterX', `url(${staticFile('fontes/inter800.ttf')})`, {weight: '800'}),
      new FontFace('InterM', `url(${staticFile('fontes/inter500.ttf')})`, {weight: '500'}),
    ];
    const t = setTimeout(() => continueRender(h), 8000);
    Promise.all(fontes.map((f) => f.load().then((ff) => (document as any).fonts.add(ff))))
      .finally(() => { clearTimeout(t); continueRender(h); });
  }, [h]);
};

// "TE *DEVE*" -> [{t:'TE',ouro:false},{t:'DEVE',ouro:true}] por palavra
const palavrasDe = (linha: string) => {
  const out: {t: string; ouro: boolean}[] = [];
  linha.split('*').forEach((trecho, i) =>
    trecho.split(' ').filter(Boolean).forEach((t) => out.push({t, ouro: i % 2 === 1})));
  return out;
};
const tamanhoTitulo = (linhas: string[], max: number) => {
  const maior = Math.max(...linhas.map((l) => l.replace(/\*/g, '').length), 1);
  return Math.min(max, Math.floor((W - 150) / (maior * 0.47)));
};

// ---------- fundo ----------
const Fundo: React.FC<{branco: boolean; raios: boolean; f: number}> = ({branco, raios, f}) => {
  const base = branco ? C.branco : C.preto;
  return (
    <AbsoluteFill style={{background: base}}>
      <AbsoluteFill style={{
        background: branco
          ? `radial-gradient(circle at 85% 10%, rgba(245,166,35,.22), transparent 45%)`
          : `radial-gradient(circle at 85% 8%, rgba(245,166,35,.30), transparent 42%), radial-gradient(circle at 10% 92%, rgba(245,166,35,.12), transparent 40%)`,
      }} />
      {raios && (
        <AbsoluteFill style={{
          background: `repeating-conic-gradient(from ${f * 0.35}deg at 50% 42%, rgba(245,166,35,${branco ? .10 : .09}) 0deg 7.5deg, transparent 7.5deg 15deg)`,
          maskImage: 'radial-gradient(circle at 50% 42%, #000 15%, transparent 75%)',
          WebkitMaskImage: 'radial-gradient(circle at 50% 42%, #000 15%, transparent 75%)',
        }} />
      )}
      <AbsoluteFill style={{
        backgroundImage: `radial-gradient(${branco ? 'rgba(10,10,12,.10)' : 'rgba(255,255,255,.12)'} 2.2px, transparent 2.6px)`,
        backgroundSize: '24px 24px',
        backgroundPosition: `${f * 0.4}px ${f * 0.2}px`,
        maskImage: 'radial-gradient(ellipse at 90% 5%, #000 0%, transparent 55%)',
        WebkitMaskImage: 'radial-gradient(ellipse at 90% 5%, #000 0%, transparent 55%)',
      }} />
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,${branco ? .10 : .55}) 100%)`}} />
    </AbsoluteFill>
  );
};

const Grao: React.FC<{f: number}> = ({f}) => (
  <AbsoluteFill style={{opacity: 0.06, mixBlendMode: 'overlay', pointerEvents: 'none'}}>
    <svg width={W} height={H}>
      <filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={Math.floor(f / 2)} /></filter>
      <rect width="100%" height="100%" filter="url(#g)" />
    </svg>
  </AbsoluteFill>
);

// ---------- título cinético ----------
const Titulo: React.FC<{linhas: string[]; tam: number; cor: string; f: number; fps: number; atraso?: number}> = ({linhas, tam, cor, f, fps, atraso = 0}) => {
  let idx = 0;
  const ab = interpolate(f, [0, 10], [10, 3], {extrapolateRight: 'clamp'});
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: tam * 0.02}}>
      {linhas.map((l, li) => (
        <div key={li} style={{display: 'flex', gap: tam * 0.22, justifyContent: 'center', flexWrap: 'nowrap'}}>
          {palavrasDe(l).map((p, pi) => {
            const d = atraso + idx++ * 3;
            const s = spring({frame: f - d, fps, config: {damping: 11, stiffness: 170, mass: 0.6}});
            const blur = interpolate(f - d, [0, 6], [10, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
            const c = p.ouro ? C.ouro : cor;
            return (
              <span key={pi} style={{
                fontFamily: 'Anton', fontSize: tam, lineHeight: 1.0, color: c, textTransform: 'uppercase',
                letterSpacing: 1, display: 'inline-block',
                transform: `scale(${interpolate(s, [0, 1], [1.7, 1])}) translateY(${interpolate(s, [0, 1], [30, 0])}px)`,
                opacity: interpolate(s, [0, 0.4], [0, 1], {extrapolateRight: 'clamp'}),
                filter: `blur(${blur}px)`,
                textShadow: `${-ab}px 0 rgba(255,40,70,.85), ${ab}px 0 rgba(40,140,255,.85)${p.ouro ? `, 0 0 40px rgba(245,166,35,.45)` : ''}`,
              }}>{p.t}</span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

// ---------- Sera ----------
const Sera: React.FC<{pose: string; f: number; fps: number}> = ({pose, f, fps}) => {
  const s = spring({frame: f - 4, fps, config: {damping: 9, stiffness: 140, mass: 0.7}});
  const bob = Math.sin((f / fps) * Math.PI * 1.6) * 14;
  const rot = Math.sin((f / fps) * Math.PI * 0.9) * 2.5;
  const pulso = 0.55 + 0.25 * Math.sin((f / fps) * Math.PI * 2.2);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 960, height: 620, display: 'flex', justifyContent: 'center'}}>
      <div style={{position: 'absolute', top: 120, width: 520, height: 420, borderRadius: '50%',
        background: `radial-gradient(circle, rgba(245,166,35,${pulso * 0.35}), transparent 65%)`, filter: 'blur(10px)'}} />
      <Img src={staticFile(`sera/${pose}.png`)} style={{
        height: 600, transform: `translateY(${bob}px) rotate(${rot}deg) scale(${interpolate(s, [0, 1], [0.3, 1])})`,
        opacity: interpolate(s, [0, 0.3], [0, 1], {extrapolateRight: 'clamp'}),
      }} />
    </div>
  );
};

// ---------- modelos de cena ----------
const CenaView: React.FC<{c: Cena; f: number; fps: number; n: number}> = ({c, f, fps, n}) => {
  const branco = c.fundo === 'branco';
  const cor = branco ? C.preto : C.branco;
  const linhas = c.linhas || [];
  const temSera = !!c.sera;
  const topo = temSera ? 230 : undefined;

  // impacto da entrada
  const punch = spring({frame: f, fps, config: {damping: 14, stiffness: 200}});
  const esc = interpolate(punch, [0, 1], [1.12, 1]);
  const shake = f < 6 ? (6 - f) * 2.4 : 0;
  const sx = Math.sin(f * 7.1) * shake, sy = Math.cos(f * 5.3) * shake;

  let conteudo: React.ReactNode = null;
  if (c.modelo === 'numero') {
    const s = spring({frame: f, fps, config: {damping: 13, stiffness: 120}});
    conteudo = (
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
        <div style={{fontFamily: 'Anton', fontSize: 360, lineHeight: 0.9, color: 'transparent',
          WebkitTextStroke: `5px ${C.ouro}`, transform: `scale(${interpolate(s, [0, 1], [0.6, 1])})`,
          clipPath: `inset(${interpolate(s, [0, 1], [100, 0])}% 0 0 0)`, filter: 'drop-shadow(0 0 30px rgba(245,166,35,.35))'}}>{c.numero}</div>
        <div style={{height: 30}} />
        <Titulo linhas={linhas} tam={tamanhoTitulo(linhas, 150)} cor={cor} f={f} fps={fps} atraso={6} />
      </div>
    );
  } else if (c.modelo === 'imagem' && c.imagem) {
    const k = interpolate(f, [0, n], [1.18, 1.0], {easing: Easing.out(Easing.quad)});
    const s = spring({frame: f, fps, config: {damping: 14, stiffness: 120}});
    conteudo = (
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 50}}>
        <Titulo linhas={linhas} tam={tamanhoTitulo(linhas, 140)} cor={cor} f={f} fps={fps} />
        <div style={{width: 900, height: 900, borderRadius: 44, overflow: 'hidden',
          border: '2px solid rgba(245,166,35,.55)', boxShadow: '0 30px 80px rgba(0,0,0,.6), 0 0 60px rgba(245,166,35,.15)',
          transform: `translateY(${interpolate(s, [0, 1], [120, 0])}px) rotate(${interpolate(s, [0, 1], [-4, 0])}deg)`,
          opacity: interpolate(s, [0, 0.3], [0, 1], {extrapolateRight: 'clamp'})}}>
          <Img src={staticFile(c.imagem)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${k})`}} />
        </div>
      </div>
    );
  } else if (c.modelo === 'lista' && c.itens) {
    const passo = n / (c.itens.length + 1);
    conteudo = (
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 60}}>
        <Titulo linhas={linhas} tam={tamanhoTitulo(linhas, 140)} cor={cor} f={f} fps={fps} />
        <div style={{display: 'flex', flexDirection: 'column', gap: 34, width: 860}}>
          {c.itens.map((it, i) => {
            const s = spring({frame: f - passo * (i + 0.6), fps, config: {damping: 12, stiffness: 160}});
            return (
              <div key={i} style={{display: 'flex', alignItems: 'center', gap: 28, opacity: s,
                transform: `translateX(${interpolate(s, [0, 1], [-80, 0])}px)`}}>
                <div style={{width: 74, height: 74, borderRadius: 37, background: C.ouro, display: 'flex',
                  alignItems: 'center', justifyContent: 'center', fontFamily: 'InterX', fontSize: 42, color: C.preto}}>✓</div>
                <div style={{fontFamily: 'InterX', fontSize: 56, color: cor}}>{it}</div>
              </div>
            );
          })}
        </div>
      </div>
    );
  } else {
    conteudo = <Titulo linhas={linhas} tam={tamanhoTitulo(linhas, temSera ? 220 : 280)} cor={cor} f={f} fps={fps} />;
  }

  const apoioS = spring({frame: f - 14, fps, config: {damping: 16}});
  const cta = c.modelo === 'cta';
  const pill = 1 + 0.04 * Math.sin((f / fps) * Math.PI * 3);

  return (
    <AbsoluteFill>
      <Fundo branco={branco} raios={!!c.raios} f={f} />
      <AbsoluteFill style={{transform: `scale(${esc}) translate(${sx}px, ${sy}px)`}}>
        <div style={{position: 'absolute', left: 60, right: 60, top: topo ?? 0, bottom: topo ? undefined : 260,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: topo ? 'flex-start' : 'center'}}>
          {conteudo}
          {c.apoio && !cta && (
            <div style={{marginTop: 40, fontFamily: 'InterM', fontSize: 46, color: branco ? '#3f3f46' : C.prata,
              textAlign: 'center', maxWidth: 900, opacity: apoioS, transform: `translateY(${(1 - apoioS) * 20}px)`}}>{c.apoio}</div>
          )}
          {cta && (
            <div style={{marginTop: 50, padding: '26px 56px', borderRadius: 999, background: C.ouro, color: C.preto,
              fontFamily: 'InterX', fontSize: 52, transform: `scale(${apoioS * pill})`, boxShadow: '0 0 60px rgba(245,166,35,.5)'}}>
              {c.apoio || 'link na bio'} →
            </div>
          )}
        </div>
        {temSera && <Sera pose={c.sera!} f={f} fps={fps} />}
      </AbsoluteFill>
      {f < 4 && <AbsoluteFill style={{background: '#fff', opacity: interpolate(f, [0, 4], [branco ? 0.9 : 0.55, 0])}} />}
    </AbsoluteFill>
  );
};

// ---------- legendas palavra a palavra ----------
const Legenda: React.FC<{palavras: Palavra[]; cenas: Cena[]; t: number}> = ({palavras, cenas, t}) => {
  if (!palavras.length) return null;
  // grupos de até 3 palavras, sem atravessar troca de cena
  const grupos: Palavra[][] = [];
  let atual: Palavra[] = [];
  const cenaDe = (x: number) => cenas.findIndex((c) => x >= c.inicio && x < c.fim);
  palavras.forEach((p) => {
    const quebra = atual.length >= 3 || (atual.length && cenaDe(atual[0].s) !== cenaDe(p.s)) ||
      (atual.length && /[.,!?:;]$/.test(atual[atual.length - 1].w));
    if (quebra) { grupos.push(atual); atual = []; }
    atual.push(p);
  });
  if (atual.length) grupos.push(atual);
  const g = grupos.find((gr) => t >= gr[0].s - 0.05 && t <= gr[gr.length - 1].e + 0.15);
  if (!g) return null;
  const cena = cenas[cenaDe(t)] || cenas[0];
  const branco = cena?.fundo === 'branco';
  return (
    <div style={{position: 'absolute', left: 40, right: 40, top: 1600, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: 30}}>
      {g.map((p, i) => {
        const ativa = t >= p.s && t <= p.e + 0.05;
        const ja = t >= p.s;
        return (
          <span key={i} style={{
            fontFamily: 'InterX', fontSize: g.reduce((n, p) => n + p.w.length, 0) > 22 ? 54 : 66, textTransform: 'lowercase',
            color: ativa ? C.ouro : (branco ? C.preto : C.branco),
            opacity: ja ? 1 : 0.35,
            transform: `translateY(${ativa ? -4 : 0}px)`, display: 'inline-block', whiteSpace: 'nowrap',
            WebkitTextStroke: branco ? '0px' : '10px rgba(10,10,12,.9)', paintOrder: 'stroke fill',
            textShadow: branco ? 'none' : '0 6px 20px rgba(0,0,0,.6)',
          }}>{p.w.replace(/[.,!?:;]$/, '')}</span>
        );
      })}
    </div>
  );
};

// ---------- vídeo ----------
export const SeraphimVideo: React.FC<Props> = (props) => {
  useFontes();
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const t = frame / fps;
  const cenaAtual = props.cenas.find((c) => t >= c.inicio && t < c.fim) || props.cenas[props.cenas.length - 1];
  const branco = cenaAtual?.fundo === 'branco';
  return (
    <AbsoluteFill style={{background: C.preto}}>
      <style>{fontesCSS}</style>
      {props.cenas.map((c, i) => {
        const from = Math.round(c.inicio * fps);
        const dur = Math.max(1, Math.round((c.fim - c.inicio) * fps));
        return (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <CenaInner c={c} n={dur} video={props.video} />
          </Sequence>
        );
      })}
      <Legenda palavras={props.palavras} cenas={props.cenas} t={t} />
      <Grao f={frame} />
      {/* barra de progresso */}
      <div style={{position: 'absolute', top: 0, left: 0, height: 10, width: `${(frame / durationInFrames) * 100}%`, background: C.ouro}} />
      {/* rodapé */}
      <div style={{position: 'absolute', left: 70, bottom: 70, display: 'flex', alignItems: 'center', gap: 22}}>
        <Img src={staticFile('marca/icone.png')} style={{width: 72, height: 72, borderRadius: 36}} />
        <span style={{fontFamily: 'InterM', fontSize: 38, color: branco ? '#52525b' : '#8a8a92'}}>{props.arroba}</span>
      </div>
      {/* áudio */}
      {props.audio && <Audio src={staticFile(props.audio)} />}
      {props.video && props.video_som && <Audio src={staticFile(props.video)} />}
      {props.batida && <Audio src={staticFile(props.batida)} volume={props.audio || props.video ? 0.12 : 0.7} />}
      {props.sfx && props.cenas.map((c, i) => (
        <React.Fragment key={'s' + i}>
          {i > 0 && <Sequence from={Math.max(0, Math.round((c.inicio - 0.22) * fps))}><Audio src={staticFile('sfx/whoosh.wav')} volume={0.45} /></Sequence>}
          <Sequence from={Math.round(c.inicio * fps)}><Audio src={staticFile('sfx/impacto.wav')} volume={0.5} /></Sequence>
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
};

const CenaInner: React.FC<{c: Cena; n: number; video?: string | null}> = ({c, n, video}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (c.modelo === 'gravacao' && video) return <CenaGravacao c={c} f={f} fps={fps} n={n} video={video} />;
  return <CenaView c={c} f={f} fps={fps} n={n} />;
};

// gravação cinematográfica em tela cheia, com título opcional no topo
const CenaGravacao: React.FC<{c: Cena; f: number; fps: number; n: number; video: string}> = ({c, f, fps, n, video}) => {
  const linhas = c.linhas || [];
  const k = interpolate(f, [0, n], [1.0, 1.035]);  // leve avanço de câmera
  return (
    <AbsoluteFill>
      <OffthreadVideo src={staticFile(video)} startFrom={Math.round(c.inicio * fps)} muted
        style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${k})`}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,10,12,.55) 0%, rgba(10,10,12,0) 28%, rgba(10,10,12,0) 70%, rgba(10,10,12,.6) 100%)'}} />
      {linhas.length > 0 && (
        <div style={{position: 'absolute', top: 170, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
          <Titulo linhas={linhas} tam={tamanhoTitulo(linhas, 110)} cor={C.branco} f={f} fps={fps} />
        </div>
      )}
    </AbsoluteFill>
  );
};
