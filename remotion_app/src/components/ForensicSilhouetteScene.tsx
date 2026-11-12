import React from "react";
import { Audio, Easing, Img, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { TornTapeLabel } from "./TornTapeLabel";

interface Props {
  bgImage: string;
  durationInFrames: number;
  silhouetteType?: "nepomuk" | "unknown_father" | "brothers" | "classified";
  stampText?: string;
  stampSubtext?: string;
  labelTitle?: string;
  labelSubtitle?: string;
  hasBoom?: boolean;
  citation?: string;
}

export const ForensicSilhouetteScene: React.FC<Props> = ({
  bgImage,
  durationInFrames,
  silhouetteType = "nepomuk",
  stampText = "NO CONFIRMED PHOTOGRAPH",
  stampSubtext = "HISTORICAL RECORD DEFICIT // ARCHIVAL VOID",
  labelTitle,
  labelSubtitle,
  hasBoom = false,
  citation,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const easeCinematic = Easing.bezier(0.22, 0.1, 0.25, 1.0);

  // Background slow zoom & drift
  const bgScale = interpolate(frame, [0, durationInFrames], [1.02, 1.1], {
    easing: easeCinematic,
  });
  const bgTranslateX = interpolate(frame, [0, durationInFrames], [-6, 6], {
    easing: easeCinematic,
  });

  // Silhouette slow continuous push and subtle perspective tilt
  const silScale = interpolate(frame, [0, durationInFrames], [1.0, 1.06], {
    easing: easeCinematic,
  });
  const silTranslateY = interpolate(frame, [0, durationInFrames], [8, -8], {
    easing: easeCinematic,
  });

  // Forensic Stamp slamming down at frame 14
  const stampSpring = spring({
    frame: frame - 14,
    fps,
    config: {
      damping: 12,
      stiffness: 180,
    },
  });
  const stampScale = interpolate(stampSpring, [0, 1], [2.4, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const stampOpacity = interpolate(stampSpring, [0, 0.2, 1], [0, 0.95, 0.92], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Camera micro-shake on stamp impact (frame 14-18)
  const shakeX = frame >= 14 && frame <= 18 ? Math.sin((frame - 14) * 3) * 3 : 0;
  const shakeY = frame >= 14 && frame <= 18 ? Math.cos((frame - 14) * 3) * 3 : 0;

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#080706",
        overflow: "hidden",
        transform: `translate(${shakeX}px, ${shakeY}px)`,
      }}
    >
      {/* 1. Diegetic Foley Audio */}
      <Audio src={staticFile("audio/sfx_paper_slide.wav")} volume={0.22} />
      <Sequence from={14}>
        <Audio src={staticFile("audio/sfx_typewriter_stamp.wav")} volume={0.28} />
      </Sequence>
      {hasBoom && (
        <Sequence from={0}>
          <Audio src={staticFile("audio/sfx_sub_boom.wav")} volume={0.12} />
        </Sequence>
      )}

      {/* 2. Archival Background */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          transform: `scale(${bgScale}) translateX(${bgTranslateX}px)`,
          filter: "blur(4px) brightness(0.42) contrast(1.2) sepia(0.35)",
        }}
      >
        <Img
          src={staticFile(bgImage)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>

      {/* Vignette & Grayscale overlay */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background:
            "radial-gradient(circle at 50% 50%, rgba(10,9,8,0.2) 20%, rgba(5,4,3,0.85) 90%)",
          zIndex: 5,
        }}
      />

      {/* 3. Forensic Archival Grid / Registration Crosshairs */}
      <div
        style={{
          position: "absolute",
          top: 60,
          right: 70,
          zIndex: 15,
          fontFamily: "'Courier New', Courier, monospace",
          fontSize: 13,
          letterSpacing: 2,
          color: "rgba(220, 38, 38, 0.8)",
          textTransform: "uppercase",
          border: "1px solid rgba(220, 38, 38, 0.4)",
          padding: "6px 14px",
          backgroundColor: "rgba(0, 0, 0, 0.65)",
        }}
      >
        [ ARCHIVAL RECORD DEFICIT // DEPT. INVESTIGATION ]
      </div>

      {/* 4. Forensic Silhouette Figure Layer */}
      <div
        style={{
          position: "absolute",
          top: "46%",
          left: "50%",
          transform: `translate(-50%, -50%) translateY(${silTranslateY}px) scale(${silScale})`,
          zIndex: 20,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {/* Archival Silhouette Graphic */}
        <div
          style={{
            position: "relative",
            width: silhouetteType === "brothers" ? 720 : 480,
            height: 580,
            filter: "drop-shadow(0 25px 45px rgba(0, 0, 0, 0.95))",
          }}
        >
          {/* Nepomuk / 19th Century Austrian Peasant Elder Silhouette */}
          {silhouetteType === "nepomuk" && (
            <svg
              viewBox="0 0 400 500"
              style={{ width: "100%", height: "100%", display: "block" }}
            >
              <defs>
                <linearGradient id="peasantGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#1e1c18" />
                  <stop offset="60%" stopColor="#12100d" />
                  <stop offset="100%" stopColor="#080706" />
                </linearGradient>
              </defs>
              {/* Silhouette Head & Hat/Cap of 19th c. Austrian Peasant Patriarch */}
              <path
                d="M200 40 C165 40 140 70 140 115 C140 150 155 180 180 195 C110 220 80 280 70 380 C65 430 60 480 60 500 L340 500 C340 480 335 430 330 380 C320 280 290 220 220 195 C245 180 260 150 260 115 C260 70 235 40 200 40 Z"
                fill="url(#peasantGrad)"
              />
              {/* Traditional High Coat Collar / Scarf silhouette lines */}
              <path
                d="M175 190 L200 230 L225 190 L210 260 L190 260 Z"
                fill="#0d0c0a"
                opacity="0.8"
              />
            </svg>
          )}

          {/* Unknown Father / Disputed Paternity Silhouette */}
          {silhouetteType === "unknown_father" && (
            <svg
              viewBox="0 0 400 500"
              style={{ width: "100%", height: "100%", display: "block" }}
            >
              <defs>
                <linearGradient id="fatherGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#221e1a" />
                  <stop offset="70%" stopColor="#100e0b" />
                  <stop offset="100%" stopColor="#070605" />
                </linearGradient>
              </defs>
              {/* Male Profile / Questioned Silhouette */}
              <path
                d="M200 50 C155 50 130 90 130 140 C130 185 155 210 175 220 C115 245 85 295 75 390 C70 440 65 480 65 500 L335 500 C335 480 330 440 325 390 C315 295 285 245 225 220 C245 210 270 185 270 140 C270 90 245 50 200 50 Z"
                fill="url(#fatherGrad)"
              />
              {/* Subtle Question Mark Archival Imprint */}
              <text
                x="200"
                y="320"
                fontFamily="'Courier New', Courier, monospace"
                fontSize="140"
                fontWeight="bold"
                fill="rgba(220, 38, 38, 0.22)"
                textAnchor="middle"
              >
                ?
              </text>
            </svg>
          )}

          {/* Stuart-Houston Brothers / The Silence Pact Trio Silhouette */}
          {silhouetteType === "brothers" && (
            <svg
              viewBox="0 0 700 500"
              style={{ width: "100%", height: "100%", display: "block" }}
            >
              <defs>
                <linearGradient id="brotherGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#25211c" />
                  <stop offset="60%" stopColor="#14110d" />
                  <stop offset="100%" stopColor="#080706" />
                </linearGradient>
              </defs>
              {/* Left Brother Silhouette */}
              <path
                d="M170 110 C140 110 120 135 120 170 C120 205 135 225 150 235 C100 255 75 300 70 380 L65 500 L275 500 L270 380 C265 300 240 255 190 235 C205 225 220 205 220 170 C220 135 200 110 170 110 Z"
                fill="url(#brotherGrad)"
                opacity="0.85"
              />
              {/* Right Brother Silhouette */}
              <path
                d="M530 110 C500 110 480 135 480 170 C480 205 495 225 510 235 C460 255 435 300 430 380 L425 500 L635 500 L630 380 C625 300 600 255 550 235 C565 225 580 205 580 170 C580 135 560 110 530 110 Z"
                fill="url(#brotherGrad)"
                opacity="0.85"
              />
              {/* Center Brother Silhouette (Foreground) */}
              <path
                d="M350 70 C310 70 285 105 285 150 C285 195 305 220 325 230 C260 255 230 305 220 390 L215 500 L485 500 L480 390 C470 305 440 255 375 230 C395 220 415 195 415 150 C415 105 390 70 350 70 Z"
                fill="#0d0c0a"
              />
            </svg>
          )}

          {/* Classified / Generic Dossier Silhouette */}
          {silhouetteType === "classified" && (
            <svg
              viewBox="0 0 400 500"
              style={{ width: "100%", height: "100%", display: "block" }}
            >
              <defs>
                <linearGradient id="classGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#1e1b17" />
                  <stop offset="60%" stopColor="#110f0c" />
                  <stop offset="100%" stopColor="#080706" />
                </linearGradient>
              </defs>
              <path
                d="M200 60 C160 60 135 95 135 145 C135 190 155 215 175 225 C115 250 85 300 75 390 L70 500 L330 500 L325 390 C315 300 285 250 225 225 C245 215 265 190 265 145 C265 95 240 60 200 60 Z"
                fill="url(#classGrad)"
              />
            </svg>
          )}
        </div>

        {/* 5. The Forensic Red Stamp (Animated Slam on Frame 14) */}
        {stampSpring > 0.05 && (
          <div
            style={{
              position: "absolute",
              top: "48%",
              transform: `scale(${stampScale}) rotate(-8deg)`,
              opacity: stampOpacity,
              zIndex: 35,
              pointerEvents: "none",
              border: "4px double rgba(220, 38, 38, 0.92)",
              backgroundColor: "rgba(15, 10, 8, 0.88)",
              padding: "12px 28px",
              boxShadow: "0 0 25px rgba(220, 38, 38, 0.45), inset 0 0 15px rgba(220, 38, 38, 0.25)",
              textAlign: "center",
              minWidth: 420,
            }}
          >
            <div
              style={{
                fontFamily: "'Courier New', Courier, monospace",
                fontSize: 22,
                fontWeight: 900,
                color: "#ef4444",
                letterSpacing: 3,
                textTransform: "uppercase",
                textShadow: "0 2px 8px rgba(0,0,0,0.9)",
              }}
            >
              [ {stampText} ]
            </div>
            {stampSubtext && (
              <div
                style={{
                  fontFamily: "'Courier New', Courier, monospace",
                  fontSize: 11,
                  fontWeight: 700,
                  color: "#fca5a5",
                  letterSpacing: 2,
                  marginTop: 4,
                  textTransform: "uppercase",
                  opacity: 0.85,
                }}
              >
                {stampSubtext}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 6. Torn Tape Label (Historical Identity & Metadata) */}
      {(labelTitle || labelSubtitle) && (
        <TornTapeLabel
          title={labelTitle || "HISTORICAL RECORD DEFICIT"}
          subtitle={labelSubtitle || "Archival Accession // Identity Unrecorded"}
          delayFrames={10}
        />
      )}

      {/* 7. Archival Overlays (Dust & Atmosphere) */}
      <AtmosphereOverlay />
      <DustParticles count={25} />

      {/* 8. Top Left Citation Badge */}
      {citation && (
        <div
          style={{
            position: "absolute",
            top: 40,
            left: 50,
            zIndex: 40,
            backgroundColor: "rgba(0, 0, 0, 0.75)",
            border: "1px solid rgba(255, 255, 255, 0.12)",
            padding: "4px 12px",
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: 11,
            color: "#a1a1aa",
            letterSpacing: 1.5,
          }}
        >
          {citation}
        </div>
      )}
    </div>
  );
};
