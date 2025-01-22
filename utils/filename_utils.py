def normalize_filename(filename):
    replacements = {
        '｜': '|',
        '|': '_',
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '_',
        '<': '_',
        '>': '_',
        '．': '.',
        '。': '.',
        '　': ' ',
    }
    
    for old, new in replacements.items():
        filename = filename.replace(old, new)
    
    filename = ' '.join(filename.split())
    return filename.strip()