#!/usr/bin/env python3
"""
Generate Python tutorial images with Persian text and syntax highlighting.
Dark theme with professional colors.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Paths
FONT_PATH = "fonts/NotoSansArabic.ttf"
OUTPUT_DIR = "images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Colors (Dark theme)
BG_COLOR = (30, 30, 45)
HEADER_COLOR = (88, 166, 255)
CODE_BG = (40, 44, 52)
TEXT_COLOR = (255, 255, 255)
CODE_COLOR = (171, 178, 191)
KEYWORD_COLOR = (198, 120, 221)
STRING_COLOR = (152, 195, 121)
COMMENT_COLOR = (92, 99, 112)
ACCENT_COLOR = (86, 182, 194)
NUMBER_COLOR = (209, 154, 102)

def get_font(size):
    return ImageFont.truetype(FONT_PATH, size)

def draw_rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
    draw.pieslice([x1, y1, x1+2*radius, y1+2*radius], 180, 270, fill=fill)
    draw.pieslice([x2-2*radius, y1, x2, y1+2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2-2*radius, x1+2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2-2*radius, y2-2*radius, x2, y2], 0, 90, fill=fill)

def create_lesson_image(lesson_num, title, persian_lines, code_lines, output_name):
    """Generate a lesson image with Persian text.
    
    IMPORTANT: Use plain text directly - do NOT use arabic_reshaper or bidi!
    The NotoSansArabic font renders Persian text correctly without reshaping.
    Using arabic_reshaper creates Arabic presentation forms that render as boxes.
    """
    width = 800
    padding = 40
    line_height = 35
    code_line_height = 28
    
    header_height = 100
    title_height = 60
    content_height = len(persian_lines) * line_height + 40
    code_height = len(code_lines) * code_line_height + 60
    total_height = header_height + title_height + content_height + code_height + 120
    
    img = Image.new('RGB', (width, total_height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Header bar
    draw.rectangle([0, 0, width, header_height], fill=HEADER_COLOR)
    header_font = get_font(28)
    draw.text((width//2, 50), f"Python Tutorial - Lesson {lesson_num}", 
              fill=TEXT_COLOR, font=header_font, anchor="mm")
    
    # Title
    y = header_height + 20
    title_font = get_font(24)
    draw.text((padding, y), title, fill=ACCENT_COLOR, font=title_font)
    y += title_height
    
    # Persian content lines - USE DIRECT TEXT, NOT RESHAPED
    content_font = get_font(18)
    for line in persian_lines:
        # Do NOT reshape - just use plain text
        draw.text((padding + 10, y), line, fill=TEXT_COLOR, font=content_font)
        y += line_height
    
    y += 20
    
    # Code block background
    code_bg_height = len(code_lines) * code_line_height + 40
    draw_rounded_rect(draw, [padding, y, width - padding, y + code_bg_height], 
                      10, CODE_BG)
    
    # Code lines with syntax highlighting
    code_font = get_font(16)
    y += 20
    for line in code_lines:
        x = padding + 20
        
        if line.strip().startswith('#'):
            color = COMMENT_COLOR
            draw.text((x, y), line, fill=color, font=code_font)
        elif any(kw in line for kw in ['print', 'input', 'int', 'float', 'if', 'else', 'elif', 'def', 'class', 'return', 'for', 'while', 'import', 'from']):
            parts = line.split()
            for part in parts:
                if part in ['print', 'input', 'int', 'float', 'if', 'else', 'elif', 'def', 'class', 'return', 'for', 'while', 'import', 'from']:
                    color = KEYWORD_COLOR
                elif part.startswith('"') or part.startswith("'") or part.startswith('f"'):
                    color = STRING_COLOR
                elif part.isdigit():
                    color = NUMBER_COLOR
                else:
                    color = CODE_COLOR
                draw.text((x, y), part + " ", fill=color, font=code_font)
                bbox = code_font.getbbox(part + " ")
                x += bbox[2] - bbox[0]
        elif '=' in line and not line.strip().startswith('#'):
            var_name, value = line.split('=', 1)
            draw.text((x, y), var_name + "=", fill=CODE_COLOR, font=code_font)
            bbox = code_font.getbbox(var_name + "=")
            x += bbox[2] - bbox[0]
            
            value = value.strip()
            if value.startswith('"') or value.startswith("'") or value.startswith('f"'):
                color = STRING_COLOR
            elif value.isdigit():
                color = NUMBER_COLOR
            else:
                color = CODE_COLOR
            draw.text((x, y), value, fill=color, font=code_font)
        else:
            draw.text((x, y), line, fill=CODE_COLOR, font=code_font)
        
        y += code_line_height
    
    # Footer
    footer_y = total_height - 40
    draw.text((width//2, footer_y), "Python Course - Project Based Learning", 
              fill=COMMENT_COLOR, font=get_font(12), anchor="mm")
    
    filepath = os.path.join(OUTPUT_DIR, output_name)
    img.save(filepath, quality=95)
    print(f"Saved: {filepath}")
    return filepath

# ============ Example Usage ============
if __name__ == "__main__":
    # Lesson 1: Hello World
    create_lesson_image(
        lesson_num=1,
        title="Lesson 1: Hello World",
        persian_lines=[
            "• print() baraye chape matn estefade mishe",
            "• Metn ra ghire ghavoos gozarid",
            "• # baraye comment (tozihat) estefade mishe",
        ],
        code_lines=[
            '# Hello World',
            'print("Hello, World!")',
            '',
            '# Output:',
            '# Hello, World!',
        ],
        output_name="lesson_01_hello_world.png"
    )
    
    # Lesson 2: Variables
    create_lesson_image(
        lesson_num=2,
        title="Lesson 2: Variables (Motaghir)",
        persian_lines=[
            "• Motaghir mesle ye jabe ke toosh chiz mizarid",
            "• Type: str (matn), int (adad), float (ashari), bool (darost/galat)",
            "• Type() baraye fahmidan NOE data estefade mishe",
        ],
        code_lines=[
            'name = "Abolfazl"',
            'age = 25',
            'price = 99.99',
            'is_student = True',
            '',
            'print(type(name))   # str',
            'print(type(age))    # int',
            'print(type(price))  # float',
        ],
        output_name="lesson_02_variables.png"
    )
    
    print("\nAll images generated!")
