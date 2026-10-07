import { useEffect, useMemo, useState } from "react";
import { Filters } from "./components/Filters";
import { RecordList } from "./components/RecordList";
import { SearchBar } from "./components/SearchBar";
import type { DefacementRecord } from "./types/record";
import { filterRecords } from "./utils/filter";
import { getCountries } from "./utils/filter";
import { sortByReportedAtDesc } from "./utils/sort";
import { formatLocalDate } from "./utils/date";

type LoadState = "idle" | "loading" | "ready" | "error";
type SourceStatus = {
  generatedAt: string;
  totalRecords: number;
  successfulSources: number;
  latestReportedAt?: string | null;
  sources: Array<{
    source: string;
    ok: boolean;
    recordCount: number;
    error: string | null;
    fetchedAt: string;
    warnings?: string[];
  }>;
};

function App() {
  const [records, setRecords] = useState<DefacementRecord[]>([]);
  const [sourceStatus, setSourceStatus] = useState<SourceStatus | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [country, setCountry] = useState("");
  const [mirrorAccessibleOnly, setMirrorAccessibleOnly] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    async function loadRecords() {
      setLoadState("loading");
      setError("");

      try {
        const [response, statusResponse] = await Promise.all([
          fetch(`${import.meta.env.BASE_URL}data/records.json`, {
            signal: controller.signal,
          }),
          fetch(`${import.meta.env.BASE_URL}data/source-status.json`, {
            signal: controller.signal,
          }),
        ]);

        if (!response.ok) {
          throw new Error(`Failed to load records: ${response.status}`);
        }
        if (!statusResponse.ok) {
          throw new Error(`Failed to load source status: ${statusResponse.status}`);
        }

        const data = (await response.json()) as DefacementRecord[];
        const status = (await statusResponse.json()) as SourceStatus;
        setRecords(sortByReportedAtDesc(data));
        setSourceStatus(status);
        setLoadState("ready");
      } catch (err) {
        if (controller.signal.aborted) {
          return;
        }

        setError(err instanceof Error ? err.message : "Failed to load records");
        setLoadState("error");
      }
    }

    loadRecords();

    return () => controller.abort();
  }, []);

  const countries = useMemo(() => getCountries(records), [records]);
  const visibleRecords = useMemo(
    () =>
      filterRecords(records, {
        query,
        country,
        mirrorAccessibleOnly,
      }),
    [records, query, country, mirrorAccessibleOnly],
  );

  return (
    <main className="app-shell">
      <header className="site-header">
        <div>
          <h1>Web Graffiti</h1>
          <p>Mirror-first archive for recognizing web defacement activity.</p>
        </div>
      </header>

      <section className="toolbar" aria-label="Search and filters">
        <SearchBar value={query} onChange={setQuery} />
        <Filters
          countries={countries}
          selectedCountry={country}
          mirrorAccessibleOnly={mirrorAccessibleOnly}
          onCountryChange={setCountry}
          onMirrorAccessibleOnlyChange={setMirrorAccessibleOnly}
        />
      </section>

      {sourceStatus && (
        <section className="source-status" aria-label="Source status">
          <strong>{sourceStatus.totalRecords} records</strong>
          <span>{sourceStatus.successfulSources} active sources</span>
          <span>Last collection: {formatLocalDate(sourceStatus.generatedAt)}</span>
          {sourceStatus.latestReportedAt && <span>Latest report: {formatLocalDate(sourceStatus.latestReportedAt)}</span>}
          {sourceStatus.sources.map((source) => (
            <span key={source.source} className={source.ok && !source.warnings?.length ? "ok" : "warn"} title={source.error || source.warnings?.join("; ")}>
              {source.source}: {source.ok ? `${source.recordCount}${source.warnings?.length ? " (partial)" : ""}` : "unavailable"}
            </span>
          ))}
        </section>
      )}

      {sourceStatus && Date.now() - Date.parse(sourceStatus.generatedAt) > 12 * 3600_000 && (
        <p role="status">収集の更新が12時間以上ありません。掲載情報は最新でない可能性があります。</p>
      )}
      {sourceStatus?.latestReportedAt && Date.now() - Date.parse(sourceStatus.latestReportedAt) > 7 * 86400_000 && (
        <p role="status">取得範囲の最新記録は7日以上前です。新たな攻撃がないことを意味しません。</p>
      )}

      {loadState === "loading" && (
        <section className="status-state" aria-live="polite">
          Loading records...
        </section>
      )}

      {loadState === "error" && (
        <section className="status-state error" aria-live="assertive">
          {error}
        </section>
      )}

      {loadState === "ready" && <RecordList records={visibleRecords} />}
    </main>
  );
}

export default App;
