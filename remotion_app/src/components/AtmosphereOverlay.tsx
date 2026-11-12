import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export const AtmosphereOverlay: React.FC = () => {
  const frame = useCurrentFrame();

  // Subtle flicker for vintage projector feel
  const flicker = interpolate(
    Math.sin(frame * 0.4) * Math.cos(frame * 0.25),
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
      {/* 1. Cinematic Radial Vignette */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background:
            "radial-gradient(circle at 50% 48%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.45) 75%, rgba(0,0,0,0.85) 100%)",
        }}
      />

      {/* 2. Top and Bottom Letterbox Soft Vignette */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 80%, rgba(0,0,0,0.65) 100%)",
        }}
      />

      {/* 3. Archival Warm Tint */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(35, 24, 15, 0.06)",
          mixBlendMode: "multiply",
          opacity: flicker,
        }}
      />

      {/* 4. SVG Film Grain Filter */}
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
        <filter id="film-grain">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.75"
            numOctaves="3"
            stitchTiles="stitch"
            seed={frame % 10}
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#film-grain)" />
      </svg>
    </div>
  );
};
