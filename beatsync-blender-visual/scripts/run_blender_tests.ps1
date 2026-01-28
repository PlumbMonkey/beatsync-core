# PowerShell script to run Blender in headless mode and enable the BeatSync add-on
param(
    [string]$BlenderPath = "blender",
    [string]$AddonPath = "../addon"
)

$env:PYTHONPATH = $null

$script = @'
import bpy
import sys
import os
addon_dir = os.path.abspath(sys.argv[-1])
if addon_dir not in sys.path:
    sys.path.append(addon_dir)
try:
    bpy.ops.preferences.addon_enable(module="beatsync_blender_visual")
    print("[BEATSYNC] Add-on enabled successfully.")
    sys.exit(0)
except Exception as e:
    print(f"[BEATSYNC] Failed to enable add-on: {e}")
    sys.exit(1)
'@

$pyfile = New-TemporaryFile
Set-Content -Path $pyfile -Value $script

& $BlenderPath --background --factory-startup --python $pyfile -- $AddonPath
$exitCode = $LASTEXITCODE
Remove-Item $pyfile
exit $exitCode
