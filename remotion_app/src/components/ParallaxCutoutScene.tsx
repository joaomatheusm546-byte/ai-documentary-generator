import React from "react";
import { Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { TornTapeLabel } from "./TornTapeLabel";

interface Props {
  bgImage: string;
  subjectImage?: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  hasBoom?: boolean;
  citation?: string;
}

export const ParallaxCutoutScene: React.FC<Props> = ({
  bgImage,
  subjectImage,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  hasBoom = false,
  citation,
}) => {
  const frame = useCurrentFrame();

  // Background slow zoom & drift
  const bgScale = interpolate(frame, [0, durationInFrames], [1.02, 1.1]);
  const bgTranslateX = interpolate(frame, [0, durationInFrames], [-8, 8]);

  // Subject cutout motion (Anchored at TOP to preserve head, hair & hats)
  const subjectScale = interpolate(frame, [0, durationInFrames], [1.2, 1.28]);
  const subjectRotateY = interpolate(
    frame,
    [0, durationInFrames],
    [-2.2, 2.2]
  );
  const subjectRotateX = interpolate(
    Math.sin(frame * 0.05),
    [-1, 1],
    [-0.5, 0.5]
  );
  const subjectFloatY = Math.sin(frame * 0.04) * 6;

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#0d0c0a",
        overflow: "hidden",
      }}
    >
      {/* --- DIEGETIC FOLEY SOUND EFFECTS --- */}
      {/* 1. Paper Slide Sound on Scene Cut */}
      <Audio
        src={staticFile("audio/sfx_paper_slide.wav")}
        volume={0.42}
      />

      {/* 2. Typewriter / Stamp Sound when Torn Tape Label Enters */}
      <Sequence from={12}>
        <Audio
          src={staticFile("audio/sfx_typewriter_stamp.wav")}
          volume={0.5}
        />
      </Sequence>

      {/* 3. Sub-Boom for Major Historical Reveals */}
      {hasBoom && (
        <Sequence from={0}>
          <Audio
            src={staticFile("audio/sfx_sub_boom.wav")}
            volume={0.55}
          />
        </Sequence>
      )}

      {/* 1. Background Layer */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          transform: `scale(${bgScale}) translateX(${bgTranslateX}px)`,
          filter: "blur(3.5px) brightness(0.58) contrast(1.15) sepia(0.25)",
        }}
      >
        <Img
          src={staticFile(bgImage)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </div>

      {/* 2. Depth Shadow Separator */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background:
            "radial-gradient(circle at 50% 45%, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0.75) 100%)",
          zIndex: 10,
        }}
      />

      {/* 3. Subject Cutout (Top-anchored Busto Framing: guarantees head, eyes, and hat stay fully in frame) */}
      {subjectImage && (
        <div
          style={{
            position: "absolute",
            top: 55,
            left: "50%",
            zIndex: 20,
            transform: `translateX(-50%) translateY(${subjectFloatY}px) perspective(1100px) rotateY(${subjectRotateY}deg) rotateX(${subjectRotateX}deg) scale(${subjectScale})`,
            transformOrigin: "center top",
            height: "92%",
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-start",
            filter:
              "drop-shadow(0 35px 50px rgba(0, 0, 0, 0.95)) drop-shadow(0 15px 22px rgba(0, 0, 0, 0.8))",
          }}
        >
          <Img
            src={staticFile(subjectImage)}
            style={{
              height: "100%",
              width: "auto",
              objectFit: "contain",
              filter: "contrast(1.12) brightness(0.95)",
            }}
          />
        </div>
      )}

      {/* 4. Torn Paper Tape Label */}
      <TornTapeLabel
        title={labelTitle}
        subtitle={labelSubtitle}
        delayFrames={12}
        position="pinned-left"
      />

      {/* 5. Atmosphere Overlays */}
      <DustParticles />
      <AtmosphereOverlay citation={citation} />
    </div>
  );
};
