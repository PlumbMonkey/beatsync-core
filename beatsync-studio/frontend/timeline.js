// timeline.js — literal rendering for Slice 4.2
export function renderTimeline(json) {
  const beats = (json.rhythm && json.rhythm.beats) || [];
  const bars = (json.rhythm && json.rhythm.bars) || [];
  const sections = json.structure || [];
  const energy = (json.energy && json.energy.curve) || [];
  const width = 800;
  const height = 200;
  const beatSpacing = beats.length > 1 ? width / (beats.length - 1) : width;
  const energyY = v => height - v * (height - 40) - 20;
  return `
    <svg width="${width}" height="${height}" style="background:#f8f8f8">
      ${beats.map((b, i) => `<line x1="${i * beatSpacing}" y1="160" x2="${i * beatSpacing}" y2="200" stroke="#333" stroke-width="1" />`).join('')}
      ${bars.map((b, i) => `<rect x="${i * beatSpacing * 4}" y="150" width="3" height="50" fill="#0074d9" />`).join('')}
      ${sections.map(s => {
        const x1 = (beats.findIndex(bt => bt >= s.start)) * beatSpacing;
        const x2 = (beats.findIndex(bt => bt >= s.end)) * beatSpacing;
        return `<rect x="${x1}" y="20" width="${x2-x1}" height="30" fill="#aaa" opacity="0.3" />`;
      }).join('')}
      <polyline fill="none" stroke="#ff4136" stroke-width="2" points="${energy.map((e,i) => `${i * (width/(energy.length-1))},${energyY(e)}`).join(' ')}" />
    </svg>
  `;
}
