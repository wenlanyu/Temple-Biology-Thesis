# Temple-Biology-Thesis

A LaTeX template for **Temple University Biology** PhD dissertations and master's theses. It is formatted to the Graduate School's *Dissertation and Thesis Handbook* (revised 11.11.25) and maintained by the Yang Lab, Department of Biology.

The template takes care of margins, page numbering, the E-Title Page, the front-matter order, the table of contents, line spacing and the reference list. It also includes a script that checks the compiled PDF against the formatting rules before you submit.

> This is a student-maintained template. It is not an official Graduate School product. The Graduate School's format review has the final say, and the Handbook can change without notice: check the revision date on the current Handbook before you submit.

## Features

- **Graduate School format**: 1.5" left and 1" top/right/bottom margins with page numbers inside them; Roman numerals for the front matter (the title page counts as i but shows no number) and Arabic numerals from Chapter 1; no running heads; Type 1 fonts only; black text.
- **Front matter in the required order**: E-Title Page, optional Copyright Page (ii), Abstract, Dedication, Acknowledgments, Table of Contents, List of Tables, List of Figures, and an optional List of Abbreviations.
- **Dissertation or thesis**: one line switches the title page between doctoral and master's wording.
- **Times 12 pt or Arial 10 pt**: the two type sizes the Handbook names, selected by one option.
- **Built for biology chapters**: manuscript-style research chapters with a publication and author-contribution note, multi-panel figures, supplementary information as appendices (Figure A.1, Table A.1, ...), landscape pages for wide tables, and Nature-style numbered superscript references.
- **Spacing rules done for you**: double-spaced text; table of contents, lists, captions and references single-spaced within entries and double-spaced between them; block quotes and footnotes in the Handbook format.
- **Format checker** (`tools/format_audit.py`): measures every page of the compiled PDF.

## Quick start

### Overleaf
1. Download this repository as a ZIP (green **Code** button → **Download ZIP**).
2. In Overleaf: **New Project → Upload Project**, and select the ZIP.
3. Make sure the compiler is **pdfLaTeX** (Menu → Settings → Compiler).
4. Edit `main.tex` and the files in `frontmatter/`, `chapters/` and `appendices/`.

### Windows: MiKTeX + TeXstudio (the setup used to develop this template)

