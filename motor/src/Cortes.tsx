// Motor de CORTES verticais da Seraphim — base: RunnyIA (cenas de tipos diferentes, cor muda a cada cena,
// acabamento de TV antiga) + toques do Iman Gadzhi (painéis de "jogo", serifa itálica).
import React from 'react';
import {
  AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing, continueRender, delayRender, random,
} from 'remotion';

const W = 1080, H = 1920;
const OURO = '#F5A623', VERM = '#E3242B', BRANCO = '#F4F4F2', PRETO = '#060607';

export type Palavra = {w: string; s: number; e: number};
export type CenaC = {
  inicio: number; fim: number; tipo: string;
  texto?: string; topo?: string; destaque?: string; sub?: string;
  rotulo?: string; de?: number; para?: number; sufixo?: string; riscar?: string;
  imagem?: string; imagens?: string[]; tom?: 'cinza' | 'vermelho' | 'dourado' | 'normal';
  itens?: {rotulo?: string; imagem?: string; texto?: string}[] | any[];
  passos?: {icone: string; rotulo: string}[];
  pose?: string; legenda?: boolean; valor?: number; apoio?: string;
};
export type PropsC = {
  fps: number; duracao: number; arroba: string; audio: string | null; batida: string | null; sfx: boolean;
  palavras: Palavra[]; cenas: CenaC[];
};

// ---------- fontes ----------
const FONTES: [string, string, string?][] = [
  ['Anton', 'anton.ttf'], ['Jet', 'jetbrains.ttf', '800'], ['Mont', 'montserrat.ttf', '800'],
  ['Playfair', 'playfair.ttf', '500'], ['InterX', 'inter800.ttf', '800'], ['InterM', 'inter500.ttf', '500'],
];
const useFontes = () => {
  const [h] = React.useState(() => delayRender('fontes'));
  React.useEffect(() => {
    const t = setTimeout(() => continueRender(h), 8000);
    Promise.all(FONTES.map(([n, f, w]) => new FontFace(n, `url(${staticFile('fontes/' + f)})`, w ? {weight: w} : {})
      .load().then((ff) => (document as any).fonts.add(ff)).catch(() => null)))
      .finally(() => { clearTimeout(t); continueRender(h); });
  }, [h]);
};

const cl = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));
const ease = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});

// ---------- fundos ----------
const Raios: React.FC<{f: number; c1: string; c2: string; n?: number; cx?: string; cy?: string}> = ({f, c1, c2, n = 18, cx = '50%', cy = '45%'}) => {
  const a = 360 / n / 2;
  return <AbsoluteFill style={{background: `repeating-conic-gradient(from ${f * 0.25}deg at ${cx} ${cy}, ${c1} 0deg ${a}deg, ${c2} ${a}deg ${a * 2}deg)`}} />;
};
const Reticula: React.FC<{cor: string; op?: number; tam?: number}> = ({cor, op = 0.18, tam = 9}) => (
  <AbsoluteFill style={{backgroundImage: `radial-gradient(${cor} ${tam * 0.32}px, transparent ${tam * 0.36}px)`, backgroundSize: `${tam}px ${tam}px`, opacity: op}} />
);
const Xadrez: React.FC<{f: number}> = ({f}) => (
  <AbsoluteFill style={{background: '#0d0d0f'}}>
    <AbsoluteFill style={{backgroundImage: 'conic-gradient(#1b1b1e 25%, transparent 0 50%, #1b1b1e 0 75%, transparent 0)', backgroundSize: '180px 180px',
      backgroundPosition: `0 ${f * 0.5}px`, opacity: 0.9}} />
  </AbsoluteFill>
);
const Flare: React.FC<{x: number; y: number; f: number; cor?: string}> = ({x, y, f, cor = '255,255,255'}) => {
  const p = 0.8 + 0.2 * Math.sin(f / 6);
  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'screen'}}>
      <div style={{position: 'absolute', left: x - 260, top: y - 260, width: 520, height: 520, borderRadius: '50%',
        background: `radial-gradient(circle, rgba(${cor},${0.95 * p}) 0%, rgba(${cor},.35) 18%, transparent 60%)`}} />
      <div style={{position: 'absolute', left: x - 700, top: y - 4, width: 1400, height: 8, background: `linear-gradient(90deg, transparent, rgba(${cor},.7), transparent)`, filter: 'blur(3px)'}} />
    </AbsoluteFill>
  );
};

