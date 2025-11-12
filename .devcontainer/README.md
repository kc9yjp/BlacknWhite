This devcontainer has been configured to make the project's `game` package importable inside the container.

What changed
- `containerEnv.PYTHONPATH` set to `${containerWorkspaceFolder}` so Python will find the `game` package when importing (for example `import game`).
- VS Code/Pylance `python.analysis.extraPaths` includes `./game` to improve editor import resolution.

How to apply
1. Rebuild the dev container so the environment changes take effect (Command Palette: "Dev Containers: Rebuild Container").
2. After rebuild, open a terminal in the container and run:

```bash
python -c "import game; print('game package:', game.__file__)"
```

Notes
- If you prefer the `game` folder specifically on PYTHONPATH (instead of the workspace root), edit `containerEnv.PYTHONPATH` to `${containerWorkspaceFolder}/game`.
- These changes only affect the container environment (and VS Code analysis). If you run Python locally outside the container, ensure your local PYTHONPATH or virtualenv includes the workspace root.
