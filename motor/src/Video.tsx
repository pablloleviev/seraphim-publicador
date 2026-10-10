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
  tema?: string;                                // identidade visual do vídeo (ver TEMAS)
};

// ---------- marca ----------
const C = {preto: '#0A0A0C', ouro: '#F5A623', ouro2: '#FFC94D', branco: '#F5F5F7', prata: '#A1A1AA'};
const W = 1080, H = 1920;

// ---------- temas: cada vídeo tem identidade própria; a Seraphim aparece de forma sutil
// (fio/realce dourado, ícone, barra de progresso) mesmo quando a paleta principal é outra.
type Paleta = {bg: string; texto: string; destaque: string; apoio: string};
export type Tema = Paleta & {
  id: string; brilho: string; marca: string; alt: Paleta;
  fonte: string; k: number; caixa: boolean; alinhar: 'center' | 'left';
  textura: 'pontos' | 'grade' | 'linhas' | 'diagonal' | 'ruido' | 'nenhuma';
  entrada: 'pop' | 'subir' | 'maquina' | 'mascara';
  aberracao: boolean; tremor: boolean;
  legenda: 'contorno' | 'pilula' | 'sublinhado'; legendaFonte: string;
  numero: 'vazado' | 'solido' | 'cartao';
};
const base = {alinhar: 'center' as const, aberracao: false, tremor: false, legendaFonte: 'InterX', caixa: true};
export const TEMAS: Record<string, Tema> = {
  noir: {...base, id: 'noir', bg: C.preto, texto: C.branco, destaque: C.ouro, apoio: C.prata, brilho: C.ouro, marca: C.ouro,
    alt: {bg: C.branco, texto: C.preto, destaque: '#B86E00', apoio: '#3f3f46'},
    fonte: 'Anton', k: 0.47, textura: 'pontos', entrada: 'pop', aberracao: true, tremor: true, legenda: 'contorno', numero: 'vazado'},
  editorial: {...base, id: 'editorial', bg: '#F1ECE3', texto: '#161412', destaque: '#B5651D', apoio: '#5b544c', brilho: '#E2B66B', marca: '#C08A2E',
    alt: {bg: '#161412', texto: '#F1ECE3', destaque: '#E2B66B', apoio: '#a8a196'},
    fonte: 'DMSerif', k: 0.5, caixa: false, alinhar: 'left', textura: 'linhas', entrada: 'mascara', legenda: 'sublinhado', numero: 'solido'},
  terminal: {...base, id: 'terminal', bg: '#06110C', texto: '#E6FFF1', destaque: '#3DFFA8', apoio: '#7FA897', brilho: '#3DFFA8', marca: C.ouro,
    alt: {bg: '#E6FFF1', texto: '#06110C', destaque: '#00895A', apoio: '#2f5546'},
    fonte: 'Jet', k: 0.68, alinhar: 'left', textura: 'grade', entrada: 'maquina', legenda: 'pilula', legendaFonte: 'Jet', numero: 'cartao'},
  meianoite: {...base, id: 'meianoite', bg: '#0A1430', texto: '#F2F6FF', destaque: '#7CC4FF', apoio: '#93A3C8', brilho: '#3D6BFF', marca: C.ouro,
    alt: {bg: '#F2F6FF', texto: '#0A1430', destaque: '#1F5FD6', apoio: '#43507a'},
    fonte: 'Space', k: 0.66, textura: 'ruido', entrada: 'subir', legenda: 'contorno', numero: 'vazado'},
  brutal: {...base, id: 'brutal', bg: '#FFD43B', texto: '#0A0A0C', destaque: '#FFFFFF', apoio: '#2a2a2a', brilho: '#FFFFFF', marca: '#0A0A0C',
    alt: {bg: '#0A0A0C', texto: '#FFD43B', destaque: '#FFFFFF', apoio: '#cfcfcf'},
    fonte: 'Archivo', k: 0.76, textura: 'diagonal', entrada: 'pop', tremor: true, legenda: 'pilula', numero: 'cartao'},
  vinho: {...base, id: 'vinho', bg: '#250B12', texto: '#F7ECDF', destaque: '#E8B77A', apoio: '#B99A90', brilho: '#7A1E30', marca: '#E8B77A',
    alt: {bg: '#F7ECDF', texto: '#250B12', destaque: '#8A2A3C', apoio: '#6b4e47'},
    fonte: 'Playfair', k: 0.55, caixa: false, textura: 'nenhuma', entrada: 'mascara', legenda: 'sublinhado', numero: 'solido'},
  eletrico: {...base, id: 'eletrico', bg: '#FAFAFA', texto: '#0A0A0C', destaque: '#2F5BFF', apoio: '#55555c', brilho: '#2F5BFF', marca: C.ouro,
    alt: {bg: '#2F5BFF', texto: '#FFFFFF', destaque: '#FFD43B', apoio: '#dfe6ff'},
    fonte: 'Montserrat', k: 0.74, alinhar: 'left', textura: 'grade', entrada: 'subir', legenda: 'pilula', numero: 'solido'},
  grafite: {...base, id: 'grafite', bg: '#1B1B1E', texto: '#F5F5F7', destaque: '#FF6A3D', apoio: '#9a9aa2', brilho: '#FF6A3D', marca: C.ouro,
    alt: {bg: '#F5F5F7', texto: '#1B1B1E', destaque: '#E0461A', apoio: '#52525b'},
    fonte: 'Bebas', k: 0.4, textura: 'diagonal', entrada: 'pop', aberracao: true, tremor: true, legenda: 'contorno', numero: 'vazado'},
  ultravioleta: {...base, id: 'ultravioleta', bg: '#120A26', texto: '#F4F0FF', destaque: '#B69CFF', apoio: '#9b91bd', brilho: '#7B4DFF', marca: C.ouro,
    alt: {bg: '#F4F0FF', texto: '#120A26', destaque: '#6A3DF0', apoio: '#4d4470'},
    fonte: 'Space', k: 0.66, textura: 'pontos', entrada: 'subir', aberracao: true, legenda: 'pilula', numero: 'cartao'},
};
const TemaCtx = React.createContext<Tema>(TEMAS.noir);
const useTema = () => React.useContext(TemaCtx);
const rgba = (hex: string, a: number) => {
  const h = hex.replace('#', '');
  const n = parseInt(h.length === 3 ? h.split('').map((x) => x + x).join('') : h, 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};
const claro = (hex: string) => {
  const h = hex.replace('#', ''); const n = parseInt(h, 16);
  return (0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) > 150;
};
const paletaDe = (t: Tema, alt: boolean): Paleta => (alt ? t.alt : t);

// ---------- fontes ----------
const fontesCSS = `
@font-face{font-family:'Anton';src:url('${staticFile('fontes/anton.ttf')}')}
@font-face{font-family:'InterX';font-weight:800;src:url('${staticFile('fontes/inter800.ttf')}')}
@font-face{font-family:'InterM';font-weight:500;src:url('${staticFile('fontes/inter500.ttf')}')}
`;
const EXTRAS: [string, string, string?][] = [
  ['Bebas', 'bebas.ttf'], ['Archivo', 'archivo.ttf'], ['DMSerif', 'dmserif.ttf'],
  ['Space', 'spacegrotesk.ttf', '700'], ['Jet', 'jetbrains.ttf', '800'], ['Playfair', 'playfair.ttf', '900'], ['Montserrat', 'montserrat.ttf', '900'],
];
const useFontes = () => {
  const [h] = React.useState(() => delayRender('fontes'));
  React.useEffect(() => {
    const fontes = [
      new FontFace('Anton', `url(${staticFile('fontes/anton.ttf')})`),
      new FontFace('InterX', `url(${staticFile('fontes/inter800.ttf')})`, {weight: '800'}),
      new FontFace('InterM', `url(${staticFile('fontes/inter500.ttf')})`, {weight: '500'}),
      ...EXTRAS.map(([n, f, w]) => new FontFace(n, `url(${staticFile('fontes/' + f)})`, w ? {weight: w} : {})),
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
    trecho.split(' ').filter(Boolean).forEach((t) => {
      // pontuação solta ("?", ",", ".") gruda na palavra anterior: "BASTA?" e não "BASTA ?"
      if (/^[?!.,:;]+$/.test(t) && out.length) out[out.length - 1].t += t;
      else out.push({t, ouro: i % 2 === 1});
    }));
  return out;
};
const tamanhoTitulo = (linhas: string[], max: number, k = 0.47) => {
  const maior = Math.max(...linhas.map((l) => l.replace(/\*/g, '').length), 1);
  return Math.min(max, Math.floor((W - 150) / (maior * k)));
};
const SIGLAS = /^(IA|AI|PC|TI|CRM|ERP|API|PDF|SEO|ROI|KPI|CNPJ|CPF|PIX|WHATSAPP|SAAS|APP|GPT|CHATGPT)([?!.,:;]*)$/;
const fraseCase = (w: string, primeira: boolean) => {
  const m = w.toUpperCase().match(SIGLAS);
  if (m) return m[1] === 'WHATSAPP' ? 'WhatsApp' + m[2] : m[1] === 'CHATGPT' ? 'ChatGPT' + m[2] : m[1] === 'SAAS' ? 'SaaS' + m[2] : w.toUpperCase();
  const l = w.toLowerCase();
  return primeira ? l.charAt(0).toUpperCase() + l.slice(1) : l;
};
const PESO: Record<string, number> = {Space: 700, Jet: 800, Playfair: 900, Montserrat: 900};

// ---------- fundo ----------
const Fundo: React.FC<{branco: boolean; raios: boolean; f: number}> = ({branco, raios, f}) => {
  const T = useTema();
  const P = paletaDe(T, branco);
  const luz = claro(P.bg);
  const tinta = luz ? 'rgba(10,10,12,' : 'rgba(255,255,255,';
  const brilho = branco ? P.destaque : T.brilho;
  const mascara = 'radial-gradient(ellipse at 85% 8%, #000 0%, transparent 60%)';
  let textura: React.ReactNode = null;
  if (T.textura === 'pontos') textura = <AbsoluteFill style={{backgroundImage: `radial-gradient(${tinta}.12) 2.2px, transparent 2.6px)`,
    backgroundSize: '24px 24px', backgroundPosition: `${f * 0.4}px ${f * 0.2}px`, maskImage: mascara, WebkitMaskImage: mascara}} />;
  if (T.textura === 'grade') textura = <AbsoluteFill style={{backgroundImage: `linear-gradient(${tinta}.07) 2px, transparent 2px), linear-gradient(90deg, ${tinta}.07) 2px, transparent 2px)`,
    backgroundSize: '90px 90px', backgroundPosition: `0 ${f * 0.6}px`}} />;
  if (T.textura === 'linhas') textura = <AbsoluteFill style={{backgroundImage: `repeating-linear-gradient(0deg, ${tinta}.06) 0 2px, transparent 2px 64px)`}} />;
  if (T.textura === 'diagonal') textura = <AbsoluteFill style={{backgroundImage: `repeating-linear-gradient(135deg, ${tinta}.07) 0 18px, transparent 18px 46px)`,
    backgroundPosition: `${f * 1.2}px 0`, maskImage: 'linear-gradient(180deg, #000, transparent 70%)', WebkitMaskImage: 'linear-gradient(180deg, #000, transparent 70%)'}} />;
  if (T.textura === 'ruido') textura = <AbsoluteFill style={{background: `radial-gradient(circle at ${30 + 10 * Math.sin(f / 40)}% 70%, ${rgba(brilho, .22)}, transparent 50%)`}} />;
  return (
    <AbsoluteFill style={{background: P.bg}}>
      <AbsoluteFill style={{background: `radial-gradient(circle at 85% 8%, ${rgba(brilho, luz ? .20 : .30)}, transparent 42%), radial-gradient(circle at 10% 92%, ${rgba(brilho, luz ? .08 : .12)}, transparent 40%)`}} />
      {raios && (
        <AbsoluteFill style={{
          background: `repeating-conic-gradient(from ${f * 0.35}deg at 50% 42%, ${rgba(brilho, .10)} 0deg 7.5deg, transparent 7.5deg 15deg)`,
          maskImage: 'radial-gradient(circle at 50% 42%, #000 15%, transparent 75%)',
          WebkitMaskImage: 'radial-gradient(circle at 50% 42%, #000 15%, transparent 75%)',
        }} />
      )}
      {textura}
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,${luz ? .08 : .55}) 100%)`}} />
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
const Titulo: React.FC<{linhas: string[]; tam: number; cor: string; f: number; fps: number; atraso?: number; destaque?: string; alinhar?: 'center' | 'left'}> = ({linhas, tam, cor, f, fps, atraso = 0, destaque, alinhar}) => {
  const T = useTema();
  let idx = 0;
  let ultimaPalavra = '';
  const al = alinhar || T.alinhar;
  const ab = T.aberracao ? interpolate(f, [0, 10], [10, 3], {extrapolateRight: 'clamp'}) : 0;
  const dest = destaque || T.destaque;
  const luz = claro(cor) === false;  // texto escuro = fundo claro
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: al === 'left' ? 'flex-start' : 'center', gap: tam * 0.04, width: '100%'}}>
      {linhas.map((l, li) => (
        <div key={li} style={{display: 'flex', gap: tam * 0.22, justifyContent: al === 'left' ? 'flex-start' : 'center', flexWrap: 'nowrap'}}>
          {palavrasDe(l).map((p, pi) => {
            const anterior = ultimaPalavra; ultimaPalavra = p.t;
            const d = atraso + idx++ * (T.entrada === 'maquina' ? 4 : 3);
            const s = spring({frame: f - d, fps, config: {damping: 11, stiffness: 170, mass: 0.6}});
            const c = p.ouro ? dest : cor;
            const txt = T.caixa ? p.t.toUpperCase() : fraseCase(p.t, (li === 0 && pi === 0) || /[.?!]$/.test(anterior));
            let transform = '', opacity: number = 1, filter = 'none', clip: string | undefined, mostrar = txt;
            if (T.entrada === 'pop') {
              const blur = interpolate(f - d, [0, 6], [10, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
              transform = `scale(${interpolate(s, [0, 1], [1.7, 1])}) translateY(${interpolate(s, [0, 1], [30, 0])}px)`;
              opacity = interpolate(s, [0, 0.4], [0, 1], {extrapolateRight: 'clamp'}); filter = `blur(${blur}px)`;
            } else if (T.entrada === 'subir') {
              transform = `translateY(${interpolate(s, [0, 1], [tam * 0.6, 0])}px)`;
              opacity = interpolate(s, [0, 0.5], [0, 1], {extrapolateRight: 'clamp'});
            } else if (T.entrada === 'mascara') {
              const k = interpolate(f - d, [0, 9], [100, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
              clip = `inset(${k}% 0 0 0)`; transform = `translateY(${k * 0.25}px)`;
            } else {
              const n = Math.max(0, Math.min(txt.length, Math.floor((f - d) / 1.2)));
              mostrar = txt.slice(0, n); opacity = n > 0 ? 1 : 0;
            }
            const sombra = ab ? `${-ab}px 0 rgba(255,40,70,.85), ${ab}px 0 rgba(40,140,255,.85)` : '';
            const glow = T.id === 'brutal' ? `${tam * 0.05}px ${tam * 0.05}px 0 #0A0A0C` : p.ouro && !luz ? `0 0 40px ${rgba(dest, .45)}` : '';
            return (
              <span key={pi} style={{
                fontFamily: T.fonte, fontWeight: PESO[T.fonte] || 400, fontSize: tam, lineHeight: 1.05, color: c,
                letterSpacing: T.fonte === 'Jet' ? -2 : 1, display: 'inline-block', position: 'relative',
                transform, opacity, filter, clipPath: clip,
                textShadow: [sombra, glow].filter(Boolean).join(', ') || 'none',
              }}>{mostrar}{T.entrada === 'maquina' && mostrar.length < txt.length && mostrar.length > 0 ? <span style={{color: T.marca}}>▍</span> : null}
                {p.ouro && T.legenda === 'sublinhado' && (
                  <span style={{position: 'absolute', left: 0, bottom: -tam * 0.06, height: Math.max(6, tam * 0.06), background: T.marca,
                    width: `${interpolate(f - d - 6, [0, 10], [0, 100], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}%`}} />
                )}</span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

// ---------- Sera ----------
const Sera: React.FC<{pose: string; f: number; fps: number}> = ({pose, f, fps}) => {
  const T = useTema();
  const s = spring({frame: f - 4, fps, config: {damping: 9, stiffness: 140, mass: 0.7}});
  const bob = Math.sin((f / fps) * Math.PI * 1.6) * 14;
  const rot = Math.sin((f / fps) * Math.PI * 0.9) * 2.5;
  const pulso = 0.55 + 0.25 * Math.sin((f / fps) * Math.PI * 2.2);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 960, height: 620, display: 'flex', justifyContent: 'center'}}>
      {claro(T.bg) && <div style={{position: 'absolute', top: 60, width: 560, height: 560, borderRadius: '50%',
        background: 'radial-gradient(circle, #1a1a1e 0%, #0A0A0C 70%)', boxShadow: `0 0 0 6px ${T.marca}, 0 30px 80px rgba(0,0,0,.25)`,
        transform: `scale(${interpolate(s, [0, 1], [0.5, 1])})`, opacity: interpolate(s, [0, 0.3], [0, 1], {extrapolateRight: 'clamp'})}} />}
      <div style={{position: 'absolute', top: 120, width: 520, height: 420, borderRadius: '50%',
        background: `radial-gradient(circle, ${rgba(T.brilho, pulso * 0.35)}, transparent 65%)`, filter: 'blur(10px)'}} />
      <Img src={staticFile(`sera/${pose}.png`)} style={{
        height: 600, transform: `translateY(${bob}px) rotate(${rot}deg) scale(${interpolate(s, [0, 1], [0.3, 1])})`,
        opacity: interpolate(s, [0, 0.3], [0, 1], {extrapolateRight: 'clamp'}),
      }} />
    </div>
  );
};

// ---------- modelos de cena ----------
const CenaView: React.FC<{c: Cena; f: number; fps: number; n: number}> = ({c, f, fps, n}) => {
  const T = useTema();
  const branco = c.fundo === 'branco';
  const P = paletaDe(T, branco);
  const cor = P.texto;
  const linhas = c.linhas || [];
  const temSera = !!c.sera;
  const topo = temSera ? 230 : undefined;
  const esq = T.alinhar === 'left' && c.modelo !== 'cta';
  const tt = (l: string[], max: number) => tamanhoTitulo(l, max, T.k);

  // impacto da entrada
  const punch = spring({frame: f, fps, config: {damping: 14, stiffness: 200}});
  const esc = T.entrada === 'pop' ? interpolate(punch, [0, 1], [1.12, 1]) : interpolate(punch, [0, 1], [1.03, 1]);
  const shake = T.tremor && f < 6 ? (6 - f) * 2.4 : 0;
  const sx = Math.sin(f * 7.1) * shake, sy = Math.cos(f * 5.3) * shake;

  let conteudo: React.ReactNode = null;
  if (c.modelo === 'numero') {
    const s = spring({frame: f, fps, config: {damping: 13, stiffness: 120}});
    const estiloNum: React.CSSProperties = T.numero === 'vazado'
      ? {color: 'transparent', WebkitTextStroke: `5px ${P.destaque}`, filter: `drop-shadow(0 0 30px ${rgba(P.destaque, .35)})`}
      : T.numero === 'solido' ? {color: P.destaque}
      : {color: P.bg, background: P.destaque, padding: '10px 46px', borderRadius: 28, fontSize: 230};
    conteudo = (
      <div style={{display: 'flex', flexDirection: 'column', alignItems: esq ? 'flex-start' : 'center', width: '100%'}}>
        <div style={{fontFamily: T.fonte === 'Jet' ? 'Jet' : T.fonte === 'DMSerif' || T.fonte === 'Playfair' ? T.fonte : 'Anton', fontWeight: PESO[T.fonte] || 400,
          fontSize: 360, lineHeight: 0.9, ...estiloNum, transform: `scale(${interpolate(s, [0, 1], [0.6, 1])})`, transformOrigin: esq ? 'left center' : 'center',
          clipPath: T.numero === 'cartao' ? undefined : `inset(${interpolate(s, [0, 1], [100, 0])}% 0 0 0)`}}>{T.fonte === 'Jet' ? `[${c.numero}]` : c.numero}</div>
        <div style={{height: 30}} />
        <Titulo linhas={linhas} tam={tt(linhas, 150)} cor={cor} destaque={P.destaque} f={f} fps={fps} atraso={6} alinhar={esq ? 'left' : 'center'} />
      </div>
    );
  } else if (c.modelo === 'imagem' && c.imagem) {
    const k = interpolate(f, [0, n], [1.18, 1.0], {easing: Easing.out(Easing.quad)});
    const s = spring({frame: f, fps, config: {damping: 14, stiffness: 120}});
    conteudo = (
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 50}}>
        <Titulo linhas={linhas} tam={tt(linhas, 140)} cor={cor} destaque={P.destaque} f={f} fps={fps} alinhar="center" />
        <div style={{width: 900, height: 900, borderRadius: 44, overflow: 'hidden',
          border: `2px solid ${rgba(T.marca, .55)}`, boxShadow: `0 30px 80px rgba(0,0,0,.6), 0 0 60px ${rgba(T.marca, .15)}`,
          transform: `translateY(${interpolate(s, [0, 1], [120, 0])}px) rotate(${interpolate(s, [0, 1], [-4, 0])}deg)`,
          opacity: interpolate(s, [0, 0.3], [0, 1], {extrapolateRight: 'clamp'})}}>
          <Img src={staticFile(c.imagem)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${k})`}} />
        </div>
      </div>
    );
  } else if (c.modelo === 'lista' && c.itens) {
    const passo = n / (c.itens.length + 1);
    conteudo = (
      <div style={{display: 'flex', flexDirection: 'column', alignItems: esq ? 'flex-start' : 'center', gap: 60, width: '100%'}}>
        <Titulo linhas={linhas} tam={tt(linhas, 140)} cor={cor} destaque={P.destaque} f={f} fps={fps} alinhar={esq ? 'left' : 'center'} />
        <div style={{display: 'flex', flexDirection: 'column', gap: 34, width: 860}}>
          {c.itens.map((it, i) => {
            const s = spring({frame: f - passo * (i + 0.6), fps, config: {damping: 12, stiffness: 160}});
            const marcador = T.fonte === 'Jet' ? '>' : T.numero === 'solido' ? String(i + 1) : '✓';
            return (
              <div key={i} style={{display: 'flex', alignItems: 'center', gap: 28, opacity: s,
                transform: `translateX(${interpolate(s, [0, 1], [-80, 0])}px)`}}>
                <div style={{width: 74, height: 74, borderRadius: T.numero === 'cartao' ? 18 : 37, background: P.destaque, display: 'flex', flexShrink: 0,
                  alignItems: 'center', justifyContent: 'center', fontFamily: 'InterX', fontSize: 42, color: P.bg}}>{marcador}</div>
                <div style={{fontFamily: T.legendaFonte, fontWeight: 800, fontSize: 56, color: cor}}>{it}</div>
              </div>
            );
          })}
        </div>
      </div>
    );
  } else {
    conteudo = <Titulo linhas={linhas} tam={tt(linhas, temSera ? 220 : 280)} cor={cor} destaque={P.destaque} f={f} fps={fps} alinhar={esq ? 'left' : 'center'} />;
  }

  const apoioS = spring({frame: f - 14, fps, config: {damping: 16}});
  const cta = c.modelo === 'cta';
  const pill = 1 + 0.04 * Math.sin((f / fps) * Math.PI * 3);
  // assinatura sutil da marca: fio dourado que se desenha sob o conteúdo
  const fio = interpolate(f, [8, 22], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});

  return (
    <AbsoluteFill>
      <Fundo branco={branco} raios={!!c.raios} f={f} />
      <AbsoluteFill style={{transform: `scale(${esc}) translate(${sx}px, ${sy}px)`}}>
        <div style={{position: 'absolute', left: esq ? 90 : 60, right: 60, top: topo ?? 0, bottom: topo ? undefined : 260,
          display: 'flex', flexDirection: 'column', alignItems: esq ? 'flex-start' : 'center', justifyContent: topo ? 'flex-start' : 'center'}}>
          {conteudo}
          {!cta && c.modelo !== 'lista' && (
            <div style={{marginTop: 34, height: 6, width: 140 * fio, background: T.marca, borderRadius: 3, opacity: .9}} />
          )}
          {c.apoio && !cta && (
            <div style={{marginTop: 30, fontFamily: 'InterM', fontSize: 46, color: P.apoio,
              textAlign: esq ? 'left' : 'center', maxWidth: 900, opacity: apoioS, transform: `translateY(${(1 - apoioS) * 20}px)`}}>{c.apoio}</div>
          )}
          {cta && (
            <div style={{marginTop: 50, padding: '26px 56px', borderRadius: T.numero === 'cartao' ? 22 : 999, background: P.destaque, color: P.bg,
              fontFamily: 'InterX', fontSize: 52, transform: `scale(${apoioS * pill})`, boxShadow: `0 0 60px ${rgba(P.destaque, .45)}`}}>
              {c.apoio || 'link na bio'} →
            </div>
          )}
        </div>
        {temSera && <Sera pose={c.sera!} f={f} fps={fps} />}
      </AbsoluteFill>
      {T.entrada === 'pop' && f < 4 && <AbsoluteFill style={{background: '#fff', opacity: interpolate(f, [0, 4], [claro(P.bg) ? 0.9 : 0.55, 0])}} />}
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
  const T = useTema();
  const P = paletaDe(T, cena?.fundo === 'branco');
  const luz = claro(P.bg);
  const tam = g.reduce((n, p) => n + p.w.length, 0) > 22 ? 54 : 66;
  return (
    <div style={{position: 'absolute', left: 40, right: 40, top: 1600, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: T.legenda === 'pilula' ? 14 : 30}}>
      {g.map((p, i) => {
        const ativa = t >= p.s && t <= p.e + 0.05;
        const ja = t >= p.s;
        const estilo: React.CSSProperties = {
          fontFamily: T.legendaFonte, fontWeight: 800, fontSize: tam, textTransform: T.legendaFonte === 'Jet' ? 'none' : 'lowercase',
          display: 'inline-block', whiteSpace: 'nowrap', opacity: ja ? 1 : 0.35, transform: `translateY(${ativa ? -4 : 0}px)`,
        };
        if (T.legenda === 'pilula') {
          const baixo = luz && claro(P.destaque);
          Object.assign(estilo, {padding: '4px 18px', borderRadius: 14, color: ativa ? (baixo ? P.bg : P.bg) : P.texto,
            background: ativa ? (baixo ? P.texto : P.destaque) : rgba(luz ? '#FFFFFF' : '#000000', .55)});
        } else if (T.legenda === 'sublinhado') {
          Object.assign(estilo, {color: P.texto, borderBottom: `6px solid ${ativa ? T.marca : 'transparent'}`, paddingBottom: 4,
            textShadow: luz ? 'none' : '0 6px 20px rgba(0,0,0,.6)'});
        } else {
          Object.assign(estilo, {color: ativa ? P.destaque : P.texto,
            WebkitTextStroke: luz ? '0px' : '10px rgba(10,10,12,.9)', paintOrder: 'stroke fill',
            textShadow: luz ? 'none' : '0 6px 20px rgba(0,0,0,.6)'});
        }
        return <span key={i} style={estilo}>{p.w.replace(/[.,!?:;]$/, '')}</span>;
      })}
    </div>
  );
};

// ---------- vídeo ----------
export const SeraphimVideo: React.FC<Props> = (props) => (
  <TemaCtx.Provider value={TEMAS[props.tema || 'noir'] || TEMAS.noir}><VideoInner {...props} /></TemaCtx.Provider>
);

const VideoInner: React.FC<Props> = (props) => {
  useFontes();
  const T = useTema();
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const t = frame / fps;
  const cenaAtual = props.cenas.find((c) => t >= c.inicio && t < c.fim) || props.cenas[props.cenas.length - 1];
  const P = paletaDe(T, cenaAtual?.fundo === 'branco');
  return (
    <AbsoluteFill style={{background: T.bg}}>
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
      <div style={{position: 'absolute', top: 0, left: 0, height: 10, width: `${(frame / durationInFrames) * 100}%`, background: T.marca}} />
      {/* rodapé */}
      <div style={{position: 'absolute', left: 70, bottom: 70, display: 'flex', alignItems: 'center', gap: 22}}>
        <Img src={staticFile('marca/icone.png')} style={{width: 72, height: 72, borderRadius: 36, boxShadow: `0 0 0 3px ${rgba(T.marca, .6)}`}} />
        <span style={{fontFamily: 'InterM', fontSize: 38, color: P.apoio, opacity: .85}}>{props.arroba}</span>
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
          <Titulo linhas={linhas} tam={tamanhoTitulo(linhas, 110)} cor={C.branco} f={f} fps={fps} alinhar="center" />
        </div>
      )}
    </AbsoluteFill>
  );
};
