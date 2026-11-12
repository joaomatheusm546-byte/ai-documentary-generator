import React from "react";
import { Composition } from "remotion";
import { DocumentaryPilot } from "./DocumentaryPilot";
import { DocumentaryConfig } from "./types";

import pilotConfig from "./pilot_config.json";

// We require act configs dynamically or import them
let act1Config: DocumentaryConfig;
let act2Config: DocumentaryConfig;
let act3Config: DocumentaryConfig;
let act4Config: DocumentaryConfig;
let act5Config: DocumentaryConfig;

try {
  act1Config = require("./act_1_config.json");
} catch {
  act1Config = pilotConfig as DocumentaryConfig;
}

try {
  act2Config = require("./act_2_config.json");
} catch {
  act2Config = pilotConfig as DocumentaryConfig;
}

try {
  act3Config = require("./act_3_config.json");
} catch {
  act3Config = pilotConfig as DocumentaryConfig;
}

try {
  act4Config = require("./act_4_config.json");
} catch {
  act4Config = pilotConfig as DocumentaryConfig;
}

try {
  act5Config = require("./act_5_config.json");
} catch {
  act5Config = pilotConfig as DocumentaryConfig;
}

function getDuration(cfg: DocumentaryConfig): number {
  if (!cfg || !cfg.beats) return 1500;
  return cfg.beats.reduce((acc, b) => acc + b.durationInFrames, 0);
}

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="DocumentaryPilot"
        component={DocumentaryPilot}
        durationInFrames={Math.max(30, getDuration(pilotConfig as DocumentaryConfig))}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ config: pilotConfig as DocumentaryConfig }}
      />
      <Composition
        id="Act1"
        component={DocumentaryPilot}
        durationInFrames={Math.max(30, getDuration(act1Config))}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ config: act1Config }}
      />
      <Composition
        id="Act2"
        component={DocumentaryPilot}
        durationInFrames={Math.max(30, getDuration(act2Config))}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ config: act2Config }}
      />
      <Composition
        id="Act3"
        component={DocumentaryPilot}
        durationInFrames={Math.max(30, getDuration(act3Config))}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ config: act3Config }}
      />
      <Composition
        id="Act4"
        component={DocumentaryPilot}
        durationInFrames={Math.max(30, getDuration(act4Config))}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ config: act4Config }}
      />
      <Composition
        id="Act5"
        component={DocumentaryPilot}
        durationInFrames={Math.max(30, getDuration(act5Config))}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ config: act5Config }}
      />
    </>
  );
};
