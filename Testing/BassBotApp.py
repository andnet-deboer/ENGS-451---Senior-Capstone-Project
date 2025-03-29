import tkinter as tk
from tkinter import ttk, messagebox

# Callback placeholders
def play():
    print(f"Playing: {song_var.get()}")

def pause():
    print("Paused")

def stop():
    print("Stopped")

# GUI Setup
root = tk.Tk()
root.title("Self-Playing Bass Guitar")
root.geometry("800x600")

# Song selection dropdown
song_var = tk.StringVar()
song_dropdown = ttk.Combobox(root, textvariable=song_var)
song_dropdown['values'] = ("Song 1", "Song 2", "Song 3")
song_dropdown.current(0)
song_dropdown.pack(pady=10)

# Playback controls
control_frame = tk.Frame(root)
play_button = tk.Button(control_frame, text="Play", command=play)
pause_button = tk.Button(control_frame, text="Pause", command=pause)
stop_button = tk.Button(control_frame, text="Stop", command=stop)
play_button.pack(side=tk.LEFT, padx=5)
pause_button.pack(side=tk.LEFT, padx=5)
stop_button.pack(side=tk.LEFT, padx=5)
control_frame.pack(pady=10)

# Extra Example Widgets (delete what you don't need)
tk.Label(root, text="Volume").pack()
tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL).pack()

tk.Label(root, text="Bass Mode").pack()
tk.Checkbutton(root, text="Slap Mode").pack()
tk.Checkbutton(root, text="Finger Style").pack()

entry_label = tk.Label(root, text="Custom Note")
entry_label.pack()
entry = tk.Entry(root)
entry.pack()

tk.Button(root, text="Submit Note", command=lambda: print(f"Note: {entry.get()}")).pack(pady=5)

text_box = tk.Text(root, height=5, width=50)
text_box.insert(tk.END, "This is a log or note box.")
text_box.pack(pady=10)

progress = ttk.Progressbar(root, length=200, mode='determinate')
progress['value'] = 40
progress.pack(pady=5)

# Treeview table
columns = ("#1", "#2")
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading("#1", text="Servo ID")
tree.heading("#2", text="Position")
tree.insert('', tk.END, values=(1, "45 deg"))
tree.insert('', tk.END, values=(2, "90 deg"))
tree.pack(pady=10)

# Message button example
def show_about():
    messagebox.showinfo("About", "Self-playing bass guitar GUI v1.0")

tk.Button(root, text="About", command=show_about).pack(pady=5)

root.mainloop()
