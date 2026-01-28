from pathlib import Path
import mido

out = Path(__file__).resolve().parents[1] / "fixtures" / "midi" / "midi_basic_100.mid"
out.parent.mkdir(parents=True, exist_ok=True)

mid = mido.MidiFile(ticks_per_beat=480)
track = mido.MidiTrack()
mid.tracks.append(track)

# tempo = 100 BPM
track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(100), time=0))

# 4 bars of quarter notes on C4
note = 60
ticks = 480  # quarter note
for _ in range(16):
    track.append(mido.Message("note_on", note=note, velocity=90, time=0))
    track.append(mido.Message("note_off", note=note, velocity=0, time=ticks))

mid.save(out.as_posix())
print(f"Wrote {out}")
