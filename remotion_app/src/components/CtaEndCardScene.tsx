import React from "react";
import { Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { CtaEndCardData } from "../types";

interface Props {
  bgImage: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  ctaData?: CtaEndCardData;
  citation?: string;
}

export const CtaEndCardScene: React.FC<Props> = ({
  bgImage,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  ctaData,
  citation,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const easeSlow = Easing.bezier(0.22, 0.1, 0.25, 1.0);
  const bgScale = interpolate(frame, [0, durationInFrames], [1.03, 1.1], {
    easing: easeSlow,
    extrapolateRight: "clamp",
  });

  const panelIn = spring({
    frame: frame - 8,
    fps,
    config: { damping: 16, mass: 0.7, stiffness: 120 },
  });
  const opacity = Math.min(1, Math.max(0, panelIn));
  const liftY = (1 - panelIn) * 20;

  const headline = ctaData?.headline || labelTitle || "THE ARCHIVE REMAINS OPEN";
  const bridgeText =
    ctaData?.bridgeText ||
    labelSubtitle ||
    "Follow the connected intelligence file on screen before the next dossier opens.";
  const nextTitle = ctaData?.nextDossierTitle || "NEXT DECLASSIFIED DOSSIER";
  const channelHandle = ctaData?.channelHandle || "@AftermathDossier";

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#060608",
        overflow: "hidden",
      }}
    >
      {/* Dark blurred archival plate */}
      <div
        style={{
          position: "absolute",
          inset: -40,
          transform: `scale(${bgScale})`,
          filter: "blur(6px) brightness(0.32) contrast(1.12) sepia(0.28)",
        }}
      >
        <Img
          src={staticFile(bgImage)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>

      {/* Top Dossier Header */}
      <div
        style={{
          position: "absolute",
          top: 76,
          left: 140,
          right: 140,
          zIndex: 40,
          opacity,
          transform: `translateY(${liftY}px)`,
          borderBottom: "1px solid rgba(212, 198, 172, 0.28)",
          paddingBottom: 18,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
        }}
      >
        <div
          style={{
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontSize: 38,
            fontWeight: 700,
            color: "#f3ede0",
            letterSpacing: "1.2px",
            textShadow: "0 3px 12px rgba(0, 0, 0, 0.9)",
          }}
        >
          {headline}
        </div>
        <div
          style={{
            fontFamily: "'Courier New', monospace",
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: "2.5px",
            color: "#dc2626",
            border: "2px solid rgba(220, 38, 38, 0.7)",
            padding: "5px 14px",
            backgroundColor: "rgba(25, 8, 8, 0.55)",
          }}
        >
          FILE CONTINUES
        </div>
      </div>

      {/* Left YouTube Subscribe Zone (keeps bottom strip free for subtitles) */}
      <div
        style={{
          position: "absolute",
          top: 230,
          left: 140,
          width: 680,
          height: 450,
          zIndex: 40,
          opacity,
          transform: `translateY(${liftY}px)`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "rgba(12, 11, 10, 0.62)",
          border: "1px solid rgba(212, 198, 172, 0.22)",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.78)",
          padding: "28px 36px",
          boxSizing: "border-box",
        }}
      >
        {/* Circular Guide Matching YouTube Channel End-Screen Element */}
        <div
          style={{
            width: 210,
            height: 210,
            borderRadius: "50%",
            border: "2px dashed rgba(220, 38, 38, 0.75)",
            backgroundColor: "rgba(24, 18, 16, 0.85)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "inset 0 0 28px rgba(185, 28, 28, 0.22)",
          }}
        >
          <span
            style={{
              fontFamily: "'Courier New', monospace",
              fontSize: 13,
              letterSpacing: "2px",
              color: "#fca5a5",
              marginBottom: 8,
            }}
          >
            SUBSCRIBE
          </span>
          <span
            style={{
              fontFamily: "Georgia, 'Times New Roman', serif",
              fontSize: 20,
              fontWeight: 700,
              color: "#f8f4ea",
              textAlign: "center",
              padding: "0 12px",
            }}
          >
            {channelHandle}
          </span>
        </div>

        <div
          style={{
            marginTop: 26,
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontStyle: "italic",
            fontSize: 23,
            lineHeight: 1.4,
            color: "#e6decb",
            textAlign: "center",
            maxWidth: 560,
          }}
        >
          {bridgeText}
        </div>
      </div>

      {/* Right YouTube Next-Video End-Screen Zone */}
      <div
        style={{
          position: "absolute",
          top: 230,
          right: 140,
          width: 800,
          height: 450,
          zIndex: 40,
          opacity,
          transform: `translateY(${liftY}px)`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          backgroundColor: "rgba(12, 11, 10, 0.72)",
          border: "2px solid rgba(185, 28, 28, 0.75)",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.85), inset 0 0 30px rgba(0, 0, 0, 0.6)",
          padding: "24px 30px",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span
            style={{
              fontFamily: "'Courier New', monospace",
              fontSize: 15,
              fontWeight: 700,
              letterSpacing: "2.4px",
              color: "#fca5a5",
            }}
          >
            NEXT DECLASSIFIED DOSSIER
          </span>
          <span
            style={{
              fontFamily: "'Courier New', monospace",
              fontSize: 14,
              color: "rgba(230, 222, 203, 0.7)",
              letterSpacing: "1.4px",
            }}
          >
            SELECT FILE ON SCREEN &rarr;
          </span>
        </div>

        {/* Inner Dark Frame Sized Cleanly for YouTube 16:9 End-Screen Video Tile */}
        <div
          style={{
            flex: 1,
            marginTop: 18,
            marginBottom: 14,
            border: "1px dashed rgba(230, 222, 203, 0.35)",
            backgroundColor: "rgba(0, 0, 0, 0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px 32px",
          }}
        >
          <div
            style={{
              fontFamily: "Georgia, 'Times New Roman', serif",
              fontSize: 28,
              fontWeight: 700,
              color: "#f5efe2",
              textAlign: "center",
              lineHeight: 1.35,
            }}
          >
            {nextTitle}
          </div>
        </div>
      </div>

      <DustParticles />
      <AtmosphereOverlay citation={citation} />
    </div>
  );
};
