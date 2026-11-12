import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

interface Props {
  title?: string;
  subtitle?: string;
  delayFrames?: number;
  position?: "pinned-left" | "lower-left";
}

export const TornTapeLabel: React.FC<Props> = ({
  title,
  subtitle,
  delayFrames = 12,
  position = "pinned-left",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!title) return null;

  const entrance = spring({
    frame: frame - delayFrames,
    fps,
    config: {
      damping: 15,
      mass: 0.6,
      stiffness: 140,
    },
  });

  const opacity = Math.min(1, Math.max(0, entrance));
  const translateY = (1 - entrance) * 25;
  const scale = 0.9 + entrance * 0.1;
  const rotation = -5.5 + (1 - entrance) * -3;

  // Position: either pinned on the lower-left of the subject or bottom-left corner
  const posStyle: React.CSSProperties =
    position === "pinned-left"
      ? { bottom: 180, left: 180 }
      : { bottom: 90, left: 110 };

  return (
    <div
      style={{
        position: "absolute",
        ...posStyle,
        zIndex: 40,
        opacity,
        transform: `translateY(${translateY}px) scale(${scale}) rotate(${rotation}deg)`,
        transformOrigin: "center center",
      }}
    >
      {/* Torn Paper Strip Container with Authentic Jagged Ends */}
      <div
        style={{
          position: "relative",
          backgroundColor: "#f6f3eb",
          backgroundImage:
            "linear-gradient(175deg, rgba(255,255,255,0.7) 0%, rgba(240,233,220,0.95) 100%)",
          padding: "12px 34px 14px 34px",
          boxShadow:
            "0 12px 24px rgba(0, 0, 0, 0.75), 0 3px 6px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255,255,255,0.9)",
          clipPath:
            "polygon(0% 4%, 2% 0%, 5% 5%, 3% 15%, 6% 25%, 2% 40%, 5% 55%, 1% 70%, 4% 85%, 0% 100%, 96% 100%, 99% 88%, 96% 75%, 100% 60%, 97% 45%, 100% 30%, 96% 15%, 100% 0%, 2% 0%)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minWidth: 260,
        }}
      >
        {/* Title: Classical Serif in Title Case (After the Crown standard) */}
        <div
          style={{
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontSize: 27,
            fontWeight: 700,
            color: "#181512",
            letterSpacing: "0.5px",
            lineHeight: 1.15,
            textAlign: "center",
            textShadow: "0 1px 1px rgba(255,255,255,0.7)",
          }}
        >
          {title}
        </div>

        {/* Subtitle: Centered Italic Serif (e.g. 'the heir', 'the unmarried mother') */}
        {subtitle && (
          <div
            style={{
              fontFamily: "Georgia, 'Times New Roman', serif",
              fontStyle: "italic",
              fontSize: 16,
              fontWeight: 400,
              color: "#4e4337",
              marginTop: 4,
              letterSpacing: "0.3px",
              textAlign: "center",
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
