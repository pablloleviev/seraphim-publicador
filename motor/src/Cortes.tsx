// Motor de CORTES verticais da Seraphim — base: RunnyIA (cenas de tipos diferentes, cor muda a cada cena,
// acabamento de TV antiga) + toques do Iman Gadzhi (painéis de "jogo", serifa itálica).
import React from 'react';
import {
  AbsoluteFill, Audio, Img, Sequence, Video, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing, continueRender, delayRender, random,
} from 'remotion';

const W = 1080, H = 1920;
// paleta VIVA: cada formato de edição (abaixo) troca estas cores antes de renderizar
let OURO = '#F5A623', VERM = '#E3242B', BRANCO = '#F4F4F2', PRETO = '#060607';
let VERMD = '#a5121a', VERML = '#e05a63', ACRGB = '245,166,35', TINTA = '#0A0A0C', FRASEF = 'Mont', LEGF = 'Mont';

export type Palavra = {w: string; s: number; e: number};
export type CenaC = {
  inicio: number; fim: number; tipo: string;
  texto?: string; topo?: string; destaque?: string; sub?: string;
  rotulo?: string; de?: number; para?: number; sufixo?: string; riscar?: string;
  imagem?: string; imagens?: string[]; tom?: 'cinza' | 'vermelho' | 'dourado' | 'normal';
  itens?: {rotulo?: string; imagem?: string; texto?: string}[] | any[];
  passos?: {icone: string; rotulo: string}[];
  pose?: string; legenda?: boolean; valor?: number; apoio?: string;
  marcas?: number[]; video?: string; etiqueta?: string;
};
export type PropsC = {
  fps: number; duracao: number; arroba: string; audio: string | null; batida: string | null; sfx: boolean;
  palavras: Palavra[]; cenas: CenaC[]; formato?: string; titulo?: string; numero?: number;
};

// ---------- fontes ----------
const FONTES: [string, string, string?][] = [
  ['Anton', 'anton.ttf'], ['Jet', 'jetbrains.ttf', '800'], ['Mont', 'montserrat.ttf', '800'],
  ['Playfair', 'playfair.ttf', '500'], ['InterX', 'inter800.ttf', '800'], ['InterM', 'inter500.ttf', '500'],
  ['Bebas', 'bebas.ttf'], ['Oswald', 'oswald-700.woff2', '700'], ['BigSh', 'big-shoulders-display-900.woff2', '900'],
  ['Sora', 'sora-700.woff2', '700'], ['Syne', 'syne-800.woff2', '800'], ['Unbounded', 'unbounded-800.woff2', '800'],
  ['StackH', 'stack-sans-headline-latin-700-normal.woff2', '700'], ['StackT', 'stack-sans-text-latin-500-normal.woff2', '500'],
];
// fonte de manchete por vídeo (Pabllo: diversificar também a tipografia). FT = condensadas (largura parecida com Anton),
// FW = largas (no lugar da Montserrat). Sorteadas pelo SEED de cada vídeo.
const FTS = ['Anton', 'Anton', 'Oswald', 'BigSh', 'Bebas'];
const FWS = ['Mont', 'Sora', 'Syne', 'Unbounded'];
let FT = 'Anton';
let FW = 'Mont';
let ARROBA = '@seraphimbr_';
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

// ---------- fundos variados: cada cena sorteia o seu (por semente do vídeo + texto da cena) ----------
const FUNDOS = ['aurora', 'diagonais', 'grade', 'ondas', 'circulos', 'pontos', 'raios', 'liso', 'cruzes', 'xadrez'] as const;
const FundoVar: React.FC<{f: number; c: CenaC; salt?: number; lista?: readonly string[]}> = ({f, c, salt = 0, lista}) => {
  const L = lista || FUNDOS;
  const k = L[(hash((c.texto || '') + (c.tipo || '')) + SEED + salt) % L.length];
  const A = `rgb(${ACRGB})`;
  const base = PRETO;
  if (k === 'xadrez') return <Xadrez f={f} />;
  if (k === 'raios') return <Raios f={f} c1="#17171b" c2={base} n={20 + (SEED % 8)} />;
  if (k === 'aurora') return (
    <AbsoluteFill style={{background: base}}>
      <AbsoluteFill style={{background: `radial-gradient(circle at ${30 + Math.sin(f / 50) * 20}% ${25 + Math.cos(f / 60) * 10}%, rgba(${ACRGB},.30), transparent 48%), radial-gradient(circle at ${75 - Math.sin(f / 45) * 15}% ${80 + Math.sin(f / 70) * 8}%, ${VERM}55, transparent 50%)`}} />
    </AbsoluteFill>
  );
  if (k === 'diagonais') return (
    <AbsoluteFill style={{background: base}}>
      <AbsoluteFill style={{backgroundImage: `repeating-linear-gradient(45deg, rgba(${ACRGB},.10) 0 26px, transparent 26px 70px)`, backgroundPosition: `${f * 1.2}px 0`}} />
    </AbsoluteFill>
  );
  if (k === 'grade') return (
    <AbsoluteFill style={{background: base}}>
      <AbsoluteFill style={{backgroundImage: `linear-gradient(rgba(${ACRGB},.13) 2px, transparent 2px), linear-gradient(90deg, rgba(${ACRGB},.13) 2px, transparent 2px)`, backgroundSize: '90px 90px', backgroundPosition: `0 ${f}px`}} />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, transparent 35%, rgba(0,0,0,.7))'}} />
    </AbsoluteFill>
  );
  if (k === 'ondas') return (
    <AbsoluteFill style={{background: base}}>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <path key={i} fill="none" stroke={A} strokeOpacity={0.10 + i * 0.03} strokeWidth={4}
            d={`M0 ${H * (0.2 + i * 0.13)} ` + Array.from({length: 13}, (_, j) => `L${j * 90} ${H * (0.2 + i * 0.13) + Math.sin(j * 0.9 + f / 18 + i) * 60}`).join(' ')} />
        ))}
      </svg>
    </AbsoluteFill>
  );
  if (k === 'circulos') return (
    <AbsoluteFill style={{background: base}}>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        {[0, 1, 2, 3, 4, 5, 6].map((i) => <circle key={i} cx={W / 2} cy={H * 0.45} r={140 + i * 170 + ((f * 1.5) % 170)} fill="none" stroke={A} strokeOpacity={0.14} strokeWidth={3} />)}
      </svg>
    </AbsoluteFill>
  );
  if (k === 'pontos') return (
    <AbsoluteFill style={{background: base}}>
      <AbsoluteFill style={{backgroundImage: `radial-gradient(rgba(${ACRGB},.22) 5px, transparent 6px)`, backgroundSize: '70px 70px', backgroundPosition: `${f * 0.6}px ${f * 0.6}px`}} />
    </AbsoluteFill>
  );
  if (k === 'cruzes') return (
    <AbsoluteFill style={{background: base}}>
      <AbsoluteFill style={{backgroundImage: `linear-gradient(rgba(${ACRGB},.22) 0 0), linear-gradient(rgba(${ACRGB},.22) 0 0)`, backgroundSize: '26px 3px, 3px 26px', backgroundPosition: 'center', backgroundRepeat: 'no-repeat',
        WebkitMaskImage: 'none'}} />
      <AbsoluteFill style={{backgroundImage: `radial-gradient(rgba(${ACRGB},.0) 0, transparent 1px)`}} />
      <AbsoluteFill style={{background: `radial-gradient(circle at 50% 40%, rgba(${ACRGB},.12), transparent 60%)`}} />
    </AbsoluteFill>
  );
  return (
    <AbsoluteFill style={{background: `radial-gradient(circle at 50% 40%, #1c1c22, ${base} 75%)`}} />
  );
};
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
let ABER = 1;   // intensidade da aberração cromática (0 = desligada), definida pelo formato/semente
const rgb = (n: number) => ABER <= 0.05 ? '0 0 0 transparent' : `${-n * ABER}px 0 rgba(255,30,60,.75), ${n * ABER}px 0 rgba(30,160,255,.75)`;
let SEED = 0;
const hash = (t: string) => { let h = 7; for (let i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) >>> 0; return h; };

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
// quadro em que o item i é FALADO (marcas calculadas a partir da voz); sem marca, usa o padrão
const mk = (c: CenaC, i: number, fps: number, padrao: number) => (c.marcas && c.marcas[i] != null ? Math.round(c.marcas[i] * fps) : padrao);

