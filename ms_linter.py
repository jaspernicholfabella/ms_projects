import pylint.lint
pylint_opts = ['import-error,wrong-import-position', 'us_ferc/ferc.py']
pylint.lint.Run(pylint_opts)