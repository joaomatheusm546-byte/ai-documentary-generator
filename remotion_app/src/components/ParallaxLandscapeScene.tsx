import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { TornTapeLabel } from "./TornTapeLabel";

interface Props {
  imageSrc: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  badgeText?: string;
}

export const ParallaxLandscapeScene: React.FC<Props> = ({
  imageSrc,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  badgeText,
}) => {
  const frame = useCurrentFrame();

  const scale = interpolate(frame, [0, durationInFrames], [1.0, 1.08]);
  const panX = interpolate(frame, [0, durationInFrames], [-20, 20]);
  const panY = interpolate(frame, [0, durationInFrames], [10, -10]);

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#080706",
        overflow: "hidden",
      }}
    >
      {/* Landscape Image with Slow Cinematic Glide */}
      <div
        style={{
          position: "absolute",
          top: -40,
          left: -40,
          width: "calc(100% + 80px)",
          height: "calc(100% + 80px)",
          transform: `scale(${scale}) translate(${panX}px, ${panY}px)`,
          filter: "contrast(1.15) brightness(0.85) sepia(0.2)",
        }}
      >
        <Img
          src={staticFile(imageSrc)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </div>

      {/* Torn Tape Label */}
      <TornTapeLabel
        title={labelTitle}
        subtitle={labelSubtitle}
        badge={badgeText}
        delayFrames={10}
      />

      {/* Atmosphere Overlays */}
      <DustParticles />
      <AtmosphereOverlay />
    </div>
  );
};
