from __future__ import annotations

import argparse
import glob
import locale
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


ROOT = Path(__file__).resolve().parent
SEPARATOR = ROOT / ".venv" / "Scripts" / "audio-separator.exe"
MODEL_DIR = ROOT / "models"
MODEL = "UVR_MDXNET_KARA_2.onnx"
ICON = ROOT / "music_off.ico"
NO_CONSOLE = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

try:
    FFMPEG = shutil.which("ffmpeg") or __import__("imageio_ffmpeg").get_ffmpeg_exe()
except (ImportError, RuntimeError):
    FFMPEG = shutil.which("ffmpeg")

try:
    LANGUAGE = "ar" if (locale.getlocale()[0] or "").lower().startswith("ar") else "en"
except (ValueError, TypeError):
    LANGUAGE = "en"

TEXT = {
    "ar": {
        "title": "إزالة الموسيقى من الفيديو",
        "starting": "جاري تجهيز الفيديو...",
        "check": "جاري فحص طريقة المعالجة...",
        "extract": "جاري استخراج الصوت من الفيديو...",
        "separate_gpu": "جاري فصل الكلام عن الموسيقى باستخدام كرت الشاشة...\nقد يستغرق ذلك بضع دقائق.",
        "separate_cpu": "لا يوجد تسريع NVIDIA متاح؛ ستتم المعالجة باستخدام المعالج وقد تستغرق وقتاً أطول...",
        "retry_cpu": "تعذر إكمال المعالجة على كرت الشاشة؛ سأحاول الآن باستخدام المعالج. قد يستغرق ذلك وقتاً أطول...",
        "download": "جاري تنزيل نموذج الفصل لأول مرة...\nاترك هذه النافذة مفتوحة حتى ينتهي التنزيل.",
        "mux": "جاري تركيب الصوت الجديد مع الفيديو...",
        "success_title": "اكتملت إزالة الموسيقى",
        "success": "تم حفظ النسخة بجانب الفيديو الأصلي باسم:\n\n{}",
        "missing_video": "لم أجد ملف الفيديو المحدد.",
        "missing_ffmpeg": "تعذر العثور على FFmpeg. أعد تشغيل install.ps1 لإصلاح التثبيت.",
        "missing_separator": "محرك فصل الصوت غير مثبت. شغّل install.ps1 من مجلد الأداة.",
        "extract_error": "تعذر استخراج الصوت. تأكد أن الفيديو يحتوي على صوت مدعوم.",
        "separate_error": "فشل فصل الصوت.",
        "no_stem": "انتهى الفصل، لكن لم يتم إنشاء مسار الكلام.",
        "mux_error": "تعذر حفظ الفيديو الناتج. صيغة الفيديو قد لا تكون مدعومة.",
        "name_error": "توجد ملفات كثيرة بالاسم الناتج نفسه. أعد تسمية بعضها ثم حاول مجدداً.",
        "error_title": "تعذر إكمال المعالجة",
        "start_error": "تعذر تشغيل الأداة",
        "description": "إزالة الموسيقى الخلفية من الفيديو مع إبقاء الكلام",
        "video_arg": "مسار الفيديو",
        "suffix": "_بدون_موسيقى",
    },
    "en": {
        "title": "Remove Background Music",
        "starting": "Preparing video...",
        "check": "Checking the available processing device...",
        "extract": "Extracting audio from the video...",
        "separate_gpu": "Separating speech from music on the NVIDIA GPU...\nThis may take a few minutes.",
        "separate_cpu": "NVIDIA acceleration is unavailable. Processing on the CPU may take longer...",
        "retry_cpu": "GPU processing failed. Retrying on the CPU; this may take longer...",
        "download": "Downloading the separation model for the first time...\nKeep this window open until it finishes.",
        "mux": "Adding the processed audio to the video...",
        "success_title": "Music removal complete",
        "success": "The processed video was saved beside the original as:\n\n{}",
        "missing_video": "The selected video could not be found.",
        "missing_ffmpeg": "FFmpeg was not found. Run install.ps1 again to repair the installation.",
        "missing_separator": "The audio separation engine is missing. Run install.ps1 from the app folder.",
        "extract_error": "Could not extract audio. Make sure the video contains a supported audio track.",
        "separate_error": "Audio separation failed.",
        "no_stem": "Separation finished, but no speech track was created.",
        "mux_error": "Could not save the output video. This video format may not be supported.",
        "name_error": "Too many files already use the output name. Rename some and try again.",
        "error_title": "Processing failed",
        "start_error": "Could not start Remove Music",
        "description": "Remove background music from a video while keeping speech",
        "video_arg": "Path to the video",
        "suffix": "_no_music",
    },
}[LANGUAGE]


