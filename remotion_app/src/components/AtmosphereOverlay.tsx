import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface Props {
  citation?: string;
}

export const AtmosphereOverlay: React.FC<Props> = ({
  citation = "[1, 2] Sources in Description",
}) => {
  const frame = useCurrentFrame();

  // 1. Optical Camera Shutter Flash on Beat Transition (Frames 0-4)
  const flashOpacity = interpolate(frame, [0, 2, 6], [0.35, 0.1, 0], {
    extrapolateRight: "clamp",
  });

  // 2. Vintage projector light flicker
  const flicker = interpolate(
    Math.sin(frame * 0.45) * Math.cos(frame * 0.2),
    [-1, 1],
    [0.96, 1.04]
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 50,
      }}
    >
      {/* 1. Camera Shutter / Light Leak Flash */}
      {flashOpacity > 0 && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "#fffbeb",
            opacity: flashOpacity,
            mixBlendMode: "screen",
          }}
        />
      )}

      {/* 2. Top-Right Citation Badge (After the Crown standard) */}
      {citation && (
        <div
          style={{
            position: "absolute",
            top: 36,
            right: 48,
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontSize: 14,
            fontWeight: 400,
            color: "rgba(255, 255, 255, 0.72)",
            letterSpacing: "0.5px",
            textShadow: "0 2px 4px rgba(0, 0, 0, 0.8)",
            zIndex: 60,
          }}
        >
          {citation}
        </div>
      )}

      {/* 3. Deep Cinematic Radial Vignette */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background:
            "radial-gradient(circle at 50% 48%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.5) 75%, rgba(0,0,0,0.88) 100%)",
        }}
      />

      {/* 4. Top and Bottom Film Shading */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 80%, rgba(0,0,0,0.6) 100%)",
        }}
      />

      {/* 5. Vintage Amber Multiplying Tint */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(35, 24, 15, 0.05)",
          mixBlendMode: "multiply",
          opacity: flicker,
        }}
      />

      {/* 6. Dynamic 35mm Film Grain SVG Filter */}
      <svg
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          opacity: 0.12,
          mixBlendMode: "overlay",
        }}
      >
        <filter id="film-grain-pilot">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.75"
            numOctaves="3"
            stitchTiles="stitch"
            seed={frame % 10}
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#film-grain-pilot)" />
      </svg>
    </div>
  );
};
