export interface TreeNode {
  id: string;
  name: string;
  role: string;
  year?: string;
  image?: string;
  x: number; // percentage (0 - 100)
  y: number; // percentage (0 - 100)
  isDead?: boolean;
  isQuestion?: boolean;
}

export interface TreeLink {
  from: string;
  to: string;
  style?: "solid" | "dashed";
  color?: string;
}

export interface FamilyTreeData {
  title: string;
  subtitle?: string;
  nodes: TreeNode[];
  links: TreeLink[];
}

export interface SplitCollageData {
  leftDocument: string;
  rightSubject: string;
  highlightText?: string;
  connectionLabel?: string;
}

export interface BeatData {
  id: string;
  durationInFrames: number;
  layoutType: "portrait" | "document" | "landscape" | "video" | "split_collage" | "family_tree" | "silhouette";
  bgImage: string;
  subjectImage?: string;
  videoSrc?: string;
  labelTitle?: string;
  labelSubtitle?: string;
  badgeText?: string;
  highlightText?: string;
  highlightStyle?: "marker" | "red_circle" | "both" | "stamp";
  stampText?: string;
  stampSubtext?: string;
  silhouetteType?: "nepomuk" | "unknown_father" | "brothers" | "classified";
  impactText?: string;
  impactFrame?: number;
  hasBoom?: boolean;
  citation?: string;
  audioSrc: string;
  splitData?: SplitCollageData;
  treeData?: FamilyTreeData;
}

export interface SoundtrackAct {
  actId: string;
  name: string;
  src: string;
  startFrame: number;
  durationInFrames: number;
}

export interface DocumentaryConfig {
  title: string;
  fps: number;
  width: number;
  height: number;
  musicSrc: string;
  soundtrackActs?: SoundtrackAct[];
  beats: BeatData[];
}
