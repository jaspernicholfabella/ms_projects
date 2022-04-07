import pylint.lint
pylint_opts = ['--disable=line-too-long,import-error,wrong-import-position', 'us_ferc/ferc.py']
pylint.lint.Run(pylint_opts)