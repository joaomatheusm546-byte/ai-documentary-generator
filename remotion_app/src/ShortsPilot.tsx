import React from "react";
import { Audio, Sequence, Series, staticFile } from "remotion";
import { ShortsScene } from "./components/ShortsScene";
import { DocumentaryConfig } from "./types";

interface Props {
  config: DocumentaryConfig;
}

export const ShortsPilot: React.FC<Props> = ({ config }) => {
  const motions = ["zoom_in", "pan_right", "zoom_out", "pan_left"] as const;

  return (
    <div
      style={{
        width: config.width,
        height: config.height,
        backgroundColor: "#000000",
      }}
    >
      {config.musicSrc && (
        <Audio src={staticFile(config.musicSrc)} volume={0.18} loop />
      )}

      <Series>
        {config.beats.map((beat, idx) => (
          <Series.Sequence key={beat.id} durationInFrames={beat.durationInFrames}>
            {beat.audioSrc && <Audio src={staticFile(beat.audioSrc)} volume={1.0} />}

            {beat.sfxPreset === "boom" && (
              <Audio src={staticFile("audio/sfx_sub_boom.wav")} volume={0.2} />
            )}
            {beat.sfxPreset === "shutter" && (
              <Audio src={staticFile("audio/sfx_camera_shutter.wav")} volume={0.18} />
            )}
            {beat.sfxPreset === "subtle_slide" && (
              <Audio src={staticFile("audio/sfx_paper_slide.wav")} volume={0.18} />
            )}
            {beat.impactText && (
              <Sequence from={beat.impactFrame || 10}>
                <Audio src={staticFile("audio/sfx_typewriter_stamp.wav")} volume={0.2} />
              </Sequence>
            )}

            <ShortsScene
              layoutType={beat.layoutType}
              bgImage={beat.bgImage}
              subjectImage={beat.subjectImage}
              durationInFrames={beat.durationInFrames}
              labelTitle={beat.labelTitle}
              labelSubtitle={beat.labelSubtitle}
              highlightText={beat.highlightText}
              highlightStyle={beat.highlightStyle}
              highlightY={beat.highlightY}
              impactText={beat.impactText}
              impactFrame={beat.impactFrame || 10}
              hookBanner={beat.hookBanner}
              motionVariant={beat.motionVariant || motions[idx % motions.length]}
              ctaNextTitle={beat.ctaData?.nextDossierTitle}
            />
          </Series.Sequence>
        ))}
      </Series>
    </div>
  );
};
