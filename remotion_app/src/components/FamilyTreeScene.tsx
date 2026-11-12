import React from "react";
import { Audio, Img, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { AtmosphereOverlay } from "./AtmosphereOverlay";
import { DustParticles } from "./DustParticles";
import { FamilyTreeData } from "../types";

interface Props {
  treeData: FamilyTreeData;
  durationInFrames: number;
  citation?: string;
  hasBoom?: boolean;
}

export const FamilyTreeScene: React.FC<Props> = ({
  treeData,
  durationInFrames,
  citation,
  hasBoom = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Slow continuous push into the tree board
  const boardScale = interpolate(frame, [0, durationInFrames], [0.97, 1.03]);

  // Overall entrance spring
  const treeSpring = spring({
    frame: frame - 5,
    fps,
    config: { damping: 16, stiffness: 80 },
  });
  const boardOpacity = Math.min(1, Math.max(0, treeSpring));

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#0a0908",
        overflow: "hidden",
      }}
    >
      {/* SFX */}
      <Audio src={staticFile("audio/sfx_paper_slide.wav")} volume={0.22} />
      <Sequence from={14}>
        <Audio src={staticFile("audio/sfx_typewriter_stamp.wav")} volume={0.24} />
      </Sequence>
      {hasBoom && (
        <Sequence from={0}>
          <Audio src={staticFile("audio/sfx_sub_boom.wav")} volume={0.12} />
        </Sequence>
      )}

      {/* 1. Archival Blackboard / Desk Blueprint Background */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          transform: `scale(${boardScale})`,
          opacity: boardOpacity,
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "#0d0b09",
            backgroundImage:
              "radial-gradient(#1e1814 1px, transparent 1px), radial-gradient(#1e1814 1px, #0d0b09 1px)",
            backgroundSize: "40px 40px",
            backgroundPosition: "0 0, 20px 20px",
          }}
        />
      </div>

      {/* 2. Title Banner */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 30,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          opacity: boardOpacity,
        }}
      >
        <div
          style={{
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontSize: 28,
            fontWeight: 800,
            color: "#f5f0e6",
            letterSpacing: "3px",
            textTransform: "uppercase",
            textShadow: "0 2px 8px rgba(0,0,0,0.9)",
          }}
        >
          {treeData.title}
        </div>
        {treeData.subtitle && (
          <div
            style={{
              fontFamily: "'Courier New', Courier, monospace",
              fontSize: 15,
              fontWeight: 600,
              color: "#a89984",
              marginTop: 4,
              letterSpacing: "1.5px",
            }}
          >
            {treeData.subtitle}
          </div>
        )}
      </div>

      {/* 3. Connecting SVG Lines (Red Thread of Bloodline) */}
      <svg
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          zIndex: 15,
          pointerEvents: "none",
        }}
      >
        {treeData.links.map((link, idx) => {
          const fromNode = treeData.nodes.find((n) => n.id === link.from);
          const toNode = treeData.nodes.find((n) => n.id === link.to);
          if (!fromNode || !toNode) return null;

          const x1 = (fromNode.x / 100) * 1920;
          const y1 = (fromNode.y / 100) * 1080;
          const x2 = (toNode.x / 100) * 1920;
          const y2 = (toNode.y / 100) * 1080;

          // Animated progressive line draw
          const linkSpring = spring({
            frame: frame - 12 - idx * 4,
            fps,
            config: { damping: 18, stiffness: 90 },
          });
          const progress = Math.min(1, Math.max(0, linkSpring));

          const curX2 = x1 + (x2 - x1) * progress;
          const curY2 = y1 + (y2 - y1) * progress;

          return (
            <line
              key={`${link.from}-${link.to}`}
              x1={x1}
              y1={y1}
              x2={curX2}
              y2={curY2}
              stroke={link.color || "#8b1e1e"}
              strokeWidth="3"
              strokeDasharray={link.style === "dashed" ? "6 5" : "none"}
              opacity={progress}
            />
          );
        })}
      </svg>

      {/* 4. Genealogical Person Nodes */}
      {treeData.nodes.map((node, idx) => {
        const nodeSpring = spring({
          frame: frame - 10 - idx * 6,
          fps,
          config: { damping: 14, mass: 0.6, stiffness: 120 },
        });
        const nodeScale = Math.min(1, Math.max(0, nodeSpring));
        const posX = (node.x / 100) * 1920;
        const posY = (node.y / 100) * 1080;

        return (
          <div
            key={node.id}
            style={{
              position: "absolute",
              left: posX,
              top: posY,
              transform: `translate(-50%, -50%) scale(${nodeScale})`,
              zIndex: 25,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              opacity: nodeScale,
            }}
          >
            {/* Oval Portrait Thumbnail with Antique Ring */}
            <div
              style={{
                width: 110,
                height: 110,
                borderRadius: "50%",
                border: "3px solid #d4af37",
                boxShadow:
                  "0 15px 30px rgba(0, 0, 0, 0.9), inset 0 0 10px rgba(0, 0, 0, 0.8)",
                overflow: "hidden",
                backgroundColor: "#1c1917",
                position: "relative",
              }}
            >
              {node.image ? (
                <Img
                  src={staticFile(node.image)}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    filter: "contrast(1.1) brightness(0.9) sepia(0.2)",
                  }}
                />
              ) : (
                <div
                  style={{
                    width: "100%",
                    height: "100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#854d0e",
                    fontFamily: "Georgia, serif",
                    fontSize: 36,
                    fontWeight: 700,
                  }}
                >
                  {node.isQuestion ? "?" : "—"}
                </div>
              )}

              {/* Red Question Badge for disputed paternity */}
              {node.isQuestion && (
                <div
                  style={{
                    position: "absolute",
                    bottom: 2,
                    right: 2,
                    backgroundColor: "#b91c1c",
                    color: "#fff",
                    borderRadius: "50%",
                    width: 26,
                    height: 26,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 16,
                    fontWeight: 900,
                    boxShadow: "0 2px 5px rgba(0,0,0,0.8)",
                  }}
                >
                  ?
                </div>
              )}
            </div>

            {/* Name Plate */}
            <div
              style={{
                backgroundColor: "#f5f0e6",
                padding: "6px 14px",
                marginTop: 8,
                borderRadius: 2,
                boxShadow: "0 6px 15px rgba(0, 0, 0, 0.7)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                maxWidth: 220,
              }}
            >
              <span
                style={{
                  fontFamily: "Georgia, serif",
                  fontSize: 14,
                  fontWeight: 700,
                  color: "#181512",
                  textAlign: "center",
                  whiteSpace: "nowrap",
                }}
              >
                {node.name}
              </span>
              <span
                style={{
                  fontFamily: "'Courier New', monospace",
                  fontSize: 11,
                  color: "#6b5c4c",
                  marginTop: 2,
                  textAlign: "center",
                }}
              >
                {node.role} {node.year ? `(${node.year})` : ""}
              </span>
            </div>
          </div>
        );
      })}

      {/* 5. Atmosphere */}
      <DustParticles />
      <AtmosphereOverlay citation={citation} />
    </div>
  );
};
