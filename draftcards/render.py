from jinja2 import Environment, FileSystemLoader, select_autoescape

class Render:
    def __init__(self):
        self.env = Environment(
                loader=FileSystemLoader('templates'),
                autoescape=select_autoescape(['html', 'xml'])
                )

    def render(self, template_name, data):
        template = self.env.get_template(template_name)
        return template.render(**data)
