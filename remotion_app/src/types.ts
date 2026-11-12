export interface BeatData {
  id: string;
  durationInFrames: number;
  layoutType: "portrait" | "document" | "landscape";
  bgImage: string;
  subjectImage?: string;
  labelTitle?: string;
  labelSubtitle?: string;
  badgeText?: string;
  highlightText?: string;
  audioSrc: string;
}

export interface DocumentaryConfig {
  title: string;
  fps: number;
  width: number;
  height: number;
  musicSrc: string;
  beats: BeatData[];
}
