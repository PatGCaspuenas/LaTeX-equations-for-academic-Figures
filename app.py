import streamlit as st
import subprocess
import tempfile
import shutil
import os
import base64
from st_clickable_images import clickable_images

def generate_latex_pdf(equation: str, output_filepath: str,
                       palette: dict, bg_color: str, base_text_color: str,
                       fontsize: float = 8.0, font_package: str = "lmodern"):
    
    color_defs = ""
    # Define the dynamic custom palette
    for name, hex_val in palette.items():
        clean_hex = hex_val.lstrip("#")
        color_defs += f"\\definecolor{{{name}}}{{HTML}}{{{clean_hex}}}\n"

    # Define background and base text colors
    bg_hex = bg_color.lstrip("#")
    text_hex = base_text_color.lstrip("#")
    color_defs += f"\\definecolor{{pagebg}}{{HTML}}{{{bg_hex}}}\n"
    color_defs += f"\\definecolor{{maintext}}{{HTML}}{{{text_hex}}}\n"

    tex_template = f"""\\documentclass[10pt, border=5pt]{{standalone}}
\\usepackage{{{font_package}}}
\\usepackage{{amsmath, amssymb, amsfonts}}
\\usepackage{{bm}}
\\usepackage{{xcolor}}
{color_defs}
\\begin{{document}}
\\pagecolor{{pagebg}}
\\color{{maintext}}
\\fontsize{{{fontsize}pt}}{{{fontsize * 1.2:.2f}pt}}\\selectfont
$\\displaystyle {equation} $
\\end{{document}}
"""

    with tempfile.TemporaryDirectory() as temp_dir:
        tex_filepath = os.path.join(temp_dir, 'equation.tex')
        with open(tex_filepath, 'w', encoding='utf-8') as f:
            f.write(tex_template)
        
        try:
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'equation.tex'],
                cwd=temp_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            st.error("LaTeX compilation failed! Check your syntax.")
            with st.expander("Show Error Log"):
                st.code(e.stdout.decode('utf-8'))
            return False

        temp_pdf_path = os.path.join(temp_dir, 'equation.pdf')
        if os.path.exists(temp_pdf_path):
            shutil.copy(temp_pdf_path, output_filepath)
            return True
        return False

# --- Web App UI ---
st.set_page_config(layout="wide")
st.title("Advanced LaTeX to PDF Editor")

# Sidebar
st.sidebar.header("🎨 Colors & Canvas")
# Added Background and Base Text configuration
user_bg_color = st.sidebar.color_picker("Background Canvas", "#1A1A1A")
user_base_text = st.sidebar.color_picker("Base Text Color", "#FFFFFF")

st.sidebar.divider()
st.sidebar.write("**Custom Highlight Palette**")
c1 = st.sidebar.color_picker("Color 1 (`colorA`)", "#DE4968")
c2 = st.sidebar.color_picker("Color 2 (`colorB`)", "#F8CD6C")
c3 = st.sidebar.color_picker("Color 3 (`colorC`)", "#F1A376")
c4 = st.sidebar.color_picker("Color 4 (`colorD`)", "#4D89F8")
user_palette = {"colorA": c1, "colorB": c2, "colorC": c3, "colorD": c4}

st.sidebar.header("⚙️ Typography")
user_fontsize = st.sidebar.slider("Font Size (pt)", 4.0, 48.0, 12.0, 0.5)
font_options = {"Computer Modern": "lmodern", "Times": "mathptmx", "Palatino": "mathpazo"}
user_font_package = font_options[st.sidebar.selectbox("Font Type", list(font_options.keys()))]

# --- Quick Insert Panel ---
st.subheader("🧰 Symbol & Structure Toolbar")

