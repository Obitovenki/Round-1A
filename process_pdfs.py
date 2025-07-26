from pathlib import Path
import fitz  # PyMuPDF
import json

def extract_title_and_headings(pdf_path):
    doc = fitz.open(pdf_path)
    font_stats = {}

    # Analyze first 5 pages for font usage
    for page_num in range(min(len(doc), 5)):
        page = doc[page_num] 
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font_key = (span["font"], round(span["size"]))
                    font_stats.setdefault(font_key, 0)
                    font_stats[font_key] += 1

    sorted_fonts = sorted(font_stats.items(), key=lambda x: (-x[0][1], -x[1]))
    title_font = next(((font, size) for (font, size), _ in sorted_fonts if "Bold" in font), None)

    bold_fonts = [(font, size) for (font, size), _ in font_stats.items() if "Bold" in font]
    top_bold_sizes = sorted(set([s for f, s in bold_fonts]), reverse=True)[:3]
    level_map = {size: f"H{i+1}" for i, size in enumerate(top_bold_sizes)}

    title = ""
    outline = []
    title_found = False

    for i, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                line_text = ""
                line_size = 0
                line_bold = False
                y0 = 9999

                for span in line["spans"]:
                    if not span["text"].strip():
                        continue
                    if not line_size:
                        line_size = round(span["size"])
                        line_bold = "Bold" in span["font"]
                    line_text += span["text"] + " "
                    y0 = min(y0, span["bbox"][1])

                line_text = line_text.strip()

                # Skip too long or too short or empty lines
                if not line_text or any(c in line_text for c in ['\t', '|']) or len(line_text) > 200:
                    continue

                # Title logic
                if (
                    not title_found and title_font and
                    round(line_size) == title_font[1] and
                    line_bold and i == 0 and y0 < 200 and len(line_text.split()) > 5
                ):
                    title = line_text
                    title_found = True
                    continue

                if line_bold and line_size in top_bold_sizes and line_text != title:
                    level = level_map.get(line_size)
                    if level:
                        outline.append({
                            "level": level,
                            "text": line_text,
                            "page": i
                        })

    return {"title": title, "outline": outline}


def process_pdfs():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_file in input_dir.glob("*.pdf"):
        result = extract_title_and_headings(pdf_file)
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"Processed {pdf_file.name} -> {output_file.name}")


if __name__ == "__main__":
    process_pdfs()


