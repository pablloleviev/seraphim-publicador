import React from 'react';
import {Composition} from 'remotion';
import {SeraphimVideo, Props} from './Video';

const exemplo: Props = {
  fps: 30,
  duracao: 6,
  arroba: '@seraphimtech_',
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
);
