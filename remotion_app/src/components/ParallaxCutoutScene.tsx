import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { TornTapeLabel } from "./TornTapeLabel";

interface Props {
  bgImage: string;
  subjectImage?: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  badgeText?: string;
}

export const ParallaxCutoutScene: React.FC<Props> = ({
  bgImage,
  subjectImage,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  badgeText,
}) => {
  const frame = useCurrentFrame();

  // Background slow zoom & drift
  const bgScale = interpolate(frame, [0, durationInFrames], [1.02, 1.1]);
  const bgTranslateX = interpolate(frame, [0, durationInFrames], [-10, 10]);

  // Subject cutout parallax motion (3D floating perspective)
  const subjectScale = interpolate(frame, [0, durationInFrames], [0.98, 1.04]);
  const subjectRotateY = interpolate(
    frame,
    [0, durationInFrames],
    [-2.5, 2.5]
  );
  const subjectRotateX = interpolate(
    Math.sin(frame * 0.05),
    [-1, 1],
    [-0.8, 0.8]
  );
  const subjectFloatY = Math.sin(frame * 0.04) * 8;

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
      {/* 1. Background Layer */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          transform: `scale(${bgScale}) translateX(${bgTranslateX}px)`,
          filter: "blur(3.5px) brightness(0.62) contrast(1.15) sepia(0.25)",
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

      {/* 2. Soft Depth Separator Shadow between BG and Subject */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background:
            "radial-gradient(circle at 50% 50%, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.7) 100%)",
          zIndex: 10,
        }}
      />

      {/* 3. Subject Cutout Layer (2.5D Isolated Foreground) */}
      {subjectImage && (
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: "50%",
            zIndex: 20,
            transform: `translateX(-50%) translateY(${subjectFloatY}px) perspective(1100px) rotateY(${subjectRotateY}deg) rotateX(${subjectRotateX}deg) scale(${subjectScale})`,
            transformOrigin: "bottom center",
            height: "92%",
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-end",
            filter:
              "drop-shadow(0 35px 45px rgba(0, 0, 0, 0.95)) drop-shadow(0 12px 18px rgba(0, 0, 0, 0.75))",
          }}
        >
          <Img
            src={staticFile(subjectImage)}
            style={{
              height: "100%",
              width: "auto",
              objectFit: "contain",
              filter: "contrast(1.1) brightness(0.95)",
            }}
          />
        </div>
      )}

      {/* 4. Lower Third Torn Tape Label */}
      <TornTapeLabel
        title={labelTitle}
        subtitle={labelSubtitle}
        badge={badgeText}
        delayFrames={12}
      />

      {/* 5. Atmosphere: Dust Particles and Film Grain */}
      <DustParticles />
      <AtmosphereOverlay />
    </div>
  );
};
