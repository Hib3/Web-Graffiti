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

    if (filters.country && record.country !== filters.country) {
      return false;
    }

    if (!query) {
      return true;
    }

    const searchable = [
      record.hackerName,
      record.hackedUrlDisplay,
      record.country,
      ...record.tags,
    ]
      .join(" ")
      .toLowerCase();

    return searchable.includes(query);
  });
}

export function getCountries(records: DefacementRecord[]) {
  return Array.from(new Set(records.map((record) => record.country))).sort(
    (a, b) => a.localeCompare(b),
  );
}
