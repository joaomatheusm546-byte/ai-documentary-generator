import React from "react";
import { Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { TornTapeLabel } from "./TornTapeLabel";

interface Props {
  imageSrc: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  hasBoom?: boolean;
  citation?: string;
}

export const ParallaxLandscapeScene: React.FC<Props> = ({
  imageSrc,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  hasBoom = false,
  citation,
}) => {
  const frame = useCurrentFrame();

  const scale = interpolate(frame, [0, durationInFrames], [1.0, 1.08]);
  const panX = interpolate(frame, [0, durationInFrames], [-16, 16]);
  const panY = interpolate(frame, [0, durationInFrames], [8, -8]);

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
      {/* SFX: Shutter & Typewriter */}
      <Audio
        src={staticFile("audio/sfx_camera_shutter.wav")}
        volume={0.18}
      />
      <Sequence from={12}>
        <Audio
          src={staticFile("audio/sfx_typewriter_stamp.wav")}
          volume={0.24}
        />
      </Sequence>
      {hasBoom && (
        <Sequence from={0}>
          <Audio
            src={staticFile("audio/sfx_sub_boom.wav")}
            volume={0.18}
          />
        </Sequence>
      )}

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
        delayFrames={10}
        position="lower-left"
      />

      {/* Atmosphere Overlays */}
      <DustParticles />
      <AtmosphereOverlay citation={citation} />
    </div>
  );
};
