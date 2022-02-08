pip install -t packages coverage pytest mock moto # more test dependencies to be added here
python -m zipapp packages -m 'coverage.cmdline:main' -c
mv packages.pyz coverage.pyz
