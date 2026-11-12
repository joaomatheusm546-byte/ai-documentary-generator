import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";

interface Particle {
  id: number;
  initialX: number;
  initialY: number;
  size: number;
  speedY: number;
  speedX: number;
  opacity: number;
}

export const DustParticles: React.FC = () => {
  const frame = useCurrentFrame();

  const particles: Particle[] = useMemo(() => {
    const list: Particle[] = [];
    for (let i = 0; i < 35; i++) {
      const pseudoRand = (seed: number) => {
        const x = Math.sin(seed * 9999) * 10000;
        return x - Math.floor(x);
      };
      list.push({
        id: i,
        initialX: pseudoRand(i * 1.7) * 1920,
        initialY: pseudoRand(i * 3.1) * 1080,
        size: 1.5 + pseudoRand(i * 5.3) * 3.5,
        speedY: 0.25 + pseudoRand(i * 7.1) * 0.45,
        speedX: (pseudoRand(i * 11.3) - 0.5) * 0.3,
        opacity: 0.2 + pseudoRand(i * 13.7) * 0.5,
      });
    }
    return list;
  }, []);

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 45,
        overflow: "hidden",
      }}
    >
      {particles.map((p) => {
        const currentY = (p.initialY - frame * p.speedY + 1080 * 10) % 1080;
        const currentX =
          (p.initialX +
            Math.sin(frame * 0.02 + p.id) * 20 +
            frame * p.speedX +
            1920 * 10) %
          1920;

        return (
          <div
            key={p.id}
            style={{
              position: "absolute",
              left: currentX,
              top: currentY,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              backgroundColor: "#fef3c7",
              opacity: p.opacity,
              boxShadow: `0 0 ${p.size * 2}px rgba(254, 243, 199, 0.8)`,
              filter: "blur(0.5px)",
            }}
          />
        );
      })}
    </div>
  );
};
