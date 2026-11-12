import React from "react";
import { Audio, Series, staticFile } from "remotion";
import { ParallaxCutoutScene } from "./components/ParallaxCutoutScene";
import { ParallaxDocumentScene } from "./components/ParallaxDocumentScene";
import { ParallaxLandscapeScene } from "./components/ParallaxLandscapeScene";
import { ParallaxVideoScene } from "./components/ParallaxVideoScene";
import { DocumentaryConfig } from "./types";

interface Props {
  config: DocumentaryConfig;
}

export const DocumentaryPilot: React.FC<Props> = ({ config }) => {
  return (
    <div
      style={{
        width: config.width,
        height: config.height,
        backgroundColor: "#000000",
      }}
    >
      {/* Background Orchestral Cello Soundtrack (Master Audio Track) */}
      {config.musicSrc && (
        <Audio
          src={staticFile(config.musicSrc)}
          volume={0.16}
          loop
        />
      )}

      {/* Sequential Beats Timeline */}
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

            {/* Visual Beat Composition */}
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

            {beat.layoutType === "document" && (
              <ParallaxDocumentScene
                bgImage={beat.bgImage}
                documentImage={beat.subjectImage || beat.bgImage}
                durationInFrames={beat.durationInFrames}
                labelTitle={beat.labelTitle}
                labelSubtitle={beat.labelSubtitle}
                highlightText={beat.highlightText}
                hasBoom={beat.hasBoom}
                citation={beat.citation}
              />
            )}

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
          </Series.Sequence>
        ))}
      </Series>
    </div>
  );
};
