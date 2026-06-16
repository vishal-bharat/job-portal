/**
 * GISMA-branded SVG spinner.
 * Usage: <Loader text="Finding your matches…" />
 */
export default function Loader({ text = 'Loading…', fullPage = false }) {
  const wrapper = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 18,
    padding: 40,
    ...(fullPage ? { minHeight: '60vh' } : {}),
  };

  return (
    <div style={wrapper}>
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Outer spinning ring */}
        <circle cx="32" cy="32" r="28" stroke="#e5e7eb" strokeWidth="5" />
        <circle
          cx="32" cy="32" r="28"
          stroke="#c9f04d"
          strokeWidth="5"
          strokeLinecap="round"
          strokeDasharray="44 132"
          strokeDashoffset="0"
        >
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="0 32 32"
            to="360 32 32"
            dur="0.9s"
            repeatCount="indefinite"
          />
        </circle>

        {/* GISMA "G" in centre */}
        <text
          x="32" y="37"
          textAnchor="middle"
          fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          fontWeight="800"
          fontSize="18"
          fill="#1a2238"
        >
          G
        </text>
      </svg>

      <div style={{ color: '#6b7494', fontSize: 14, fontWeight: 500 }}>{text}</div>
    </div>
  );
}
