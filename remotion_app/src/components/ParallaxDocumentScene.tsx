import React from "react";
import { Audio, Img, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { TornTapeLabel } from "./TornTapeLabel";

interface Props {
  bgImage: string;
  documentImage: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  highlightText?: string;
  hasBoom?: boolean;
  citation?: string;
}

export const ParallaxDocumentScene: React.FC<Props> = ({
  bgImage,
  documentImage,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  highlightText,
  hasBoom = false,
  citation,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Slow continuous camera push on the document
  const docScale = interpolate(frame, [0, durationInFrames], [0.93, 1.01]);
  const docRotateX = interpolate(frame, [0, durationInFrames], [9, 5]);
  const docRotateY = interpolate(frame, [0, durationInFrames], [-6, -2]);
  const docPanY = interpolate(frame, [0, durationInFrames], [12, -12]);

  // Highlight line animation (marker stroke)
  const markerSpring = spring({
    frame: frame - 18,
    fps,
    config: {
      damping: 18,
      stiffness: 90,
    },
  });
  const markerProgress = Math.min(1, Math.max(0, markerSpring));

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
      {/* --- DIEGETIC FOLEY SOUND EFFECTS --- */}
      <Audio
        src={staticFile("audio/sfx_paper_slide.wav")}
        volume={0.22}
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

      {/* 1. Archival Table Background */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          transform: `scale(1.05)`,
          filter: "brightness(0.35) blur(3px) contrast(1.2)",
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

      {/* 2. Soft Ambient Vignette */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background:
            "radial-gradient(circle at 50% 50%, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.82) 100%)",
          zIndex: 10,
        }}
      />

      {/* 3. Document Layer in 2.5D Physical Perspective */}
      <div
        style={{
          position: "absolute",
          top: "47%",
          left: "50%",
          zIndex: 20,
          transform: `translate(-50%, -50%) translateY(${docPanY}px) perspective(1200px) rotateX(${docRotateX}deg) rotateY(${docRotateY}deg) scale(${docScale})`,
          maxWidth: "76%",
          maxHeight: "78%",
          boxShadow:
            "0 40px 65px rgba(0, 0, 0, 0.95), 0 15px 25px rgba(0, 0, 0, 0.7)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          borderRadius: 4,
          backgroundColor: "#111",
        }}
      >
        <Img
          src={staticFile(documentImage)}
          style={{
            width: "100%",
            height: "auto",
            display: "block",
            borderRadius: 3,
            filter: "contrast(1.15) brightness(0.92)",
          }}
        />

        {/* Animated Forensic Highlight */}
        {highlightText && (
          <div
            style={{
              position: "absolute",
              top: "44%",
              left: "14%",
              width: `${markerProgress * 72}%`,
              height: 48,
              backgroundColor: "rgba(250, 204, 21, 0.42)",
              mixBlendMode: "multiply",
              border: "2px solid rgba(234, 179, 8, 0.85)",
              boxShadow: "0 0 16px rgba(250, 204, 21, 0.35)",
              display: "flex",
              alignItems: "center",
              paddingLeft: 12,
              overflow: "hidden",
            }}
          >
            <span
              style={{
                fontFamily: "'Courier New', Courier, monospace",
                fontSize: 16,
                fontWeight: 700,
                color: "#713f12",
                letterSpacing: 1.5,
                textTransform: "uppercase",
                whiteSpace: "nowrap",
                opacity: markerProgress,
              }}
            >
              {highlightText}
            </span>
          </div>
        )}
      </div>

      {/* 4. Lower Third Torn Tape Label */}
      <TornTapeLabel
        title={labelTitle}
        subtitle={labelSubtitle}
        delayFrames={10}
        position="lower-left"
      />

      {/* 5. Atmosphere: Dust Particles and Film Grain */}
      <DustParticles />
      <AtmosphereOverlay citation={citation} />
    </div>
  );
};