1. **Install MiKTeX** from [miktex.org](https://miktex.org/download). When the installer asks about missing packages, choose **Always install missing packages on-the-fly**. The first compile then downloads whatever the template needs. (Already installed? Open **MiKTeX Console → Settings** and set the same option. Under **Updates**, check for updates.)
2. **Install TeXstudio** from [texstudio.org](https://www.texstudio.org/).
3. **Configure TeXstudio once:** **Options → Configure TeXstudio → Build**, then set
   - **Default Compiler:** `PdfLaTeX`
   - **Default Bibliography Tool:** `BibTeX`
4. **Open `main.tex`** and compile:
   - **F5** (Build & View) compiles and shows the PDF.
   - **F8** (Bibliography) runs BibTeX. Run it after adding or changing citations, then press **F5** twice so that the reference numbers and the table of contents update.
5. **Edit the chapter files freely.** Each file in `chapters/`, `frontmatter/` and `appendices/` starts with `% !TeX root = ../main.tex`, so pressing F5 while editing a chapter still builds the whole thesis.

To run the format check on Windows (requires [Python](https://www.python.org/downloads/)), open a terminal in the template folder:
```
py -m pip install pdfplumber pypdf
py tools\format_audit.py main.pdf
```

### Local installation from the command line (TeX Live, MacTeX or MiKTeX)
```
git clone https://github.com/Temple-Biology-YangLab/Temple-Biology-Thesis.git
cd Temple-Biology-Thesis
latexmk -pdf main
```
Or run `pdflatex main`, `bibtex main`, `pdflatex main`, `pdflatex main`. (On MiKTeX, `latexmk` requires Perl, e.g. [Strawberry Perl](https://strawberryperl.com/); the four separate commands do not.) Use pdfLaTeX, not XeLaTeX or LuaLaTeX: the template relies on pdfLaTeX to produce Type 1 fonts.

## Filling in the template

All title-page information is set at the top of `main.tex`:

| Command | What to enter |
|---|---|
| `\thesistitle{...}` | Title in ALL CAPITALS, as an inverted pyramid (break lines with `\\`). Spell out symbols, Greek letters and formulae. |
| `\thesisauthor{...}` | Your name exactly as it appears on your Temple transcript |
| `\thesistype{...}` | `Dissertation` (doctoral, the default) or `Thesis` (master's) |
| `\thesisdegree{...}` | `DOCTOR OF PHILOSOPHY` or `MASTER OF SCIENCE`, as in your SSB record |
| `\diplomadate{...}` | The official diploma date. Only December, May or August are allowed (not the defense date). |
| `\copyrightyear{...}` | Year of graduation (Copyright Page) |
| `\committee{...}` | One line per member: name, role, department or institution |

**Font:** Times 12 pt is the default. For Arial 10 pt, change the first lines of `main.tex` to
`\documentclass[10pt,oneside,letterpaper]{report}` and `\usepackage[arial]{templethesis}`.

**Master's students:** `\thesistype{Thesis}` switches the title page to the thesis E-Title Page wording in Handbook **Appendix E**: "A Thesis", your degree, and the "Thesis Approvals:" heading above the committee list. The E-Title Page in your PDF carries typed names only. The signed signature page is emailed to the Graduate School separately, as described in the Handbook.

## Files

| File / folder | Content |
|---|---|
| `main.tex` | Title-page information and the order of the document |
| `templethesis.sty` | All formatting. You should not need to edit it. |
| `frontmatter/` | Abstract, dedication, acknowledgments, list of abbreviations |
| `chapters/` | One file per chapter (the samples show headings, figures, tables, equations, citations, block quotes and footnotes) |
| `appendices/` | Supplementary information (sample with a supplementary figure and a landscape table) |
| `figures/` | Figure files |
| `references.bib` | BibTeX database (replace the examples with your own) |
| `thesis.bst` | Nature-style reference format (numbered in citation order, abbreviated journal names) |
| `unicode-chars.tex` | Maps characters pasted from Word (μ, ±, Å, Greek letters, ...) to LaTeX commands |
| `tools/format_audit.py` | Format checker for the compiled PDF |
| `tools/unicode_chars.py` | Regenerates `unicode-chars.tex` from the characters used in your files |

## Checking the format before submission

```
pip install pdfplumber pypdf
python tools/format_audit.py main.pdf
```

The script checks every page and reports, for each check, `OK` or `CHECK` with the page numbers:

- content (text, figures, table rules, page numbers) outside the 1.5"/1" margins, including on landscape pages
- the page-number sequence (Roman, then Arabic from Chapter 1), and page numbers that are missing, off-center or too small
- lines of text smaller than 10 pt
- non-black text (e.g., leftover red placeholder text)
- numbered headings stranded at the bottom of a page
- fonts that are not embedded or are not Type 1, **including fonts inside PDF figures**
- PDF encryption

Run it after every substantial edit, and again before you upload to ETD Administrator. It is a self-check only. Also read the Handbook's Final Checklist.

## Notes for biology dissertations

- **Manuscript-style chapters.** If a chapter is a published or submitted article, open it with the `chapternote` block (see `chapters/ch2_manuscript.tex`) giving the publication status and author contributions. If the article is copyrighted, the Handbook requires written permission from the copyright owner and the permission letter in an appendix. Many open-access journals (CC BY) allow reuse with attribution. Check your journal's policy.
- **Supplementary information** goes in appendices. Figures and tables there are numbered A.1, A.2, ...
- **Movies and other multimedia** cannot be embedded in the PDF. Upload them as supplementary files in ETD Administrator and describe each file in the Abstract.
- **Figures and fonts.** The Handbook requires embedded Type 1 fonts. PDF figures exported from matplotlib, Prism, Illustrator or similar programs often contain Type 3 or TrueType fonts, which the format checker flags. Either export figures as high-resolution PNG, TIFF or JPEG (300–600 dpi), or convert the text in vector figures to outlines before export.
- **Headings.** The template uses numbered headings (1.1, 1.1.1), which the Handbook permits for the "hard sciences" (its examples are Engineering and Statistics). If your program or advisor prefers APA-style headings, ask the Graduate School before changing the format.
- **Color.** Color figures are fine (they are reproduced in color), but all text must be black.

## Handbook coverage

| Handbook requirement | Where it is handled |
|---|---|
| Margins 1.5" left, 1" top/right/bottom; page numbers inside the margins | `geometry` settings in `templethesis.sty` |
| Title page counted as i with no number; Roman numerals for the front matter; Arabic from Chapter 1 | `\maketitlepage`, `main.tex` |
| E-Title Page layout | `\maketitlepage` |
| Copyright Page centered, numbered ii | `\makecopyrightpage` |
| Front-matter order; front-matter sections listed in the TOC (not the Copyright Page or the TOC itself) | `main.tex`, `\frontsection` |
| "CHAPTER #" and title centered in capitals at the top of a new page | `\chapter` format |
| TOC and lists: dot leaders, single-spaced within entries, double-spaced between | `tocloft` settings |
| Double-spaced body text; no running heads | `\doublespacing`, `\pagestyle{plain}` |
| Block quotes single-spaced, indented ½" from both margins | `quote` / `quotation` |
| Notes single-spaced within, double-spaced between, first line indented ½", not below 10 pt | footnote settings |
| References single-spaced within entries, double-spaced between, turnover lines indented ½" | `natbib` settings |
| Embedded Type 1 fonts, 12-pt Times or 10-pt Arial, black text | font settings; `format_audit.py` |
| Widows and orphans avoided | penalties in `templethesis.sty`; `format_audit.py` |

## Other Temple LaTeX templates

- [whit2333/tuthesis](https://github.com/whit2333/tuthesis): an earlier Temple thesis template (based on the Purdue thesis class)
- The Department of Mathematics distributes a *TU-Thesis* LaTeX archive on its graduate-student pages

This template was written independently of both.

## Contributing

Found a formatting problem, or did the Graduate School ask for a change during your format review? Please open an issue or a pull request, and mention the Handbook revision you checked. Reports from master's students and from other departments are especially welcome.

## License

The template is released under the [MIT License](LICENSE), **except `thesis.bst`**. That file is a modification of `unsrtnat.bst` (© Patrick W. Daly) and remains under the [LaTeX Project Public License](https://www.latex-project.org/lppl/).

The license covers the template files only. The content of your dissertation or thesis is your own.

Developed by Wenlan Yu (Yang Lab, Department of Biology, Temple University).
