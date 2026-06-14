import os
import subprocess
import tempfile

# 1. Your dictionary (simplified here, but paste your full one)
snippet_categories = {
    "Calculus": {
        "fraction": r"\frac{a}{b}", 
        "integral": r"\int",
        "summation": r"\sum_{i=1}^{n}"
    },
    "Greek": {
        "alpha": r"\alpha", 
        "beta": r"\beta"
    }
}

# 2. Setup output folder
output_dir = "svg_icons"
os.makedirs(output_dir, exist_ok=True)

tex_template = r"""\documentclass[12pt, border=2pt]{standalone}
\usepackage{amsmath, amssymb, amsfonts, bm}
\usepackage{xcolor}
\begin{document}
% We color the text white so it shows up beautifully on a dark Streamlit theme. 
% Change to \color{black} if you prefer a light theme.
\color{white} 
$\displaystyle %s $
\end{document}
"""

print(f"Generating SVGs in ./{output_dir}...")

with tempfile.TemporaryDirectory() as temp_dir:
    for category, snippets in snippet_categories.items():
        for label, snippet in snippets.items():
            # Create a safe filename (e.g., "Calculus_fraction")
            safe_name = f"{category}_{label}".replace(" ", "_").replace("/", "over")
            
            tex_filepath = os.path.join(temp_dir, 'icon.tex')
            pdf_filepath = os.path.join(temp_dir, 'icon.pdf')
            svg_filepath = os.path.join(output_dir, f"{safe_name}.svg")
            
            with open(tex_filepath, 'w', encoding='utf-8') as f:
                f.write(tex_template.replace("%s", snippet))
            
            # Compile to PDF
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'icon.tex'],
                cwd=temp_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            
            # Convert PDF to SVG
            if os.path.exists(pdf_filepath):
                subprocess.run(['pdf2svg', pdf_filepath, svg_filepath])
                print(f"Created: {safe_name}.svg")

print("All SVGs generated successfully!")