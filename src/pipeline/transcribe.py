"""Transcreve a narração com timestamp por palavra, usando Whisper local.

Gera um arquivo `transcript_words.json` editável: cada objeto do array é uma
palavra com {start, end, word}. O usuário deve revisar e corrigir o texto de
"word" (nomes de jogos, pronúncia confusa) antes da etapa de renderização —
os timestamps não devem ser alterados.
"""

import argparse
import json
from pathlib import Path

import whisper

DEFAULT_MODEL = "small"


def transcribe_words(audio_path: Path, model_size: str = DEFAULT_MODEL, language: str = "pt") -> list[dict]:
    model = whisper.load_model(model_size)
    result = model.transcribe(str(audio_path), language=language, word_timestamps=True)

    words = []
    for segment in result["segments"]:
        for w in segment.get("words", []):
            words.append({
                "start": round(w["start"], 3),
                "end": round(w["end"], 3),
                "word": w["word"].strip(),
            })
    return words


def write_words_json(words: list[dict], out_path: Path) -> None:
    lines = [json.dumps(w, ensure_ascii=False) for w in words]
    out_path.write_text("[\n" + ",\n".join(lines) + "\n]\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcreve narração com timestamp por palavra")
    parser.add_argument("project_dir", type=Path, help="Pasta do vídeo, ex: media/raw/mortal-kombat-1")
    parser.add_argument("--narration", default="narration.wav", help="Nome do arquivo de narração dentro da pasta")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Tamanho do modelo Whisper (tiny/base/small/medium/large)")
    parser.add_argument("--language", default="pt")
    args = parser.parse_args()

    audio_path = args.project_dir / args.narration
    if not audio_path.exists():
        raise SystemExit(f"Narração não encontrada: {audio_path}")

    words = transcribe_words(audio_path, model_size=args.model, language=args.language)

    out_path = args.project_dir / "transcript_words.json"
    write_words_json(words, out_path)

    print(f"Transcrição gerada: {out_path}")
    print(f"{len(words)} palavras. Revise o campo \"word\" de cada item antes de renderizar (não altere start/end).")


if __name__ == "__main__":
    main()
