import React from "react";
import { Composition } from "remotion";
import { DocumentaryPilot } from "./DocumentaryPilot";
import pilotConfig from "./pilot_config.json";
import { DocumentaryConfig } from "./types";

export const Root: React.FC = () => {
  const config = pilotConfig as DocumentaryConfig;
  const totalDuration = config.beats.reduce(
    (acc, b) => acc + b.durationInFrames,
    0
  );

  return (
    <Composition
      id="DocumentaryPilot"
      component={DocumentaryPilot}
      durationInFrames={Math.max(30, totalDuration)}
      fps={config.fps || 30}
      width={config.width || 1920}
      height={config.height || 1080}
      defaultProps={{
        config,
      }}
    />
  );
};