class JobWindow:
    def __init__(self, video: Path):
        self.video = video
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()
        self.root = tk.Tk()
        self.root.title(TEXT["title"])
        if ICON.exists():
            self.root.iconbitmap(str(ICON))
        self.root.geometry("440x145")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        frame = ttk.Frame(self.root, padding=18)
        frame.pack(fill="both", expand=True)
        self.status = tk.StringVar(value=TEXT["starting"])
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        anchor = "e" if LANGUAGE == "ar" else "w"
        justify = "right" if LANGUAGE == "ar" else "left"
        self.label = ttk.Label(frame, text=self.status.get(), font=("Segoe UI", 11), wraplength=400, anchor=anchor, justify=justify)
        self.label.pack(anchor=anchor, fill="x")
        self.bar = ttk.Progressbar(frame, mode="indeterminate", length=400)
        self.bar.pack(fill="x", pady=(17, 10))
        ttk.Label(frame, text=video.name, wraplength=400).pack(anchor=anchor)
        self.bar.start(12)
        self.root.protocol("WM_DELETE_WINDOW", self._hide_window)
        self.root.after(150, self._poll)
        threading.Thread(target=self._worker, daemon=True).start()
        self.root.mainloop()

    def _hide_window(self) -> None:
        self.root.withdraw()

    def _set_status(self, text: str) -> None:
        self.events.put(("status", text))

    def _poll(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "status":
                    self.status.set(value)
                    self.label.configure(text=value)
                elif kind == "success":
                    self.bar.stop()
                    self.bar.configure(mode="determinate", value=100)
                    self.root.deiconify()
                    self.root.lift()
                    self.root.attributes("-topmost", True)
                    messagebox.showinfo(TEXT["success_title"], TEXT["success"].format(Path(value).name), parent=self.root)
                    self.root.destroy()
                    return
                elif kind == "error":
                    self.bar.stop()
                    self.root.deiconify()
                    self.root.lift()
                    messagebox.showerror(TEXT["error_title"], value, parent=self.root)
                    self.root.destroy()
                    return
        except queue.Empty:
            pass
        self.root.after(150, self._poll)

    def _run(self) -> Path:
        if not self.video.exists() or not self.video.is_file():
            raise RuntimeError(TEXT["missing_video"])
        if not FFMPEG:
            raise RuntimeError(TEXT["missing_ffmpeg"])
        if not SEPARATOR.exists():
            raise RuntimeError(TEXT["missing_separator"])

        self._set_status(TEXT["check"])
        env = self._runtime_environment()
        device_check = subprocess.run(
            [str(SEPARATOR), "--env_info"], cwd=str(ROOT), env=env,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=NO_CONSOLE,
        )
        device_report = device_check.stdout + "\n" + device_check.stderr
        gpu_available = device_check.returncode == 0 and "CUDAExecutionProvider available" in device_report

        self._set_status(TEXT["extract"])
        with tempfile.TemporaryDirectory(prefix="remove_music_") as work:
            workdir = Path(work)
            source_wav = workdir / "source.wav"
            stems_dir = workdir / "stems"
            stems_dir.mkdir()
            extract = [
                FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(self.video), "-map", "0:a:0", "-vn", "-ac", "2",
                "-ar", "44100", "-c:a", "pcm_s16le", str(source_wav),
            ]
            result = subprocess.run(extract, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=NO_CONSOLE)
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or TEXT["extract_error"])

            self._set_status(TEXT["separate_gpu"] if gpu_available else TEXT["separate_cpu"])
            command = [
                str(SEPARATOR), str(source_wav),
                "--model_filename", MODEL,
                "--single_stem", "Vocals",
                "--output_format", "WAV",
                "--output_dir", str(stems_dir),
                "--model_file_dir", str(MODEL_DIR),
                "--log_level", "info",
            ]
            attempts = [env]
            if gpu_available:
                cpu_env = env.copy()
                cpu_env["CUDA_VISIBLE_DEVICES"] = "-1"
                attempts.append(cpu_env)
            log_tail: list[str] = []
            separated = False
            for attempt_index, attempt_env in enumerate(attempts):
                if attempt_index == 1:
                    for partial in stems_dir.iterdir():
                        if partial.is_file():
                            partial.unlink()
                    self._set_status(TEXT["retry_cpu"])
                process = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace", bufsize=1, env=attempt_env,
                    creationflags=NO_CONSOLE,
                )
                log_tail = []
                assert process.stdout is not None
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        log_tail.append(line)
                        if len(log_tail) > 12:
                            log_tail.pop(0)
                    if line and ("Downloading" in line or "download" in line.lower()):
                        self._set_status(TEXT["download"])
                if process.wait() == 0:
                    separated = True
                    break
            if not separated:
                detail = "\n".join(log_tail[-6:])
                raise RuntimeError(TEXT["separate_error"] + (f"\n\n{detail}" if detail else ""))

            outputs = [Path(p) for p in glob.glob(str(stems_dir / "*.wav"))]
            outputs = [p for p in outputs if p.name.lower() != "source.wav"]
            if not outputs:
                raise RuntimeError(TEXT["no_stem"])
            voice_wav = outputs[0]

            output = self._available_output_path()
            self._set_status(TEXT["mux"])
            audio_codec = "libopus" if output.suffix.lower() == ".webm" else ("libmp3lame" if output.suffix.lower() == ".avi" else "aac")
            temp_output = output.with_name(output.stem + ".processing" + output.suffix)
            mux = [
                FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(self.video), "-i", str(voice_wav),
                "-map", "0:v:0", "-map", "1:a:0", "-map_metadata", "0", "-map_chapters", "0",
                "-c:v", "copy", "-c:a", audio_codec,
            ]
            if audio_codec == "aac":
                mux.extend(["-b:a", "192k"])
            elif audio_codec == "libopus":
                mux.extend(["-b:a", "160k"])
            mux.append(str(temp_output))
            result = subprocess.run(mux, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=NO_CONSOLE)
            if result.returncode != 0:
                temp_output.unlink(missing_ok=True)
                raise RuntimeError(TEXT["mux_error"] + "\n" + (result.stderr.strip() or ""))
            temp_output.replace(output)
            return output

    @staticmethod
    def _runtime_environment() -> dict[str, str]:
        env = os.environ.copy()
        package_root = ROOT / ".venv" / "Lib" / "site-packages" / "nvidia"
        dll_dirs = [str(path) for path in package_root.rglob("bin") if path.is_dir()] if package_root.exists() else []
        if dll_dirs:
            env["PATH"] = os.pathsep.join(dll_dirs + [env.get("PATH", "")])
        return env

    def _available_output_path(self) -> Path:
        suffix = TEXT["suffix"]
        base = self.video.with_name(f"{self.video.stem}{suffix}{self.video.suffix}")
        if not base.exists():
            return base
        for number in range(2, 1000):
            candidate = self.video.with_name(f"{self.video.stem}{suffix}_{number}{self.video.suffix}")
            if not candidate.exists():
                return candidate
        raise RuntimeError(TEXT["name_error"])

    def _worker(self) -> None:
        try:
            output = self._run()
            self.events.put(("success", str(output)))
        except Exception as error:
            self.events.put(("error", str(error)))


def main() -> int:
    parser = argparse.ArgumentParser(description=TEXT["description"])
    parser.add_argument("video", help=TEXT["video_arg"])
    args = parser.parse_args()
    try:
        JobWindow(Path(args.video))
        return 0
    except Exception as error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(TEXT["start_error"], str(error), parent=root)
        root.destroy()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
