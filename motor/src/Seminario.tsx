// Vídeo acadêmico (exceção, fora da grade): gravação do Pabllo em cartão 3:4 + painel com os tópicos sincronizados à fala.
// Mesma linguagem do motor: Stack Sans, fundo tinta com brilho suave, vidro, molas e grão; sem marca da Seraphim.
import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, continueRender, delayRender} from 'remotion';

const INK = '#0B0D12', AZ = '#2F6BFF', AZ2 = '#9DB8FF', MARFIM = '#F2EEE6', CINZA = '#8A90A0', LINHA = 'rgba(255,255,255,.10)';
type Item = {t: number; txt: string; sub?: string};
type Secao = {inicio: number; fim: number; n: string; rotulo: string; titulo: string; tipo: string; itens: Item[]; ativo?: Item[]};
type Parte = {inicio: number; fim: number; escala: number; ox: number; oy: number};
export type PropsS = {duracao: number; video: string; secoes: Secao[]; partes: Parte[]; cortes: number[]; titulo: string; nome: string};

const useFontes = () => {
  const [h] = React.useState(() => delayRender('fontes'));
  React.useEffect(() => {
    const fs: [string, string, string][] = [['SH', 'stack-sans-headline-latin-700-normal.woff2', '700'], ['SH', 'stack-sans-headline-latin-600-normal.woff2', '600'],
      ['ST', 'stack-sans-text-latin-400-normal.woff2', '400'], ['ST', 'stack-sans-text-latin-500-normal.woff2', '500']];
    const t = setTimeout(() => continueRender(h), 8000);
    Promise.all(fs.map(([n, f, w]) => new FontFace(n, `url(${staticFile('fontes/' + f)})`, {weight: w}).load().then((ff) => (document as any).fonts.add(ff)).catch(() => null)))
      .finally(() => { clearTimeout(t); continueRender(h); });
  }, [h]);
};

const Grao: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{pointerEvents: 'none', opacity: 0.07, mixBlendMode: 'overlay',
    backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='${Math.floor(f / 2) % 6}'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")`}} />;
};

const fps = 30;
const entra = (f: number, t: number, d = 18) => spring({frame: f - t * fps, fps, config: {damping: d, stiffness: 150}});
const destaque = (s: string) => s.split(/(\*[^*]+\*)/).map((p, i) => p.startsWith('*') ? <span key={i} style={{color: AZ2}}>{p.slice(1, -1)}</span> : <React.Fragment key={i}>{p}</React.Fragment>);

const Lista: React.FC<{s: Secao; numerada?: boolean}> = ({s, numerada}) => {
  const f = useCurrentFrame(); const agora = f / fps;
  const ativo = [...s.itens].reverse().find((it) => agora >= it.t);
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: numerada ? 14 : 22}}>
      {s.itens.map((it, i) => {
        const e = entra(f, it.t); const on = numerada ? ativo === it : true;
        return (
          <div key={i} style={{display: 'flex', alignItems: 'flex-start', gap: 22, opacity: Math.min(1, e * 1.4) * (numerada && !on ? 0.42 : 1), transform: `translateX(${(1 - e) * 40}px)`,
            filter: `blur(${(1 - e) * 6}px)`}}>
            {numerada
              ? <div style={{minWidth: 58, height: 58, borderRadius: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 28px SH',
                  background: on ? AZ : 'rgba(255,255,255,.06)', color: on ? '#fff' : CINZA, border: on ? 'none' : `1.5px solid ${LINHA}`, boxShadow: on ? '0 10px 30px rgba(47,107,255,.35)' : 'none'}}>{i + 1}</div>
              : <div style={{minWidth: 12, height: 12, borderRadius: 6, background: AZ, marginTop: 17}} />}
            <div>
              <div style={{font: `600 ${numerada ? 36 : 38}px/1.2 SH`, color: MARFIM, letterSpacing: -0.4}}>{destaque(it.txt)}</div>
              {it.sub && (!numerada || on) && <div style={{font: '400 26px/1.35 ST', color: CINZA, marginTop: 6}}>{destaque(it.sub)}</div>}
            </div>
          </div>);
      })}
    </div>);
};

const Tabela: React.FC<{s: Secao}> = ({s}) => {
  const f = useCurrentFrame(); const agora = f / fps;
  const linhas = [['GET', 'Sim', 'Sim'], ['POST', 'Não', 'Não'], ['PUT', 'Sim', 'Não'], ['PATCH', 'Depende', 'Não'], ['DELETE', 'Sim', 'Não']];
  const marca = (v: string) => <span style={{color: v === 'Sim' ? '#7BE0A5' : v === 'Não' ? '#FF8A8A' : '#FFD27A'}}>{v}</span>;
  const ativo = [...(s.ativo || [])].reverse().find((it) => agora >= it.t)?.txt;
  return (
    <div>
      {s.itens.map((it, i) => { const e = entra(f, it.t); return (
        <div key={i} style={{font: '500 30px/1.4 ST', color: CINZA, marginBottom: 26, opacity: e, transform: `translateY(${(1 - e) * 20}px)`}}>{destaque(it.txt)}</div>); })}
      <div style={{border: `1.5px solid ${LINHA}`, borderRadius: 24, overflow: 'hidden', background: 'rgba(255,255,255,.03)', opacity: entra(f, s.itens[0]?.t ?? 0)}}>
        <div style={{display: 'grid', gridTemplateColumns: '1.1fr 1fr 1fr', padding: '18px 30px', font: '600 22px SH', letterSpacing: 3, color: CINZA, borderBottom: `1.5px solid ${LINHA}`}}>
          <span>VERBO</span><span>IDEMPOTENTE</span><span>SEGURO</span></div>
        {linhas.map(([v, a, b]) => { const on = ativo === v; return (
          <div key={v} style={{display: 'grid', gridTemplateColumns: '1.1fr 1fr 1fr', padding: '16px 30px', font: '600 32px SH', color: MARFIM,
            background: on ? 'rgba(47,107,255,.22)' : 'transparent', borderLeft: `6px solid ${on ? AZ : 'transparent'}`, transition: 'none'}}>
            <span>{v}</span>{marca(a)}{marca(b)}</div>); })}
      </div>
    </div>);
};