// ---------- acabamento (TV antiga) ----------
const Acabamento: React.FC<{f: number}> = ({f}) => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,.22) 0 2px, transparent 2px 5px)', opacity: 0.55}} />
    <AbsoluteFill style={{opacity: 0.09, mixBlendMode: 'overlay'}}>
      <svg width={W} height={H}><filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 7} /></filter>
        <rect width="100%" height="100%" filter="url(#gr)" /></svg>
    </AbsoluteFill>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, transparent 60%, rgba(0,0,0,.38) 100%)'}} />
  </AbsoluteFill>
);
const rgb = (n: number) => `${-n}px 0 rgba(255,30,60,.75), ${n}px 0 rgba(30,160,255,.75)`;

// ---------- ícones simples (SVG, traço branco) ----------
const ICONES: Record<string, React.ReactNode> = {
  tela: <><rect x="8" y="12" width="84" height="56" rx="6" /><path d="M35 86h30M50 68v18" /></>,
  pessoas: <><circle cx="50" cy="30" r="12" /><path d="M28 78c0-14 10-24 22-24s22 10 22 24" /><circle cx="20" cy="40" r="8" /><circle cx="80" cy="40" r="8" /><path d="M6 76c0-10 6-16 14-16M94 76c0-10-6-16-14-16" /></>,
  dinheiro: <><rect x="8" y="24" width="84" height="52" rx="6" /><circle cx="50" cy="50" r="13" /><path d="M20 36v28M80 36v28" /></>,
  robo: <><rect x="20" y="30" width="60" height="48" rx="10" /><circle cx="38" cy="52" r="6" /><circle cx="62" cy="52" r="6" /><path d="M50 30V16M40 66h20" /><circle cx="50" cy="12" r="4" /></>,
  grafico: <><path d="M10 90V10M10 90h80" /><path d="M20 70l20-20 16 12 28-34" /></>,
  chat: <><path d="M10 18h80v50H40L22 84V68H10z" /><path d="M26 38h48M26 52h30" /></>,
  engrenagem: <><circle cx="50" cy="50" r="14" /><path d="M50 10v14M50 76v14M10 50h14M76 50h14M22 22l10 10M68 68l10 10M78 22L68 32M22 78l10-10" /></>,
  raio: <path d="M56 6L22 56h24l-6 38 36-52H52z" />,
  relogio: <><circle cx="50" cy="50" r="38" /><path d="M50 26v26l16 10" /></>,
  cadeado: <><rect x="20" y="44" width="60" height="44" rx="6" /><path d="M32 44V30a18 18 0 0136 0v14" /></>,
  carrinho: <><path d="M6 14h14l10 50h50l8-34H26" /><circle cx="38" cy="80" r="6" /><circle cx="72" cy="80" r="6" /></>,
  planilha: <><rect x="12" y="10" width="76" height="80" rx="4" /><path d="M12 34h76M12 58h76M38 10v80" /></>,
  check: <><circle cx="50" cy="50" r="38" /><path d="M32 52l12 12 24-28" /></>,
  alerta: <><path d="M50 10L92 86H8z" /><path d="M50 38v22M50 70v2" /></>,
};
const Icone: React.FC<{nome: string; tam: number; cor?: string}> = ({nome, tam, cor = '#fff'}) => (
  <svg width={tam} height={tam} viewBox="0 0 100 100" fill="none" stroke={cor} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round">
    {ICONES[nome] || ICONES.raio}
  </svg>
);

