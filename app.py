import streamlit as st
import subprocess
import tempfile
import shutil
import os

def generate_latex_pdf(equation: str, output_filepath: str,
                       palette: dict, fontsize: float = 8.0, font_package: str = "lmodern"):
    """
    Generates a cropped PDF from a LaTeX equation with support for a multi-color palette.
    """
    # Build custom color definitions from our palette dict
    color_defs = ""
    for name, hex_val in palette.items():
        clean_hex = hex_val.lstrip("#")
        color_defs += f"\\definecolor{{{name}}}{{HTML}}{{{clean_hex}}}\n"

    tex_template = f"""\\documentclass[10pt, border=1pt]{{standalone}}
\\usepackage{{{font_package}}}
\\usepackage{{amsmath, amssymb}}
\\usepackage{{bm}}
\\usepackage{{xcolor}}
{color_defs}
\\begin{{document}}
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
                cwd=temp_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
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
st.title("Multi-Color LaTeX to PDF Generator")

# Sidebar: Global Configurations & Palette
st.sidebar.header("🎨 Color Palette Setup")
st.sidebar.write("Pick your custom colors here, then use them in your equation via the tags below.")

c1 = st.sidebar.color_picker("Color 1 (`colorA`)", "#DE4968")
c2 = st.sidebar.color_picker("Color 2 (`colorB`)", "#F8CD6C")
c3 = st.sidebar.color_picker("Color 3 (`colorC`)", "#F1A376")
c4 = st.sidebar.color_picker("Color 4 (`colorD`)", "#FFFFFF") # Default white/text color

user_palette = {"colorA": c1, "colorB": c2, "colorC": c3, "colorD": c4}

st.sidebar.header("⚙️ Typography Settings")
user_fontsize = st.sidebar.slider("Font Size (pt)", min_value=4.0, max_value=48.0, value=12.0, step=0.5)

font_options = {
    "Computer Modern (Default)": "lmodern",
    "Times / MathPTMX": "mathptmx",
    "Palatino": "mathpazo"
}
selected_font_label = st.sidebar.selectbox("Font Type", list(font_options.keys()))
user_font_package = font_options[selected_font_label]

# --- Quick Insert Panel ---
st.subheader("🧰 Quick Insert Panel")
st.caption("Click to append common LaTeX structures to the end of your equation.")

# Define your snippet dictionary
snippets = {
    "Fraction": r"\frac{numerator}{denominator}",
    "Integral": r"\int_{a}^{b} x \,dx",
    "Summation": r"\sum_{i=1}^{n} i",
    "2x2 Matrix": r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}",
    "Square Root": r"\sqrt{x^2 + y^2}",
    "Limit": r"\lim_{x \to \infty}",
    "Color Block": r"\textcolor{colorA}{text}"
}

# Callback function to update the text area
def add_snippet(snippet):
    # This appends the snippet to whatever is currently in the text box
    st.session_state.equation_text += f" {snippet} "

# Initialize the text box state if it doesn't exist yet
if "equation_text" not in st.session_state:
    st.session_state.equation_text = r"\textcolor{colorA}{\bm{x}_{n+1}} = \underset{\bm{x}}{\operatorname{argmax}}\,\textcolor{colorC}{\alpha} + \textcolor{colorB}{\sum_{i=1}^n \beta_i}"

# Create a row of columns for the buttons so they sit cleanly in a grid
cols = st.columns(len(snippets))
for i, (label, snippet) in enumerate(snippets.items()):
    with cols[i]:
        # Connect the button to the callback function
        st.button(label, on_click=add_snippet, args=(snippet,), key=f"btn_{label}")

# --- Main Area: Equation Input ---
# By assigning key="equation_text", Streamlit links this box to our session state
user_equation = st.text_area(
    "LaTeX Equation Editor", 
    key="equation_text",
    height=150
)

# Live Preview
st.subheader("Live Web Preview")
st.latex(user_equation)

with st.expander("💡 Quick Syntax Guide for Colors"):
    st.markdown("""
    To color an individual term, wrap it in a `\\textcolor{colorName}{...}` block:
    * Use `\\textcolor{colorA}{your math here}` for <span style="color:blue">Color 1</span>
    * Use `\\textcolor{colorB}{your math here}` for <span style="color:green">Color 2</span>
    * Use `\\textcolor{colorC}{your math here}` for <span style="color:orange">Color 3</span>
    """, unsafe_allow_html=True)

# Export & Download
if st.button("Render PDF", type="primary"):
    with st.spinner("Compiling LaTeX engine..."):
        temp_out = os.path.join(tempfile.gettempdir(), "final_equation.pdf")
        
        success = generate_latex_pdf(
            equation=user_equation, 
            output_filepath=temp_out, 
            palette=user_palette, 
            fontsize=user_fontsize,
            font_package=user_font_package
        )

        if success:
            st.success("PDF generated successfully!")
            with open(temp_out, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            st.download_button(
                label="📥 Save Multi-Color PDF to Downloads",
                data=pdf_bytes,
                file_name="multicolor_equation.pdf",
                mime="application/pdf"
            )