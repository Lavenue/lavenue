\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{lavenue}

\LoadClass[titlepage]{article}

\RequirePackage{fontspec}
\RequirePackage[french]{babel}
\RequirePackage{comment}

\RequirePackage{tikz}
\usetikzlibrary{positioning, calc}
\definecolor{lvert}{RGB}{10,207,128}
\definecolor{lbleu}{RGB}{10,176,207}

\RequirePackage{moresize}
\RequirePackage{titlesec}
\RequirePackage{parskip}

\RequirePackage{fancyhdr}
\pagestyle{fancy}
\lhead{\begin{tikzpicture}[line width=1.4,line cap=round, scale=0.01]
\path[draw=lvert] (0,0)arc(-33.279:33.279:19.500);
\path[shift={(35.1,21.4)},draw=lbleu,scale=-1.000] (0,0)arc(-33.279:33.279:19.500);
\path[draw=lvert] (7.1,-7.1)arc(-36.394:36.394:30.000);
\path[shift={(35.1,21.4)},draw=lbleu,scale=-1.000] (7.1,-7.1)arc(-36.394:36.394:30.000);
\path[draw=lvert] (13.6,-13.6)arc(-38.777:38.777:38.800);
\path[shift={(35.1,21.4)},draw=lbleu,scale=-1.000] (13.6,-13.6)arc(-38.777:38.777:38.800);
\end{tikzpicture}}
\rhead{Lavenue}

\setmainfont{Avenir Book}

\renewcommand{\maketitle}{
\frontmatter
\begin{titlepage}
\begin{tikzpicture}[remember picture, overlay, line width=21,line cap=round, scale=0.15]
\begin{scope}[shift={($(current page.north west)-(-10,45)$)}]
\path[draw=lvert] (0,0)arc(-33.279:33.279:19.500);
\path[draw=lvert] (7.1,-7.1)arc(-36.394:36.394:30.000);
\path[draw=lvert] (13.6,-13.6)arc(-38.777:38.777:38.800);
\end{scope}
\begin{scope}[shift={($(current page.south east)+(-10,45)$)}]
\path[draw=lbleu,scale=-1.000] (0,0)arc(-33.279:33.279:19.500);
\path[draw=lbleu,scale=-1.000] (7.1,-7.1)arc(-36.394:36.394:30.000);
\path[draw=lbleu,scale=-1.000] (13.6,-13.6)arc(-38.777:38.777:38.800);
\end{scope}
\end{tikzpicture}
\vspace*{-2em}
\begin{flushright}
{\fontsize{40}{48}\selectfont Lavenue}\\
Pour les assemblées délibérantes
\end{flushright}
\vfill
{\fontsize{36}{44}\selectfont \@title}\\
\@date
\vfill
\end{titlepage}
\setcounter{page}{2}}

\RequirePackage{hyperref}
\hypersetup{
	bookmarks=true,
}

\newif\if@mainmatter \@mainmattertrue
\newcommand\frontmatter{%
		\cleardoublepage
	\@mainmatterfalse
	\pagenumbering{roman}}
\newcommand\mainmatter{%
		\cleardoublepage
	\@mainmattertrue
	\pagenumbering{arabic}}