const Foto: React.FC<{src?: string; f: number; n: number; tom?: string; zoom?: number}> = ({src, f, n, tom = 'normal', zoom = 0.12}) => {
  const k = interpolate(f, [0, n], [1 + zoom, 1], {easing: Easing.out(Easing.quad)});
  const filtro = tom === 'cinza' ? 'grayscale(1) contrast(1.15) brightness(.85)' : tom === 'vermelho' ? 'grayscale(1) contrast(1.2) brightness(.9)'
    : tom === 'dourado' ? 'grayscale(1) contrast(1.15) brightness(.9)' : 'saturate(.85) contrast(1.08)';
  return (
    <AbsoluteFill style={{background: '#111'}}>
      {src && <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${k})`, filter: filtro}} />}
      {tom === 'vermelho' && <AbsoluteFill style={{background: '#c41a22', mixBlendMode: 'multiply', opacity: 0.85}} />}
      {tom === 'dourado' && <AbsoluteFill style={{background: '#c98a1b', mixBlendMode: 'multiply', opacity: 0.8}} />}
    </AbsoluteFill>
  );
};

// ---------- cenas ----------
type CP = {c: CenaC; f: number; fps: number; n: number};

// palavra gigante preta no branco, uma de cada vez, entrando com borrão de movimento
const CPalavra: React.FC<CP> = ({c, f, n}) => {
  const ws = (c.texto || '').split('|').map((s) => s.trim()).filter(Boolean);
  const passo = n / Math.max(1, ws.length);
  const i = Math.min(ws.length - 1, Math.floor(f / passo));
  const lf = f - i * passo;
  const dir = i % 2 ? -1 : 1;
  const x = interpolate(lf, [0, 5], [dir * 420, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const blur = interpolate(lf, [0, 5], [26, 0], {extrapolateRight: 'clamp'});
  const w = ws[i] || '';
  const tam = Math.min(330, Math.floor((W - 140) / (Math.max(w.length, 1) * 0.5)));
  const verm = c.destaque && w.toUpperCase().includes(c.destaque.toUpperCase());
  return (
    <AbsoluteFill style={{background: BRANCO, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{fontFamily: 'Anton', fontSize: tam, lineHeight: 0.95, color: verm ? VERM : '#0b0b0c', textAlign: 'center', textTransform: 'uppercase',
        transform: `translateX(${x}px) scaleX(${1 + blur / 120})`, filter: `blur(${blur * 0.35}px)`, textShadow: rgb(4 + blur * 0.4), padding: '0 50px'}}>{w}</div>
    </AbsoluteFill>
  );
};

// card 3D de interface com contador sobre raios vermelhos
const CContador: React.FC<CP> = ({c, f, fps, n}) => {
  const s = spring({frame: f, fps, config: {damping: 14, stiffness: 90}});
  const prog = ease(f, 4, Math.min(n - 8, 50));
  const v = (c.de ?? 0) + ((c.para ?? 0) - (c.de ?? 0)) * prog;
  const desce = (c.para ?? 0) < (c.de ?? 0);
  const fmt = Math.abs(c.para ?? 0) >= 100 ? Math.round(v).toLocaleString('pt-BR') : v.toFixed(1).replace('.', ',');
  const risca = c.riscar ? ease(f, n * 0.55, n * 0.55 + 8) : 0;
  return (
    <AbsoluteFill>
      <Raios f={f} c1="#d81e26" c2="#a5121a" n={22} />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, rgba(255,120,120,.35), transparent 55%)'}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 1400}}>
        <div style={{transform: `rotateY(${interpolate(s, [0, 1], [-35, -14])}deg) rotateX(${8 + Math.sin(f / 30) * 3}deg) scale(${interpolate(s, [0, 1], [0.7, 1.0])})`, maxWidth: 940,
          background: 'linear-gradient(180deg,#fff,#ecebef)', borderRadius: 60, padding: '40px 64px 40px 40px', display: 'flex', alignItems: 'center', gap: 34,
          boxShadow: '0 40px 90px rgba(80,0,0,.55), inset 0 -6px 0 rgba(0,0,0,.08)', position: 'relative'}}>
          <div style={{width: 130, height: 130, borderRadius: 65, background: '#d81e26', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontFamily: 'InterX', fontSize: 80}}>
            {desce ? '↓' : '↑'}</div>
          <div>
            <div style={{fontFamily: 'InterX', fontSize: 46, color: '#e05a63'}}>{c.rotulo}</div>
            <div style={{fontFamily: 'InterX', fontSize: 128, lineHeight: 1, color: '#d81e26', letterSpacing: -3}}>{fmt}{c.sufixo || ''}</div>
          </div>
          {c.riscar && <div style={{position: 'absolute', left: 30, top: '52%', height: 16, width: `${risca * 92}%`, background: VERM, borderRadius: 8, boxShadow: '0 0 20px rgba(255,0,0,.6)'}} />}
        </div>
        {c.riscar && risca > 0.5 && (
          <div style={{marginTop: 70, fontFamily: 'InterX', fontSize: 120, color: '#fff', textShadow: rgb(5) + ', 0 10px 40px rgba(0,0,0,.4)',
            transform: `scale(${spring({frame: f - n * 0.6, fps, config: {damping: 10}})})`}}>{c.riscar}</div>
        )}
      </AbsoluteFill>
      <Flare x={420} y={620} f={f} />
    </AbsoluteFill>
  );
};

// texto de computador sendo digitado, cursor de bloco, fundo xadrez escuro
const CDigitando: React.FC<CP> = ({c, f}) => {
  const t = (c.texto || '').toUpperCase();
  const k = Math.min(t.length, Math.floor(Math.max(0, f - 6) / 1.6));
  const pisca = Math.floor(f / 8) % 2 === 0;
  return (
    <AbsoluteFill>
      <Xadrez f={f} />
      <AbsoluteFill style={{alignItems: 'flex-start', justifyContent: 'center', padding: '0 90px'}}>
        {c.topo && <div style={{fontFamily: 'Anton', fontSize: 150, color: '#ff6b78', textShadow: rgb(4), marginBottom: 30, marginLeft: 120,
          opacity: ease(f, 0, 4)}}>{c.topo}</div>}
        <div style={{fontFamily: 'Jet', fontWeight: 800, fontSize: Math.min(150, Math.floor(880 / Math.max(6, t.length) / 0.6)), color: '#fff', textShadow: rgb(3), display: 'flex', alignItems: 'center'}}>
          {t.slice(0, k)}
          <span style={{display: 'inline-block', width: '0.6em', height: '1em', background: k < t.length || pisca ? '#fff' : 'transparent', marginLeft: 6}} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// pergunta em letra de máquina sobre branco, palavra-chave em vermelho, avatar pequeno
const CPergunta: React.FC<CP> = ({c, f, fps}) => {
  const s = spring({frame: f, fps, config: {damping: 12}});
  const partes = (c.texto || '').split(/(\*[^*]+\*)/);
  return (
    <AbsoluteFill style={{background: BRANCO, alignItems: 'center', justifyContent: 'center', padding: '0 80px'}}>
      <div style={{width: 240, height: 240, borderRadius: 30, overflow: 'hidden', background: '#111', marginBottom: 60, transform: `scale(${s})`,
        boxShadow: '0 20px 50px rgba(0,0,0,.25)'}}>
        <Img src={staticFile(`sera/${c.pose || 'pensando'}.png`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </div>
      <div style={{fontFamily: 'Jet', fontWeight: 800, fontSize: 88, lineHeight: 1.25, color: '#111', textAlign: 'center', textShadow: rgb(1.5)}}>
        {partes.map((p, i) => p.startsWith('*') ? <span key={i} style={{color: VERM}}>{p.slice(1, -1)}</span> : <span key={i}>{p}</span>)}
      </div>
    </AbsoluteFill>
  );
};

// frase curta minúscula centralizada no preto
const CFrase: React.FC<CP> = ({c, f, fps}) => {
  const ws = (c.texto || '').toLowerCase().split(' ');
  return (
    <AbsoluteFill style={{background: PRETO, alignItems: 'center', justifyContent: 'center', padding: '0 90px'}}>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '10px 26px', maxWidth: 900}}>
        {ws.map((w, i) => {
          const s = spring({frame: f - i * 2.5, fps, config: {damping: 13, stiffness: 160}});
          const verm = c.destaque && w.includes(c.destaque.toLowerCase());
          return <span key={i} style={{fontFamily: 'Mont', fontWeight: 800, fontSize: 124, color: verm ? OURO : '#fff', opacity: s,
            transform: `translateY(${(1 - s) * 40}px)`, display: 'inline-block'}}>{w}</span>;
        })}
      </div>
    </AbsoluteFill>
  );
};

// foto/vídeo de apoio em tela cheia, dessaturado ou tingido, com texto grande
const CFoto: React.FC<CP> = ({c, f, fps, n}) => {
  const s = spring({frame: f - 4, fps, config: {damping: 12}});
  return (
    <AbsoluteFill>
      <Foto src={c.imagem} f={f} n={n} tom={c.tom || 'cinza'} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.15), rgba(0,0,0,.05) 40%, rgba(0,0,0,.45))'}} />
      {c.texto && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
          <div style={{fontFamily: 'InterX', fontSize: Math.min(210, Math.floor(1700 / Math.max(4, c.texto.length))), color: '#fff', textAlign: 'center', lineHeight: 1,
            textShadow: rgb(3) + ', 0 12px 40px rgba(0,0,0,.45)', transform: `scale(${interpolate(s, [0, 1], [1.4, 1])})`, opacity: s, padding: '0 60px'}}>{c.texto}</div>
          {c.sub && <div style={{marginTop: 18, fontFamily: 'InterX', fontSize: 64, color: c.tom === 'vermelho' ? '#ffd0d0' : VERM, opacity: ease(f, 10, 16)}}>{c.sub}</div>}
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

// parede 3D de cards inclinada, com desfoque e o Sera no meio
const CParede: React.FC<CP> = ({c, f, n}) => {
  const imgs = c.imagens || [];
  const cols = 3, linhas = 5;
  const desl = interpolate(f, [0, n], [120, -120]);
  return (
    <AbsoluteFill style={{background: '#050506', perspective: 1600, overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: -260, top: -200, width: W + 520, height: H + 400,
        transform: `rotateX(18deg) rotateZ(-8deg) translateY(${desl}px)`, display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 36, padding: 40}}>
        {Array.from({length: cols * linhas}).map((_, i) => {
          const centro = i === Math.floor(cols * linhas / 2);
          const src = imgs.length ? imgs[i % imgs.length] : undefined;
          return (
            <div key={i} style={{borderRadius: 26, overflow: 'hidden', background: '#1a1a1d', height: 380,
              filter: centro ? 'none' : `blur(${3 + (i % 3)}px) grayscale(.6) brightness(.7)`, boxShadow: centro ? `0 0 0 6px ${OURO}, 0 30px 80px rgba(0,0,0,.7)` : '0 20px 50px rgba(0,0,0,.6)'}}>
              {centro ? <div style={{width: '100%', height: '100%', background: '#0b0b0d', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                <Img src={staticFile('sera/surpreso.png')} style={{height: '92%'}} /></div>
                : src && <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />}
            </div>
          );
        })}
      </div>
      <AbsoluteFill style={{boxShadow: 'inset 0 0 300px 120px #000'}} />
    </AbsoluteFill>
  );
};

// cards de imagem flutuando com rótulos minúsculos
const CCards: React.FC<CP> = ({c, f, fps}) => {
  const itens = (c.itens || []).slice(0, 2) as {rotulo?: string; imagem?: string}[];
  return (
    <AbsoluteFill>
      <Raios f={f} c1="#141416" c2="#0c0c0d" n={26} />
      <Reticula cor="#fff" op={0.06} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 90}}>
        {itens.map((it, i) => {
          const s = spring({frame: f - i * 8, fps, config: {damping: 12}});
          const bob = Math.sin((f + i * 20) / 18) * 10;
          return (
            <div key={i} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', transform: `translateY(${(1 - s) * 200 + bob}px) rotate(${i ? 3 : -3}deg)`, opacity: s}}>
              <div style={{fontFamily: 'Mont', fontWeight: 800, fontSize: 70, color: '#fff', marginBottom: 14}}>{(it.rotulo || '').toLowerCase()}</div>
              <div style={{width: 500, height: 500, borderRadius: 50, overflow: 'hidden', background: '#222', boxShadow: '0 30px 80px rgba(0,0,0,.7), 0 0 0 4px rgba(255,255,255,.08)'}}>
                {it.imagem && <Img src={staticFile(it.imagem)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// diagrama de ícones brancos ligados por setas
const CDiagrama: React.FC<CP> = ({c, f, fps}) => {
  const ps = (c.passos || []).slice(0, 4);
  return (
    <AbsoluteFill style={{background: '#0b0b0c'}}>
      <Reticula cor="#fff" op={0.05} tam={14} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 20}}>
        {ps.map((p, i) => {
          const s = spring({frame: f - i * 9, fps, config: {damping: 12}});
          const seta = ease(f, i * 9 + 4, i * 9 + 12);
          return (
            <React.Fragment key={i}>
              <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: s, transform: `scale(${interpolate(s, [0, 1], [0.6, 1])})`}}>
                <div style={{fontFamily: 'Jet', fontWeight: 800, fontSize: 40, color: i === ps.length - 1 ? OURO : '#cfcfcf', marginBottom: 10}}>{p.rotulo}</div>
                <Icone nome={p.icone} tam={230} />
              </div>
              {i < ps.length - 1 && (
                <svg width="60" height="110" viewBox="0 0 60 110" style={{opacity: seta}}>
                  <path d={`M30 5 V${5 + 85 * seta}`} stroke="#fff" strokeWidth="6" strokeLinecap="round" />
                  {seta > 0.9 && <path d="M12 75 L30 98 L48 75" stroke="#fff" strokeWidth="6" fill="none" strokeLinecap="round" strokeLinejoin="round" />}
                </svg>
              )}
            </React.Fragment>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// mascote grande sobre raios cinza com retícula
const CSera: React.FC<CP> = ({c, f, fps}) => {
  const s = spring({frame: f, fps, config: {damping: 10, stiffness: 120}});
  const bob = Math.sin(f / 12) * 12;
  return (
    <AbsoluteFill>
      <Raios f={f} c1="#8d8d92" c2="#6d6d72" n={30} />
      <Reticula cor="#000" op={0.25} tam={10} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        <Img src={staticFile(`sera/${c.pose || 'pensando'}.png`)} style={{height: 1100, transform: `translateY(${80 + bob}px) scale(${interpolate(s, [0, 1], [0.5, 1])})`,
          filter: 'drop-shadow(0 30px 60px rgba(0,0,0,.5))'}} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// painel de "jogo" (Iman): alerta com barra de poder
const CPainel: React.FC<CP> = ({c, f, fps, n}) => {
  const s = spring({frame: f, fps, config: {damping: 13}});
  const v = (c.valor ?? 10) * ease(f, 6, 30);
  const pisca = 0.75 + 0.25 * Math.sin(f / 3);
  return (
    <AbsoluteFill>
      <Foto src={c.imagem} f={f} n={n} tom="normal" zoom={0.06} />
      <AbsoluteFill style={{background: 'rgba(8,12,24,.62)', backdropFilter: 'blur(6px)'}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', transform: `scale(${interpolate(s, [0, 1], [0.85, 1])})`, opacity: s}}>
        <div style={{width: 420, height: 420, borderRadius: '50%', border: '10px solid rgba(255,80,90,.35)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: `0 0 80px rgba(255,60,70,${0.4 * pisca})`, background: 'radial-gradient(circle, rgba(255,60,70,.35), transparent 70%)'}}>
          <Icone nome="alerta" tam={230} cor="#ff6b75" />
        </div>
        <div style={{marginTop: 50, fontFamily: 'InterX', fontSize: 74, color: '#fff', textAlign: 'center', lineHeight: 1.05, padding: '0 70px'}}>{c.texto}</div>
        {c.rotulo && <div style={{marginTop: 50, width: 760}}>
          <div style={{display: 'flex', justifyContent: 'space-between', fontFamily: 'InterX', fontSize: 48, color: '#dbe4ff'}}><span>{c.rotulo}</span><span>{Math.round(v)}%</span></div>
          <div style={{marginTop: 14, height: 26, borderRadius: 13, background: 'rgba(255,255,255,.15)', overflow: 'hidden'}}>
            <div style={{width: `${v}%`, height: '100%', background: 'linear-gradient(90deg,#ff4d5a,#ff9a62)'}} /></div>
        </div>}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// cards de nível (Iman): iniciante / intermediário / avançado
const CNiveis: React.FC<CP> = ({c, f, fps}) => {
  const itens = (c.itens || []).slice(0, 3) as string[];
  const cores = ['#ff8a3d', '#3db7ff', '#b25cff'];
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 30%, #2a1d12, #0b0907 70%)'}}>
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 46}}>
        {c.texto && <div style={{fontFamily: 'Playfair', fontStyle: 'italic', fontSize: 92, color: '#f3e9dc', marginBottom: 20}}>{c.texto}</div>}
        {itens.map((t, i) => {
          const s = spring({frame: f - 6 - i * 7, fps, config: {damping: 12}});
          return (
            <div key={i} style={{width: 760, padding: '36px 44px', borderRadius: 36, display: 'flex', alignItems: 'center', gap: 36, opacity: s,
              transform: `translateX(${(1 - s) * (i % 2 ? 300 : -300)}px)`, background: 'linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,.03))',
              border: `2px solid ${cores[i]}66`, boxShadow: `0 0 50px ${cores[i]}33`}}>
              <div style={{filter: `drop-shadow(0 0 22px ${cores[i]})`}}><Icone nome="raio" tam={120} cor={cores[i]} /></div>
              <div style={{fontFamily: 'Playfair', fontStyle: 'italic', fontSize: 70, color: '#fff'}}>{t}</div>
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// lista elegante com serifa itálica e asterisco laranja (Iman)
const CSerifa: React.FC<CP> = ({c, f, fps, n}) => {
  const itens = (c.itens || []).slice(0, 4) as string[];
  return (
    <AbsoluteFill>
      <Foto src={c.imagem} f={f} n={n} tom="normal" zoom={0.08} />
      <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(10,12,20,.88), rgba(10,12,20,.55))'}} />
      <AbsoluteFill style={{justifyContent: 'center', padding: '0 110px', gap: 34}}>
        {itens.map((t, i) => {
          const s = spring({frame: f - 4 - i * 8, fps, config: {damping: 14}});
          return <div key={i} style={{fontFamily: 'Playfair', fontStyle: 'italic', fontSize: 96, color: '#f4efe6', opacity: s,
            transform: `translateY(${(1 - s) * 30}px)`, display: 'flex', alignItems: 'center', gap: 30}}>
            <span style={{color: OURO, fontSize: 80, fontStyle: 'normal'}}>✳</span>{t}</div>;
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// encerramento da marca
const CCta: React.FC<CP> = ({c, f, fps, n}) => {
  const s = spring({frame: f, fps, config: {damping: 11}});
  const pill = 1 + 0.04 * Math.sin(f / 5);
  const fundo = (c as any).funil === 'fundo';
  // botão "Seguir" estilo Instagram: o cursor toca e vira "Seguindo"
  const toque = Math.round(n * 0.45);
  const clicou = f >= toque;
  const cur = interpolate(f, [toque - 14, toque - 2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const aperta = f >= toque - 2 && f < toque + 3 ? 0.92 : 1;
  const bs = spring({frame: f - 8, fps, config: {damping: 12}});
  return (
    <AbsoluteFill style={{background: PRETO}}>
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 34%, rgba(245,166,35,.28), transparent 55%)'}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        <Img src={staticFile(`sera/${c.pose || 'confiante'}.png`)} style={{height: 640, transform: `scale(${s}) translateY(${Math.sin(f / 12) * 10}px)`}} />
        <div style={{fontFamily: 'Anton', fontSize: 120, color: '#fff', textAlign: 'center', lineHeight: 1.02, marginTop: 10, textShadow: rgb(3), padding: '0 60px'}}>
          {(c.texto || '').split('*').map((t, i) => <span key={i} style={{color: i % 2 ? OURO : '#fff'}}>{t}</span>)}</div>
        {fundo && (
          <div style={{marginTop: 44, padding: '24px 56px', borderRadius: 999, background: OURO, color: PRETO, fontFamily: 'InterX', fontSize: 50,
            transform: `scale(${bs * pill})`}}>{c.apoio || 'link na bio'} →</div>
        )}
        <div style={{position: 'relative', marginTop: fundo ? 34 : 56, display: 'flex', alignItems: 'center', gap: 22, transform: `scale(${bs * (fundo ? 0.8 : 1) * aperta})`}}>
          <Img src={staticFile('marca/icone.png')} style={{width: 92, height: 92, borderRadius: 46, boxShadow: `0 0 0 4px ${OURO}`}} />
          <div style={{fontFamily: 'InterX', fontSize: 44, color: '#fff'}}>seraphimtech_</div>
          <div style={{padding: '18px 44px', borderRadius: 18, fontFamily: 'InterX', fontSize: 44,
            background: clicou ? '#363639' : '#0095F6', color: '#fff', transition: 'none'}}>{clicou ? 'Seguindo ✓' : 'Seguir'}</div>
          <div style={{position: 'absolute', right: 40 - (1 - cur) * 160, top: 50 + (1 - cur) * 220, fontSize: 90, opacity: cur > 0 && f < toque + 20 ? 1 : 0,
            filter: 'drop-shadow(0 6px 10px rgba(0,0,0,.6))'}}>👆</div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const MAPA: Record<string, React.FC<CP>> = {
  palavra: CPalavra, contador: CContador, digitando: CDigitando, pergunta: CPergunta, frase: CFrase, foto: CFoto,
  parede: CParede, cards: CCards, diagrama: CDiagrama, sera: CSera, painel: CPainel, niveis: CNiveis, serifa: CSerifa, cta: CCta,
};
// cenas onde a narração NÃO está escrita na tela -> mostram legenda pequena
const COM_LEGENDA = new Set(['foto', 'parede', 'cards', 'diagrama', 'sera', 'contador', 'niveis', 'serifa', 'painel']);

const CenaWrap: React.FC<{c: CenaC; n: number; idx: number}> = ({c, n, idx}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const Comp = MAPA[c.tipo] || CFrase;
  // entrada: tranco + zoom; saída: borrão de chicote
  const push = interpolate(f, [0, n], [1.0, 1.05]);
  const entra = interpolate(f, [0, 4], [1.18, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const sai = interpolate(f, [n - 4, n], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tremor = f < 5 ? (5 - f) * 3 : 0;
  const dir = idx % 2 ? 1 : -1;
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `scale(${push * entra}) translate(${Math.sin(f * 7) * tremor + dir * sai * 260}px, ${Math.cos(f * 5) * tremor}px)`,
        filter: sai > 0 ? `blur(${sai * 18}px)` : undefined}}>
        <Comp c={c} f={f} fps={fps} n={n} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// transições: flash de luz (amarelo/laranja) ou glitch, sorteados por cena
const Transicao: React.FC<{i: number}> = ({i}) => {
  const f = useCurrentFrame();
  const tipo = random('t' + i) < 0.5 ? 'luz' : 'glitch';
  if (tipo === 'luz') {
    const a = interpolate(f, [0, 3, 8], [0, 1, 0], {extrapolateRight: 'clamp'});
    return <AbsoluteFill style={{mixBlendMode: 'screen', opacity: a, background: `radial-gradient(ellipse at ${30 + random('x' + i) * 40}% 50%, #fff7c2 0%, #ffd400 25%, #ff7a00 55%, transparent 80%)`}} />;
  }
  if (f > 6) return null;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {Array.from({length: 7}).map((_, k) => (
        <div key={k} style={{position: 'absolute', left: 0, right: 0, top: random(`g${i}${k}${f}`) * H, height: 20 + random(`h${i}${k}${f}`) * 90,
          background: k % 2 ? 'rgba(255,40,70,.5)' : 'rgba(40,160,255,.45)', mixBlendMode: 'screen', transform: `translateX(${(random(`d${i}${k}${f}`) - 0.5) * 200}px)`}} />
      ))}
    </AbsoluteFill>
  );
};

