"""Extrai metadados técnicos de arquivos de vídeo/áudio via ffprobe.

Uso:
    python src/utils/video_info.py media/reference/ --table
        -> lista tabular de todos os vídeos no diretório

    python src/utils/video_info.py media/raw/mortal-kombat-1/cover.mp4 --json
        -> JSON completo de streams + formato

    python src/utils/video_info.py media/reference/ --summary
        -> estatísticas agregadas (resolução mais comum, codecs, etc.)
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def probe(path: Path) -> dict:
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate",
        "-show_entries", "stream=codec_type,codec_name,width,height,duration,r_frame_rate,sample_rate,channels",
        "-of", "json",
        str(path),
    ], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def fmt_fps(r_frame_rate: str) -> str:
    if not r_frame_rate or r_frame_rate == "0/0":
        return "N/A"
    parts = r_frame_rate.split("/")
    if len(parts) == 2 and int(parts[1]) != 0:
        return f"{int(parts[0]) / int(parts[1]):.2f}"
    return r_frame_rate


def size_str(size_bytes: str) -> str:
    if not size_bytes:
        return "N/A"
    mb = int(size_bytes) / (1024 * 1024)
    return f"{mb:.1f} MB"


def cmd_single(args: argparse.Namespace) -> None:
    data = probe(args.path)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    fmt = data.get("format", {})
    print(f"Arquivo: {args.path.name}")
    print(f"  Duração: {float(fmt.get('duration', 0)):.2f}s")
    print(f"  Tamanho: {size_str(fmt.get('size', '0'))}")
    print(f"  Bitrate: {fmt.get('bit_rate', 'N/A')} bps")
    for s in data.get("streams", []):
        t = s.get("codec_type", "?")
        print(f"  Stream [{t}]:")
        print(f"    Codec: {s.get('codec_name', '?')}")
        if t == "video":
            print(f"    Resolução: {s.get('width', '?')}x{s.get('height', '?')}")
            print(f"    FPS: {fmt_fps(s.get('r_frame_rate', ''))}")
        elif t == "audio":
            print(f"    Sample rate: {s.get('sample_rate', '?')} Hz")
            print(f"    Canais: {s.get('channels', '?')}")


def cmd_table(args: argparse.Namespace) -> None:
    pattern = "*." + args.ext
    files = sorted(args.path.glob(pattern)) if args.path.is_dir() else [args.path]
    if not files:
        print(f"Nenhum arquivo *.{args.ext} encontrado em {args.path}")
        sys.exit(1)

    rows = []
    for f in files:
        data = probe(f)
        fmt = data.get("format", {})
        vid = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
        aud = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
        rows.append({
            "nome": f.name,
            "duracao": float(fmt.get("duration", 0)),
            "tamanho": size_str(fmt.get("size", "0")),
            "resolucao": f"{vid.get('width', '?')}x{vid.get('height', '?')}",
            "fps": fmt_fps(vid.get("r_frame_rate", "")),
            "vcodec": vid.get("codec_name", "?"),
            "acodec": aud.get("codec_name", "sem áudio"),
        })

    col_w = max(len(r["nome"]) for r in rows) + 2
    header = f"{'Arquivo':<{col_w}} {'Duração':>8} {'Tamanho':>10} {'Resolução':>14} {'FPS':>8} {'V.Codec':>8} {'A.Codec':>10}"
    sep = "-" * len(header)
    print(header)
    print(sep)
    for r in rows:
        print(f"{r['nome']:<{col_w}} {r['duracao']:>7.1f}s {r['tamanho']:>10} {r['resolucao']:>14} {r['fps']:>8} {r['vcodec']:>8} {r['acodec']:>10}")


def cmd_summary(args: argparse.Namespace) -> None:
    files = sorted(args.path.rglob("*.*")) if args.path.is_dir() else [args.path]
    videos = [f for f in files if f.suffix.lower() in (".mp4", ".mov", ".mkv", ".avi", ".webm")]

    if not videos:
        print(f"Nenhum vídeo encontrado em {args.path}")
        sys.exit(1)

    resolutions = Counter()
    codecs = Counter()
    durations = []

    for f in videos:
        data = probe(f)
        fmt = data.get("format", {})
        dur = float(fmt.get("duration", 0))
        if dur > 0:
            durations.append(dur)
        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                w, h = s.get("width", "?"), s.get("height", "?")
                resolutions[f"{w}x{h}"] += 1
                codecs[s.get("codec_name", "?")] += 1

    print(f"Total de arquivos de vídeo: {len(videos)}")
    print(f"Resoluções: {dict(resolutions)}")
    print(f"Codecs de vídeo: {dict(codecs)}")
    if durations:
        print(f"Duração total: {sum(durations):.1f}s")
        print(f"Duração média: {sum(durations)/len(durations):.1f}s")
        print(f"Mín/Máx: {min(durations):.1f}s / {max(durations):.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrai metadados de vídeo/áudio via ffprobe")
    sub = parser.add_subparsers(dest="command", required=True)

    p_single = sub.add_parser("info", help="Info detalhada de um único arquivo")
    p_single.add_argument("path", type=Path)
    p_single.add_argument("--json", action="store_true", help="Saída em JSON bruto")
    p_single.set_defaults(func=cmd_single)

    p_table = sub.add_parser("table", help="Tabela de todos os vídeos de um diretório")
    p_table.add_argument("path", type=Path)
    p_table.add_argument("--ext", default="mp4", help="Extensão a buscar (default: mp4)")
    p_table.set_defaults(func=cmd_table)

    p_summary = sub.add_parser("summary", help="Estatísticas agregadas de um diretório")
    p_summary.add_argument("path", type=Path)
    p_summary.set_defaults(func=cmd_summary)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
