from pathlib import Path
import json
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, XPreformatted

SITE = Path(__file__).resolve().parents[1]
OUTPUT = SITE.parent / "pdf/PaintingChristmas_Storyboard_Screenplay.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
scenes = json.loads((SITE / "app/scenes.json").read_text(encoding="utf-8"))

pdfmetrics.registerFont(TTFont("CourierNew", "/System/Library/Fonts/Supplemental/Courier New.ttf"))
pdfmetrics.registerFont(TTFont("CourierNewBold", "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"))

page_width, page_height = A4
doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
    topMargin=15 * mm, bottomMargin=16 * mm,
    title="Painting Christmas With You - Storyboard and Screenplay",
)
styles = getSampleStyleSheet()
scene_style = ParagraphStyle("Scene", parent=styles["Heading1"], fontName="CourierNewBold", fontSize=13, leading=16, textColor="#a92324", spaceAfter=5 * mm)
action_style = ParagraphStyle("Action", fontName="CourierNew", fontSize=9.2, leading=11.5, alignment=TA_LEFT, spaceAfter=3.5 * mm)
character_style = ParagraphStyle("Character", fontName="CourierNew", fontSize=9.2, leading=11.5, leftIndent=70 * mm, spaceBefore=2 * mm)
paren_style = ParagraphStyle("Paren", fontName="CourierNew", fontSize=9.2, leading=11.5, leftIndent=55 * mm, rightIndent=38 * mm)
dialogue_style = ParagraphStyle("Dialogue", fontName="CourierNew", fontSize=9.2, leading=11.5, leftIndent=38 * mm, rightIndent=38 * mm, spaceAfter=3.5 * mm)


def footer(canvas, document):
    canvas.saveState()
    canvas.setFont("CourierNew", 7.5)
    canvas.setFillColor("#777777")
    canvas.drawCentredString(page_width / 2, 8 * mm, f"PAINTING CHRISTMAS WITH YOU   |   {document.page}")
    canvas.restoreState()


story = []
for scene_index, scene in enumerate(scenes):
    if scene_index:
        story.append(PageBreak())
    story.append(Paragraph(f"SCENE {scene['number']}   {escape(scene['title'])}", scene_style))
    for image_url in scene["images"]:
        image_path = SITE / "public" / image_url.lstrip("/")
        picture = Image(str(image_path))
        max_w, max_h = 174 * mm, 105 * mm
        scale = min(max_w / picture.imageWidth, max_h / picture.imageHeight)
        picture.drawWidth = picture.imageWidth * scale
        picture.drawHeight = picture.imageHeight * scale
        story.extend([picture, Spacer(1, 4 * mm)])
    if not scene["images"]:
        story.append(Paragraph("No storyboard artwork for this scene.", action_style))
    for block in scene["blocks"]:
        style = {"action": action_style, "character": character_style, "parenthetical": paren_style, "dialogue": dialogue_style}[block["type"]]
        story.append(XPreformatted(escape(block["text"]), style))

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"Created {OUTPUT}: {OUTPUT.stat().st_size / 1048576:.1f} MB")
