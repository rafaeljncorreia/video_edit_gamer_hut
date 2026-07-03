"""Gera legenda estilo karaokê (.ass) a partir de transcript_words.json.

Palavra atualmente falada em laranja (Orange Sunset #F26641), demais em
branco, conforme docs/brand/gamer-hut-brandbook.md e
docs/brand/style-guide-video.md.
"""

import argparse
import json
from pathlib import Path

WHITE = "&H00FFFFFF&"
ORANGE = "&H004166F2&"  # #F26641 em BGR (formato de cor do ASS)
BLACK_OUTLINE = "&H00000000&"

MAX_WORDS_PER_CHUNK = 5
MAX_CHARS_PER_CHUNK = 30
PAUSE_BREAK_SECONDS = 0.6

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Russo One,72,{white},{white},{black},{black},1,0,0,0,100,100,0,0,1,5,0,2,60,60,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".format(white=WHITE, black=BLACK_OUTLINE)


def _fmt_time(seconds: float) -> str:
    cs = round(seconds * 100)
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def chunk_words(words: list[dict]) -> list[list[dict]]:
    chunks: list[list[dict]] = []
    current: list[dict] = []
    current_chars = 0

    for i, w in enumerate(words):
        word_text = w["word"]
        gap = w["start"] - words[i - 1]["end"] if i > 0 else 0
        strong_break = current and (gap > PAUSE_BREAK_SECONDS or words[i - 1]["word"].endswith((".", "!", "?")))

        would_overflow = current and (
            len(current) >= MAX_WORDS_PER_CHUNK
            or current_chars + 1 + len(word_text) > MAX_CHARS_PER_CHUNK
        )

        if strong_break or would_overflow:
            chunks.append(current)
            current = []
            current_chars = 0

        current.append(w)
        current_chars += (1 if current_chars else 0) + len(word_text)

    if current:
        chunks.append(current)
    return chunks


def build_dialogue_lines(chunks: list[list[dict]], offset: float = 0.0) -> list[str]:
    lines = []
    for chunk in chunks:
        for active_idx, active_word in enumerate(chunk):
            text_parts = []
            for idx, w in enumerate(chunk):
                color = ORANGE if idx == active_idx else WHITE
                text_parts.append("{\\c%s}%s" % (color, w["word"]))
            text = " ".join(text_parts)
            start = _fmt_time(active_word["start"] + offset)
            end = _fmt_time(active_word["end"] + offset)
            lines.append(f"Dialogue: 0,{start},{end},Caption,,0,0,0,,{text}")
    return lines


def generate_ass(words: list[dict], out_path: Path, offset: float = 0.0) -> None:
    """offset: segundos a somar em todos os timestamps (ex: duração da capa,
    já que a narração começa depois dela na timeline final)."""
    chunks = chunk_words(words)
    dialogue_lines = build_dialogue_lines(chunks, offset=offset)
    out_path.write_text(ASS_HEADER + "\n".join(dialogue_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera legenda karaokê .ass a partir de transcript_words.json")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--words-file", default="transcript_words.json")
    parser.add_argument("--out", default="captions.ass")
    parser.add_argument("--offset", type=float, default=0.0, help="Segundos a somar nos timestamps (ex: duração da capa)")
    args = parser.parse_args()

    words_path = args.project_dir / args.words_file
    words = json.loads(words_path.read_text(encoding="utf-8"))

    out_path = args.project_dir / args.out
    generate_ass(words, out_path, offset=args.offset)
    print(f"Legenda gerada: {out_path}")


if __name__ == "__main__":
    main()
