import React from "react";
import { Audio, Sequence, staticFile, Video } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { TornTapeLabel } from "./TornTapeLabel";

interface Props {
  videoSrc: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  hasBoom?: boolean;
  citation?: string;
}

export const ParallaxVideoScene: React.FC<Props> = ({
  videoSrc,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  hasBoom = false,
  citation,
}) => {
  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#050505",
        overflow: "hidden",
      }}
    >
      {/* SFX: Projector start & Typewriter stamp */}
      <Audio
        src={staticFile("audio/sfx_paper_slide.wav")}
        volume={0.35}
      />
      <Sequence from={12}>
        <Audio
          src={staticFile("audio/sfx_typewriter_stamp.wav")}
          volume={0.45}
        />
      </Sequence>
      {hasBoom && (
        <Sequence from={0}>
          <Audio
            src={staticFile("audio/sfx_sub_boom.wav")}
            volume={0.5}
          />
        </Sequence>
      )}

      {/* Archival Historical Video Stream */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          filter: "contrast(1.15) brightness(0.9) grayscale(0.85) sepia(0.15)",
        }}
      >
        <Video
          src={staticFile(videoSrc)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
          volume={0} // Muted because master voiceover and music drive the documentary
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
