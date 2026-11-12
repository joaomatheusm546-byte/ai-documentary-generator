import React from "react";
import { Audio, Easing, Img, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { ImpactTextStamp } from "./ImpactTextStamp";
import { TornTapeLabel } from "./TornTapeLabel";

interface Props {
  bgImage: string;
  leftDocument: string;
  rightSubject: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  highlightText?: string;
  impactText?: string;
  connectionLabel?: string;
  hasBoom?: boolean;
  citation?: string;
}

export const ParallaxSplitCollageScene: React.FC<Props> = ({
  bgImage,
  leftDocument,
  rightSubject,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  highlightText,
  impactText,
  connectionLabel,
  hasBoom = false,
  citation,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const easeCinematic = Easing.bezier(0.22, 0.1, 0.25, 1.0);

  // Subtle camera drift with organic easing
  const bgScale = interpolate(frame, [0, durationInFrames], [1.02, 1.08], {
    easing: easeCinematic,
  });

  // Document motion (left side)
  const docScale = interpolate(frame, [0, durationInFrames], [0.96, 1.02], {
    easing: easeCinematic,
  });
  const docRotateX = interpolate(frame, [0, durationInFrames], [8, 5], {
    easing: easeCinematic,
  });
  const docRotateY = interpolate(frame, [0, durationInFrames], [6, 3], {
    easing: easeCinematic,
  });

  // Subject cutout motion (right side, anchored top)
  const subjectScale = interpolate(frame, [0, durationInFrames], [1.18, 1.25], {
    easing: easeCinematic,
  });
  const subjectRotateY = interpolate(frame, [0, durationInFrames], [-4, -1], {
    easing: easeCinematic,
  });
  const subjectFloatY = Math.sin(frame * 0.04) * 6;

  // Connecting line animation (draws from frame 15 to 35)
  const lineProgress = spring({
    frame: frame - 15,
    fps,
    config: { damping: 16, stiffness: 85 },
  });
  const clampedLine = Math.min(1, Math.max(0, lineProgress));

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
      {/* SFX */}
      <Audio src={staticFile("audio/sfx_paper_slide.wav")} volume={0.22} />
      <Sequence from={12}>
        <Audio src={staticFile("audio/sfx_typewriter_stamp.wav")} volume={0.24} />
      </Sequence>
      {hasBoom && (
        <Sequence from={0}>
          <Audio src={staticFile("audio/sfx_sub_boom.wav")} volume={0.18} />
        </Sequence>
      )}

      {/* 1. Background Archival Texture */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          transform: `scale(${bgScale})`,
          filter: "blur(3.5px) brightness(0.45) contrast(1.15) sepia(0.25)",
        }}
      >
        <Img
          src={staticFile(bgImage)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>

      {/* 2. Left Element: 3D Archival Document */}
      <div
        style={{
          position: "absolute",
          top: "48%",
          left: "26%",
          transform: `translate(-50%, -50%) perspective(1100px) rotateX(${docRotateX}deg) rotateY(${docRotateY}deg) scale(${docScale})`,
          maxWidth: "42%",
          maxHeight: "75%",
          zIndex: 20,
          boxShadow: "0 30px 50px rgba(0,0,0,0.9), 0 10px 20px rgba(0,0,0,0.6)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 4,
          backgroundColor: "#111",
        }}
      >
        <Img
          src={staticFile(leftDocument)}
          style={{
            width: "100%",
            height: "auto",
            display: "block",
            borderRadius: 3,
            filter: "contrast(1.15) brightness(0.92)",
          }}
        />

        {/* Highlight Marker */}
        {highlightText && (
          <div
            style={{
              position: "absolute",
              top: "40%",
              left: "10%",
              width: `${clampedLine * 80}%`,
              height: 40,
              backgroundColor: "rgba(250, 204, 21, 0.42)",
              mixBlendMode: "multiply",
              border: "2px solid rgba(234, 179, 8, 0.85)",
              display: "flex",
              alignItems: "center",
              paddingLeft: 10,
              overflow: "hidden",
            }}
          >
            <span
              style={{
                fontFamily: "'Courier New', Courier, monospace",
                fontSize: 14,
                fontWeight: 700,
                color: "#713f12",
                letterSpacing: 1.2,
                textTransform: "uppercase",
                whiteSpace: "nowrap",
                opacity: clampedLine,
              }}
            >
              {highlightText}
            </span>
          </div>
        )}
      </div>

      {/* 3. Center Connecting Line (SVG Red Forensic Thread) */}
      <svg
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          zIndex: 25,
          pointerEvents: "none",
        }}
      >
        <line
          x1="880"
          y1="520"
          x2={880 + clampedLine * 220}
          y2="520"
          stroke="#b91c1c"
          strokeWidth="3"
          strokeDasharray="6 4"
        />
      </svg>

      {/* 4. Right Element: 2.5D Person Cutout */}
      <div
        style={{
          position: "absolute",
          top: 60,
          right: "8%",
          zIndex: 30,
          transform: `translateY(${subjectFloatY}px) perspective(1100px) rotateY(${subjectRotateY}deg) scale(${subjectScale})`,
          transformOrigin: "center top",
          height: "90%",
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start",
          filter:
            "drop-shadow(0 35px 50px rgba(0, 0, 0, 0.95)) drop-shadow(0 15px 22px rgba(0, 0, 0, 0.8))",
        }}
      >
        <Img
          src={staticFile(rightSubject)}
          style={{
            height: "100%",
            width: "auto",
            objectFit: "contain",
            filter: "contrast(1.12) brightness(0.95)",
          }}
        />
        {/* Micro-print archival texture overlay */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundImage:
              "radial-gradient(rgba(0,0,0,0.15) 1px, transparent 0)",
            backgroundSize: "3px 3px",
            mixBlendMode: "multiply",
            pointerEvents: "none",
            opacity: 0.35,
          }}
        />
      </div>

      {/* 5. Torn Paper Tape Label */}
      <TornTapeLabel
        title={labelTitle}
        subtitle={labelSubtitle}
        delayFrames={12}
        position="pinned-left"
      />

      {/* 6. Kinetic Impact Text Stamp */}
      <ImpactTextStamp text={impactText} delayFrames={20} holdFrames={45} />

      {/* 7. Atmosphere */}
      <DustParticles />
      <AtmosphereOverlay citation={citation} />
    </div>
  );
};
