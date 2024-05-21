import re

REGEXES = [
    (r'replace this', 'with this')
]

def normalize(article_list):
    for regex in REGEXES:
        compiled_regex = re.compile(regex[0])

        for article in article_list:
            for paragraph in article.body:
                re.sub(compiled_regex, regex[1], paragraph)