// palavra gigante preta no branco, uma de cada vez, entrando com borrão de movimento
const CPalavra: React.FC<CP> = ({c, f, n}) => {
  const ws = (c.texto || '').split('|').map((s) => s.trim()).filter(Boolean);
  const passo = n / Math.max(1, ws.length);
  const ini = ws.map((_, k) => (k === 0 ? 0 : mk(c, k, 30, Math.round(k * passo))));
  let i = 0; ini.forEach((q, k) => { if (f >= q) i = k; });
  const lf = f - ini[i];
  const dir = i % 2 ? -1 : 1;
  const x = interpolate(lf, [0, 5], [dir * 420, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const blur = interpolate(lf, [0, 5], [26, 0], {extrapolateRight: 'clamp'});
  const w = ws[i] || '';
  const tam = Math.min(330, Math.floor((W - 140) / (Math.max(w.length, 1) * 0.5)));
  const verm = c.destaque && w.toUpperCase().includes(c.destaque.toUpperCase());
  return (
    <AbsoluteFill style={{background: BRANCO, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{fontFamily: FT, fontSize: tam, lineHeight: 0.95, color: verm ? VERM : '#0b0b0c', textAlign: 'center', textTransform: 'uppercase',
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
  const inteiro = Number.isInteger(c.para ?? 0) && Number.isInteger(c.de ?? 0);
  const fmt = inteiro || Math.abs(c.para ?? 0) >= 100 ? Math.round(v).toLocaleString('pt-BR') : v.toFixed(1).replace('.', ',');
  const risca = c.riscar ? ease(f, n * 0.55, n * 0.55 + 8) : 0;
  return (
    <AbsoluteFill>
      <Raios f={f} c1={VERM} c2={VERMD} n={22} />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, rgba(255,120,120,.35), transparent 55%)'}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 1400}}>
        <div style={{transform: `rotateY(${interpolate(s, [0, 1], [-35, -14])}deg) rotateX(${8 + Math.sin(f / 30) * 3}deg) scale(${interpolate(s, [0, 1], [0.7, 1.0])})`, maxWidth: 940,
          background: 'linear-gradient(180deg,#fff,#ecebef)', borderRadius: 60, padding: '40px 64px 40px 40px', display: 'flex', alignItems: 'center', gap: 34,
          boxShadow: '0 40px 90px rgba(80,0,0,.55), inset 0 -6px 0 rgba(0,0,0,.08)', position: 'relative'}}>
          <div style={{width: 130, height: 130, borderRadius: 65, background: VERM, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontFamily: 'InterX', fontSize: 80}}>
            {desce ? '↓' : '↑'}</div>
          <div>
            <div style={{fontFamily: 'InterX', fontSize: 46, color: VERML}}>{c.rotulo}</div>
            <div style={{fontFamily: 'InterX', fontSize: 128, lineHeight: 1, color: VERM, letterSpacing: -3}}>{fmt}{c.sufixo || ''}</div>
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
// texto digitado: no máximo 2 linhas, letra grande
const quebra = (t: string) => {
  if (t.length <= 13) return t;
  const ps = t.split(' '); let best = t, dif = 999;
  for (let i = 1; i < ps.length; i++) { const a = ps.slice(0, i).join(' '), b = ps.slice(i).join(' '); const d = Math.abs(a.length - b.length); if (d < dif) { dif = d; best = a + '\n' + b; } }
  return best;
};
const tamDig = (t: string) => Math.max(84, Math.min(150, Math.floor(880 / (Math.max(6, ...quebra(t).split('\n').map((l) => l.length)) * 0.6))));
const CDigitando: React.FC<CP> = ({c, f}) => {
  const t = (c.texto || '').toUpperCase();
  const k = Math.min(t.length, Math.floor(Math.max(0, f - 6) / 1.6));
  const pisca = Math.floor(f / 8) % 2 === 0;
  return (
    <AbsoluteFill>
      <FundoVar f={f} c={c} />
      <AbsoluteFill style={{alignItems: 'flex-start', justifyContent: 'center', padding: '0 90px'}}>
        {c.topo && <div style={{fontFamily: FT, fontSize: 150, color: VERML, textShadow: rgb(4), marginBottom: 30, marginLeft: 120,
          opacity: ease(f, 0, 4)}}>{c.topo}</div>}
        <div style={{fontFamily: 'Jet', fontWeight: 800, fontSize: tamDig(t), lineHeight: 1.1, color: '#fff', textShadow: rgb(3), maxWidth: 900, whiteSpace: 'pre-wrap'}}>
          {quebra(t).slice(0, k + (quebra(t).length - t.length))}
          {(() => { const v = SEED % 3; const on = k < t.length || pisca; return <span style={{display: 'inline-block', width: v === 0 ? '0.6em' : v === 1 ? '0.12em' : '0.55em', height: v === 2 ? '0.12em' : '1em', verticalAlign: v === 2 ? 'baseline' : 'middle', background: on ? (v === 0 ? '#fff' : OURO) : 'transparent', marginLeft: 6}} />; })()}
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
  // *palavra* no texto = destaque dourado (o asterisco nunca aparece na tela)
  const bruto = (c.texto || '').toLowerCase();
  const marcadas = new Set((bruto.match(/\*([^*]+)\*/g) || []).flatMap((m) => m.replace(/\*/g, '').split(' ')));
  const ws = bruto.replace(/\*/g, '').split(' ').filter(Boolean);
  return (
    <AbsoluteFill style={{background: PRETO, alignItems: 'center', justifyContent: 'center', padding: '0 90px'}}>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '10px 26px', maxWidth: 900}}>
        {ws.map((w, i) => {
          const s = spring({frame: f - i * 2.5, fps, config: {damping: 13, stiffness: 160}});
          const verm = marcadas.has(w) || (c.destaque && w.includes(c.destaque.toLowerCase()));
          return <span key={i} style={{fontFamily: FRASEF, fontWeight: 800, fontSize: 124, color: verm ? OURO : '#fff', opacity: s,
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
      {c.video ? (
        <AbsoluteFill style={{background: '#111'}}>
          <Video src={staticFile(c.video)} muted loop style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${interpolate(f, [0, n], [1.12, 1.0])})`,
            filter: (c.tom || 'cinza') === 'normal' ? 'saturate(.95) contrast(1.08) brightness(1.05)' : 'grayscale(1) contrast(1.2) brightness(1.25)'}} />
          {c.tom === 'vermelho' && <AbsoluteFill style={{background: '#d42a30', mixBlendMode: 'multiply', opacity: 0.55}} />}
          {c.tom === 'dourado' && <AbsoluteFill style={{background: '#d99a2b', mixBlendMode: 'multiply', opacity: 0.5}} />}
        </AbsoluteFill>
      ) : <Foto src={c.imagem} f={f} n={n} tom={c.tom || 'cinza'} />}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.15), rgba(0,0,0,.05) 40%, rgba(0,0,0,.45))'}} />
      {c.texto && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
          <div style={{fontFamily: 'InterX', fontSize: Math.min(210, Math.floor(1700 / Math.max(4, c.texto.length))), color: '#fff', textAlign: 'center', lineHeight: 1,
            textShadow: rgb(3) + ', 0 12px 40px rgba(0,0,0,.45)', transform: `scale(${interpolate(s, [0, 1], [1.4, 1])})`, opacity: s, padding: '0 60px'}}>{c.texto}</div>
          {c.sub && <div style={{marginTop: 18, fontFamily: 'InterX', fontSize: 64, color: c.tom === 'vermelho' ? '#ffd0d0' : c.tom === 'dourado' ? '#FFFFFF' : VERM, textShadow: '0 4px 18px rgba(0,0,0,.7)', opacity: ease(f, 10, 16)}}>{c.sub}</div>}
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
      <FundoVar f={f} c={c} salt={3} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 90}}>
        {itens.map((it, i) => {
          const s = spring({frame: f - mk(c, i, fps, i * 8), fps, config: {damping: 12}});
          const bob = Math.sin((f + i * 20) / 18) * 10;
          return (
            <div key={i} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', transform: `translateY(${(1 - s) * 200 + bob}px) rotate(${i ? 3 : -3}deg)`, opacity: s}}>
              <div style={{fontFamily: FW, fontWeight: 800, fontSize: 70, color: '#fff', marginBottom: 14}}>{(it.rotulo || '').toLowerCase()}</div>
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
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 20, paddingBottom: ps.length >= 4 ? 260 : 0}}>
        {ps.map((p, i) => {
          const q = mk(c, i, fps, i * 9);
          const s = spring({frame: f - q, fps, config: {damping: 12}});
          const q2 = mk(c, i + 1, fps, (i + 1) * 9);
          const seta = ease(f, q2 - 8, q2);
          const bob = Math.sin((f + i * 17) / 14) * 8;
          return (
            <React.Fragment key={i}>
              <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: s, transform: `translateY(${bob}px) scale(${interpolate(s, [0, 1], [0.6, 1]) * (f - q < 12 && f >= q ? 1 + 0.08 * Math.sin((f - q) / 12 * Math.PI) : 1)})`}}>
                <div style={{fontFamily: 'Jet', fontWeight: 800, fontSize: 40, color: i === ps.length - 1 ? OURO : '#cfcfcf', marginBottom: 10}}>{p.rotulo}</div>
                <Icone nome={p.icone} tam={ps.length >= 4 ? 165 : 230} />
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
          <Icone nome="alerta" tam={230} cor={VERML} />
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
          const s = spring({frame: f - mk(c, i, fps, 6 + i * 7), fps, config: {damping: 12}});
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
  const itens = ((c.itens && c.itens.length ? c.itens : [c.texto || '']) as string[]).slice(0, 4);
  const um = itens.length === 1;
  return (
    <AbsoluteFill style={{background: 'linear-gradient(160deg,#1a1410,#0a0a0b 70%)'}}>
      <Foto src={c.imagem} f={f} n={n} tom="normal" zoom={0.08} />
      <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(10,12,20,.88), rgba(10,12,20,.55))'}} />
      <AbsoluteFill style={{justifyContent: 'center', padding: '0 110px', gap: 34}}>
        {itens.map((t, i) => {
          const s = spring({frame: f - mk(c, i, fps, 4 + i * 8), fps, config: {damping: 14}});
          return <div key={i} style={{fontFamily: 'Playfair', fontStyle: 'italic', fontSize: um ? 110 : 96, lineHeight: 1.12, color: '#f4efe6', opacity: s,
            transform: `translateY(${(1 - s) * 30}px)`, display: 'flex', alignItems: 'center', gap: 30}}>
            {!um && <span style={{color: OURO, fontSize: 80, fontStyle: 'normal'}}>✳</span>}{t.replace(/\*/g, '')}</div>;
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
      <AbsoluteFill style={{background: `radial-gradient(circle at 50% 34%, rgba(${ACRGB},.28), transparent 55%)`}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        {/* "marca": imagem no lugar da Sera (peças de produto, como o AutoFlow, não usam o mascote) */}
        <Img src={staticFile((c as any).marca || `sera/${c.pose || 'confiante'}.png`)}
          style={{height: (c as any).marca ? 300 : 640, transform: `scale(${s}) translateY(${Math.sin(f / 12) * 10}px)`}} />
        <div style={{fontFamily: FT, fontSize: 120, color: '#fff', textAlign: 'center', lineHeight: 1.02, marginTop: 10, textShadow: rgb(3), padding: '0 60px'}}>
          {(c.texto || '').split('*').map((t, i) => <span key={i} style={{color: i % 2 ? OURO : '#fff'}}>{t}</span>)}</div>
        {fundo && (
          <div style={{marginTop: 44, padding: '24px 56px', borderRadius: 999, background: OURO, color: PRETO, fontFamily: 'InterX', fontSize: 50,
            transform: `scale(${bs * pill})`}}>{c.apoio || 'link na bio'} →</div>
        )}
        <div style={{position: 'relative', marginTop: fundo ? 34 : 56, display: 'flex', alignItems: 'center', gap: 22, transform: `scale(${bs * (fundo ? 1.05 : 1.25) * aperta})`}}>
          <Img src={staticFile('marca/icone.png')} style={{width: 92, height: 92, borderRadius: 46, boxShadow: `0 0 0 4px ${OURO}`}} />
          <div style={{fontFamily: 'InterX', fontSize: 44, color: '#fff'}}>{ARROBA.replace('@', '')}</div>
          <div style={{padding: '18px 44px', borderRadius: 18, fontFamily: 'InterX', fontSize: 44,
            background: clicou ? '#363639' : '#0095F6', color: '#fff', transition: 'none'}}>{clicou ? 'Seguindo ✓' : 'Seguir'}</div>
          <div style={{position: 'absolute', right: 40 - (1 - cur) * 160, top: 50 + (1 - cur) * 220, fontSize: 90, opacity: cur > 0 && f < toque + 20 ? 1 : 0,
            filter: 'drop-shadow(0 6px 10px rgba(0,0,0,.6))'}}>👆</div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- inspiradas na Blue Ocean (13/10/2026) ----------
const FundoOuro: React.FC<{f: number}> = ({f}) => (
  <AbsoluteFill style={{background: `radial-gradient(circle at ${75 + Math.sin(f / 40) * 5}% 12%, rgba(${ACRGB},.28), transparent 45%), radial-gradient(circle at 10% 95%, rgba(${ACRGB},.12), transparent 40%), ${PRETO}`}}>
    <Reticula cor="#fff" op={0.05} />
  </AbsoluteFill>
);

// interruptor de app que DESLIGA no meio da cena (a ideia vira objeto de tela)
// rotulo = nome do interruptor, texto = subtítulo ligado, sub = subtítulo desligado, valor = 0..1 (quando desliga)
const CInterruptor: React.FC<CP> = ({c, f, fps, n}) => {
  const s = spring({frame: f, fps, config: {damping: 11, stiffness: 140}});
  const tOff = Math.round(n * (c.valor ?? 0.5));
  const off = ease(f, tOff, tOff + 6);
  const x = spring({frame: f - tOff - 8, fps, config: {damping: 8, stiffness: 220}});
  const knob = interpolate(off, [0, 1], [96, 10]);
  return (
    <AbsoluteFill>
      <FundoVar f={f} c={c} salt={1} lista={['aurora', 'grade', 'diagonais', 'circulos', 'liso']} />
      <div style={{position: 'absolute', left: 80, right: 80, top: 520, height: 210, background: '#fff', borderRadius: 42, display: 'flex', alignItems: 'center',
        padding: '0 46px', gap: 34, boxShadow: '0 40px 100px rgba(0,0,0,.6)', transform: `translateY(${(1 - s) * -160}px) scale(${0.9 + 0.1 * s})`, opacity: s}}>
        <div style={{width: 112, height: 112, borderRadius: 28, background: OURO, display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'InterX', fontSize: 58, color: TINTA}}>{(c.rotulo || '?').trim().charAt(0).toUpperCase()}</div>
        <div style={{flex: 1, position: 'relative'}}>
          <div style={{fontFamily: 'InterX', fontSize: 54, color: '#111', lineHeight: 1.1}}>{c.rotulo}</div>
          <div style={{fontFamily: 'InterM', fontSize: 38, color: '#8a8a93', opacity: 1 - off}}>{c.texto}</div>
          <div style={{fontFamily: 'InterM', fontSize: 38, color: '#e5484d', position: 'absolute', bottom: 0, opacity: off}}>{c.sub}</div>
        </div>
        <div style={{width: 190, height: 104, borderRadius: 52, background: off > 0.5 ? '#d4d4d8' : OURO, position: 'relative', flexShrink: 0}}>
          <div style={{position: 'absolute', top: 10, left: knob, width: 84, height: 84, borderRadius: '50%', background: '#fff', boxShadow: '0 4px 10px rgba(0,0,0,.25)'}} />
        </div>
        <div style={{position: 'absolute', right: -22, top: -22, width: 72, height: 72, borderRadius: '50%', background: '#e5484d', color: '#fff',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'InterX', fontSize: 40, transform: `scale(${x})`}}>✕</div>
      </div>
    </AbsoluteFill>
  );
};

// checklist em card que vai sendo preenchido (rotulo = título do card, itens = textos)
const CChecklist: React.FC<CP> = ({c, f, fps, n}) => {
  const itens = ((c.itens || []) as any[]).map((it) => (typeof it === 'string' ? it : it.texto || it.rotulo || '')).slice(0, 5);
  const s = spring({frame: f, fps, config: {damping: 13}});
  const passo = Math.max(6, Math.floor((n * 0.75) / Math.max(1, itens.length)));
  return (
    <AbsoluteFill>
      <FundoVar f={f} c={c} salt={1} lista={['aurora', 'grade', 'diagonais', 'circulos', 'liso']} />
      <div style={{position: 'absolute', left: 90, right: 90, top: 380, background: '#141418', border: '2px solid #26262c', borderRadius: 40, padding: '46px 50px',
        boxShadow: '0 40px 100px rgba(0,0,0,.6)', transform: `translateY(${(1 - s) * 120}px)`, opacity: s}}>
        <div style={{fontFamily: 'InterX', fontSize: 50, color: OURO, marginBottom: 30}}>{c.rotulo}</div>
        {itens.map((t, i) => {
          const q = mk(c, i, fps, 6 + i * passo);
          const a = spring({frame: f - q, fps, config: {damping: 12}});
          const ok = ease(f, q + 6, q + 10);
          return (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 26, padding: '22px 0', borderTop: i ? '1px solid #26262c' : 'none',
              opacity: a, transform: `translateX(${(1 - a) * 60}px)`}}>
              <div style={{width: 58, height: 58, borderRadius: 16, border: `3px solid ${OURO}`, background: ok > 0.5 ? OURO : 'transparent', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'InterX', fontSize: 36, color: TINTA}}>{ok > 0.5 ? '✓' : ''}</div>
              <div style={{fontFamily: 'InterX', fontSize: 50, color: '#fff', lineHeight: 1.15}}>{t}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};


// calendário: a data vira (tempo passando = resultado). "de" e "para" são textos tipo "18 OUT" / "28 NOV"; "rotulo" legenda do card
const CCalendario: React.FC<CP> = ({c, f, fps, n}) => {
  const s = spring({frame: f, fps, config: {damping: 13}});
  const t0 = Math.round(n * 0.38);
  const vira = interpolate(f, [t0, t0 + 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const sep = (v?: string) => { const m = (v || '').trim().split(/\s+/); return [m[0] || '', (m[1] || '').toUpperCase()]; };
  const [d1, m1] = sep(String(c.apoio || c.sub || '18 OUT')); const [d2, m2] = sep(String(c.texto || '28 NOV'));
  const ang = vira * 180;
  const Face: React.FC<{d: string; m: string; cor: string}> = ({d, m, cor}) => (
    <div style={{width: 640, height: 700, borderRadius: 50, background: '#f4f1ea', boxShadow: '0 50px 120px rgba(0,0,0,.65)', overflow: 'hidden', backfaceVisibility: 'hidden', position: 'absolute'}}>
      <div style={{height: 190, background: cor, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FT, fontSize: 110, color: '#fff', letterSpacing: 8}}>{m}</div>
      <div style={{textAlign: 'center', fontFamily: FT, fontSize: 380, lineHeight: 1.15, color: '#111'}}>{d}</div>
    </div>);
  return (
    <AbsoluteFill>
      <FundoVar f={f} c={c} salt={5} lista={['aurora', 'grade', 'circulos', 'liso']} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', perspective: 1800}}>
        <div style={{position: 'relative', width: 640, height: 700, transformStyle: 'preserve-3d', transform: `translateY(${(1 - s) * 200}px) scale(${0.8 + 0.2 * s}) rotateY(${ang}deg)`}}>
          <Face d={d1} m={m1} cor={VERM} />
          <div style={{position: 'absolute', inset: 0, transform: 'rotateY(180deg)', backfaceVisibility: 'hidden'}}><Face d={d2} m={m2} cor={OURO} /></div>
        </div>
      </AbsoluteFill>
      {c.rotulo && <div style={{position: 'absolute', left: 60, right: 60, top: 300, textAlign: 'center', fontFamily: 'InterX', fontSize: 56, color: '#fff', textShadow: '0 4px 30px rgba(0,0,0,.7)', opacity: ease(f, t0, t0 + 12)}}>{c.rotulo}</div>}
    </AbsoluteFill>
  );
};

const MAPA: Record<string, React.FC<CP>> = {
  palavra: CPalavra, contador: CContador, digitando: CDigitando, pergunta: CPergunta, frase: CFrase, foto: CFoto,
  parede: CParede, cards: CCards, diagrama: CDiagrama, sera: CSera, painel: CPainel, niveis: CNiveis, serifa: CSerifa, cta: CCta,
  interruptor: CInterruptor, checklist: CChecklist, calendario: CCalendario,
};
// cenas onde a narração NÃO está escrita na tela -> mostram legenda pequena
const COM_LEGENDA = new Set(['foto', 'parede', 'cards', 'diagrama', 'sera', 'contador', 'niveis', 'serifa', 'painel', 'interruptor', 'checklist', 'calendario']);

// transições (referências: Blue Ocean + @gene.digital): luz = estouro de luz dourada; saturado = tela tinge e estoura;
// foco = entra desfocada e foca; corte = corte seco já mais perto (punch-in); chicote = borrão lateral + glitch
let PESOS_TRANS: [string, number][] = [['luz', 0.34], ['foco', 0.18], ['corte', 0.18], ['saturado', 0.12], ['chicote', 0.18]];
export const tipoTrans = (c: CenaC | undefined, i: number): string => {
  if (!c || i === 0) return 'nenhuma';
  if ((c as any).transicao) return (c as any).transicao;
  const r = random('tr' + i);
  let acc = 0;
  for (const [nome, peso] of PESOS_TRANS) { acc += peso; if (r < acc) return nome; }
  return 'corte';
};

const CenaWrap: React.FC<{c: CenaC; n: number; idx: number; tin: string; tout: string}> = ({c, n, idx, tin, tout}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const Comp = MAPA[c.tipo] || CFrase;
  // entrada: tranco + zoom; saída: borrão de chicote
  const push = interpolate(f, [0, n], [1.0, 1.09]);
  const deriva = Math.sin((f + idx * 40) / 45) * 14;
  const giro = Math.sin((f + idx * 25) / 60) * 0.5;
  const entra = tin === 'corte' ? 1.08 : tin === 'chicote' || tin === 'nenhuma'
    ? interpolate(f, [0, 4], [1.18, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)})
    : interpolate(f, [0, 10], [1.05, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const sai = tout === 'chicote' ? interpolate(f, [n - 4, n], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  const foco = tin === 'foco' ? interpolate(f, [0, 9], [16, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.quad)}) : 0;
  const tremor = tin === 'chicote' && f < 5 ? (5 - f) * 3 : 0;
  const dir = idx % 2 ? 1 : -1;
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `scale(${push * entra}) rotate(${giro}deg) translate(${Math.sin(f * 7) * tremor + dir * sai * 260 + deriva}px, ${Math.cos(f * 5) * tremor}px)`,
        filter: sai > 0 || foco > 0 ? `blur(${sai * 18 + foco}px)` : undefined}}>
        <Comp c={c} f={f} fps={fps} n={n} />
      </AbsoluteFill>
      {c.etiqueta && (
        <div style={{position: 'absolute', top: 150, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: ease(f, 4, 12), transform: `translateY(${(1 - ease(f, 4, 12)) * -30}px)`}}>
          <div style={{fontFamily: 'InterX', fontSize: 38, letterSpacing: 6, textTransform: 'uppercase', color: '#fff', padding: '16px 40px', borderRadius: 60,
            background: 'rgba(255,255,255,.12)', border: `2px solid rgba(255,255,255,.35)`, boxShadow: `0 10px 40px rgba(0,0,0,.45), inset 0 0 30px rgba(${ACRGB},.18)`}}>{c.etiqueta}</div>
        </div>)}
    </AbsoluteFill>
  );
};

// sobreposição das transições (fica por cima do corte: começa ~0,25 s antes e termina ~0,35 s depois)
const CORES_SAT = ['#E8B33A', '#FF5A1F', '#B04BFF', '#2EC4B6'];
const Transicao: React.FC<{i: number; tipo: string}> = ({i, tipo}) => {
  const f = useCurrentFrame();   // corte acontece no quadro 8
  const cx = 25 + random('x' + i) * 50;
  if (tipo === 'luz' || tipo === 'saturado') {
    const branco = interpolate(f, [3, 8, 11, 17], [0, 1, 0.85, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    const vaz = interpolate(f, [0, 6, 13, 19], [0, 1, 0.8, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    const anda = f * 3;
    const cor = tipo === 'saturado' ? CORES_SAT[Math.floor(random('c' + i) * CORES_SAT.length)] : `rgb(${ACRGB})`;
    return (
      <AbsoluteFill style={{pointerEvents: 'none'}}>
        {tipo === 'saturado' && <AbsoluteFill style={{background: cor, mixBlendMode: 'color', opacity: interpolate(f, [0, 5, 9], [0, 0.85, 0], {extrapolateRight: 'clamp'})}} />}
        <AbsoluteFill style={{mixBlendMode: 'screen', opacity: vaz,
          background: `radial-gradient(ellipse 70% 55% at ${cx + anda}% ${40 + Math.sin(f / 4) * 10}%, #fff6dc 0%, ${cor} 35%, transparent 75%),
                       radial-gradient(ellipse 60% 70% at ${100 - cx - anda}% 85%, #ff7a2a 0%, rgba(255,90,40,.6) 30%, transparent 70%)`}} />
        <AbsoluteFill style={{background: '#fffaf0', opacity: branco}} />
      </AbsoluteFill>
    );
  }
  if (tipo === 'chicote') {
    if (f < 8 || f > 13) return null;
    const g = f - 8;
    return (
      <AbsoluteFill style={{pointerEvents: 'none'}}>
        {Array.from({length: 7}).map((_, k) => (
          <div key={k} style={{position: 'absolute', left: 0, right: 0, top: random(`g${i}${k}${g}`) * H, height: 20 + random(`h${i}${k}${g}`) * 90,
            background: k % 2 ? 'rgba(255,40,70,.5)' : 'rgba(40,160,255,.45)', mixBlendMode: 'screen', transform: `translateX(${(random(`d${i}${k}${g}`) - 0.5) * 200}px)`}} />
        ))}
      </AbsoluteFill>
    );
  }

  const cobre = interpolate(f, [2, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const abre = interpolate(f, [8, 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const cor2 = random('cc' + i) > 0.5 ? OURO : VERM;
  if (tipo === 'varrer') {
    const x = (cobre - 1) * W + abre * W;   // entra da esquerda cobrindo, sai pela direita
    return <AbsoluteFill style={{pointerEvents: 'none'}}><div style={{position: 'absolute', left: x, top: 0, width: W, height: H, background: cor2,
      boxShadow: `-30px 0 0 ${PRETO}, 30px 0 0 ${PRETO}`}} /></AbsoluteFill>;
  }
  if (tipo === 'cortina') {
    const h = (cobre * (1 - abre)) * (H / 2);
    return <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: h, background: PRETO, borderBottom: `8px solid ${cor2}`}} />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: h, background: PRETO, borderTop: `8px solid ${cor2}`}} />
    </AbsoluteFill>;
  }
  if (tipo === 'iris') {
    const r = (1 - cobre + abre) * 1300;
    if (r >= 1290) return null;
    return <AbsoluteFill style={{pointerEvents: 'none', background: `radial-gradient(circle at 50% 50%, transparent ${r}px, ${cor2} ${r}px, ${cor2} ${r + 14}px, ${PRETO} ${r + 14}px)`}} />;
  }
  if (tipo === 'relogio') {
    if (f < 2 || f > 14) return null;
    const bg = f < 8 ? `conic-gradient(from 0deg at 50% 50%, ${PRETO} 0deg ${cobre * 360}deg, transparent ${cobre * 360}deg)`
      : `conic-gradient(from 0deg at 50% 50%, transparent 0deg ${abre * 360}deg, ${PRETO} ${abre * 360}deg)`;
    return <AbsoluteFill style={{pointerEvents: 'none', background: bg}} />;
  }
  return null;   // 'foco' e 'corte' acontecem dentro da própria cena
};

const Legenda: React.FC<{palavras: Palavra[]; cenas: CenaC[]; t: number; bottom?: number}> = ({palavras, cenas, t, bottom = 230}) => {
  const cena = cenas.find((c) => t >= c.inicio && t < c.fim);
  if (!cena || !COM_LEGENDA.has(cena.tipo) || cena.legenda === false) return null;
  const ps = palavras.filter((p) => p.s >= cena.inicio - 0.05 && p.s < cena.fim);
  const grupos: Palavra[][] = [];
  ps.forEach((p, i) => { if (i % 3 === 0) grupos.push([]); grupos[grupos.length - 1].push(p); });
  const g = grupos.find((gr) => t >= gr[0].s - 0.05 && t <= gr[gr.length - 1].e + 0.2);
  if (!g) return null;
  return (
    <div style={{position: 'absolute', left: 70, right: 70, bottom, display: 'flex', gap: 18, flexWrap: 'wrap', justifyContent: 'center', textAlign: 'center'}}>
      {g.map((p, i) => (
        <span key={i} style={(() => { const ativa = t >= p.s - 0.03 && t < (g[i + 1] ? g[i + 1].s - 0.03 : p.e + 0.25);
          return {fontFamily: LEGF, fontWeight: 800, fontSize: 64, padding: '2px 16px', borderRadius: 14,
            background: ativa ? OURO : 'transparent', color: ativa ? TINTA : t >= p.s ? '#fff' : 'rgba(255,255,255,.45)',
            textShadow: ativa ? 'none' : '0 4px 0 rgba(0,0,0,.7), 0 0 24px rgba(0,0,0,.6)'}; })()}>{p.w.toLowerCase().replace(/[.,!?:;]$/, '')}</span>
      ))}
    </div>
  );
};


// ================= FORMATOS DE EDIÇÃO =================
// Cada vídeo usa UM formato (o planejador alterna). Muda paleta, fontes, moldura, acabamento, legenda e transições.
type Fmt = {pal: {OURO: string; VERM: string; PRETO: string; ACRGB: string; TINTA: string; VERMD: string; VERML: string; FRASEF: string; LEGF: string};
  trans: [string, number][]; legBottom: number; badge: boolean; aber?: number};
const FORMATOS: Record<string, Fmt> = {
  noir: {aber: 1, pal: {OURO: '#F5A623', VERM: '#E3242B', PRETO: '#060607', ACRGB: '245,166,35', TINTA: '#0A0A0C', VERMD: '#a5121a', VERML: '#e05a63', FRASEF: 'Mont', LEGF: 'Mont'},
    trans: [['luz', 0.34], ['foco', 0.18], ['corte', 0.18], ['saturado', 0.12], ['chicote', 0.18]], legBottom: 230, badge: true},
  celular: {aber: 0.5, pal: {OURO: '#2EE6C5', VERM: '#FF5D73', PRETO: '#07090D', ACRGB: '46,230,197', TINTA: '#04120F', VERMD: '#b32a45', VERML: '#ff8a9b', FRASEF: 'InterX', LEGF: 'InterX'},
    trans: [['foco', 0.35], ['corte', 0.35], ['luz', 0.1], ['chicote', 0.2]], legBottom: 300, badge: false},
  terminal: {aber: 0.3, pal: {OURO: '#39FF88', VERM: '#FF4D4D', PRETO: '#030806', ACRGB: '57,255,136', TINTA: '#02140A', VERMD: '#8f1f1f', VERML: '#ff7a7a', FRASEF: 'Jet', LEGF: 'Jet'},
    trans: [['corte', 0.55], ['chicote', 0.25], ['foco', 0.2]], legBottom: 250, badge: false},
  cartaz: {pal: {OURO: '#D9502E', VERM: '#B3261E', PRETO: '#0D0D0F', ACRGB: '217,80,46', TINTA: '#FFF7EC', VERMD: '#7d1a14', VERML: '#e8695a', FRASEF: 'Playfair', LEGF: 'Playfair'},
    trans: [['foco', 0.4], ['corte', 0.45], ['luz', 0.15]], legBottom: 330, badge: false},
  documentario: {aber: 0, pal: {OURO: '#FFB454', VERM: '#E4572E', PRETO: '#08090A', ACRGB: '255,180,84', TINTA: '#0A0A0C', VERMD: '#9a3418', VERML: '#f0866a', FRASEF: 'Playfair', LEGF: 'InterX'},
    trans: [['foco', 0.5], ['luz', 0.3], ['corte', 0.2]], legBottom: 260, badge: false},
  noticia: {aber: 0, pal: {OURO: '#FFD23F', VERM: '#E11D2E', PRETO: '#05070F', ACRGB: '255,210,63', TINTA: '#0A0A0C', VERMD: '#8f0f1b', VERML: '#ff6b78', FRASEF: 'InterX', LEGF: 'InterX'},
    trans: [['corte', 0.5], ['foco', 0.3], ['luz', 0.2]], legBottom: 360, badge: false},
  navegador: {aber: 0, pal: {OURO: '#4DA3FF', VERM: '#FF5C7A', PRETO: '#070A12', ACRGB: '77,163,255', TINTA: '#04101F', VERMD: '#a32a44', VERML: '#ff8fa3', FRASEF: 'InterX', LEGF: 'InterX'},
    trans: [['foco', 0.4], ['corte', 0.4], ['chicote', 0.2]], legBottom: 300, badge: false},
  story: {aber: 0, pal: {OURO: '#FF7A59', VERM: '#E1306C', PRETO: '#0A0608', ACRGB: '255,122,89', TINTA: '#1A0A0A', VERMD: '#8f1b45', VERML: '#ff7aa6', FRASEF: 'Mont', LEGF: 'Mont'},
    trans: [['corte', 0.6], ['foco', 0.25], ['luz', 0.15]], legBottom: 330, badge: false},
  hud: {aber: 0.8, pal: {OURO: '#00E5FF', VERM: '#FF3D6E', PRETO: '#02070B', ACRGB: '0,229,255', TINTA: '#021014', VERMD: '#9a1a40', VERML: '#ff7a9a', FRASEF: 'Jet', LEGF: 'Jet'},
    trans: [['chicote', 0.35], ['corte', 0.35], ['saturado', 0.3]], legBottom: 270, badge: false},
  vhs: {aber: 1, pal: {OURO: '#FFC857', VERM: '#FF4D4D', PRETO: '#07060A', ACRGB: '255,200,87', TINTA: '#0A0A0C', VERMD: '#9a2020', VERML: '#ff8080', FRASEF: 'Jet', LEGF: 'Jet'},
    trans: [['chicote', 0.5], ['corte', 0.3], ['saturado', 0.2]], legBottom: 260, badge: false},
  eletrico: {aber: 1, pal: {OURO: '#5B6CFF', VERM: '#FF2E9A', PRETO: '#05050F', ACRGB: '91,108,255', TINTA: '#FFFFFF', VERMD: '#a31a66', VERML: '#ff7ac0', FRASEF: 'Mont', LEGF: 'InterX'},
    trans: [['chicote', 0.4], ['saturado', 0.3], ['luz', 0.2], ['corte', 0.1]], legBottom: 230, badge: true},
  // identidade do AutoFlow (laranja #FF6A13 sobre #0E0E10, Stack Sans) dentro do nosso estilo de edição
  autoflow: {aber: 0.4, pal: {OURO: '#FF6A13', VERM: '#E03A00', PRETO: '#0E0E10', ACRGB: '255,106,19', TINTA: '#0E0E10', VERMD: '#9a3a0c', VERML: '#ff9a5e', FRASEF: 'StackH', LEGF: 'StackT'},
    trans: [['corte', 0.38], ['foco', 0.27], ['luz', 0.2], ['chicote', 0.15]], legBottom: 300, badge: false},
};
const aplicarFormato = (nome?: string): Fmt => {
  const F = FORMATOS[nome || 'noir'] || FORMATOS.noir;
  OURO = F.pal.OURO; VERM = F.pal.VERM; PRETO = F.pal.PRETO; ACRGB = F.pal.ACRGB; TINTA = F.pal.TINTA;
  VERMD = F.pal.VERMD; VERML = F.pal.VERML; FRASEF = F.pal.FRASEF; LEGF = F.pal.LEGF;
  PESOS_TRANS = [...F.trans.map(([n, w]) => [n, w * 0.6] as [string, number]), ['varrer', 0.1], ['cortina', 0.1], ['iris', 0.1], ['relogio', 0.1]];
  ABER = F.aber ?? 1;
  return F;
};

// cena inteira (1080x1920) reduzida e recortada dentro de uma moldura
const Encaixe: React.FC<{k: number; raio: number; children: React.ReactNode}> = ({k, raio, children}) => (
  <div style={{width: W * k, height: H * k, borderRadius: raio, overflow: 'hidden', position: 'relative', background: PRETO}}>
    <div style={{width: W, height: H, transform: `scale(${k})`, transformOrigin: 'top left', position: 'absolute', left: 0, top: 0}}>{children}</div>
  </div>
);
const Grao: React.FC<{f: number; op: number; claro?: boolean}> = ({f, op, claro}) => (
  <AbsoluteFill style={{opacity: op, mixBlendMode: claro ? 'multiply' : 'overlay', pointerEvents: 'none'}}>
    <svg width={W} height={H}><filter id={'gf' + (claro ? 'c' : 'e')}><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={f % 9} /></filter>
      <rect width="100%" height="100%" filter={`url(#gf${claro ? 'c' : 'e'})`} /></svg>
  </AbsoluteFill>
);

const Moldura: React.FC<{formato: string; f: number; durationInFrames: number; titulo?: string; numero?: number; arroba: string; children: React.ReactNode}> =
({formato, f, durationInFrames, titulo, numero, arroba, children}) => {
  const t = f / 30;
  if (formato === 'noticia') {
    const txt = `${(titulo || 'IA PARA PEQUENAS EMPRESAS').toUpperCase()}  •  SERAPHIM NEWS  •  AUTOMAÇÃO E INTELIGÊNCIA ARTIFICIAL  •  `;
    return (
      <AbsoluteFill style={{background: PRETO}}>
        {children}
        <AbsoluteFill style={{pointerEvents: 'none', background: 'linear-gradient(180deg, rgba(0,0,0,.45), transparent 16%, transparent 76%, rgba(0,0,0,.7))'}} />
        <div style={{position: 'absolute', top: 70, left: 50, display: 'flex', alignItems: 'center', gap: 16}}>
          <div style={{background: VERM, color: '#fff', fontFamily: 'InterX', fontSize: 42, padding: '8px 22px', borderRadius: 8, letterSpacing: 2, opacity: Math.floor(f / 18) % 2 ? 0.8 : 1}}>● AO VIVO</div>
          <div style={{background: '#fff', color: '#111', fontFamily: 'InterX', fontSize: 42, padding: '8px 22px', borderRadius: 8}}>SERAPHIM NEWS</div>
        </div>
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 190, display: 'flex', alignItems: 'stretch', height: 112, boxShadow: '0 10px 40px rgba(0,0,0,.6)'}}>
          <div style={{background: VERM, color: '#fff', fontFamily: 'InterX', fontSize: 40, padding: '0 34px', display: 'flex', alignItems: 'center'}}>IA</div>
          <div style={{flex: 1, background: 'linear-gradient(90deg,#0b2a66,#123a8f)', color: '#fff', fontFamily: 'InterX', fontSize: 46, padding: '0 34px', display: 'flex', alignItems: 'center', overflow: 'hidden', whiteSpace: 'nowrap'}}>
            {(titulo || '').slice(0, 34)}</div>
        </div>
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 100, height: 70, background: OURO, overflow: 'hidden', display: 'flex', alignItems: 'center'}}>
          <div style={{whiteSpace: 'nowrap', fontFamily: 'InterX', fontSize: 38, color: '#111', transform: `translateX(${-(f * 5) % 1700}px)`}}>{txt + txt + txt}</div>
        </div>
      </AbsoluteFill>
    );
  }
  if (formato === 'navegador') {
    const k = 0.86;
    return (
      <AbsoluteFill style={{background: `radial-gradient(circle at ${25 + Math.sin(f / 55) * 15}% 15%, ${OURO}66, transparent 50%), radial-gradient(circle at 85% ${80 + Math.cos(f / 50) * 10}%, #7a5cff55, transparent 55%), #070A12`}}>
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
          <div style={{borderRadius: 34, overflow: 'hidden', background: '#10141d', boxShadow: '0 60px 140px rgba(0,0,0,.75), 0 0 0 2px #2b3342'}}>
            <div style={{height: 150, background: '#1a2030', padding: '16px 28px 0', position: 'relative'}}>
              <div style={{display: 'flex', gap: 14, alignItems: 'center'}}>
                {['#ff5f56', '#ffbd2e', '#27c93f'].map((c) => <div key={c} style={{width: 20, height: 20, borderRadius: 10, background: c}} />)}
                <div style={{marginLeft: 24, background: '#10141d', borderRadius: '16px 16px 0 0', padding: '12px 30px', fontFamily: 'InterM', fontSize: 28, color: '#cfd6e6'}}>● seraphim · post {String(numero ?? 1).padStart(2, '0')}</div>
              </div>
              <div style={{position: 'absolute', left: 28, right: 28, bottom: 12, height: 56, borderRadius: 28, background: '#10141d', display: 'flex', alignItems: 'center', padding: '0 26px', fontFamily: 'InterM', fontSize: 28, color: '#8fa0bd'}}>
                🔒 seraphim.ia/{String((titulo || 'post').toLowerCase().replace(/[^a-z0-9]+/g, '-')).slice(0, 26)}</div>
            </div>
            <Encaixe k={k} raio={0}>{children}</Encaixe>
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }
  if (formato === 'story') {
    const seg = 6, prog = f / durationInFrames;
    return (
      <AbsoluteFill style={{background: PRETO}}>
        {children}
        <AbsoluteFill style={{pointerEvents: 'none', background: 'linear-gradient(180deg, rgba(0,0,0,.6), transparent 14%, transparent 84%, rgba(0,0,0,.65))'}} />
        <div style={{position: 'absolute', top: 36, left: 28, right: 28, display: 'flex', gap: 8}}>
          {Array.from({length: seg}).map((_, i) => {
            const v = Math.max(0, Math.min(1, prog * seg - i));
            return <div key={i} style={{flex: 1, height: 7, borderRadius: 4, background: 'rgba(255,255,255,.35)', overflow: 'hidden'}}><div style={{width: `${v * 100}%`, height: '100%', background: '#fff'}} /></div>;
          })}
        </div>
        <div style={{position: 'absolute', top: 70, left: 36, display: 'flex', alignItems: 'center', gap: 20}}>
          <div style={{padding: 5, borderRadius: 50, background: `linear-gradient(135deg, ${OURO}, ${VERM})`}}>
            <Img src={staticFile('marca/icone.png')} style={{width: 88, height: 88, borderRadius: 44, border: '4px solid #000'}} /></div>
          <div style={{fontFamily: 'InterX', fontSize: 40, color: '#fff'}}>{arroba.replace('@', '')} <span style={{fontFamily: 'InterM', color: 'rgba(255,255,255,.7)', fontSize: 32}}>· agora</span></div>
        </div>
        <div style={{position: 'absolute', left: 40, right: 40, bottom: 70, display: 'flex', alignItems: 'center', gap: 24}}>
          <div style={{flex: 1, height: 92, borderRadius: 46, border: '3px solid rgba(255,255,255,.75)', color: 'rgba(255,255,255,.85)', fontFamily: 'InterM', fontSize: 36, display: 'flex', alignItems: 'center', padding: '0 36px'}}>Enviar mensagem</div>
          <div style={{fontSize: 62, color: '#fff'}}>♡</div><div style={{fontSize: 56, color: '#fff'}}>➤</div>
        </div>
      </AbsoluteFill>
    );
  }
  if (formato === 'hud') {
    const L = (st: React.CSSProperties) => <div style={{position: 'absolute', width: 120, height: 120, border: `5px solid ${OURO}`, ...st}} />;
    const sy = (f * 9) % H;
    return (
      <AbsoluteFill style={{background: PRETO}}>
        {children}
        <AbsoluteFill style={{background: `${OURO}`, mixBlendMode: 'soft-light', opacity: 0.18, pointerEvents: 'none'}} />
        <AbsoluteFill style={{pointerEvents: 'none', backgroundImage: `linear-gradient(${OURO}22 1px, transparent 1px), linear-gradient(90deg, ${OURO}22 1px, transparent 1px)`, backgroundSize: '90px 90px'}} />
        <div style={{position: 'absolute', left: 0, right: 0, top: sy, height: 6, background: `linear-gradient(90deg, transparent, ${OURO}, transparent)`, opacity: 0.55, boxShadow: `0 0 30px ${OURO}`}} />
        {L({top: 40, left: 40, borderRight: 'none', borderBottom: 'none'})}{L({top: 40, right: 40, borderLeft: 'none', borderBottom: 'none'})}
        {L({bottom: 40, left: 40, borderRight: 'none', borderTop: 'none'})}{L({bottom: 40, right: 40, borderLeft: 'none', borderTop: 'none'})}
        <div style={{position: 'absolute', top: 70, left: 190, right: 190, display: 'flex', justifyContent: 'space-between', fontFamily: 'Jet', fontWeight: 800, fontSize: 30, color: OURO}}>
          <span>SYS//SERAPHIM</span><span style={{opacity: Math.floor(f / 12) % 2 ? 0.3 : 1}}>▸ LIVE</span></div>
        <div style={{position: 'absolute', bottom: 70, left: 190, right: 190, display: 'flex', justifyContent: 'space-between', fontFamily: 'Jet', fontWeight: 800, fontSize: 28, color: `${OURO}cc`}}>
          <span>LAT -15.79 · LON -47.88</span><span>T+{t.toFixed(1)}s</span></div>
      </AbsoluteFill>
    );
  }
  if (formato === 'vhs') {
    const trk = (f * 11) % H;
    return (
      <AbsoluteFill style={{background: PRETO}}>
        <AbsoluteFill style={{transform: `translateX(${Math.sin(f * 1.7) * (f % 40 < 3 ? 14 : 2)}px)`}}>{children}</AbsoluteFill>
        <AbsoluteFill style={{pointerEvents: 'none', background: 'linear-gradient(90deg, rgba(255,0,60,.10), transparent 30%, transparent 70%, rgba(0,120,255,.10))', mixBlendMode: 'screen'}} />
        <AbsoluteFill style={{pointerEvents: 'none', backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,.28) 0 3px, transparent 3px 6px)'}} />
        <div style={{position: 'absolute', left: 0, right: 0, top: trk, height: 90, background: 'rgba(255,255,255,.10)', mixBlendMode: 'overlay', filter: 'blur(2px)'}} />
        <div style={{position: 'absolute', left: 0, right: 0, bottom: (f * 3) % 260, height: 26, background: 'rgba(255,255,255,.18)', transform: `translateX(${Math.sin(f) * 40}px)`}} />
        <Grao f={f} op={0.16} />
        <div style={{position: 'absolute', top: 70, left: 60, fontFamily: 'Jet', fontWeight: 800, fontSize: 56, color: '#fff', textShadow: '3px 0 rgba(255,0,60,.7), -3px 0 rgba(0,160,255,.7)'}}>▶ PLAY</div>
        <div style={{position: 'absolute', top: 80, right: 60, fontFamily: 'Jet', fontWeight: 800, fontSize: 40, color: '#fff', textShadow: '3px 0 rgba(255,0,60,.7)'}}>SP {Math.floor(t / 60)}:{String(Math.floor(t % 60)).padStart(2, '0')}</div>
        <div style={{position: 'absolute', bottom: 60, right: 60, fontFamily: 'Jet', fontWeight: 800, fontSize: 40, color: OURO, textShadow: '3px 0 rgba(255,0,60,.6)'}}>15 OUT 2026</div>
      </AbsoluteFill>
    );
  }
  if (formato === 'celular') {
    const k = 0.86;
    return (
      <AbsoluteFill style={{background: `radial-gradient(circle at ${30 + Math.sin(f / 50) * 20}% ${20 + Math.cos(f / 60) * 10}%, ${OURO}55, transparent 50%), radial-gradient(circle at ${75 + Math.cos(f / 45) * 15}% 85%, ${VERM}44, transparent 55%), #05070B`}}>
        <Reticula cor="#fff" op={0.05} tam={22} />
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
          <div style={{padding: 16, borderRadius: 120, background: '#0c0e12', boxShadow: `0 0 0 3px #2a2e36, 0 0 120px ${OURO}44, 0 60px 120px rgba(0,0,0,.7)`, position: 'relative'}}>
            <Encaixe k={k} raio={104}>{children}</Encaixe>
            <div style={{position: 'absolute', top: 34, left: '50%', transform: 'translateX(-50%)', width: 210, height: 52, borderRadius: 26, background: '#000'}} />
            <div style={{position: 'absolute', bottom: 28, left: '50%', transform: 'translateX(-50%)', width: 260, height: 9, borderRadius: 5, background: 'rgba(255,255,255,.55)'}} />
          </div>
        </AbsoluteFill>
        <div style={{position: 'absolute', top: 60, left: 0, right: 0, textAlign: 'center', fontFamily: 'InterX', fontSize: 34, color: '#9aa3b2', letterSpacing: 3}}>{arroba}</div>
      </AbsoluteFill>
    );
  }
  if (formato === 'terminal') {
    const k = 0.86;
    return (
      <AbsoluteFill style={{background: '#030806'}}>
        <AbsoluteFill style={{backgroundImage: 'linear-gradient(rgba(57,255,136,.07) 1px, transparent 1px), linear-gradient(90deg, rgba(57,255,136,.07) 1px, transparent 1px)',
          backgroundSize: '60px 60px', backgroundPosition: `0 ${f}px`}} />
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
          <div style={{borderRadius: 22, overflow: 'hidden', border: `2px solid ${OURO}88`, boxShadow: `0 0 90px ${OURO}33, 0 50px 120px rgba(0,0,0,.8)`, background: '#071009'}}>
            <div style={{height: 64, display: 'flex', alignItems: 'center', gap: 14, padding: '0 24px', background: '#0d1a11', borderBottom: `1px solid ${OURO}44`}}>
              {['#ff5f56', '#ffbd2e', '#27c93f'].map((c) => <div key={c} style={{width: 20, height: 20, borderRadius: 10, background: c}} />)}
              <div style={{marginLeft: 14, fontFamily: 'Jet', fontWeight: 800, fontSize: 28, color: `${OURO}cc`}}>seraphim@ia:~/post_{String(numero ?? 1).padStart(2, '0')} — zsh</div>
              <div style={{marginLeft: 'auto', fontFamily: 'Jet', fontWeight: 800, fontSize: 26, color: `${OURO}99`}}>{Math.floor(t / 60)}:{String(Math.floor(t % 60)).padStart(2, '0')}</div>
            </div>
            <Encaixe k={k} raio={0}>{children}</Encaixe>
          </div>
        </AbsoluteFill>
        <AbsoluteFill style={{pointerEvents: 'none', backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,.35) 0 2px, transparent 2px 4px)', opacity: 0.5}} />
      </AbsoluteFill>
    );
  }
  if (formato === 'cartaz') {
    const k = 0.80;
    return (
      <AbsoluteFill style={{background: '#EDE6D8'}}>
        <Grao f={Math.floor(f / 3)} op={0.35} claro />
        <div style={{position: 'absolute', top: 58, left: 80, right: 80, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          borderBottom: '3px solid #1a1a1a', paddingBottom: 12, fontFamily: 'Playfair', color: '#1a1a1a'}}>
          <span style={{fontSize: 50, fontWeight: 700, letterSpacing: 4}}>SERAPHIM</span>
          <span style={{fontSize: 28, fontStyle: 'italic'}}>edição IA · nº {String(numero ?? 1).padStart(2, '0')}</span>
        </div>
        <AbsoluteFill style={{alignItems: 'center', top: 128}}>
          <div style={{padding: 34, background: '#FAF7F0', boxShadow: '0 30px 70px rgba(40,30,10,.35), 0 0 0 2px #d8cfbc', transform: `rotate(${Math.sin(f / 90) * 0.35}deg)`}}>
            <Encaixe k={k} raio={4}>{children}</Encaixe>
          </div>
        </AbsoluteFill>
        <div style={{position: 'absolute', left: 90, right: 90, bottom: 110, fontFamily: 'Playfair', fontStyle: 'italic', fontSize: 40, color: '#2a2a2a', display: 'flex', justifyContent: 'space-between'}}>
          <span>fig. {String(numero ?? 1).padStart(2, '0')} — {(titulo || '').slice(0, 46)}</span><span>{arroba}</span>
        </div>
      </AbsoluteFill>
    );
  }
  if (formato === 'documentario') {
    return (
      <AbsoluteFill style={{background: PRETO}}>
        {children}
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(255,150,60,.16), rgba(20,90,110,.20))', mixBlendMode: 'soft-light', pointerEvents: 'none'}} />
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, transparent 52%, rgba(0,0,0,.55) 100%)', pointerEvents: 'none'}} />
        <Grao f={f} op={0.22} />
        <div style={{position: 'absolute', top: 0, left: 0, right: 0, height: 150, background: '#000'}} />
        <div style={{position: 'absolute', bottom: 0, left: 0, right: 0, height: 150, background: '#000'}} />
        <div style={{position: 'absolute', top: 54, left: 56, right: 56, display: 'flex', justifyContent: 'space-between', fontFamily: 'Jet', fontWeight: 800, fontSize: 32, color: '#e8e8e8'}}>
          <span style={{color: '#ff4040', opacity: Math.floor(f / 15) % 2 ? 0.25 : 1}}>● REC</span>
          <span>{`00:${String(Math.floor(t)).padStart(2, '0')}:${String(Math.floor((t % 1) * 30)).padStart(2, '0')}`}</span>
        </div>
        <div style={{position: 'absolute', bottom: 56, left: 56, fontFamily: 'Playfair', fontStyle: 'italic', fontSize: 36, color: '#d8d0c4'}}>{(titulo || '').slice(0, 52)}</div>
      </AbsoluteFill>
    );
  }
  if (formato === 'eletrico') {
    const h = (f * 2) % 360;
    return (
      <AbsoluteFill style={{background: PRETO}}>
        {children}
        <AbsoluteFill style={{pointerEvents: 'none', boxShadow: `inset 0 0 0 10px ${OURO}, inset 0 0 120px 20px ${VERM}66, inset 0 0 220px 40px ${OURO}55`, opacity: 0.75 + 0.25 * Math.sin(f / 8)}} />
        <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'screen', opacity: 0.18, background: `linear-gradient(${h}deg, ${OURO}, transparent 40%, ${VERM})`}} />
        <Grao f={f} op={0.07} />
      </AbsoluteFill>
    );
  }
  return <>{children}<Acabamento f={f} /></>;
};

export const SeraphimCortes: React.FC<PropsC> = (props) => {
  useFontes();
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const t = frame / fps;
  const formato = FORMATOS[props.formato || 'noir'] ? (props.formato || 'noir') : 'noir';
  const FM = aplicarFormato(formato);
  SEED = hash(`${props.titulo || ''}${props.numero || ''}${props.cenas.length}`);
  FT = FTS[hash(SEED + 'ft') % FTS.length]; FW = FWS[hash(SEED + 'fw') % FWS.length]; ARROBA = props.arroba || ARROBA;
  if (formato === 'autoflow') { FT = 'Anton'; FW = 'StackH'; }   // AutoFlow: impacto em Anton, apoio em Stack Sans
  if (FRASEF === 'Mont') FRASEF = FW; else if (FRASEF === 'Anton') FRASEF = FT;
  if (LEGF === 'Mont') LEGF = ['Mont', 'Sora', 'Mont', 'Syne'][hash(SEED + 'lg') % 4];
  if (SEED % 3 === 0) ABER = Math.min(ABER, 0.4);
  return (
    <AbsoluteFill style={{background: PRETO}}>
      <Moldura formato={formato} f={frame} durationInFrames={durationInFrames} titulo={props.titulo} numero={props.numero} arroba={props.arroba}>
      {props.cenas.map((c, i) => {
        const from = Math.round(c.inicio * fps);
        const dur = Math.max(1, Math.round((c.fim - c.inicio) * fps));
        return (
          <React.Fragment key={i}>
            <Sequence from={from} durationInFrames={dur}><CenaWrap c={c} n={dur} idx={i} tin={tipoTrans(c, i)} tout={tipoTrans(props.cenas[i + 1], i + 1)} /></Sequence>
            {i > 0 && <Sequence from={Math.max(0, from - 8)} durationInFrames={20}><Transicao i={i} tipo={tipoTrans(c, i)} /></Sequence>}
          </React.Fragment>
        );
      })}
      </Moldura>
      <Legenda palavras={props.palavras} cenas={props.cenas} t={t} bottom={FM.legBottom} />
      {/* assinatura sutil da marca */}
      <div style={{position: 'absolute', top: 0, left: 0, height: 8, width: `${(frame / durationInFrames) * 100}%`, background: OURO}} />
      {FM.badge && <div style={{position: 'absolute', left: 50, bottom: 60, display: 'flex', alignItems: 'center', gap: 16, opacity: 0.9, background: 'rgba(0,0,0,.45)', padding: '8px 22px 8px 8px', borderRadius: 40}}>
        <Img src={staticFile('marca/icone.png')} style={{width: 60, height: 60, borderRadius: 30, boxShadow: `0 0 0 3px ${OURO}`}} />
        <span style={{fontFamily: 'InterM', fontSize: 34, color: '#e8e8e8', textShadow: '0 2px 8px rgba(0,0,0,.8)'}}>{props.arroba}</span>
      </div>}
      {props.audio && <Audio src={staticFile(props.audio)} />}
      {props.batida && <Audio src={staticFile(props.batida)} volume={(props as any).trilha_mix ? 1 : props.audio ? 0.12 : 0.7} />}
      {props.sfx && props.cenas.map((c, i) => (
        <React.Fragment key={'s' + i}>
          {i > 0 && ['luz', 'saturado', 'chicote', 'varrer', 'cortina', 'iris', 'relogio'].includes(tipoTrans(c, i)) && <Sequence from={Math.max(0, Math.round((c.inicio - 0.25) * fps))}>
            <Audio src={staticFile('sfx/whoosh.wav')} volume={tipoTrans(c, i) === 'chicote' ? 0.4 : 0.28} /></Sequence>}
          {['palavra', 'contador', 'painel'].includes(c.tipo) && <Sequence from={Math.round(c.inicio * fps)}><Audio src={staticFile('sfx/impacto.wav')} volume={0.45} /></Sequence>}
          {(c.marcas || []).map((m, k) => (k === 0 && c.tipo === 'palavra') ? null : (
            <Sequence key={'m' + k} from={Math.round((c.inicio + m) * fps) + (c.tipo === 'checklist' ? 6 : 0)}>
              <Audio src={staticFile(c.tipo === 'checklist' ? 'sfx/tic.wav' : c.tipo === 'palavra' ? 'sfx/impacto.wav' : 'sfx/pop.wav')} volume={c.tipo === 'palavra' ? 0.3 : 0.35} />
            </Sequence>))}
          {c.tipo === 'interruptor' && <Sequence from={Math.round((c.inicio + (c.fim - c.inicio) * (c.valor ?? 0.5)) * fps)}><Audio src={staticFile('sfx/clique.wav')} volume={0.5} /></Sequence>}
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
};
