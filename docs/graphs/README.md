# How to generate graphs
(based on https://simpleit.rocks/python/django/generate-uml-class-diagrams-from-django-models/)

- Install django extensions: `pip install django-extensions`
- Add to installed apps:
```
INSTALLED_APPS = (
    ...
    'django_extensions',
    ...
)
```
- Install diagrams generators, either graphviz or dotplus
- If you install graphviz on windows, don't forget to add the binaries location to the PATH system variable

## Generate diagrams
- All applications organized in groups: `python manage.py graph_models --pydot -a -g -o my_project_visualized.png`
- A specific application: `python manage.py graph_models discussions --pydot -o discussion.dot`
- Multiple applications: `python manage.py graph_models courses discussions videos --pydot -o multiple.dot`
- Convert a dot file into pdf: `dot -T pdf discussion.dot > discussion.pdf`
- For more information regarding the command options, check https://django-extensions.readthedocs.io/en/latest/graph_models.html
