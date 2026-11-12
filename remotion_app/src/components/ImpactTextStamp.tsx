import React from "react";
import { Audio, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

interface Props {
  text?: string;
  delayFrames?: number;
  holdFrames?: number;
}

export const ImpactTextStamp: React.FC<Props> = ({
  text,
  delayFrames = 18,
  holdFrames = 48,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!text) return null;

  // Spring slam entrance
  const entrance = spring({
    frame: frame - delayFrames,
    fps,
    config: {
      damping: 12,
      mass: 0.6,
      stiffness: 160,
    },
  });

  // Fade out after holdFrames
  const fadeOutStart = delayFrames + holdFrames;
  const exitOpacity = interpolate(
    frame,
    [fadeOutStart, fadeOutStart + 15],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const opacity = Math.min(1, Math.max(0, entrance)) * exitOpacity;
  const scale = 1.35 - entrance * 0.35;
  const rotation = -3.5 + entrance * 0.5;

  if (opacity <= 0.01) return null;

  return (
    <div
      style={{
        position: "absolute",
        top: "38%",
        left: "50%",
        transform: `translate(-50%, -50%) scale(${scale}) rotate(${rotation}deg)`,
        transformOrigin: "center center",
        zIndex: 55,
        opacity,
        pointerEvents: "none",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      {/* Sound Effect triggered on impact */}
      {frame === delayFrames && (
        <Audio
          src={staticFile("audio/sfx_typewriter_stamp.wav")}
          volume={0.28}
        />
      )}

      {/* Forensic Ink Stamp Box */}
      <div
        style={{
          border: "4px solid #8b1e1e",
          padding: "10px 28px",
          backgroundColor: "rgba(20, 15, 12, 0.4)",
          backdropFilter: "blur(2px)",
          boxShadow:
            "0 15px 30px rgba(0, 0, 0, 0.8), inset 0 0 15px rgba(139, 30, 30, 0.3)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <span
          style={{
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontSize: 38,
            fontWeight: 900,
            letterSpacing: "4px",
            color: "#fecaca",
            textTransform: "uppercase",
            textShadow: "0 2px 4px rgba(0, 0, 0, 0.9)",
            whiteSpace: "nowrap",
          }}
        >
          {text}
        </span>
      </div>
    </div>
  );
};
