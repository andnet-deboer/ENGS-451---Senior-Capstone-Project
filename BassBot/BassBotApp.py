import threading
import importlib
from flask import request, jsonify
from pathlib import Path
import os
import re
from flask import Flask, render_template, request, jsonify, send_from_directory
from play import BassPlayer
from config import SERVO_PINS, RELAY_NUMBERS
from werkzeug.utils import secure_filename
from bass import Bass
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device
import pigpio
import json
from currentLogger import CurrentLogger
from config import SENSOR_ADDRESSES 
from flask import send_file
from io import BytesIO
from matplotlib.figure import Figure
from flask import send_file

Device.pin_factory = PiGPIOFactory()  # Prevents fallback to default

# Clear pin states manually
pi = pigpio.pi()
pi.stop()

SONGS_FOLDER = "songs"
COVERS_FOLDER = "static/covers"
ALLOWED_SONGS = {"xml"}
ALLOWED_IMAGES = {"jpg", "jpeg", "png"}
DEFAULT_SONG = "7NationArmy.xml"



app = Flask(__name__)
bass = Bass()
# === App State ===
try:
    os.sched_setaffinity(0, {0})
except Exception:
    pass
current_logger = CurrentLogger(interval=0.001, history_seconds=20)
current_logger.start()

current_song = DEFAULT_SONG
log = ["This is a log or note box."]
servo_positions = [(1, "45 deg"), (2, "90 deg")]
model_viewer_expanded = False


SONGS_FOLDER = "songs"
COVERS_FOLDER = "static/covers"
ALLOWED_SONGS = {"xml"}
ALLOWED_IMAGES = {"jpg", "jpeg", "png"}

# === Playback Control ===
player_thread = None
player_instance = None
is_playing = False
lock = threading.Lock()
pause_event = threading.Event()
stop_event = threading.Event()
pause_event.set()


BASE_DIR      = Path(__file__).resolve().parent      
FUNCTION_DIR  = BASE_DIR / 'ScratchFunctions'       
FUNCTION_DIR.mkdir(exist_ok=True)
# === Thread-Safe Logging ===
log_lock = threading.Lock()


def safe_log_append(message):
    with log_lock:
        log.append(message)
        if len(log) > 50:
            log.pop(0)
    print(f"[LOG] {message}")  # Console debug


def get_song_list():
    song_dir = "songs"
    return sorted(os.path.splitext(f)[0] for f in os.listdir(song_dir) if f.endswith(".xml")) if os.path.exists(song_dir) else []


def start_playback_thread(song_filename):
    global player_thread, is_playing, player_instance, bass

    with lock:
        if is_playing:
            if not pause_event.is_set():
                pause_event.set()
                safe_log_append("▶️ Resumed playback.")
            else:
                safe_log_append("⚠️ Already playing.")
            return

        stop_event.clear()

        def start_playback(song_filename):
            global is_playing, player_instance, bass
            try:
                # === Cleanup before new run ===
                if player_instance and hasattr(player_instance, 'bass'):
                    try:
                        player_instance.bass.cleanup()
                        safe_log_append("🧹 Previous Bass instance cleaned.")
                    except Exception as e:
                        safe_log_append(f"⚠️ Error during previous cleanup: {e}")

                if bass:
                    try:
                        bass.cleanup()
                        safe_log_append("🧼 Global Bass instance cleaned.")
                    except Exception as e:
                        safe_log_append(f"⚠️ Error cleaning global Bass: {e}")

                base_dir = os.path.dirname(__file__)
                full_path = os.path.join(base_dir, "songs", f"{song_filename}.xml")
                print(f"[DEBUG] Attempting to play: {full_path}")

                if not os.path.exists(full_path):
                    raise FileNotFoundError(f"File not found: {full_path}")

                is_playing = True
                pause_event.set()

                player_instance = BassPlayer(
                    music_file=full_path,
                    pause_event=pause_event,
                    stop_event=stop_event
                )
                player_instance.log_function = safe_log_append

                def estop_callback():
                    safe_log_append("🚨 Emergency stop triggered during playback.")
                player_instance.estop_callback = estop_callback

                print("[DEBUG] Running BassPlayer...")
                player_instance.run()
                print("[DEBUG] Playback finished.")

            except Exception as e:
                safe_log_append(f"❌ Playback error: {e}")
                print(f"[ERROR] Playback thread failed: {e}")

            finally:
                is_playing = False
                try:
                    if player_instance and hasattr(player_instance, 'bass'):
                        player_instance.bass.cleanup()
                        safe_log_append("✅ Player Bass cleaned up.")
                except Exception as e:
                    safe_log_append(f"❌ Error during final cleanup: {e}")
                player_instance = None

        player_thread = threading.Thread(
            target=start_playback,
            args=(song_filename,),
            daemon=True
        )
        player_thread.start()
        safe_log_append(f"▶️ Started playback: {song_filename}")



