# BeatSync Studio — Frontend

Professional audio analysis UI for video editors. Upload an audio file, get beat/bar markers, and export for your NLE.

## Development

```bash
npm install
npm run dev
```

Visit `http://localhost:5173` — the frontend will connect to the backend API at `http://localhost:8000` (configurable via `.env.local`).

## Build for production

```bash
npm run build
npm run preview
```

## Environment

Create `.env.local`:
```
VITE_API_URL=http://localhost:8000
```

For Vercel deployment, set `VITE_API_URL` as an environment variable in the Vercel dashboard pointing to your production backend.

## Features

- Drag-and-drop audio file upload (WAV, MP3, FLAC, OGG)
- Real-time analysis via BeatSync backend
- Interactive beat/bar timeline visualization
- BPM and key detection with confidence indicators
- Export beat timestamps as CSV or EDL (cinema format)
- Dark theme, professional design
- Responsive on desktop and tablet

## Deployment

- **Frontend:** Vercel (free tier)
- **Backend:** Railway or similar (free tier)

See `vercel.json` for API rewrite configuration.
