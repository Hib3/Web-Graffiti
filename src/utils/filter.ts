import type { DefacementRecord } from "../types/record";

export type RecordFilters = {
  query: string;
  country: string;
  mirrorAccessibleOnly: boolean;
};

export function filterRecords(
  records: DefacementRecord[],
  filters: RecordFilters,
) {
  const query = filters.query.trim().toLowerCase();

  return records.filter((record) => {
    if (filters.mirrorAccessibleOnly && !record.mirrorAccessible) {
      return false;
    }

    const japanRelated = record.countryCode === "JP" || record.hackedUrl.split("/")[0].endsWith(".jp");
    if (filters.country === "japan-related" ? !japanRelated : filters.country && record.country !== filters.country) {
      return false;
    }

    if (!query) {
      return true;
    }

    const searchable = [
      record.hackerName,
      record.hackedUrl,
      record.country ?? "",
      record.countryCode ?? "",
      japanRelated ? "日本 Japan" : "",
      record.source,
    ]
      .join(" ")
      .toLowerCase();

    return searchable.includes(query);
  });
}

export function getCountries(records: DefacementRecord[]) {
  return Array.from(
    new Set(records.map((record) => record.country).filter(Boolean) as string[]),
  ).sort((a, b) => a.localeCompare(b));
}
