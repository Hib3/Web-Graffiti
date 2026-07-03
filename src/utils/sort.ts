import type { DefacementRecord } from "../types/record";

export function sortByReportedAtDesc(records: DefacementRecord[]) {
  return [...records].sort(
    (a, b) =>
      new Date(b.reportedAt ?? 0).getTime() -
      new Date(a.reportedAt ?? 0).getTime(),
  );
}
