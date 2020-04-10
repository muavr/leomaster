import lxml
import lxml.html
from leoparser.models import Rule


class Parser:
    def __init__(self):
        self.rules = {rule.id: rule for rule in Rule.objects.all()}

    def _get_roots(self):
        return [rule for rule in self.rules.values() if rule.parent is None]

    def _go_through_rules(self, root, html, doc, level=1):
        try:
            result = root.apply(html)
        except Exception:
            result = '__error__'
        if isinstance(result, (list, tuple)):
            for index, peace_of_result in enumerate(result):
                if isinstance(peace_of_result, lxml.html.HtmlElement):
                    context_doc = dict()
                    doc[root.name + '_' + str(index)] = context_doc
                    context_html = peace_of_result
                else:
                    doc.setdefault(root.name, dict()).update({index: peace_of_result})
                    context_doc = doc[root.name]
                    context_html = html
                for rule in root.children.all():
                    print(' ' * (level * 3) + '|_', str(rule))
                    self._go_through_rules(rule, context_html, context_doc, level=level + 1)
        else:
            if isinstance(result, lxml.html.HtmlElement):
                context_doc = dict()
                doc[root.name] = context_doc
                context_html = result
            else:
                doc[root.name] = result
                context_doc = doc
                context_html = html
            for rule in root.children.all():
                print(' ' * (level * 3) + '|_', str(rule))
                self._go_through_rules(rule, context_html, context_doc, level=level + 1)

    def go_through(self, html, doc):
        root_rules = self._get_roots()
        for root in root_rules:
            print('|_', str(root))
            self._go_through_rules(root, html, doc)

    def parse(self, content):
        doc = dict()
        html = lxml.html.document_fromstring(content)
        self.go_through(html, doc)
        return doc
