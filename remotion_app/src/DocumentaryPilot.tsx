import React from "react";
import { Audio, interpolate, Sequence, Series, staticFile, useCurrentFrame } from "remotion";
import { FamilyTreeScene } from "./components/FamilyTreeScene";
import { ForensicSilhouetteScene } from "./components/ForensicSilhouetteScene";
import { ImpactTextStamp } from "./components/ImpactTextStamp";
import { ParallaxCutoutScene } from "./components/ParallaxCutoutScene";
import { ParallaxDocumentScene } from "./components/ParallaxDocumentScene";
import { ParallaxLandscapeScene } from "./components/ParallaxLandscapeScene";
import { ParallaxSplitCollageScene } from "./components/ParallaxSplitCollageScene";
import { ParallaxVideoScene } from "./components/ParallaxVideoScene";
import { DocumentaryConfig, SoundtrackAct } from "./types";

interface Props {
  config: DocumentaryConfig;
}

const ActAudio: React.FC<{ act: SoundtrackAct }> = ({ act }) => {
  const frame = useCurrentFrame();

  // 45-frame crossfade at start and end of each musical act
  const fadeIn = interpolate(frame, [0, 45], [0, 0.16], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(
    frame,
    [act.durationInFrames - 45, act.durationInFrames],
    [0.16, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const volume = Math.min(fadeIn, fadeOut);

  return <Audio src={staticFile(act.src)} volume={volume} loop />;
};

export const DocumentaryPilot: React.FC<Props> = ({ config }) => {
  return (
    <div
      style={{
        width: config.width,
        height: config.height,
        backgroundColor: "#000000",
      }}
    >
      {/* 1. Multi-Act Narrative Soundtrack with Crossfading */}
      {config.soundtrackActs && config.soundtrackActs.length > 0 ? (
        <>
          {config.soundtrackActs.map((act) => (
            <Sequence
              key={act.actId}
              from={act.startFrame}
              durationInFrames={act.durationInFrames}
            >
              <ActAudio act={act} />
            </Sequence>
          ))}
        </>
      ) : (
        config.musicSrc && (
          <Audio src={staticFile(config.musicSrc)} volume={0.16} loop />
        )
      )}

      {/* 2. Sequential Beats Timeline */}
      <Series>
        {config.beats.map((beat) => (
          <Series.Sequence
            key={beat.id}
            durationInFrames={beat.durationInFrames}
          >
            {/* Beat Voiceover Narration */}
            {beat.audioSrc && (
              <Audio src={staticFile(beat.audioSrc)} volume={1.0} />
            )}

            {/* Kinetic Impact Words Stamp (if defined for this beat) */}
            {beat.impactText && (
              <ImpactTextStamp
                text={beat.impactText}
                delayFrames={beat.impactFrame || 18}
              />
            )}

            {/* A. Single Subject Cutout (Busto / Medium Close-up) */}
            {beat.layoutType === "portrait" && (
              <ParallaxCutoutScene
                bgImage={beat.bgImage}
                subjectImage={beat.subjectImage}
                durationInFrames={beat.durationInFrames}
                labelTitle={beat.labelTitle}
                labelSubtitle={beat.labelSubtitle}
                hasBoom={beat.hasBoom}
                citation={beat.citation}
              />
            )}

            {/* B. Archival 3D Document / Ledger */}
            {beat.layoutType === "document" && (
              <ParallaxDocumentScene
                bgImage={beat.bgImage}
                documentImage={beat.subjectImage || beat.bgImage}
                durationInFrames={beat.durationInFrames}
                labelTitle={beat.labelTitle}
                labelSubtitle={beat.labelSubtitle}
                highlightText={beat.highlightText}
                highlightStyle={beat.highlightStyle}
                hasBoom={beat.hasBoom}
                citation={beat.citation}
              />
            )}

            {/* B2. Forensic Silhouette Scene (Unrecorded / Secret Lineage) */}
            {beat.layoutType === "silhouette" && (
              <ForensicSilhouetteScene
                bgImage={beat.bgImage}
                durationInFrames={beat.durationInFrames}
                silhouetteType={beat.silhouetteType}
                stampText={beat.stampText}
                stampSubtext={beat.stampSubtext}
                labelTitle={beat.labelTitle}
                labelSubtitle={beat.labelSubtitle}
                hasBoom={beat.hasBoom}
                citation={beat.citation}
              />
            )}

            {/* C. Cinematic Establishing Landscape */}
            {beat.layoutType === "landscape" && (
              <ParallaxLandscapeScene
                imageSrc={beat.bgImage}
                durationInFrames={beat.durationInFrames}
                labelTitle={beat.labelTitle}
                labelSubtitle={beat.labelSubtitle}
                hasBoom={beat.hasBoom}
                citation={beat.citation}
              />
            )}

            {/* D. Historical Video Clip */}
            {beat.layoutType === "video" && beat.videoSrc && (
              <ParallaxVideoScene
                videoSrc={beat.videoSrc}
                durationInFrames={beat.durationInFrames}
                labelTitle={beat.labelTitle}
                labelSubtitle={beat.labelSubtitle}
                hasBoom={beat.hasBoom}
                citation={beat.citation}
              />
            )}

            {/* E. Split-Collage (Document on Left + Person on Right with Connection) */}
            {beat.layoutType === "split_collage" && beat.splitData && (
              <ParallaxSplitCollageScene
                bgImage={beat.bgImage}
                leftDocument={beat.splitData.leftDocument}
                rightSubject={beat.splitData.rightSubject}
                durationInFrames={beat.durationInFrames}
                labelTitle={beat.labelTitle}
                labelSubtitle={beat.labelSubtitle}
                highlightText={beat.splitData.highlightText}
                impactText={beat.impactText}
                hasBoom={beat.hasBoom}
                citation={beat.citation}
              />
            )}

            {/* F. Modular SVG Family Tree / Genealogical Board */}
            {beat.layoutType === "family_tree" && beat.treeData && (
              <FamilyTreeScene
                treeData={beat.treeData}
                durationInFrames={beat.durationInFrames}
                citation={beat.citation}
                hasBoom={beat.hasBoom}
              />
            )}
          </Series.Sequence>
        ))}
      </Series>
    </div>
  );
};
