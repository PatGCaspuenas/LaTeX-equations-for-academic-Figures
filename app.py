import streamlit as st
import subprocess
import tempfile
import shutil
import os

def generate_latex_pdf(equation: str, output_filepath: str,
                       palette: dict, fontsize: float = 8.0, font_package: str = "lmodern"):
    color_defs = ""
    for name, hex_val in palette.items():
        clean_hex = hex_val.lstrip("#")
        color_defs += f"\\definecolor{{{name}}}{{HTML}}{{{clean_hex}}}\n"

    tex_template = f"""\\documentclass[10pt, border=1pt]{{standalone}}
\\usepackage{{{font_package}}}
\\usepackage{{amsmath, amssymb, amsfonts}}
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
st.sidebar.header("🎨 Color Palette")
c1 = st.sidebar.color_picker("Color 1 (`colorA`)", "#DE4968")
c2 = st.sidebar.color_picker("Color 2 (`colorB`)", "#F8CD6C")
c3 = st.sidebar.color_picker("Color 3 (`colorC`)", "#F1A376")
c4 = st.sidebar.color_picker("Color 4 (`colorD`)", "#FFFFFF")
user_palette = {"colorA": c1, "colorB": c2, "colorC": c3, "colorD": c4}

st.sidebar.header("⚙️ Typography")
user_fontsize = st.sidebar.slider("Font Size (pt)", 4.0, 48.0, 12.0, 0.5)
font_options = {"Computer Modern": "lmodern", "Times": "mathptmx", "Palatino": "mathpazo"}
user_font_package = font_options[st.sidebar.selectbox("Font Type", list(font_options.keys()))]

# --- Quick Insert Panel ---
st.subheader("🧰 Symbol & Structure Toolbar")

snippet_categories = {
    "Calculus & Structures": {
        "a/b": r"\frac{a}{b}", "xᵃ": r"x^{a}", "xₐ": r"x_{a}", "√x": r"\sqrt{x}", "ⁿ√x": r"\sqrt[n]{x}",
        "∫": r"\int", "∫ₐᵇ": r"\int_{a}^{b}", "∬": r"\iint", "∮": r"\oint",
        "∑": r"\sum_{i=1}^{n}", "∏": r"\prod_{i=1}^{n}", "lim": r"\lim_{x \to \infty}",
        "∂": r"\partial", "∂f/∂x": r"\frac{\partial f}{\partial x}", "d/dx": r"\frac{\mathrm{d}}{\mathrm{d}x}"
    },
    "Greek Letters": {
        "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta", "ε": r"\epsilon", "ζ": r"\zeta",
        "η": r"\eta", "θ": r"\theta", "ι": r"\iota", "κ": r"\kappa", "λ": r"\lambda", "μ": r"\mu",
        "ν": r"\nu", "ξ": r"\xi", "π": r"\pi", "ρ": r"\rho", "σ": r"\sigma", "τ": r"\tau", "υ": r"\upsilon",
        "ϕ": r"\phi", "χ": r"\chi", "ψ": r"\psi", "ω": r"\omega", 
        "Γ": r"\Gamma", "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda", "Π": r"\Pi", "Σ": r"\Sigma", "Ω": r"\Omega",
        "ϑ": r"\vartheta", "φ": r"\varphi", "ϖ": r"\varpi", "ϱ": r"\varrho", "ς": r"\varsigma"
    },
    "Operators & Relations": {
        "±": r"\pm", "∓": r"\mp", "×": r"\times", "÷": r"\div", "·": r"\cdot", "∘": r"\circ",
        "≈": r"\approx", "≠": r"\neq", "≡": r"\equiv", "≤": r"\leq", "≥": r"\geq", "∝": r"\propto",
        "∼": r"\sim", "≃": r"\simeq", "≅": r"\cong", "≪": r"\ll", "≫": r"\gg", "≐": r"\doteq",
        "≺": r"\prec", "≻": r"\succ", "⊧": r"\models", "⊢": r"\vdash", "⊣": r"\dashv", "⋈": r"\bowtie"
    },
    "Logic & Sets": {
        "∩": r"\cap", "∪": r"\cup", "∈": r"\in", "∉": r"\notin", "⊂": r"\subset", "⊆": r"\subseteq",
        "∀": r"\forall", "∃": r"\exists", "∄": r"\nexists", "∞": r"\infty", "∅": r"\emptyset",
        "ℝ": r"\mathbb{R}", "ℂ": r"\mathbb{C}", "ℕ": r"\mathbb{N}", "ℤ": r"\mathbb{Z}", "ℚ": r"\mathbb{Q}",
        "ℙ": r"\mathbb{P}", "𝔼": r"\mathbb{E}"
    },
    "Matrices & Layouts": {
        "(n r)": r"\binom{n}{r}", "…": r"\dots", "⋯": r"\cdots", "⋮": r"\vdots", "⋱": r"\ddots",
        "[ ] Mat": r"\begin{bmatrix} a & b \\ c & d \end{bmatrix}",
        "( ) Mat": r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}",
        "| | Mat": r"\begin{vmatrix} a & b \\ c & d \end{vmatrix}",
        "‖ ‖ Mat": r"\begin{Vmatrix} a & b \\ c & d \end{Vmatrix}",
        "Cases": r"\begin{cases} x & \text{if } x > 0 \\ 0 & \text{otherwise} \end{cases}",
        "Aligned": r"\begin{aligned} y &= mx + b \\ &= 2x + 1 \end{aligned}"
    },
    "Arrows & Fonts": {
        "→": r"\rightarrow", "←": r"\leftarrow", "↔": r"\leftrightarrow", "⇒": r"\Rightarrow", "⇔": r"\Leftrightarrow",
        "↦": r"\mapsto", "↑": r"\uparrow", "↓": r"\downarrow",
        "Bold Text": r"\mathbf{text}", "Italic": r"\mathit{text}", "Callig": r"\mathcal{A}", "Fraktur": r"\mathfrak{R}",
        "Bold Math": r"\bm{x}", "Color Block": r"\textcolor{colorA}{text}",
        "â": r"\hat{a}", "ã": r"\tilde{a}", "ā": r"\bar{a}", "a⃗": r"\vec{a}"
    }
}

def add_snippet(snippet):
    st.session_state.equation_text += f" {snippet} "

if "equation_text" not in st.session_state:
    st.session_state.equation_text = r"\textcolor{colorA}{\bm{x}_{n+1}} = \underset{\bm{x}}{\operatorname{argmax}}\,\textcolor{colorC}{\alpha} + \textcolor{colorB}{\sum_{i=1}^n \beta_i}"

tabs = st.tabs(list(snippet_categories.keys()))

for i, (category_name, snippets) in enumerate(snippet_categories.items()):
    with tabs[i]:
        # Create a grid layout (8 columns per row so buttons aren't too wide)
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
st.latex(user_equation)

# Export & Download
if st.button("Render PDF", type="primary"):
    with st.spinner("Compiling LaTeX engine..."):
        temp_out = os.path.join(tempfile.gettempdir(), "final_equation.pdf")
        success = generate_latex_pdf(user_equation, temp_out, user_palette, user_fontsize, user_font_package)

        if success:
            st.success("PDF generated successfully!")
            with open(temp_out, "rb") as pdf_file:
                st.download_button(
                    label="📥 Save PDF to Downloads",
                    data=pdf_file.read(),
                    file_name="equation.pdf",
                    mime="application/pdf"
                )