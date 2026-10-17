import React from 'react';
import {Composition} from 'remotion';
import {SeraphimVideo, Props} from './Video';
import {SeraphimCortes, PropsC} from './Cortes';
import {Relancamento, PropsR} from './Relancamento';
import {Estilo, PropsE} from './Estilo';

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
