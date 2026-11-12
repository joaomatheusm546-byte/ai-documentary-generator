export interface BeatData {
  id: string;
  durationInFrames: number;
  layoutType: "portrait" | "document" | "landscape" | "video";
  bgImage: string;
  subjectImage?: string;
  videoSrc?: string;
  labelTitle?: string;
  labelSubtitle?: string;
  badgeText?: string;
  highlightText?: string;
  hasBoom?: boolean;
  citation?: string;
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
