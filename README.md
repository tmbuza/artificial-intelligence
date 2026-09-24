# Artificial Intelligence

A learner-focused Quarto book from Complex Data Insights. The guide builds from AI foundations through modern generative AI, evaluation and responsible practice to a beginner-friendly hackathon. It leads naturally to optional CDI AI practicals.

## Status

This is a chapter scaffold. Chapter prompts are placeholders for drafted, cited content. Add the cover image at `assets/images/cover/artificial-intelligence-cover-free.png` before rendering. Replace `REPLACE-WITH-OWNER` in `_quarto.yml` with your GitHub account or organization.

## Format

- Keep QMD examples non-executable (`execute.enabled: false`). Put runnable Python programs in `scripts/python/`, prefixed by chapter number, and wrappers in `scripts/bash/`.
- Put generated tables and figures in `results/tables/` and `results/figures/`, with reproducible commands and source descriptions.
- Cite sources using `library/references.bib`. Do not depend on an optional paid practical to understand a chapter.
- Develop one chapter at a time, then run `quarto render` and inspect the output.
- Set `git config core.hooksPath .githooks` to activate the date update hook. Review staged changes before committing.

The hackathon spans chapters 12–14: choose a feasible problem, build and test a small prototype, then present evidence and limitations. Chapter 15 introduces optional structured practicals.
