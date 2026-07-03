import type { DefacementRecord } from "../types/record";
import { RecordCard } from "./RecordCard";

type RecordListProps = {
  records: DefacementRecord[];
};

export function RecordList({ records }: RecordListProps) {
  if (records.length === 0) {
    return (
      <section className="empty-state" aria-live="polite">
        No records match the current filters.
      </section>
    );
  }

  return (
    <section className="record-list" aria-label="Defacement records">
      {records.map((record) => (
        <RecordCard key={record.id} record={record} />
      ))}
    </section>
  );
}
