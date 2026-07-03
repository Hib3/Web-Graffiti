export type DefacementRecord = {
  id: string;
  thumbnailUrl?: string;
  hackerName: string;
  hackedUrlDisplay: string;
  hackedUrlHash: string;
  country: string;
  countryCode: string;
  mirrorUrl: string;
  mirrorAccessible: boolean;
  source: string;
  sourceUrl?: string;
  reportedAt: string;
  fetchedAt: string;
  tags: string[];
  safetyFlags: string[];
};
