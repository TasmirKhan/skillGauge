from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

NAVY = RGBColor(12, 55, 98)
BLUE = RGBColor(45, 120, 180)
LIGHT = RGBColor(240, 245, 250)
ACCENT = RGBColor(86, 168, 233)
TEXT = RGBColor(26, 32, 44)
WHITE = RGBColor(255, 255, 255)


def add_bg(slide, color=WHITE):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background()


def add_title(slide, text, x=0.7, y=0.3, w=12.0, h=0.6, color=TEXT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    p = box.text_frame.paragraphs[0]
    p.text = text
    r = p.runs[0]
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = color


def add_textbox_lines(container, x=None, y=None, w=None, h=None, lines=None, size=18, color=TEXT, bold=False, align=PP_ALIGN.LEFT, bullet=False):
    if hasattr(container, 'shapes'):
        box = container.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    else:
        box = container
    tf = box.text_frame
    tf.text = '\n'.join(lines)
    for p in tf.paragraphs:
        if bullet:
            p.level = 0
            p.bullet = True
        p.alignment = align
        for run in p.runs:
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
    return box

# Slide 1
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, NAVY)
shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(5.9), Inches(2.2))
shape.fill.solid(); shape.fill.fore_color.rgb = BLUE; shape.line.fill.background()
add_textbox_lines(slide, 1.15, 1.4, 5.0, 0.8, ['DSA Practice'], size=30, color=WHITE, bold=True)
add_textbox_lines(slide, 1.15, 2.2, 6.0, 0.8, ['Randomized question selector for coding practice'], size=18, color=WHITE)
card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.0), Inches(1.8), Inches(3.8), Inches(2.3))
card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = WHITE; card.line.width = 1
frame = card.text_frame
frame.text = 'Project Type: Java Console App\nPurpose: Pick 5 unique DSA questions\nRange: 101 to 140'
for p in frame.paragraphs:
    p.alignment = PP_ALIGN.LEFT
    for run in p.runs:
        run.font.size = Pt(16)
        run.font.color.rgb = NAVY

# Slide 2
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, LIGHT)
add_title(slide, 'Project Overview', color=NAVY)
left = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.1), Inches(5.7), Inches(4.4))
left.fill.solid(); left.fill.fore_color.rgb = WHITE; left.line.color.rgb = BLUE; left.line.width = 1
add_textbox_lines(left, 0.2, 0.2, 5.0, 3.8, [
    'Generates a list of DSA question IDs from 101 to 140',
    'Shuffles the list with a fixed random seed',
    'Selects only 5 unique values',
    'Displays the final output in the console',
    'Helps users revise different problems without repetition'
], size=20, color=TEXT, bullet=True)

cyl = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.3), Inches(1.8), Inches(4.7), Inches(3.2))
cyl.fill.solid(); cyl.fill.fore_color.rgb = BLUE; cyl.line.color.rgb = BLUE
cbox = slide.shapes.add_textbox(Inches(7.6), Inches(2.6), Inches(4.1), Inches(1.2))
cb = cbox.text_frame
cb.text = '101-140\nQuestion Pool'
for p in cb.paragraphs:
    p.alignment = PP_ALIGN.CENTER
    for run in p.runs:
        run.font.size = Pt(20); run.font.bold = True; run.font.color.rgb = WHITE

# Slide 3
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, WHITE)
add_title(slide, 'Key Features', color=NAVY)
add_textbox_lines(slide, 0.9, 1.3, 12.0, 4.8, [
    'Randomized selection using Collections.shuffle()',
    'Duplicates are prevented using LinkedHashSet',
    'Uses a fixed random seed for repeatable output',
    'Focuses on a small, manageable set of 5 questions',
    'Simple, beginner-friendly Java implementation'], size=22, color=TEXT, bullet=True)

