// List of lines with their live status text (Japanese, as provided by ODPT).
export default function LineStatusList({ lines }) {
  if (!lines.length) return <p>No status reported.</p>

  return (
    <ul>
      {lines.map((line) => (
        <li key={line.railway}>
          {line.railway.split('.').pop()}: {line.status || line.text || 'no information'}
        </li>
      ))}
    </ul>
  )
}
