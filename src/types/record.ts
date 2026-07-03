export type DefacementRecord = {
  id: string;
  source: string;
  sourceUrl: string;
  thumbnailUrl: string | null;
  hackerName: string;
  hackedUrl: string;
  country: string | null;
  countryCode: string | null;
  mirrorUrl: string;
  mirrorAccessible: boolean;
  reportedAt: string | null;
  fetchedAt: string;
};
