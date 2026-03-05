# BeatSync UI - Development Guide

## Project Structure

```
beatsync-ui/
├── src/
│   ├── api/
│   │   └── beatsync.js              # Backend API client
│   ├── components/
│   │   ├── UploadZone.jsx           # File upload interface (drag-drop + click)
│   │   ├── TrackMeta.jsx            # BPM/key/duration display with confidence
│   │   ├── BeatTimeline.jsx         # Canvas-based interactive timeline
│   │   ├── SectionMap.jsx           # Section visualization (colored blocks)
│   │   ├── ExportPanel.jsx          # CSV/EDL export with FPS selector
│   │   ├── AnalysisResult.jsx       # Result container (orchestrates all display components)
│   │   └── ErrorBoundary.jsx        # Error catch boundary for graceful fallback
│   ├── utils/
│   │   ├── exportCsv.js             # CSV generation with 24/25/30fps columns
│   │   └── exportEdl.js             # CMX 3600 EDL format generation
│   ├── styles/                      # (Tailwind CSS via CDN, no local CSS needed)
│   ├── App.jsx                      # Main state machine (idle → selected → uploading → complete/error)
│   └── main.js                      # React entry point
├── index.html                       # HTML shell with Tailwind CDN
├── vite.config.js                   # Vite bundler configuration
├── package.json                     # Node dependencies
├── .env.example                     # Environment variable template
├── .gitignore                       # Ignore patterns for Git
├── vercel.json                      # Vercel deployment configuration
└── README.md                        # (This file)
```

## Technology Stack

- **Vite** ^5.0.0 — Fast build tool for React development
- **React** ^18.2.0 — UI component library with hooks
- **React DOM** ^18.2.0 — DOM rendering for React
- **Tailwind CSS** — Utility-first CSS (via CDN, no build step)
- **HTML5 Canvas** — Custom timeline visualization
- **Google Fonts (Inter)** — Typography

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create `.env.local` in the project root:

```env
VITE_API_URL=http://localhost:8000
```

Adjust the API URL based on your backend deployment:
- Local development: `http://localhost:8000`
- Production: `https://your-backend-domain.com`

### 3. Run Development Server

```bash
npm run dev
```

Opens at `http://localhost:5173` with hot module reload.

## Build & Deployment

### Build for Production

```bash
npm run build
```

Generates optimized bundle in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Deploy to Vercel

This project is configured for Vercel deployment with API proxying:

```bash
vercel
```

**Note:** Environment variable `VITE_API_URL` must be set in Vercel dashboard.

## Application Flow

### State Machine (App.jsx)

```
idle
  ↓ (file selected)
selected
  ↓ (analyze clicked)
uploading (API call in flight)
  ├→ complete (success → show AnalysisResult)
  └→ error (failure → show error message + retry)
```

### Component Hierarchy

```
App (state machine)
├── UploadZone (when state = idle/selected)
└── AnalysisResult (when state = complete)
    ├── TrackMeta (BPM/key display)
    ├── BeatTimeline (canvas visualization)
    ├── SectionMap (section indicator)
    └── ExportPanel (export buttons)
```

### API Integration

The `analyzeAudio(file)` function in `api/beatsync.js`:
1. Sends audio file via multipart/form-data POST
2. Endpoint: `{API_URL}/api/analysis`
3. Returns JSON contract with schema:
   - `beats[]`: Array of beat timestamps
   - `bars[]`: Array of bar timestamps
   - `bpm`: Number (detected tempo)
   - `bpm_confidence`: Number [0-1]
   - `key`: String (e.g., "C major", "A minor")
   - `key_confidence`: Number [0-1]
   - `duration`: Number (seconds)
   - `sections[]`: Array of `{label, start, end}`

### Component APIs

#### UploadZone

Props:
- `onFileSelected(file)` — Callback when file selected
- `isLoading` — Show loading state

Accepts: WAV, MP3, FLAC, OGG (20–100MB typical)

#### TrackMeta

Props:
- `contract` — API response JSON

