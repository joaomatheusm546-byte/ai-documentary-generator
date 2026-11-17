import React from "react";
import { Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { DustParticles } from "./DustParticles";

type MotionVariant = "zoom_in" | "zoom_out" | "pan_left" | "pan_right";

interface Props {
  layoutType: string;
  bgImage: string;
  subjectImage?: string;
  durationInFrames: number;
  labelTitle?: string;
  labelSubtitle?: string;
  highlightText?: string;
  highlightStyle?: "marker" | "red_circle" | "both" | "stamp";
  highlightY?: number;
  impactText?: string;
  impactFrame?: number;
  hookBanner?: string;
  motionVariant?: MotionVariant;
  ctaNextTitle?: string;
}

export const ShortsScene: React.FC<Props> = ({
  layoutType,
  bgImage,
  subjectImage,
  durationInFrames,
  labelTitle,
  labelSubtitle,
  highlightText,
  highlightStyle = "both",
  highlightY = 44,
  impactText,
  impactFrame = 10,
  hookBanner,
  motionVariant = "zoom_in",
  ctaNextTitle = "FULL DECLASSIFIED DOSSIER",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const ease = Easing.bezier(0.22, 0.1, 0.25, 1.0);
  const popScale = interpolate(frame, [0, 4], [1.035, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const motionTable: Record<MotionVariant, { s0: number; s1: number; x0: number; x1: number }> = {
    zoom_in: { s0: 1.02, s1: 1.15, x0: -14, x1: 14 },
    zoom_out: { s0: 1.16, s1: 1.03, x0: 14, x1: -14 },
    pan_left: { s0: 1.08, s1: 1.13, x0: 28, x1: -28 },
    pan_right: { s0: 1.08, s1: 1.13, x0: -28, x1: 28 },
  };
  const m = motionTable[motionVariant] || motionTable.zoom_in;

  const bgScale =
    interpolate(frame, [0, durationInFrames], [m.s0, m.s1], {
      easing: ease,
      extrapolateRight: "clamp",
    }) * popScale;
  const bgPanX = interpolate(frame, [0, durationInFrames], [m.x0, m.x1], {
    easing: ease,
    extrapolateRight: "clamp",
  });

  const stampIn = spring({
    frame: frame - impactFrame,
    fps,
    config: { damping: 12, mass: 0.55, stiffness: 170 },
  });
  const stampOpacity = impactText
    ? Math.min(1, Math.max(0, stampIn)) *
      interpolate(frame, [impactFrame + 38, impactFrame + 50], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  const markerIn = spring({
    frame: frame - 10,
    fps,
    config: { damping: 16, stiffness: 95 },
  });
  const markerProg = Math.min(1, Math.max(0, markerIn));

  const isLayered = layoutType === "portrait" || layoutType === "document" || layoutType === "cta_short";

  return (
    <div
      style={{
        position: "relative",
        width: 1080,
        height: 1920,
        backgroundColor: "#070709",
        overflow: "hidden",
      }}
    >
      {/* 1. Full-Bleed Vertical Background */}
      <div
        style={{
          position: "absolute",
          inset: -45,
          transform: `scale(${bgScale}) translateX(${bgPanX}px)`,
          filter: isLayered
            ? "blur(7px) brightness(0.36) contrast(1.15) sepia(0.26)"
            : "brightness(0.84) contrast(1.16) sepia(0.22)",
        }}
      >
        <Img
          src={staticFile(bgImage)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>

      {/* 2. Top & Bottom Mobile UI Contrast Gradients */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.18) 22%, rgba(0,0,0,0.14) 58%, rgba(0,0,0,0.88) 82%, rgba(0,0,0,0.96) 100%)",
          zIndex: 10,
        }}
      />

      {/* 3. Top Case File Tag (Safely below mobile status bar & notch) */}
      {labelTitle && (
        <div
          style={{
            position: "absolute",
            top: 150,
            left: 64,
            right: 64,
            zIndex: 35,
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-start",
          }}
        >
          <div
            style={{
              backgroundColor: "#f5f0e4",
              borderLeft: "6px solid #991b1b",
              padding: "10px 22px",
              boxShadow: "0 12px 28px rgba(0,0,0,0.85)",
              maxWidth: "100%",
            }}
          >
            <div
              style={{
                fontFamily: "Georgia, 'Times New Roman', serif",
                fontSize: 30,
                fontWeight: 700,
                color: "#181512",
                letterSpacing: "0.8px",
                lineHeight: 1.15,
              }}
            >
              {labelTitle}
            </div>
            {labelSubtitle && (
              <div
                style={{
                  fontFamily: "Georgia, 'Times New Roman', serif",
                  fontStyle: "italic",
                  fontSize: 20,
                  color: "#4a3f34",
                  marginTop: 4,
                }}
              >
                {labelSubtitle}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 3B. Scroll-Stopper Hook Banner (Beats 1-2 Muted Feed Grabber) */}
      {hookBanner && (
        <div
          style={{
            position: "absolute",
            top: 295,
            left: 64,
            right: 64,
            zIndex: 38,
            display: "flex",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              backgroundColor: "rgba(153, 27, 27, 0.94)",
              border: "2px solid #fef2f2",
              padding: "12px 26px",
              boxShadow: "0 14px 34px rgba(0,0,0,0.92)",
              textAlign: "center",
            }}
          >
            <span
              style={{
                fontFamily: "Impact, 'Arial Black', sans-serif",
                fontSize: 42,
                letterSpacing: "1.5px",
                color: "#ffffff",
                textTransform: "uppercase",
                textShadow: "0 3px 6px rgba(0,0,0,0.85)",
              }}
            >
              {hookBanner}
            </span>
          </div>
        </div>
      )}

      {/* 4A. Vertical Portrait Cutout (Top-Anchored above Subtitle Zone) */}
      {layoutType === "portrait" && subjectImage && (
        <div
          style={{
            position: "absolute",
            top: 295,
            left: "50%",
            height: 880,
            zIndex: 25,
            transform: `translateX(-50%) scale(${interpolate(frame, [0, durationInFrames], [1.0, 1.08], { easing: ease })})`,
            transformOrigin: "center top",
            filter: "drop-shadow(0 28px 46px rgba(0,0,0,0.95))",
          }}
        >
          <Img
            src={staticFile(subjectImage)}
            style={{ height: "100%", width: "auto", objectFit: "contain", filter: "contrast(1.12) brightness(0.96)" }}
          />
        </div>
      )}

      {/* 4B. Framed Archival Document with Animated Mobile Highlight */}
      {layoutType === "document" && (
        <div
          style={{
            position: "absolute",
            top: 360,
            left: "50%",
            width: 920,
            zIndex: 25,
            transform: `translateX(-50%) scale(${interpolate(frame, [0, durationInFrames], [0.96, 1.03], { easing: ease })})`,
            boxShadow: "0 30px 55px rgba(0,0,0,0.95)",
            border: "2px solid rgba(220, 210, 190, 0.22)",
            backgroundColor: "#141311",
          }}
        >
          <Img
            src={staticFile(subjectImage || bgImage)}
            style={{ width: "100%", height: "auto", display: "block", filter: "contrast(1.14) brightness(0.94)" }}
          />
          {highlightText && (highlightStyle === "marker" || highlightStyle === "both") && (
            <div
              style={{
                position: "absolute",
                top: `${highlightY}%`,
                left: "10%",
                width: `${markerProg * 80}%`,
                height: 46,
                backgroundColor: "rgba(250, 204, 21, 0.45)",
                border: "2px solid rgba(234, 179, 8, 0.9)",
                display: "flex",
                alignItems: "center",
                paddingLeft: 12,
                overflow: "hidden",
              }}
            >
              <span
                style={{
                  fontFamily: "'Courier New', monospace",
                  fontSize: 18,
                  fontWeight: 700,
                  color: "#451a03",
                  letterSpacing: 1.2,
                  whiteSpace: "nowrap",
                  opacity: markerProg,
                }}
              >
                {highlightText}
              </span>
            </div>
          )}
        </div>
      )}

      {/* 4C. Final Short CTA Card Pointing to Native Related Video Button */}
      {layoutType === "cta_short" && (
        <div
          style={{
            position: "absolute",
            top: 390,
            left: 72,
            right: 140,
            zIndex: 30,
            backgroundColor: "rgba(14, 12, 11, 0.86)",
            border: "2px solid rgba(185, 28, 28, 0.85)",
            padding: "40px 36px",
            boxShadow: "0 24px 60px rgba(0,0,0,0.92)",
          }}
        >
          <div
            style={{
              fontFamily: "'Courier New', monospace",
              fontSize: 20,
              fontWeight: 700,
              letterSpacing: "3px",
              color: "#fca5a5",
              marginBottom: 18,
            }}
          >
            DECLASSIFIED EVIDENCE // @AFTERMATHDOSSIER
          </div>
          <div
            style={{
              fontFamily: "Georgia, 'Times New Roman', serif",
              fontSize: 44,
              fontWeight: 700,
              color: "#f8f4ea",
              lineHeight: 1.22,
              marginBottom: 28,
            }}
          >
            {ctaNextTitle}
          </div>
          <div
            style={{
              display: "inline-block",
              backgroundColor: "#991b1b",
              color: "#ffffff",
              fontFamily: "'Courier New', monospace",
              fontSize: 22,
              fontWeight: 700,
              letterSpacing: "1.6px",
              padding: "14px 24px",
              transform: `translateY(${Math.sin(frame * 0.25) * 6}px)`,
            }}
          >
            ▼ WATCH FULL DOSSIER BELOW
          </div>
          <div
            style={{
              marginTop: 18,
              borderTop: "1px solid rgba(255,255,255,0.18)",
              paddingTop: 16,
              fontFamily: "'Courier New', monospace",
              fontSize: 18,
              fontWeight: 700,
              letterSpacing: "1.4px",
              color: "#fde68a",
            }}
          >
            + SUBSCRIBE FOR NEXT DECLASSIFIED FILE
          </div>
        </div>
      )}

      {/* 5. Kinetic Impact Red Stamp (Sized safely for 1080px width) */}
      {impactText && stampOpacity > 0.01 && (
        <div
          style={{
            position: "absolute",
            top: 980,
            left: "50%",
            transform: `translate(-50%, -50%) scale(${1.3 - stampIn * 0.3}) rotate(-3deg)`,
            zIndex: 45,
            opacity: stampOpacity,
          }}
        >
          <div
            style={{
              border: "4px solid #991b1b",
              backgroundColor: "rgba(18, 12, 10, 0.72)",
              padding: "10px 26px",
              boxShadow: "0 14px 32px rgba(0,0,0,0.9)",
            }}
          >
            <span
              style={{
                fontFamily: "Georgia, 'Times New Roman', serif",
                fontSize: 34,
                fontWeight: 900,
                letterSpacing: "3px",
                color: "#fecaca",
                whiteSpace: "nowrap",
              }}
            >
              {impactText}
            </span>
          </div>
        </div>
      )}

      <DustParticles />
    </div>
  );
};
