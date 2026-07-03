"""Monta o anúncio de Mercado Livre: capa (3s) + trailer (fundo desfocado +
centro nítido) + narração/música, e queima a legenda karaokê.

Convenção de pasta (media/raw/<slug>/):
    cover.mp4         vídeo da capa do jogo (>= COVER_DURATION segundos)
    trailer.mp4        trailer horizontal do jogo (qualquer duração; repete em loop se for curto)
    narration.<ext>    narração do usuário (wav/mp3)
    music.<ext>        (opcional) música de fundo (repete em loop se for curta)
    captions.ass        gerado por subtitles.py a partir de transcript_words.json revisado

Saída: 1080x1920, 30fps, sem áudio nos clipes originais — só narração + música.

Nota de implementação: o pipeline roda em múltiplos passes de ffmpeg (cada um
com um único filtro/saída) em vez de um único filter_complex gigante. Um
grafo único combinando trim+concat+overlay(boxblur) nesta build do ffmpeg
produzia frames corrompidos (conteúdo da capa vazando pro centro nítido do
trailer) — reproduzido de forma isolada e contornado com passes separados.
"""

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

CANVAS_W = 1080
CANVAS_H = 1920
BAND_H = CANVAS_H // 3  # faixa central nítida do trailer
COVER_DURATION = 3.0
MUSIC_VOLUME = 0.12
FPS = 30


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def find_media(project_dir: Path, stem: str) -> Path | None:
    for ext in (".mp4", ".mov", ".mkv", ".wav", ".mp3", ".m4a"):
        candidate = project_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def _render_cover_segment(cover_path: Path, cover_duration: float, out_path: Path) -> None:
    vf = f"scale={CANVAS_W}:{CANVAS_H}:force_original_aspect_ratio=increase,crop={CANVAS_W}:{CANVAS_H},setsar=1,fps={FPS}"
    _run([
        "ffmpeg", "-y", "-i", str(cover_path), "-t", str(cover_duration),
        "-vf", vf, "-an",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(out_path),
    ])


def _render_trailer_segment(trailer_path: Path, duration: float, out_path: Path) -> None:
    filter_complex = ";".join([
        f"[0:v]trim=0:{duration},setpts=PTS-STARTPTS,fps={FPS}[src]",
        f"[src]scale={CANVAS_W}:{CANVAS_H}:force_original_aspect_ratio=increase,crop={CANVAS_W}:{CANVAS_H},boxblur=20:5,setsar=1[bg]",
        f"[src]scale={CANVAS_W}:{BAND_H}:force_original_aspect_ratio=decrease,pad={CANVAS_W}:{BAND_H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[fg]",
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[out]",
    ])
    _run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(trailer_path),
        "-filter_complex", filter_complex, "-map", "[out]", "-an",
        "-t", str(duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(out_path),
    ])


def _concat_segments(cover_seg: Path, trailer_seg: Path, out_path: Path, tmp_dir: Path) -> None:
    filelist = tmp_dir / "concat_list.txt"
    filelist.write_text(
        f"file '{cover_seg.resolve().as_posix()}'\nfile '{trailer_seg.resolve().as_posix()}'\n",
        encoding="utf-8",
    )
    _run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(filelist),
        "-c", "copy", str(out_path),
    ])


def _render_audio(narration_path: Path, music_path: Path | None, cover_duration: float,
                   narration_duration: float, total_duration: float, out_path: Path) -> None:
    narration_delay_ms = int(round(cover_duration * 1000))
    inputs = ["-i", str(narration_path)]
    if music_path:
        inputs += ["-stream_loop", "-1", "-i", str(music_path)]

    filters = [
        f"[0:a]adelay={narration_delay_ms}|{narration_delay_ms},apad,atrim=0:{total_duration}[narr]",
    ]
    if music_path:
        filters.append(f"[1:a]volume={MUSIC_VOLUME},aloop=loop=-1:size=2147483647,atrim=0:{total_duration}[music]")
        filters.append("[narr][music]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]")
        map_label = "[aout]"
    else:
        map_label = "[narr]"

    _run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", map_label,
        "-c:a", "aac", "-b:a", "192k",
        str(out_path),
    ])


def _mux_final(silent_video: Path, audio: Path, ass_path: Path, total_duration: float, out_path: Path) -> None:
    ass_filter_path = str(ass_path).replace("\\", "/").replace(":", "\\:")
    _run([
        "ffmpeg", "-y", "-i", str(silent_video), "-i", str(audio),
        "-vf", f"ass='{ass_filter_path}'",
        "-map", "0:v", "-map", "1:a",
        "-t", str(total_duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k",
        str(out_path),
    ])


def render(project_dir: Path, output_path: Path, cover_duration: float = COVER_DURATION) -> None:
    cover_path = find_media(project_dir, "cover")
    trailer_path = find_media(project_dir, "trailer")
    narration_path = find_media(project_dir, "narration")
    music_path = find_media(project_dir, "music")
    ass_path = project_dir / "captions.ass"

    if not cover_path or not trailer_path or not narration_path:
        raise SystemExit("Faltam arquivos: cover.*, trailer.* e narration.* são obrigatórios em " + str(project_dir))
    if not ass_path.exists():
        raise SystemExit(f"Legenda não encontrada: {ass_path}. Rode subtitles.py primeiro.")

    cover_duration_available = probe_duration(cover_path)
    if cover_duration_available < cover_duration:
        raise SystemExit(
            f"cover ({cover_duration_available:.2f}s) é mais curto que os {cover_duration}s esperados. "
            "Use um clipe de capa mais longo ou ajuste --cover-duration."
        )

    narration_duration = probe_duration(narration_path)
    total_duration = cover_duration + narration_duration

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="gh_build_") as tmp:
        tmp_dir = Path(tmp)
        cover_seg = tmp_dir / "cover_seg.mp4"
        trailer_seg = tmp_dir / "trailer_seg.mp4"
        silent_video = tmp_dir / "silent_video.mp4"
        audio_mix = tmp_dir / "audio_mix.m4a"

        _render_cover_segment(cover_path, cover_duration, cover_seg)
        _render_trailer_segment(trailer_path, narration_duration, trailer_seg)
        _concat_segments(cover_seg, trailer_seg, silent_video, tmp_dir)
        _render_audio(narration_path, music_path, cover_duration, narration_duration, total_duration, audio_mix)
        _mux_final(silent_video, audio_mix, ass_path, total_duration, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Renderiza o anúncio final de Mercado Livre")
    parser.add_argument("project_dir", type=Path, help="Pasta em media/raw/<slug>")
    parser.add_argument("--out", type=Path, help="Caminho de saída (default: media/output/<slug>.mp4)")
    parser.add_argument("--cover-duration", type=float, default=COVER_DURATION)
    args = parser.parse_args()

    out_path = args.out or (Path("media/output") / f"{args.project_dir.name}.mp4")
    render(args.project_dir, out_path, cover_duration=args.cover_duration)
    print(f"Vídeo final: {out_path}")


if __name__ == "__main__":
    main()