# Slide 4
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, LIGHT)
add_title(slide, 'How the Program Works', color=NAVY)
steps = [
    ('1. Create list', 'Adds numbers from 101 to 140'),
    ('2. Shuffle', 'Uses Random(42) to randomize order'),
    ('3. Select', 'Keeps the first 5 unique values'),
    ('4. Print', 'Shows final selected IDs in the console')
]
start_x = 0.8
for idx, (title, desc) in enumerate(steps):
    x = Inches(start_x + idx * 3.0)
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(2.4), Inches(2.6))
    card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = ACCENT; card.line.width = 1
    tf = card.text_frame
    tf.text = f'{title}\n{desc}'
    for p in tf.paragraphs:
        p.alignment = PP_ALIGN.CENTER
        for run in p.runs:
            run.font.color.rgb = TEXT
    p0 = tf.paragraphs[0]; p0.runs[0].font.size = Pt(18); p0.runs[0].font.bold = True; p0.runs[0].font.color.rgb = NAVY
    p1 = tf.paragraphs[1]; p1.runs[0].font.size = Pt(11); p1.runs[0].font.color.rgb = TEXT
    if idx < len(steps) - 1:
        arr = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + Inches(2.4), Inches(2.8), Inches(0.5), Inches(0.5))
        arr.fill.solid(); arr.fill.fore_color.rgb = ACCENT; arr.line.fill.background()

# Slide 5
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, WHITE)
add_title(slide, 'Data Structures Used', color=NAVY)
items = [
    ('ArrayList', 'Stores all question IDs before selection.'),
    ('Random', 'Creates a predictable random order for testing.'),
    ('LinkedHashSet', 'Ensures only unique values are kept, in insertion order.'),
    ('Set', 'Represents a collection of unique question IDs.')
]
for idx, (name, desc) in enumerate(items):
    y = Inches(1.5 + idx * 1.4)
    pill = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(2.3), Inches(0.8))
    pill.fill.solid(); pill.fill.fore_color.rgb = BLUE; pill.line.fill.background()
    tp = pill.text_frame.paragraphs[0]; tp.text = name; tp.alignment = PP_ALIGN.CENTER
    for run in tp.runs:
        run.font.size = Pt(16); run.font.bold = True; run.font.color.rgb = WHITE
    txt = slide.shapes.add_textbox(Inches(3.3), y, Inches(8.5), Inches(0.8))
    p = txt.text_frame.paragraphs[0]; p.text = desc
    for run in p.runs:
        run.font.size = Pt(20); run.font.color.rgb = TEXT

# Slide 6
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, LIGHT)
add_title(slide, 'Code Snapshot', color=NAVY)
codebox = slide.shapes.add_textbox(Inches(0.7), Inches(1.3), Inches(11.8), Inches(4.6))
code = '\n'.join([
    'List<Integer> questionIds = new ArrayList<>();',
    'for (int i = 101; i <= 140; i++) {',
    '    questionIds.add(i);',
    '}',
    '',
    'Random random = new Random(42);',
    'Collections.shuffle(questionIds, random);',
    '',
    'Set<Integer> selected = new LinkedHashSet<>();',
    'for (int id : questionIds) {',
    '    if (selected.size() == 5) break;',
    '    selected.add(id);',
    '}'
])
codebox.text_frame.text = code
for p in codebox.text_frame.paragraphs:
    for run in p.runs:
        run.font.size = Pt(18); run.font.name = 'Consolas'; run.font.color.rgb = TEXT

# Slide 7
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, WHITE)
add_title(slide, 'Sample Output', color=NAVY)
panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.5), Inches(11.2), Inches(4.2))
panel.fill.solid(); panel.fill.fore_color.rgb = LIGHT; panel.line.color.rgb = BLUE; panel.line.width = 1
panel.text_frame.text = 'DSA Practice: randomized unique question selections\nSelected question IDs: [104, 119, 126, 111, 133]'
for p in panel.text_frame.paragraphs:
    p.alignment = PP_ALIGN.CENTER
    for run in p.runs:
        run.font.size = Pt(20); run.font.name = 'Consolas'; run.font.color.rgb = NAVY

# Slide 8
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, NAVY)
add_title(slide, 'Conclusion', color=WHITE)
text = 'This project demonstrates how Java collections can be used to create a simple DSA practice selector.\nIt is easy to understand, useful for revision, and beginner-friendly.\nThe app shows real-world concepts like randomization, uniqueness, and list processing.\nFuture ideas: add difficulty levels, a timer, or custom question categories.'
box = slide.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.1), Inches(3.8))
box.text_frame.text = text
for p in box.text_frame.paragraphs:
    p.alignment = PP_ALIGN.LEFT
    for run in p.runs:
        run.font.size = Pt(22); run.font.color.rgb = WHITE

out = '/workspaces/skillGauge/DSA_Practice_Presentation.pptx'
prs.save(out)
print('Created:', out)
print('Slides:', len(prs.slides))
