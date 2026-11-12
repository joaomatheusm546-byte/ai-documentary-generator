import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

interface Props {
  title?: string;
  subtitle?: string;
  badge?: string;
  delayFrames?: number;
}

export const TornTapeLabel: React.FC<Props> = ({
  title,
  subtitle,
  badge,
  delayFrames = 10,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!title) return null;

  const entrance = spring({
    frame: frame - delayFrames,
    fps,
    config: {
      damping: 14,
      mass: 0.8,
      stiffness: 110,
    },
  });

  const opacity = Math.min(1, Math.max(0, entrance));
  const translateY = (1 - entrance) * 35;
  const rotation = (1 - entrance) * -3;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 85,
        left: 95,
        zIndex: 40,
        opacity,
        transform: `translateY(${translateY}px) rotate(${rotation}deg)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        maxWidth: 750,
      }}
    >
      {/* Category / Badge Tab */}
      {badge && (
        <div
          style={{
            backgroundColor: "#7f1d1d",
            color: "#fef2f2",
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: 13,
            fontWeight: 700,
            letterSpacing: "2.5px",
            textTransform: "uppercase",
            padding: "5px 14px 4px 14px",
            marginBottom: -2,
            marginLeft: 8,
            boxShadow: "0 4px 10px rgba(0,0,0,0.5)",
            border: "1px solid rgba(255,255,255,0.15)",
            clipPath: "polygon(0% 0%, 100% 0%, 96% 100%, 0% 100%)",
          }}
        >
          {badge}
        </div>
      )}

      {/* Main Torn Tape Card */}
      <div
        style={{
          position: "relative",
          backgroundColor: "#f4eee3",
          backgroundImage:
            "linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(0,0,0,0.04) 100%)",
          padding: "16px 28px 18px 24px",
          boxShadow:
            "0 18px 30px rgba(0,0,0,0.65), 0 4px 8px rgba(0,0,0,0.4), inset 0 1px 2px rgba(255,255,255,0.8)",
          borderLeft: "4px solid #8b1e1e",
          clipPath:
            "polygon(0% 2%, 98% 0%, 100% 97%, 99% 100%, 1% 99%, 0% 95%)",
        }}
      >
        {/* Subtle tape corner piece */}
        <div
          style={{
            position: "absolute",
            top: -10,
            right: 25,
            width: 55,
            height: 22,
            backgroundColor: "rgba(225, 215, 190, 0.65)",
            boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
            transform: "rotate(4deg)",
            backdropFilter: "blur(1px)",
            border: "1px dashed rgba(0,0,0,0.15)",
          }}
        />

        {/* Title */}
        <div
          style={{
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontSize: 32,
            fontWeight: 800,
            color: "#181410",
            letterSpacing: "1.2px",
            textTransform: "uppercase",
            lineHeight: 1.15,
            textShadow: "0 1px 1px rgba(255,255,255,0.8)",
          }}
        >
          {title}
        </div>

        {/* Subtitle */}
        {subtitle && (
          <div
            style={{
              fontFamily: "'Courier New', Courier, monospace",
              fontSize: 16,
              fontWeight: 600,
              color: "#544638",
              marginTop: 6,
              letterSpacing: "0.8px",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <span
              style={{
                width: 6,
                height: 6,
                backgroundColor: "#8b1e1e",
                display: "inline-block",
                borderRadius: "50%",
              }}
            />
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
