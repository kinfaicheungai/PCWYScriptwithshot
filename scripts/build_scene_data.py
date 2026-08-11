from pathlib import Path
import json
import re
from PIL import Image

PROJECT = Path(__file__).resolve().parents[3]
SITE = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT / "tmp/pdfs/painting_christmas_blue_draft.txt"
BOARDS = PROJECT / "output/storyboards"
PUBLIC = SITE / "public/boards"

CHARACTERS = {
    "SHELBY", "HENRY", "BEVERLY", "NIGEL", "GEORGE", "KING GEORGE", "BECKS",
    "MIA", "VOICE", "PHONE VOICE", "VOICE MESSAGE", "VOLUNTEER", "AUDIENCE MEMBER",
    "SHELBY & HENRY", "SHELBY/HENRY", "UNKNOWN NUMBER", "MOM",
}


def clean(line: str) -> str:
    return line.replace("*", "").strip()


def scene_number(line: str):
    if not re.match(r"^(INT\.|EXT\.|INT\./EXT\.)", line):
        return None
    match = re.search(r"(\d+)[A-Z]?\s+(\d+)[A-Z]?$", line)
    return int(match.group(2)) if match else None


def title_from_heading(line: str) -> str:
    return re.sub(r"\d+[A-Z]?\s+\d+[A-Z]?$", "", line).strip(" -")


def character_cue(line: str) -> bool:
    base = re.sub(r"\s*\([^)]*\)\s*", "", line).strip()
    return base in CHARACTERS or base.replace("’", "'") in CHARACTERS


def action_start(line: str) -> bool:
    subjects = r"(?:Shelby|Henry|Beverly|Nigel|George|Becks|Mia|He|She|They|Both|Everyone|Someone|The camera|The crew|The room|The crowd|A camera|A person|One of the artists)"
    verbs = r"(?:looks?|smiles?|laughs?|nods?|turns?|steps?|walks?|runs?|sits?|stands?|grabs?|takes?|holds?|offers?|pulls?|pushes?|opens?|closes?|enters?|exits?|leaves?|pauses?|stops?|begins?|watches?|stares?|glances?|rolls?|shakes?|sighs?|frowns?|grins?|beams?|freezes?|rushes?|picks?|sets?|puts?|throws?|reaches?|gestures?|points?|notices?|reads?|dials?|hangs?|answers?|removes?|approaches?|arrives?|follows?|crosses?|kisses?|hugs?|shrugs?|paints?|sketches?|studies?|rummages?|pours?|lifts?|reveals?|claps?|falls?|leans?|continues?|breaks?|erupts?)"
    return bool(re.match(rf"^{subjects}\s+{verbs}\b", line, re.I) or re.match(r"^(CUT TO|INSERT|FOCUS ON|CLOSE ON|BEGIN |END |Just then)", line, re.I))


def parse_script():
    raw = SCRIPT.read_text(encoding="utf-8").splitlines()
    scenes = {}
    current = None
    heading = ""
    blocks = []
    i = 0

    def flush_scene():
        if current is not None:
            scenes.setdefault(current, {"title": heading, "blocks": []})["blocks"].extend(blocks)

    while i < len(raw):
        line = clean(raw[i])
        if not line or re.match(r"^BLUE SCRIPT 07/08/26 \d+[A-Z]?\.$", line):
            i += 1
            continue
        number = scene_number(line)
        if number is not None:
            flush_scene()
            current, heading, blocks = number, title_from_heading(line), []
            i += 1
            continue
        if current is None:
            i += 1
            continue
        if character_cue(line):
            blocks.append({"type": "character", "text": line})
            i += 1
            dialogue = []
            while i < len(raw):
                part = clean(raw[i])
                if not part or re.match(r"^BLUE SCRIPT 07/08/26 \d+[A-Z]?\.$", part):
                    i += 1
                    continue
                if scene_number(part) is not None or character_cue(part) or action_start(part):
                    break
                if part.startswith("(") and part.endswith(")"):
                    if dialogue:
                        blocks.append({"type": "dialogue", "text": "\n".join(dialogue)})
                        dialogue = []
                    blocks.append({"type": "parenthetical", "text": part})
                else:
                    dialogue.append(part)
                i += 1
            if dialogue:
                blocks.append({"type": "dialogue", "text": "\n".join(dialogue)})
            continue
        action = [line]
        i += 1
        while i < len(raw):
            part = clean(raw[i])
            if not part or re.match(r"^BLUE SCRIPT 07/08/26 \d+[A-Z]?\.$", part):
                i += 1
                if action:
                    break
                continue
            if scene_number(part) is not None or character_cue(part):
                break
            action.append(part)
            i += 1
        text = "\n".join(action)
        if text not in {"CUT TO:", "CUT TO", "THE END."}:
            blocks.append({"type": "action", "text": text})
    flush_scene()
    return scenes


def collect_boards():
    boards = {}
    for path in sorted(BOARDS.glob("S*-S*/*.png")):
        match = re.match(r"S(\d+)([A-Z]?)", path.name, re.I)
        if match:
            boards.setdefault(int(match.group(1)), []).append(path)
    return boards


scenes = parse_script()
boards = collect_boards()
PUBLIC.mkdir(parents=True, exist_ok=True)
data = []
for number in sorted(set(scenes) | set(boards)):
    images = []
    for index, source in enumerate(boards.get(number, []), 1):
        target_name = f"S{number:02d}_{index:02d}.jpg"
        target = PUBLIC / target_name
        with Image.open(source) as image:
            image = image.convert("RGB")
            if image.width > 1600:
                height = round(image.height * 1600 / image.width)
                image = image.resize((1600, height), Image.Resampling.LANCZOS)
            image.save(target, "JPEG", quality=76, optimize=True, progressive=True)
        images.append(f"/boards/{target_name}")
    info = scenes.get(number, {"title": "Storyboard scene", "blocks": [{"type": "action", "text": "No screenplay text found for this scene."}]})
    data.append({"number": number, "title": info["title"], "blocks": info["blocks"], "images": images})

(SITE / "app/scenes.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Built {len(data)} scenes with {sum(len(s['images']) for s in data)} storyboard images")
