type FiltersProps = {
  countries: string[];
  selectedCountry: string;
  mirrorAccessibleOnly: boolean;
  onCountryChange: (country: string) => void;
  onMirrorAccessibleOnlyChange: (enabled: boolean) => void;
};

export function Filters({
  countries,
  selectedCountry,
  mirrorAccessibleOnly,
  onCountryChange,
  onMirrorAccessibleOnlyChange,
}: FiltersProps) {
  return (
    <div className="filters" aria-label="Record filters">
      <label className="select-filter">
        <span>Country</span>
        <select
          value={selectedCountry}
          onChange={(event) => onCountryChange(event.target.value)}
          aria-label="Filter by country"
        >
          <option value="">All countries</option>
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
