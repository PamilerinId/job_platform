from slugify import slugify


def to_slug(value: str):
    if value:
        return slugify(value, max_length=15, word_boundary=True, 
                    separator=".", stopwords=['the', 'and', 'of'])