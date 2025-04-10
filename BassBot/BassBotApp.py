import threading
import importlib
import os
import re
from flask import Flask, render_template, request, jsonify
from play import BassPlayer
from config import SERVO_PINS, RELAY_NUMBERS

app = Flask(__name__)

# === App State ===
DEFAULT_SONG = "7NationArmy"
current_song = DEFAULT_SONG
log = ["This is a log or note box."]
servo_positions = [(1, "45 deg"), (2, "90 deg")]
model_viewer_expanded = False

# === Playback Control ===
player_thread = None
player_instance = None
is_playing = False
lock = threading.Lock()
pause_event = threading.Event()
stop_event = threading.Event()
pause_event.set()

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
    global player_thread, is_playing, player_instance
    with lock:
        if is_playing:
            if not pause_event.is_set():
                pause_event.set()
                log.append("▶️ Resumed playback.")
            else:
                log.append("⚠️ Already playing.")
            return

        stop_event.clear()

        def start_playback(song_filename):
            global is_playing, player_instance
            try:
                full_path = os.path.join(song_filename+".xml")
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
                player_instance.log = log

                def estop_callback():
                    log.append("🚨 Emergency stop triggered during playback.")
                player_instance.estop_callback = estop_callback

                print("[DEBUG] Running BassPlayer...")
                player_instance.run()
                print("[DEBUG] Playback finished.")

            except Exception as e:
                log.append(f"❌ Playback error: {e}")
                print(f"[ERROR] Playback thread failed: {e}")

            finally:
                is_playing = False
                if player_instance and hasattr(player_instance.bass, "cleanup"):
                    try:
                        player_instance.bass.cleanup()
                        log.append("✅ GPIO cleaned up.")
                    except Exception as e:
                        log.append(f"❌ Cleanup error: {e}")
                    finally:
                        player_instance = None

        player_thread = threading.Thread(
            target=start_playback,
            args=(song_filename,),
            daemon=True
        )
        player_thread.start()
        log.append(f"▶️ Started playback: {current_song}")


def toggle_pause():
    if pause_event.is_set():
        pause_event.clear()
        log.append("⏸️ Paused playback.")
    else:
        pause_event.set()
        log.append("▶️ Resumed playback.")


def stop_playback():
    global is_playing
    if is_playing and player_instance:
        stop_event.set()
        pause_event.set()
        is_playing = False
        log.append("⏹️ Stop signal sent.")
    else:
        log.append("⚠️ No active playback to stop.")


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


@app.route("/trigger_action", methods=["POST"])
def trigger_action():
    global current_song
    action = request.form.get("action")

    if action == "Play":
        song = request.form.get("song", current_song)
        current_song = song
        log.append(f"Requested to play: {current_song}")
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
        return jsonify({"status": "success", "message": "Log cleared"})

    else:
        return jsonify({"status": "error", "message": "Invalid action"})


@app.route("/get_log")
def get_log():
    return jsonify({"log": log[-50:]})


@app.route("/configurations", methods=["GET", "POST"])
def configurations():
    global SERVO_PINS, RELAY_NUMBERS

    if request.method == "POST" and request.form.get("action") == "SaveIDs":
        try:
            updated_servo_pins = {k[6:]: int(v) for k, v in request.form.items() if k.startswith("SERVO_")}
            updated_fret_pins = {k[5:]: int(v) for k, v in request.form.items() if k.startswith("fret_")}

            with open("config.py", "r") as file:
                config_data = file.read()

            def replace_dict(text, var_name, new_dict):
                pattern = rf"{var_name}\s*=\s*\{{[^}}]*\}}"
                formatted = f"{var_name} = {{\n"
                for k, v in new_dict.items():
                    formatted += f"    '{k}': {v},\n"
                formatted += "}"
                return re.sub(pattern, formatted, text)

            config_data = replace_dict(config_data, "SERVO_PINS", updated_servo_pins)
            config_data = replace_dict(config_data, "RELAY_NUMBERS", updated_fret_pins)

            with open("config.py", "w") as file:
                file.write(config_data)

            import config
            importlib.reload(config)
            SERVO_PINS = config.SERVO_PINS
            RELAY_NUMBERS = config.RELAY_NUMBERS

            log.append("✅ Saved and reloaded config.")

            if request.is_json:
                return jsonify({"status": "success", "message": "Configurations updated"})

        except Exception as e:
            log.append(f"❌ Error saving config: {e}")
            if request.is_json:
                return jsonify({"status": "error", "message": str(e)})

    return render_template("configurations.html",
        servo_pins=SERVO_PINS,
        relay_numbers=RELAY_NUMBERS
    )


if __name__ == "__main__":
    print("[Flask] Starting app...")
    app.run(host="0.0.0.0", port=5000, debug=True)
