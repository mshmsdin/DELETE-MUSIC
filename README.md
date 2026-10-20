# Remove Music

![Remove Music icon](music_off.png)

A small Windows utility that removes background music from a video while keeping speech. It creates a new video beside the original and leaves the original untouched. Processing stays on the user's computer.

The app automatically uses an NVIDIA GPU when its CUDA runtime is available. It also supports CPU-only computers; processing on a CPU takes longer. If GPU processing fails, the app retries on the CPU. A high-end GPU is not required.

## Use

After installation, right-click a video and choose **Send to > Remove Background Music**. On Windows 11, open **Show more options** if the classic menu is not visible. A progress window appears during processing, followed by the location and name of the result.

The output is saved in the same folder as the source video. On English Windows, its name ends in `_no_music`; on Arabic Windows, it ends in `_بدون_موسيقى`. If that filename already exists, a number is added so the existing file is not overwritten.

The app supports common video formats through FFmpeg, including MP4, MKV, MOV, M4V, WebM, AVI, WMV, FLV, TS, MTS, and M2TS. The video stream is copied without re-encoding when the container allows it.

## Install from source

Requirements: Windows 10 or 11, Python 3.10 available through the `py` launcher, and an internet connection for setup and the first model download.

1. Download or clone this repository.
2. Run `install.ps1` from PowerShell.
3. Wait for the installer to create an isolated Python environment, install the appropriate CPU or NVIDIA runtime, download the model, and add the **Send to** shortcut.

The installer detects a working NVIDIA driver with `nvidia-smi`. It installs CUDA-enabled libraries when found and CPU libraries otherwise. No CUDA toolkit setup is required from the user.

The model is downloaded during installation and is not stored in this repository. The app uses the open-source [Audio Separator](https://github.com/nomadkaraoke/python-audio-separator) project and FFmpeg through [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg). Their respective licenses and the model terms apply to those components.

## Uninstall the menu shortcut

Run `uninstall.ps1`. This removes the **Send to** shortcut and keeps the app files and downloaded model.

## Build the launcher

After setup, run `build_launcher.ps1` to compile the small Windows GUI launcher with the bundled icon. Python starts with `pythonw.exe`, so processing does not open a terminal window.

## Quality notes

The separation model identifies a vocal stem. It works best when speech and music are reasonably distinct. Some music can remain, and speech can be softened or distorted when it overlaps heavily with instruments.

## العربية

أداة لويندوز تزيل موسيقى الخلفية من الفيديو وتُبقي الكلام، ثم تحفظ نسخة جديدة بجانب الملف الأصلي دون استبداله. تتم المعالجة محلياً على جهاز المستخدم.

تستخدم الأداة بطاقة NVIDIA تلقائياً إذا كان تسريع CUDA متاحاً، وتعمل أيضاً على المعالج في الأجهزة التي لا تحتوي على بطاقة مناسبة. وإذا تعذر إكمال المعالجة على البطاقة، تعيد المحاولة بالمعالج؛ ستكون المعالجة أبطأ ولا يلزم كرت شاشة قوي.

بعد التثبيت: انقر بزر الفأرة الأيمن على الفيديو ثم اختر **إرسال إلى ← Remove Background Music**. في ويندوز 11 قد تحتاج إلى **إظهار المزيد من الخيارات**. تحفظ الأداة الناتج في المجلد نفسه، وتضيف `_بدون_موسيقى` إلى الاسم في ويندوز العربي أو `_no_music` في ويندوز الإنجليزي.

للتثبيت، نزّل المستودع وشغّل `install.ps1` من PowerShell. يحتاج التثبيت إلى Python 3.10 واتصال بالإنترنت لتنزيل المكتبات والنموذج. يكتشف المثبّت بطاقة NVIDIA ويختار CUDA أو نسخة المعالج تلقائياً.

قد تبقى آثار موسيقية أو يتأثر الكلام إذا تداخل بقوة مع الآلات الموسيقية.
