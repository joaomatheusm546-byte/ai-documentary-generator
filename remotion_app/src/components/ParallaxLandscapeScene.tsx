import React from "react";
import { Audio, Easing, Img, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { TornTapeLabel } from "./TornTapeLabel";

type LandscapeMotion = "zoom_in" | "zoom_out" | "pan_left" | "pan_right";

interface Props {
  imageSrc: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  hasBoom?: boolean;
  disableAutoSfx?: boolean;
  citation?: string;
  motionVariant?: LandscapeMotion;
}

export const ParallaxLandscapeScene: React.FC<Props> = ({
  imageSrc,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  hasBoom = false,
  disableAutoSfx = false,
  citation,
  motionVariant = "zoom_in",
}) => {
  const frame = useCurrentFrame();

  const easeCinematic = Easing.bezier(0.22, 0.1, 0.25, 1.0);

  const motionTable: Record<LandscapeMotion, { s0: number; s1: number; x0: number; x1: number; y0: number; y1: number }> = {
    zoom_in: { s0: 1.0, s1: 1.08, x0: -14, x1: 14, y0: 6, y1: -6 },
    zoom_out: { s0: 1.09, s1: 1.01, x0: 14, x1: -14, y0: -6, y1: 6 },
    pan_left: { s0: 1.04, s1: 1.06, x0: 22, x1: -22, y0: 4, y1: -4 },
    pan_right: { s0: 1.04, s1: 1.06, x0: -22, x1: 22, y0: -4, y1: 4 },
  };
  const m = motionTable[motionVariant] || motionTable.zoom_in;

  const scale = interpolate(frame, [0, durationInFrames], [m.s0, m.s1], {
    easing: easeCinematic,
  });
  const panX = interpolate(frame, [0, durationInFrames], [m.x0, m.x1], {
    easing: easeCinematic,
  });
  const panY = interpolate(frame, [0, durationInFrames], [m.y0, m.y1], {
    easing: easeCinematic,
  });

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
      {!disableAutoSfx && (
        <>
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
                volume={0.12}
              />
            </Sequence>
          )}
        </>
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