const Legenda: React.FC<{palavras: Palavra[]; cenas: CenaC[]; t: number}> = ({palavras, cenas, t}) => {
  const cena = cenas.find((c) => t >= c.inicio && t < c.fim);
  if (!cena || !COM_LEGENDA.has(cena.tipo) || cena.legenda === false) return null;
  const ps = palavras.filter((p) => p.s >= cena.inicio - 0.05 && p.s < cena.fim);
  const grupos: Palavra[][] = [];
  ps.forEach((p, i) => { if (i % 3 === 0) grupos.push([]); grupos[grupos.length - 1].push(p); });
  const g = grupos.find((gr) => t >= gr[0].s - 0.05 && t <= gr[gr.length - 1].e + 0.2);
  if (!g) return null;
  return (
    <div style={{position: 'absolute', left: 70, right: 70, bottom: 230, display: 'flex', gap: 18, flexWrap: 'wrap', justifyContent: 'center', textAlign: 'center'}}>
      {g.map((p, i) => (
        <span key={i} style={{fontFamily: 'Mont', fontWeight: 800, fontSize: 64, color: t >= p.s ? '#fff' : 'rgba(255,255,255,.4)',
          textShadow: '0 4px 0 rgba(0,0,0,.7), 0 0 24px rgba(0,0,0,.6)'}}>{p.w.toLowerCase().replace(/[.,!?:;]$/, '')}</span>
      ))}
    </div>
  );
};

