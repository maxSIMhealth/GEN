from django import template

register = template.Library()


@register.filter
def field_type(bound_field):
    return bound_field.field.widget.__class__.__name__


@register.filter
def input_class(bound_field):
    css_class_list = []

    if bound_field.form.is_bound:
        if bound_field.errors:
            css_class_list.append("is-invalid")
        elif field_type(bound_field) != "PasswordInput":
            css_class_list.append("is-valid")

    if bound_field.widget_type == "checkbox":
        css_class_list.append("form-check-input")
        css_class = " ".join(css_class_list)
        return "{}".format(css_class)

    css_class = " ".join(css_class_list)

    return "form-control {}".format(css_class)