const Painel: React.FC<{s: Secao; total: number}> = ({s, total}) => {
  const f = useCurrentFrame(); const e = entra(f, 0, 20);
  return (
    <div style={{position: 'absolute', left: 900, top: 96, width: 924, opacity: e, transform: `translateY(${(1 - e) * 24}px)`}}>
      <div style={{font: '600 22px SH', letterSpacing: 5, color: AZ2}}>{s.n} / {String(total).padStart(2, '0')} · {s.rotulo}</div>
      <div style={{font: '700 62px/1.06 SH', color: MARFIM, letterSpacing: -1.6, margin: '18px 0 44px'}}>{destaque(s.titulo)}</div>
      {s.tipo === 'tabela' ? <Tabela s={s} /> : <Lista s={s} numerada={s.tipo === 'pilares' || s.tipo === 'verbos'} />}
    </div>);
};

export const Seminario: React.FC<PropsS> = (p) => {
  useFontes();
  const f = useCurrentFrame(); const t = f / fps;
  const parte = p.partes.find((x) => t >= x.inicio && t < x.fim) || p.partes[p.partes.length - 1];
  const nCorte = p.cortes.filter((c) => c <= t).length;              // alterna enquadramento a cada corte (disfarça o salto)
  const zoom = parte.escala * (nCorte % 2 ? 1.045 : 1);
  const tag = interpolate(t, [0.6, 1.2, 7.5, 8.2], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const fade = interpolate(t, [0, 0.5, p.duracao - 0.6, p.duracao], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const secIdx = p.secoes.findIndex((s) => t >= s.inicio && t < s.fim);
  return (
    <AbsoluteFill style={{background: INK, opacity: fade}}>
      <AbsoluteFill style={{background: 'radial-gradient(60% 70% at 78% 30%,rgba(47,107,255,.16),transparent 70%),radial-gradient(50% 60% at 10% 100%,rgba(47,107,255,.10),transparent 70%)'}} />
      {/* cartão do vídeo */}
      <div style={{position: 'absolute', left: 96, top: 60, width: 720, height: 960, borderRadius: 34, overflow: 'hidden', border: `1.5px solid ${LINHA}`,
        boxShadow: '0 40px 90px rgba(0,0,0,.55)', background: '#000'}}>
        <div style={{position: 'absolute', inset: 0, transform: `translate(${parte.ox}px, ${parte.oy}px) scale(${zoom})`, transformOrigin: '50% 28%'}}>
          <OffthreadVideo src={staticFile(p.video)} style={{width: 720, height: 1280, position: 'absolute', left: 0, top: -40}} />
        </div>
        <div style={{position: 'absolute', left: 28, bottom: 28, padding: '18px 26px', borderRadius: 20, background: 'rgba(11,13,18,.55)', backdropFilter: 'blur(14px)',
          border: '1.5px solid rgba(255,255,255,.16)', opacity: tag, transform: `translateY(${(1 - tag) * 16}px)`}}>
          <div style={{font: '700 34px SH', color: MARFIM}}>{p.nome}</div>
          <div style={{font: '500 22px ST', color: '#C9CEDA', marginTop: 4}}>com Gabriel Foletto</div>
        </div>
      </div>
      {p.secoes.map((s, i) => (
        <Sequence key={i} from={Math.round(s.inicio * fps)} durationInFrames={Math.max(1, Math.round((s.fim - s.inicio) * fps))} layout="none">
          <Painel s={{...s, itens: s.itens.map((it) => ({...it, t: it.t - s.inicio})), ativo: (s.ativo || []).map((it) => ({...it, t: it.t - s.inicio}))}} total={p.secoes.length} />
        </Sequence>))}
      {/* rodapé: título + progresso das seções */}
      <div style={{position: 'absolute', left: 900, right: 96, bottom: 66, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
        <div style={{font: '500 22px ST', color: CINZA, letterSpacing: 0.5}}>{p.titulo}</div>
        <div style={{display: 'flex', gap: 8}}>{p.secoes.map((_, i) => <div key={i} style={{width: i === secIdx ? 34 : 10, height: 10, borderRadius: 5, background: i <= secIdx ? AZ : 'rgba(255,255,255,.18)'}} />)}</div>
      </div>
      <Grao />
    </AbsoluteFill>
  );
};