export const SeraphimCortes: React.FC<PropsC> = (props) => {
  useFontes();
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill style={{background: PRETO}}>
      {props.cenas.map((c, i) => {
        const from = Math.round(c.inicio * fps);
        const dur = Math.max(1, Math.round((c.fim - c.inicio) * fps));
        return (
          <React.Fragment key={i}>
            <Sequence from={from} durationInFrames={dur}><CenaWrap c={c} n={dur} idx={i} /></Sequence>
            {i > 0 && <Sequence from={Math.max(0, from - 2)} durationInFrames={10}><Transicao i={i} /></Sequence>}
          </React.Fragment>
        );
      })}
      <Legenda palavras={props.palavras} cenas={props.cenas} t={t} />
      <Acabamento f={frame} />
      {/* assinatura sutil da marca */}
      <div style={{position: 'absolute', top: 0, left: 0, height: 8, width: `${(frame / durationInFrames) * 100}%`, background: OURO}} />
      <div style={{position: 'absolute', left: 50, bottom: 60, display: 'flex', alignItems: 'center', gap: 16, opacity: 0.9, background: 'rgba(0,0,0,.45)', padding: '8px 22px 8px 8px', borderRadius: 40}}>
        <Img src={staticFile('marca/icone.png')} style={{width: 60, height: 60, borderRadius: 30, boxShadow: `0 0 0 3px ${OURO}`}} />
        <span style={{fontFamily: 'InterM', fontSize: 34, color: '#e8e8e8', textShadow: '0 2px 8px rgba(0,0,0,.8)'}}>{props.arroba}</span>
      </div>
      {props.audio && <Audio src={staticFile(props.audio)} />}
      {props.batida && <Audio src={staticFile(props.batida)} volume={props.audio ? 0.12 : 0.7} />}
      {props.sfx && props.cenas.map((c, i) => (
        <React.Fragment key={'s' + i}>
          {i > 0 && <Sequence from={Math.max(0, Math.round((c.inicio - 0.2) * fps))}><Audio src={staticFile('sfx/whoosh.wav')} volume={0.4} /></Sequence>}
          {['palavra', 'contador', 'painel'].includes(c.tipo) && <Sequence from={Math.round(c.inicio * fps)}><Audio src={staticFile('sfx/impacto.wav')} volume={0.45} /></Sequence>}
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
};