# Helper function to load local SVGs safely
def load_svg(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            svg_content = f.read()
        # Convert SVG to base64 so Streamlit can render it securely inside HTML
        b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"
    except FileNotFoundError:
        return "" # Returns empty if the SVG hasn't been generated yet

# We will loop through the categories just like before
tabs = st.tabs(list(snippet_categories.keys()))

for i, (category_name, snippets) in enumerate(snippet_categories.items()):
    with tabs[i]:
        
        # Prepare lists for the clickable_images component
        svg_images = []
        titles = []
        raw_snippets = []
        
        for label, snippet in snippets.items():
            safe_name = f"{category_name}_{label}".replace(" ", "_").replace("/", "over")
            svg_path = os.path.join("svg_icons", f"{safe_name}.svg")
            
            svg_data = load_svg(svg_path)
            if svg_data:
                svg_images.append(svg_data)
                titles.append(label)
                raw_snippets.append(snippet)
        
        if svg_images:
            # Render the grid of clickable SVGs
            clicked = clickable_images(
                svg_images,
                titles=titles,
                div_style={"display": "flex", "flex-wrap": "wrap", "gap": "10px"},
                img_style={
                    "cursor": "pointer", 
                    "padding": "10px", 
                    "border-radius": "5px", 
                    "background-color": "#2D2D2D", # Box behind the SVG
                    "height": "50px"
                },
                key=f"grid_{category_name}"
            )
            
            # The component returns the index of the clicked image (or -1 if none clicked)
            if clicked > -1:
                # Append the corresponding LaTeX snippet to the session state
                st.session_state.equation_text += f" {raw_snippets[clicked]} "
                # Force a rerun so the text area updates immediately
                st.rerun()


def add_snippet(snippet):
    st.session_state.equation_text += f" {snippet} "

if "equation_text" not in st.session_state:
    st.session_state.equation_text = r"\textcolor{colorA}{\bm{x}_{n+1}} = \underset{\bm{x}}{\operatorname{argmax}}\,\textcolor{colorC}{\alpha} + \textcolor{colorB}{\sum_{i=1}^n \beta_i}"

tabs = st.tabs(list(snippet_categories.keys()))

for i, (category_name, snippets) in enumerate(snippet_categories.items()):
    with tabs[i]:
        cols_per_row = 8
        items = list(snippets.items())
        
        for row_start in range(0, len(items), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                item_idx = row_start + col_idx
                if item_idx < len(items):
                    label, snippet = items[item_idx]
                    with cols[col_idx]:
                        st.button(
                            label, 
                            on_click=add_snippet, 
                            args=(snippet,), 
                            key=f"btn_{category_name}_{label}_{item_idx}",
                            use_container_width=True
                        )

# --- Main Area: Equation Input ---
st.write("---")
user_equation = st.text_area("LaTeX Editor", key="equation_text", height=150)

# Live Preview
st.subheader("Live Preview")

# Intercept the text and swap custom names for literal hex codes for the KaTeX web preview
preview_equation = user_equation
for color_name, hex_code in user_palette.items():
    preview_equation = preview_equation.replace(
        f"\\textcolor{{{color_name}}}", 
        f"\\textcolor{{{hex_code}}}"
    )

# Inject the base text color directly into the KaTeX engine at the start of the string
preview_equation = f"\\color{{{user_base_text}}} {preview_equation}"

# CRITICAL FIX: Notice the empty lines before and after the $$ block. 
# This forces Streamlit to switch from HTML mode back into Math mode.
st.markdown(f"""
<div style="background-color: {user_bg_color}; padding: 30px; border-radius: 8px; text-align: center; overflow-x: auto; font-size: 1.5em;">

$$
{preview_equation}
$$

</div>
""", unsafe_allow_html=True)

# Export & Download
if st.button("Render PDF", type="primary"):
    with st.spinner("Compiling LaTeX engine..."):
        temp_out = os.path.join(tempfile.gettempdir(), "final_equation.pdf")
        success = generate_latex_pdf(
            equation=user_equation, 
            output_filepath=temp_out, 
            palette=user_palette, 
            bg_color=user_bg_color,
            base_text_color=user_base_text,
            fontsize=user_fontsize, 
            font_package=user_font_package
        )

        if success:
            st.success("PDF generated successfully!")
            with open(temp_out, "rb") as pdf_file:
                st.download_button(
                    label="📥 Save PDF to Downloads",
                    data=pdf_file.read(),
                    file_name="equation.pdf",
                    mime="application/pdf"
                )