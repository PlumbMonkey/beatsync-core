from pathlib import Path
import mido

out = Path(__file__).resolve().parents[1] / "fixtures" / "batch" / "valid2.mid"
out.parent.mkdir(parents=True, exist_ok=True)

mid = mido.MidiFile(ticks_per_beat=480)
track = mido.MidiTrack()
mid.tracks.append(track)
track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(90), time=0))
for i in range(8):
    note = 72 - i
    track.append(mido.Message("note_on", note=note, velocity=80, time=0))
    track.append(mido.Message("note_off", note=note, velocity=0, time=480))
mid.save(out.as_posix())
print(f"Wrote {out}")
