type FiltersProps = {
  countries: string[];
  sources: string[];
  selectedSource: string;
  onSourceChange: (source: string) => void;
  selectedCountry: string;
  mirrorAccessibleOnly: boolean;
  onCountryChange: (country: string) => void;
  onMirrorAccessibleOnlyChange: (enabled: boolean) => void;
};

export function Filters({
  countries,
  sources,
  selectedSource,
  onSourceChange,
  selectedCountry,
  mirrorAccessibleOnly,
  onCountryChange,
  onMirrorAccessibleOnlyChange,
}: FiltersProps) {
  return (
    <div className="filters" aria-label="Record filters">
      <label className="select-filter">
        <span>Source</span>
        <select value={selectedSource} onChange={(event) => onSourceChange(event.target.value)} aria-label="Filter by source">
          <option value="">All sources</option>
          {sources.map((source) => <option key={source} value={source}>{source}</option>)}
        </select>
      </label>
      <label className="select-filter">
        <span>Country</span>
        <select
          value={selectedCountry}
          onChange={(event) => onCountryChange(event.target.value)}
          aria-label="Filter by country"
        >
          <option value="">All countries</option>
          <option value="japan-related">日本関連 (JP / .jp)</option>
          {countries.map((country) => (
            <option key={country} value={country}>
              {country}
            </option>
          ))}
        </select>
      </label>

      <label className="checkbox-filter">
        <input
          type="checkbox"
          checked={mirrorAccessibleOnly}
          onChange={(event) =>
            onMirrorAccessibleOnlyChange(event.target.checked)
          }
        />
        <span>Mirror accessible only</span>
      </label>
    </div>
  );
}