Displays: BPM, key, duration, confidence indicators

#### BeatTimeline

Props:
- `contract` — API response JSON
- `onPlayheadChange(seconds)` — Optional callback for playhead position

Features:
- Interactive playhead (click to seek, drag to scrub)
- Energy curve visualization
- Beat markers (yellow ticks)
- Bar markers (red ticks)
- Section boundaries (green lines)
- Time grid labels

#### SectionMap

Props:
- `contract` — API response JSON

Features:
- Colored section blocks
- Hover tooltips showing start/end times
- Responsive width based on section duration

#### ExportPanel

Props:
- `contract` — API response JSON
- `filename` — Default export filename

Features:
- Frame rate selector (24, 25, 29.97, 30 fps)
- CSV export (beat timestamps with multiple FPS columns)
- EDL export (CMX 3600 format for NLE software)

#### AnalysisResult

Props:
- `contract` — API response JSON
- `filename` — Source audio filename
- `onReset()` — Callback for "Analyze Another File"

Orchestrates all result display components.

## Styling

Dark theme with Tailwind CSS:
- Base: `#1a1a2e` (slate-950)
- Text: `#ffffff` (white)
- Accents: Blue (analysis), green (sections), red (errors), yellow (beats), indigo (export)

All styling uses Tailwind utility classes (no custom CSS). Tailwind is loaded via CDN in `index.html`.

## Export Formats

### CSV Format

Headers:
- `timestamp_seconds`
- `timestamp_frames_24fps`
- `timestamp_frames_25fps`
- `timestamp_frames_30fps`
- `type` (beat|bar)

Example:
```csv
timestamp_seconds,timestamp_frames_24fps,timestamp_frames_25fps,timestamp_frames_30fps,type
0.5,12,12,15,beat
1.0,24,25,30,beat
2.0,48,50,60,bar
```

### EDL Format

CMX 3600 standard. Each beat = 1-frame cut event.

Example:
```
TITLE: beatsync_export

000  AUD      V     C        00:00:00:00 00:00:00:01 00:00:00:00 00:00:00:01
001  AUD      V     C        00:00:00:01 00:00:00:02 00:00:00:01 00:00:00:02
...
```

Compatible with Premiere Pro, Final Cut Pro, Media Composer, etc.

## Error Handling

- **Network errors**: "Unable to connect to analysis service"
- **Invalid audio**: "Unsupported audio format or corrupt file"
- **Server errors**: "Analysis service unavailable"
- **Unexpected errors**: Caught by ErrorBoundary, displays graceful UI

## Browser Support

- Chrome/Edge 90+
- Firefox 89+
- Safari 14+
- Requires:
  - ES2020+
  - Canvas API
  - Blob/fetch APIs
  - FormData API

## Performance Notes

- Canvas timeline renders at native resolution
- Timeline lazily computed on first paint
- Drag operations use requestAnimationFrame for smooth 60fps
- CSV/EDL generation < 1s for typical files (< 10k events)

## Troubleshooting

### "Cannot find module" errors

Ensure all relative imports use correct paths:
- From App.jsx: `./components/UploadZone`
- From UploadZone: `../api/beatsync`

### API connection errors

1. Verify `VITE_API_URL` in `.env.local`
2. Check backend is running at that URL
3. Verify CORS headers if different domain
4. Check browser console for specific error

### Canvas not rendering

Open DevTools console. Canvas timeline uses `canvas.getContext('2d')`. Verify:
- Contract has valid `energy` array
- Contract has valid `beats` array
- Browser supports Canvas

## Development Workflow

1. Start dev server: `npm run dev`
2. Edit components in `src/components/`
3. Vite hot-reloads on save
4. Build for production: `npm run build`
5. Preview production build: `npm run preview`

## Related Projects

- **beatsync-core** — Audio BPM/key/structure analysis
- **beatsync-midi** — MIDI key detection
- **beatsync-blender-visual** — Blender add-on for beat visualization
- **beatsync-studio** — FastAPI backend server (frozen, complete)

## License

See LICENSE file in repository root
