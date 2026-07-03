import type { DefacementRecord } from "../types/record";
import { formatLocalDate } from "../utils/date";

type RecordCardProps = {
  record: DefacementRecord;
};

export function RecordCard({ record }: RecordCardProps) {
  return (
    <article className="record-card">
      <div className="thumb-frame" aria-label="Mirror thumbnail">
        {record.thumbnailUrl ? (
          <img
            src={`${import.meta.env.BASE_URL}${record.thumbnailUrl.replace(/^\//, "")}`}
            alt={`Mirror thumbnail for ${record.hackerName}`}
            loading="lazy"
          />
        ) : (
          <div className="thumb-placeholder">Thumbnail required</div>
        )}
      </div>

      <div className="record-body">
        <div className="record-topline">
          <h2>{record.hackerName}</h2>
          <span className="country">
            {record.country} ({record.countryCode})
          </span>
        </div>

        <p className="masked-url" title="Masked victim URL, not clickable">
          {record.hackedUrlDisplay}
        </p>

        <dl className="record-meta">
          <div>
            <dt>Reported</dt>
            <dd>{formatLocalDate(record.reportedAt)}</dd>
          </div>
          <div>
            <dt>Source</dt>
            <dd>{record.source}</dd>
          </div>
          <div>
            <dt>Fetched</dt>
            <dd>{formatLocalDate(record.fetchedAt)}</dd>
          </div>
        </dl>

        <div className="record-footer">
          <div className="tags" aria-label="Tags">
            {record.tags.map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>

          {record.mirrorAccessible ? (
            <a
              className="mirror-button"
              href={record.mirrorUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              View mirror
            </a>
          ) : (
            <button className="mirror-button" type="button" disabled>
              Mirror unavailable
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
