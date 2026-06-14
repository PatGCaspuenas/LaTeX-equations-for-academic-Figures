import os
import subprocess
import tempfile

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

output_dir = "svg_icons"
os.makedirs(output_dir, exist_ok=True)

tex_template = r"""\documentclass[12pt, border=2pt]{standalone}
\usepackage{amsmath, amssymb, amsfonts, bm}
\usepackage{xcolor}
\begin{document}
\color{white} 
$\displaystyle REPLACE_ME $
\end{document}
"""

print(f"Generating SVGs in ./{output_dir}...")

with tempfile.TemporaryDirectory() as temp_dir:
    for category, snippets in snippet_categories.items():
        for label, snippet in snippets.items():
            safe_name = f"{category}_{label}".replace(" ", "_").replace("/", "over")
            
            tex_filepath = os.path.join(temp_dir, 'icon.tex')
            pdf_filepath = os.path.join(temp_dir, 'icon.pdf')
            svg_filepath = os.path.join(output_dir, f"{safe_name}.svg")
            
            with open(tex_filepath, 'w', encoding='utf-8') as f:
                f.write(tex_template.replace("REPLACE_ME", snippet))
            
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'icon.tex'],
                cwd=temp_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            
            if os.path.exists(pdf_filepath):
                subprocess.run(['pdf2svg', pdf_filepath, svg_filepath])
                print(f"Created: {safe_name}.svg")

print("All SVGs generated successfully!")