def toggle_pause():
    if is_playing:
        if pause_event.is_set():
            pause_event.clear()
            safe_log_append("⏸️ Paused playback.")
        else:
            pause_event.set()
            safe_log_append("▶️ Resumed playback.")
    else:
        safe_log_append("⚠️ No active playback to pause/resume.")


def stop_playback():
    global is_playing
    if is_playing and player_instance:
        stop_event.set()
        pause_event.set()
        is_playing = False
        safe_log_append("⏹️ Stop signal sent.")
    else:
        safe_log_append("⚠️ No active playback to stop.")


@app.route("/", methods=["GET", "POST"])
def index():
    global current_song, model_viewer_expanded
    songs = get_song_list()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "toggle_model_viewer":
            model_viewer_expanded = not model_viewer_expanded
            return jsonify({"status": "success", "expanded": model_viewer_expanded})

    return render_template("gui.html",
        current_song=current_song,
        songs=songs,
        log=log[-50:],
        servo_positions=servo_positions,
        servo_pins=SERVO_PINS,
        relay_numbers=RELAY_NUMBERS,
        model_viewer_expanded=model_viewer_expanded
    )

@app.route("/configurations")
def configurations():
    return render_template("configurations.html", servo_pins=SERVO_PINS, relay_numbers=RELAY_NUMBERS)

@app.route("/testing")
def testing_interface():
    return render_template("testing.html")

@app.route("/execute_blocks", methods=["POST"])
def execute_blocks():
    from bass import Bass
    from gpiozero.pins.pigpio import PiGPIOFactory
    import threading

    data = request.get_json(force=True)
    code = data.get("code", "")

    if not code:
        return jsonify({"message": "No code provided."}), 400

    # Define wait function
    def wait(seconds: float):
        threading.Event().wait(seconds)

    # Initialize fresh bass
    bass_instance = Bass(factory=PiGPIOFactory())

    # Local execution environment
    local_env = {
        "bass": bass_instance,
        "wait": wait
    }

    safe_log_append(f"Executing Blockly code:\n{code}")
    try:
        exec(code, globals(), local_env)
        bass_instance.cleanup()
        return jsonify({"message": "Blockly code executed successfully.", "log": log[-1]})
    except Exception as e:
        bass_instance.cleanup()
        safe_log_append(f"❌ Error executing Blockly code: {e}")
        return jsonify({"message": f"Error executing Blockly code: {e}", "log": log[-1]}), 400


@app.route("/save_function", methods=["POST"])
def save_function():
    data = request.get_json()
    name = data["name"].strip()
    code = data["code"]          # we save *Python code*, not XML
    if not name:
        return jsonify({"error": "Name required"}), 400
    if not name.replace('_','').isalnum():
        return jsonify({"error":"Letters, numbers, underscore only"}), 400

    (FUNCTION_DIR / f"{name}.py").write_text(code, encoding="utf-8")
    return jsonify({"ok": True})

@app.route("/list_functions")
def list_functions():
    files = [p.stem for p in FUNCTION_DIR.glob("*.py")]
    return jsonify(sorted(files))

@app.route("/get_function/<fname>")
def get_function(fname):
    return send_from_directory(FUNCTION_DIR, f"{fname}.py")

@app.route('/start_monitor', methods=['POST'])
def start_monitor():
    global current_logger
    if current_logger is None:
        current_logger = CurrentLogger(interval=0.5, history_seconds=60)
        current_logger.start()
        return jsonify(status='started')
    return jsonify(status='already running')

@app.route('/stop_monitor', methods=['POST'])
def stop_monitor():
    global current_logger
    if current_logger:
        current_logger.stop()
        current_logger = None
        return jsonify(status='stopped')
    return jsonify(status='not running')

@app.route('/current_plot.png')
def current_plot():
    if not current_logger:            # guard until the very first sample
        return ('', 204)

    fig = Figure()
    ax  = fig.subplots()
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (mA)')

    # grab times & buffers
    times = list(current_logger._times)
    for name, buf in current_logger._buf.items():
        ys = list(buf)
        n  = min(len(times), len(ys))
        ax.plot(times[-n:], ys[-n:], label=name)

    ax.legend(loc='upper right')
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


@app.route("/trigger_action", methods=["POST"])
def trigger_action():
    global current_song
    action = request.form.get("action")

    if action == "Play":
        song = request.form.get("song", current_song)
        current_song = song
        safe_log_append(f"Requested to play: {current_song}")
        start_playback_thread(current_song)
        return jsonify({"status": "success", "message": f"Started playing {current_song}", "log": log[-1]})

    elif action == "Pause":
        toggle_pause()
        return jsonify({"status": "success", "message": "Playback paused/resumed", "log": log[-1]})

    elif action == "Stop":
        stop_playback()
        return jsonify({"status": "success", "message": "Stop requested", "log": log[-1]})

    elif action == "clear_log":
        with log_lock:
            log.clear()
            log.append("Log cleared.")
        return jsonify({"status": "success", "message": "Log cleared."})

    return jsonify({"status": "error", "message": f"Unknown action: {action}"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)