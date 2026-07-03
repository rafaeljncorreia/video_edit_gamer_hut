"""CLI principal do pipeline de anúncio de Mercado Livre da Gamer Hut.

Uso:
    python src/build_ad.py transcribe media/raw/<slug>
        -> gera transcript_words.json (revise o texto antes de continuar)

    python src/build_ad.py render media/raw/<slug>
        -> gera captions.ass a partir do transcript revisado e renderiza
           o vídeo final em media/output/<slug>.mp4

Convenção de pasta (media/raw/<slug>/):
    cover.mp4           vídeo da capa do jogo (>= 3s)
    trailer.mp4          trailer horizontal do jogo
    narration.wav|mp3    narração gravada pelo usuário
    music.mp3 (opcional) música de fundo
"""

import argparse
from pathlib import Path

from pipeline import compose, subtitles, transcribe


def cmd_transcribe(args: argparse.Namespace) -> None:
    audio_path = compose.find_media(args.project_dir, "narration")
    if not audio_path:
        raise SystemExit(f"narration.* não encontrado em {args.project_dir}")

    words = transcribe.transcribe_words(audio_path, model_size=args.model, language=args.language)
    out_path = args.project_dir / "transcript_words.json"
    transcribe.write_words_json(words, out_path)

    print(f"Transcrição gerada: {out_path}")
    print(f'{len(words)} palavras. Revise o campo "word" de cada item (nomes de jogos, pronúncia) antes de rodar `render`.')
    print("Não altere os valores de start/end.")


def cmd_render(args: argparse.Namespace) -> None:
    project_dir = args.project_dir
    words_path = project_dir / "transcript_words.json"
    if not words_path.exists():
        raise SystemExit(f"{words_path} não existe. Rode `transcribe` primeiro e revise o texto.")

    import json
    words = json.loads(words_path.read_text(encoding="utf-8"))

    ass_path = project_dir / "captions.ass"
    subtitles.generate_ass(words, ass_path, offset=args.cover_duration)
    print(f"Legenda gerada: {ass_path}")

    out_path = args.out or (Path("media/output") / f"{project_dir.name}.mp4")
    compose.render(project_dir, out_path, cover_duration=args.cover_duration)
    print(f"Vídeo final: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline de anúncio Gamer Hut (Mercado Livre)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_transcribe = sub.add_parser("transcribe", help="Transcreve a narração com timestamp por palavra")
    p_transcribe.add_argument("project_dir", type=Path)
    p_transcribe.add_argument("--model", default=transcribe.DEFAULT_MODEL)
    p_transcribe.add_argument("--language", default="pt")
    p_transcribe.set_defaults(func=cmd_transcribe)

    p_render = sub.add_parser("render", help="Gera legenda final e renderiza o vídeo")
    p_render.add_argument("project_dir", type=Path)
    p_render.add_argument("--out", type=Path, default=None)
    p_render.add_argument("--cover-duration", type=float, default=compose.COVER_DURATION)
    p_render.set_defaults(func=cmd_render)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
