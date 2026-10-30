import React from 'react';
import {Composition} from 'remotion';
import {SeraphimVideo, Props} from './Video';
import {SeraphimCortes, PropsC} from './Cortes';
import {Relancamento, PropsR} from './Relancamento';
import {Estilo, PropsE} from './Estilo';
import {SinalVivo, PropsV} from './SinalVivo';
import {Seminario, PropsS} from './Seminario';
import {AutoFlowV1, PropsAF} from './AutoFlowV1';
import {AutoFlowV2} from './AutoFlowV2';
import {AutoFlowV3} from './AutoFlowV3';
import {AutoFlowV12} from './AutoFlowV12';
import {AutoFlowV13} from './AutoFlowV13';
import {AutoFlowLapidado, PropsLap} from './AutoFlowLapidado';

const exemplo: Props = {
  fps: 30,
  duracao: 6,
  arroba: '@seraphimbr_',
  audio: null,
  batida: null,
  sfx: true,
  palavras: [],
  cenas: [
    {inicio: 0, fim: 3, modelo: 'impacto', linhas: ['SUA', '*OFICINA*'], sera: 'surpreso'},
    {inicio: 3, fim: 6, modelo: 'numero', numero: '01', linhas: ['COBRA NO', '*ACHÔMETRO*']},
  ],
};

export const Root: React.FC = () => (
  <>
  <Composition id="AutoFlowV1" component={AutoFlowV1 as any} width={1080} height={1920} fps={30} durationInFrames={1140} defaultProps={{trilha: null} as PropsAF} />
  <Composition id="AutoFlowV2" component={AutoFlowV2 as any} width={1080} height={1920} fps={30} durationInFrames={1260} defaultProps={{trilha: null}} />
  <Composition id="AFLapV2" component={AutoFlowLapidado as any} width={1080} height={1920} fps={30} durationInFrames={1110}
    defaultProps={{video: 'lap/v2_limpo.mp4', audio: null, dur: 1110, shots: [], caps: [], hits: [], fimCard: 31, nome: 'v2'} as PropsLap}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil((props as PropsLap).dur)})} />
  <Composition id="AFLapV3" component={AutoFlowLapidado as any} width={1080} height={1920} fps={30} durationInFrames={1125}
    defaultProps={{video: 'lap/v3_limpo.mp4', audio: null, dur: 1125, shots: [], caps: [], hits: [], fimCard: 30, nome: 'v3'} as PropsLap}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil((props as PropsLap).dur)})} />
  <Composition id="AutoFlowV12" component={AutoFlowV12 as any} width={1080} height={1920} fps={30} durationInFrames={1170} defaultProps={{trilha: null}} />
  <Composition id="AutoFlowV13" component={AutoFlowV13 as any} width={1080} height={1920} fps={30} durationInFrames={1320} defaultProps={{trilha: null}} />
  <Composition id="AutoFlowV3" component={AutoFlowV3 as any} width={1080} height={1920} fps={30} durationInFrames={1350} defaultProps={{trilha: null}} />
  <Composition
    id="Cortes"
    component={SeraphimCortes as any}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={180}
    defaultProps={{fps: 30, duracao: 6, arroba: '@seraphimbr_', audio: null, batida: null, sfx: false, palavras: [], cenas: [{inicio: 0, fim: 6, tipo: 'frase', texto: 'teste'}]} as PropsC}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil((props as PropsC).duracao * (props as PropsC).fps), fps: (props as PropsC).fps})}
  />
  <Composition
    id="Relancamento"
    component={Relancamento as any}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={180}
    defaultProps={{fps: 30, duracao: 6, arroba: '@seraphimbr_', audio: null, batida: null, palavras: [], peca: 'V1', cenas: [{inicio: 0, fim: 6, tipo: 'cresce'}]} as PropsR}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil((props as PropsR).duracao * (props as PropsR).fps), fps: (props as PropsR).fps})}
  />
  <Composition id="Seminario" component={Seminario as any} width={1920} height={1080} fps={30} durationInFrames={300}
    defaultProps={{duracao: 10, video: 'sem/video.mp4', secoes: [], partes: [{inicio: 0, fim: 9999, escala: 1, ox: 0, oy: 0}], cortes: [], titulo: '', nome: 'Pabllo'} as PropsS}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil((props as PropsS).duracao * 30)})} />
  <Composition
    id="SinalVivo"
    component={SinalVivo as any}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={450}
    defaultProps={{fps: 30, duracao: 15, arroba: '@seraphimbr_', audio: null, cenas: [{inicio: 0, fim: 15, tipo: 'texto', linhas: [{t: 'teste', y: 800}]}]} as PropsV}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil((props as PropsV).duracao * 30), fps: 30})}
  />
  <Composition
    id="Estilo"
    component={Estilo as any}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={180}
    defaultProps={{fps: 30, duracao: 6, arroba: '@seraphimbr_', audio: null, batida: null, palavras: [], cenas: [{inicio: 0, fim: 6, tipo: 'frase', titulo: 'teste'}]} as PropsE}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil((props as PropsE).duracao * (props as PropsE).fps), fps: (props as PropsE).fps})}
  />
  <Composition
    id="Seraphim"
    component={SeraphimVideo as any}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={180}
    defaultProps={exemplo}
    calculateMetadata={({props}) => ({
      durationInFrames: Math.ceil((props as Props).duracao * (props as Props).fps),
      fps: (props as Props).fps,
    })}
  />

  </>
);
