# Plagx Research Kit – Kaggle notebook

*A free academic writing utility by Plagiarism Checker X.*

A Kaggle notebook tutorial on keeping a source log and turning it into APA 7 or MLA 9 citations, plus academic research templates (source log, literature matrix, annotated bibliography, research plan). Citations use the open-source [plagx-cite](https://pypi.org/project/plagx-cite/) package. All example sources are made up.

```
├── build_notebook.py          # Generates the notebook (edit cells here, not in the .ipynb)
├── plagx-research-kit.ipynb   # Generated notebook
├── kernel-metadata.json       # Kaggle CLI metadata
└── LICENSE                    # MIT
```

## Rebuild and test

```bash
python build_notebook.py
pip install pandas nbconvert ipykernel
jupyter nbconvert --to notebook --execute plagx-research-kit.ipynb --output executed.ipynb
```

Outside Kaggle the templates are written to `output/`.

## Publish to Kaggle automatically (GitHub Actions)

Every push to `main` rebuilds the notebook, test-runs it, and pushes it to Kaggle ([publish-kaggle.yml](.github/workflows/publish-kaggle.yml)).

One-time setup: in the GitHub repo, open **Settings → Secrets and variables → Actions** and add `KAGGLE_USERNAME` and either `KAGGLE_API_TOKEN` (new-style token shown once in Kaggle Settings → API Tokens) or `KAGGLE_KEY` (from a legacy `kaggle.json`). To publish it publicly, set `"is_private": false` in `kernel-metadata.json`.

## Publish to Kaggle manually

1. Kaggle → **Settings → API → Create New Token**. Keep `kaggle.json` in `~/.kaggle/` only (never commit it or paste it in chat).
2. Replace `KAGGLE_USERNAME` in `kernel-metadata.json` with the account's username. Phone verification is required for Internet access in notebooks.
3. `pip install kaggle` then `kaggle kernels push -p .` (uploads as **private**).
4. Open the notebook on Kaggle, **Run All**, check the output, then **Save Version → Save & Run All**.
5. Set **Sharing → Public**. Add a cover image and tags if you like.

## What this notebook does not do

It does not check for plagiarism or detect AI-generated text. To check complete documents, use [Plagiarism Checker X](https://plagiarismcheckerx.com/).

## License

[MIT](LICENSE) © 2026 Plagiarism Checker X
