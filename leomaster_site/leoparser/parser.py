from leoparser.models import Rule


class Parser:
    def __init__(self):
        rules = Rule.objects.all()
