import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
import subprocess
import os
import sys
import threading

class SimpleAudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Audio Converter v1.0")
        self.root.geometry("650x800")
        self.root.resizable(False, False)

        # Variables
        self.input_files = [] # List to store multiple file paths
        self.output_dir = tk.StringVar()
        self.target_format = tk.StringVar(value="FLAC")
        
        # Format Specific Variables
        self.flac_compression = tk.StringVar(value="5")
        self.flac_bitdepth = tk.StringVar(value="16 bit")
        self.alac_bitdepth = tk.StringVar(value="16 bit")
        self.channels = tk.StringVar(value="Stereo")
        self.bitrate_mode = tk.StringVar(value="VBR")
        self.target_bitrate = tk.StringVar(value="320k")
        self.vbr_quality = tk.StringVar(value="High")
        
        # Audio Processing Variables
        self.remove_start_silence = tk.BooleanVar(value=False)
        self.remove_end_silence = tk.BooleanVar(value=False)

        # App Settings
        self.open_folder = tk.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        # 1. Select Input Files (Batch Processing)
        frame_input = tk.LabelFrame(self.root, text="1. Input Files", padx=10, pady=5)
        frame_input.pack(fill="x", padx=15, pady=5)
        
        self.listbox_files = tk.Listbox(frame_input, selectmode=tk.EXTENDED, height=4, width=70)
        self.listbox_files.pack(side="left", padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(frame_input, orient="vertical", command=self.listbox_files.yview)
        scrollbar.pack(side="left", fill="y")
        self.listbox_files.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(frame_input)
        btn_frame.pack(side="left", padx=10)
        tk.Button(btn_frame, text="Add Files...", command=self.add_files, width=12).pack(pady=2)
        tk.Button(btn_frame, text="Clear List", command=self.clear_files, width=12).pack(pady=2)

        # 2. Select Output Folder
        frame_output = tk.LabelFrame(self.root, text="2. Destination Folder", padx=10, pady=5)
        frame_output.pack(fill="x", padx=15, pady=5)
        tk.Entry(frame_output, textvariable=self.output_dir, state="readonly", width=75).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame_output, text="Browse...", command=self.browse_output).grid(row=0, column=1)

        # 3. Select Format
        frame_format = tk.LabelFrame(self.root, text="3. Output Format", padx=10, pady=5)
        frame_format.pack(fill="x", padx=15, pady=5)
        formats = ["FLAC", "ALAC", "WAV", "MP3", "AAC", "WMA", "OGG"]
        ttk.Combobox(frame_format, textvariable=self.target_format, values=formats, state="readonly", width=15).pack(side="left", pady=5)
        self.target_format.trace_add("write", self.update_options_ui)

        # 4. Format & Audio Options Frame
        self.frame_options = tk.LabelFrame(self.root, text="4. Encoding Options", padx=10, pady=5)
        self.frame_options.pack(fill="x", padx=15, pady=5)
        
        # --- Silence Removal Settings ---
        silence_frame = tk.Frame(self.frame_options)
        silence_frame.pack(fill="x", pady=5)
        tk.Label(silence_frame, text="Audio Trimming:").pack(side="left")
        tk.Checkbutton(silence_frame, text="Remove Start Silence", variable=self.remove_start_silence).pack(side="left", padx=10)
        tk.Checkbutton(silence_frame, text="Remove End Silence", variable=self.remove_end_silence).pack(side="left", padx=10)
        
        ttk.Separator(self.frame_options, orient='horizontal').pack(fill='x', pady=5)

        # --- Sub-Frames for Codec Options ---
        self.flac_frame = tk.Frame(self.frame_options)
        self.alac_frame = tk.Frame(self.frame_options)
        self.lossy_frame = tk.Frame(self.frame_options)
        
        # -- FLAC Settings --
        tk.Label(self.flac_frame, text="Compression (0-8):").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Combobox(self.flac_frame, textvariable=self.flac_compression, values=[str(i) for i in range(9)], state="readonly", width=5).grid(row=0, column=1, padx=10)
        tk.Label(self.flac_frame, text="Bit Depth:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Combobox(self.flac_frame, textvariable=self.flac_bitdepth, values=["16 bit", "24 bit"], state="readonly", width=10).grid(row=1, column=1, padx=10)

        # -- ALAC Settings --
        tk.Label(self.alac_frame, text="Bit Depth:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Combobox(self.alac_frame, textvariable=self.alac_bitdepth, values=["16 bit", "24 bit"], state="readonly", width=10).grid(row=0, column=1, padx=10)

        # -- Lossy Settings --
        tk.Label(self.lossy_frame, text="Audio Channels:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Combobox(self.lossy_frame, textvariable=self.channels, values=["Stereo", "Mono"], state="readonly", width=10).grid(row=0, column=1, padx=10)

        tk.Label(self.lossy_frame, text="Bitrate Mode:").grid(row=1, column=0, sticky="w", pady=2)
        self.mode_frame = tk.Frame(self.lossy_frame)
        self.mode_frame.grid(row=1, column=1, sticky="w", padx=10)
        
        self.rb_cbr = tk.Radiobutton(self.mode_frame, text="CBR", variable=self.bitrate_mode, value="CBR", command=self.update_bitrate_ui)
        self.rb_cbr.pack(side="left")
        self.rb_abr = tk.Radiobutton(self.mode_frame, text="ABR", variable=self.bitrate_mode, value="ABR", command=self.update_bitrate_ui)
        self.rb_abr.pack(side="left")
        self.rb_vbr = tk.Radiobutton(self.mode_frame, text="VBR", variable=self.bitrate_mode, value="VBR", command=self.update_bitrate_ui)
        self.rb_vbr.pack(side="left")

        self.lbl_rate = tk.Label(self.lossy_frame, text="Bitrate:")
        self.lbl_rate.grid(row=2, column=0, sticky="w", pady=2)
        self.cb_bitrate = ttk.Combobox(self.lossy_frame, textvariable=self.target_bitrate, values=["128k", "160k", "192k", "256k", "320k"], state="readonly", width=10)
        self.cb_vbr = ttk.Combobox(self.lossy_frame, textvariable=self.vbr_quality, values=["Highest", "High", "Medium", "Low"], state="readonly", width=10)

        self.update_options_ui() 
        self.update_bitrate_ui()

        # 5. Bottom Actions & Real-time Log
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        tk.Checkbutton(bottom_frame, text="Open destination folder after conversion", variable=self.open_folder).pack(side="top", pady=2)
        
        self.btn_convert = tk.Button(bottom_frame, text="Start Conversion", command=self.start_conversion_thread, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.btn_convert.pack(side="top", pady=5, ipadx=20, ipady=5)

        # Log Window
        tk.Label(bottom_frame, text="Real-time Log:").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(bottom_frame, height=8, state="disabled", bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, pady=5)

    def add_files(self):
        filepaths = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=(("Audio files", "*.wav *.flac *.mp3 *.aac *.m4a *.wma *.ogg"), ("All files", "*.*"))
        )
        for path in filepaths:
            if path not in self.input_files:
                self.input_files.append(path)
                self.listbox_files.insert(tk.END, os.path.basename(path))
        
        # Auto-set output directory if empty
        if self.input_files and not self.output_dir.get():
            self.output_dir.set(os.path.dirname(self.input_files[0]))

    def clear_files(self):
        self.input_files.clear()
        self.listbox_files.delete(0, tk.END)

    def browse_output(self):
        folderpath = filedialog.askdirectory(title="Select destination folder")
        if folderpath:
            self.output_dir.set(folderpath)

    def update_options_ui(self, *args):
        self.flac_frame.pack_forget()
        self.alac_frame.pack_forget()
        self.lossy_frame.pack_forget()

        fmt = self.target_format.get()
        if fmt == "FLAC":
            self.flac_frame.pack(fill="x", anchor="w")
        elif fmt == "ALAC":
            self.alac_frame.pack(fill="x", anchor="w")
        elif fmt in ["MP3", "AAC", "WMA", "OGG"]:
            self.lossy_frame.pack(fill="x", anchor="w")
            self.update_bitrate_ui()

    def update_bitrate_ui(self):
        self.cb_bitrate.grid_remove()
        self.cb_vbr.grid_remove()
        
        mode = self.bitrate_mode.get()
        if mode == "CBR":
            self.lbl_rate.config(text="Bitrate (CBR):")
            self.cb_bitrate.grid(row=2, column=1, padx=10, sticky="w")
        elif mode == "ABR":
            self.lbl_rate.config(text="Target Bitrate (ABR):")
            self.cb_bitrate.grid(row=2, column=1, padx=10, sticky="w")
        else:
            self.lbl_rate.config(text="Quality (VBR):")
            self.cb_vbr.grid(row=2, column=1, padx=10, sticky="w")

    def get_vbr_value(self, fmt, quality):
        mappings = {
            "MP3": {"Highest": "0", "High": "2", "Medium": "5", "Low": "7"},
            "AAC": {"Highest": "2", "High": "1.5", "Medium": "1", "Low": "0.5"},
            "WMA": {"Highest": "90", "High": "75", "Medium": "50", "Low": "25"},
            "OGG": {"Highest": "9", "High": "7", "Medium": "5", "Low": "3"}
        }
        return mappings.get(fmt, {}).get(quality, "5")

    def log(self, message):
        """Thread-safe way to update the log window"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def start_conversion_thread(self):
        if not self.input_files:
            messagebox.showwarning("Warning", "Please add at least one file to the list!")
            return
        if not self.output_dir.get():
            messagebox.showwarning("Warning", "Please select a destination folder!")
            return

        # Disable UI during conversion
        self.btn_convert.config(text="Converting...", state="disabled")
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END) # Clear previous log
        self.log_text.config(state="disabled")
        
        # Start processing in a background thread
        threading.Thread(target=self.process_files, daemon=True).start()

    def process_files(self):
        output_folder = self.output_dir.get()
        fmt = self.target_format.get()
        ext_map = {"FLAC": ".flac", "MP3": ".mp3", "AAC": ".m4a", "WAV": ".wav", "WMA": ".wma", "OGG": ".ogg", "ALAC": ".m4a"}
        
        has_error = False

        for index, input_path in enumerate(self.input_files, 1):
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}_converted{ext_map[fmt]}"
            output_path = os.path.join(output_folder, output_filename)

            self.root.after(0, self.log, f"\n[{index}/{len(self.input_files)}] Processing: {base_name}...")

            cmd = ["ffmpeg", "-y", "-i", input_path]

            # --- AUDIO FILTERS (Silence Removal) ---
            audio_filters = []
            if self.remove_start_silence.get():
                audio_filters.append("silenceremove=start_periods=1:start_duration=0.1:start_threshold=-50dB")
            if self.remove_end_silence.get():
                audio_filters.append("silenceremove=stop_periods=-1:stop_duration=0.1:stop_threshold=-50dB")
            
            if audio_filters:
                # Join multiple filters with commas
                cmd.extend(["-af", ",".join(audio_filters)])

            # --- CODEC SETTINGS ---
            if fmt == "FLAC":
                cmd.extend(["-c:a", "flac", "-compression_level", self.flac_compression.get()])
                s_fmt = "s16" if self.flac_bitdepth.get() == "16 bit" else "s32"
                cmd.extend(["-sample_fmt", s_fmt])
                
            elif fmt == "ALAC":
                cmd.extend(["-c:a", "alac"])
                s_fmt = "s16p" if self.alac_bitdepth.get() == "16 bit" else "s32p"
                cmd.extend(["-sample_fmt", s_fmt])
                
            elif fmt == "WAV":
                cmd.extend(["-c:a", "pcm_s16le"])
                
            elif fmt in ["MP3", "AAC", "WMA", "OGG"]:
                codec_map = {"MP3": "libmp3lame", "AAC": "aac", "WMA": "wmav2", "OGG": "libvorbis"}
                cmd.extend(["-c:a", codec_map[fmt]])
                
                ch = "2" if self.channels.get() == "Stereo" else "1"
                cmd.extend(["-ac", ch])
                
                mode = self.bitrate_mode.get()
                target_bw = self.target_bitrate.get()
                
                if mode in ["CBR", "ABR"]:
                    cmd.extend(["-b:a", target_bw])
                    if mode == "ABR" and fmt == "MP3":
                        cmd.extend(["-abr", "1"])
                    elif mode == "CBR" and fmt == "OGG":
                        cmd.extend(["-minrate", target_bw, "-maxrate", target_bw])
                else:
                    q_val = self.get_vbr_value(fmt, self.vbr_quality.get())
                    cmd.extend(["-q:a", q_val])

            cmd.append(output_path)

            # --- EXECUTE FFmpeg ---
            try:
                # Use Popen to read real-time output
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, # FFmpeg writes logs to stderr, merge it with stdout
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )

                # Read output line by line in real-time
                for line in process.stdout:
                    # Filter output so it doesn't flood the UI with too much garbage, 
                    # mostly show lines containing time/progress or errors
                    clean_line = line.strip()
                    if "size=" in clean_line and "time=" in clean_line:
                        # Extract just the time part for a cleaner log
                        parts = clean_line.split()
                        time_part = [p for p in parts if p.startswith("time=")]
                        if time_part:
                            self.root.after(0, self.log, f"  -> {time_part[0]}")
                    elif "Error" in clean_line or "Invalid" in clean_line:
                        self.root.after(0, self.log, f"  [ERROR] {clean_line}")

                process.wait()

                if process.returncode == 0:
                    self.root.after(0, self.log, f"✅ Done: {output_filename}")
                else:
                    self.root.after(0, self.log, f"❌ Failed: {output_filename}")
                    has_error = True

            except FileNotFoundError:
                self.root.after(0, self.log, "CRITICAL ERROR: ffmpeg.exe not found!")
                has_error = True
                break # Stop processing if FFmpeg is missing

        # --- AFTER ALL FILES PROCESSED ---
        self.root.after(0, self.finish_conversion, output_folder, has_error)

    def finish_conversion(self, output_folder, has_error):
        self.btn_convert.config(text="Start Conversion", state="normal")
        self.log("\n--- BATCH PROCESSING COMPLETE ---")
        
        if not has_error:
            messagebox.showinfo("Success!", "All files were converted successfully!")
            if self.open_folder.get():
                if os.name == 'nt':
                    os.startfile(output_folder)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', output_folder])
                else:
                    subprocess.Popen(['xdg-open', output_folder])
        else:
            messagebox.showwarning("Finished with errors", "Processing finished, but some files had errors. Check the log.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleAudioConverterApp(root)
    root.mainloop()