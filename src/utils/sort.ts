import type { DefacementRecord } from "../types/record";

export function sortByReportedAtDesc(records: DefacementRecord[]) {
  return [...records].sort(
    (a, b) =>
      new Date(b.reportedAt).getTime() - new Date(a.reportedAt).getTime(),
  );
}
