import re
from pathlib import Path
from html.parser import HTMLParser

class RubyBaseTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.in_ruby = False
        self.in_rt = False

    def handle_starttag(self, tag, attrs):
        if tag == 'ruby':
            self.in_ruby = True
        elif tag == 'rt':
            self.in_rt = True

    def handle_endtag(self, tag):
        if tag == 'ruby':
            self.in_ruby = False
        elif tag == 'rt':
            self.in_rt = False

    def handle_data(self, data):
        if self.in_ruby and self.in_rt:
            return  # skip ruby annotation
        self.result.append(data)

    def extract(self, html_text):
        self.result = []
        self.feed(html_text)
        return ''.join(self.result).strip()

def extract_ruby_base(text):
    parser = RubyBaseTextExtractor()
    return parser.extract(text)



def split_qmd( input_file, lang_id ):
    input_path = Path(input_file)
    base_dir = input_path.parent
    input_text = input_path.read_text(encoding='utf-8')

    # Match level-2 headers with ID: ## Title {#id}
    # h2_pattern = re.compile(r'^## (.+?)\s*\{#([^}]+)\}\s*$', re.MULTILINE)
    h2_pattern = re.compile(r'^## (.+?)(?:\s*\{#([^\}]+)\})?\s*$', re.MULTILINE)
    h3_pattern = re.compile(r'^### (.+?)(?:\s*\{#([^\}]+)\})?\s*$', re.MULTILINE)

    h2_matches = list(h2_pattern.finditer(input_text))
    if not h2_matches:
        print("No level-2 headers with IDs found.")
        return

    # Extract and write each H2 section into its own file
    preamble = input_text[:h2_matches[0].start()].strip()
    sections = []

    for i, h2 in enumerate(h2_matches):
        h2_title = h2.group(1).strip()
        # h2_id = h2.group(2).strip() if h2.group(2) else re.sub(r'[^a-zA-Z0-9_-]+', '-', h2.group(1).strip()).lower()
        h2_id = h2.group(2).strip() if h2.group(2) else re.sub(r'[^\w\u4e00-\u9fff\u3040-\u30ff\u3000-\u303f-]+', '-', extract_ruby_base( h2.group(1).strip() ), flags=re.UNICODE).strip('-')

        h2_start = h2.start()
        h2_end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(input_text)
        h2_block = input_text[h2_start:h2_end].strip()

        # Extract child sections (H3)
        h3_matches = list(h3_pattern.finditer(h2_block))
        h2_desc_end = h3_matches[0].start() if h3_matches else 0
        h2_description = h2_block[len(h2.group(0)):h2_desc_end].strip()

        for j, h3 in enumerate(h3_matches):
            h3_title = h3.group(1).strip()
            # h3_id = h3.group(2).strip()
            h3_id = h3.group(2).strip() if h3.group(2) else re.sub(r'[^\w\u4e00-\u9fff\u3040-\u30ff\u3000-\u303f-]+', '-', extract_ruby_base( h3.group(1).strip() ), flags=re.UNICODE).strip('-')
            h3_start = h3.start()
            h3_end = h3_matches[j + 1].start() if j + 1 < len(h3_matches) else 0
            h3_block = h2_block[h3_start:h3_end].strip()

        # Save split H2 section file
        # section_path = base_dir / f"{h2_id}.qmd"
        # section_path.write_text(h2_block + "\n", encoding='utf-8')

        section_dir = base_dir / h2_id
        section_dir.mkdir(exist_ok=True)

        section_path = section_dir / "index.qmd"
        section_path.write_text(h2_block + "\n", encoding='utf-8')

        sections.append((h2_title, h2_id, h2_description ))
        print(f"✅ Wrote: {section_path}")

    # Write combined index
    index_dir = base_dir / f"{lang_id}"
    index_dir.mkdir(exist_ok=True)
    index_file = index_dir / "index.qmd"

    # Build index.qmd
    index_lines = []
    if preamble:
        index_lines.append(preamble)
        index_lines.append("")

    index_lines.append("## Contents\n")
    for h2_title, h2_id, h2_desc in sections:
        index_lines.append(f"### [{h2_title}]({h2_id}/)")
        if h2_desc:
            index_lines.append(h2_desc)
        index_lines.append("")

    index_file.write_text("\n".join(index_lines).strip() + "\n", encoding='utf-8')
    print(f"✅ Wrote: {index_file}")

for file in Path('.').glob( 'master-*.qmd' ):
    print( file )
    # lang_id_match = re.match(r'master-\(([^)]+)\)\.qmd', file.name )
    lang_id_match = re.match(r'master-([^.]+)\.qmd', file.name)
    if lang_id_match:
        lang_id = lang_id_match.group(1)
        print(f"🔧 Processing: {file.name} → Language ID: {lang_id}")
        split_qmd(str(file), lang_id)
    else:
        print( 'else' );



# Test
# print(extract_ruby_base('<ruby><rb>多層弱拍基軸律動</rb><rt>グルーヴィダンスミュージック</rt></ruby>理論で得られるもの'))
# print(extract_ruby_base('<ruby>多層弱拍基軸律動<rt>グルーヴィダンスミュージック</rt></ruby>理論で得られるもの'))
# print('end')

