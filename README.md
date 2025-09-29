
```
# from anywhere in Rhythmpress
from rhythmpress.quarto_vars import get_variables

vars_all = get_variables(lang="ja")

print(vars_all.get("RUBY-MOP"))

# with extra overrides
vars_en = get_variables(lang="en", extra={"site_url": "https://example.com"})
```
