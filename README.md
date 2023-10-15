# Pre-commit installation

Pre-commit automatically runs Git hooks to check your code when you commit to this repo.

First, install the pre-commit tool: 

```bash 
pip install pre-commit
```

Next, install the pre-commit hooks on your system:

```bash
pre-commit install
```
Pre-commit should run automatically when attempting to commit. If it doesn't, run the following after staging your changes:

```bash
pre-commit run
```

I haven't tested these hooks, so let me know if there's any problems. -Javin