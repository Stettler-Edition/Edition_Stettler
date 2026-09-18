import re

def reformat_tei(text: str) -> str:
    """
    Reformate un document TEI en réduisant les sauts de ligne superflus :
    - Le bloc <head><choice><orig>...</orig><reg/></choice></head> est replié
      sur une seule ligne.
    - Chaque bloc <lb/><choice><orig>...</orig><reg/></choice> dans un <p>
      est reformaté sur 3 lignes : lb+choice / orig / reg+fermeture choice.
    - Le contenu de <reg> n'est jamais inventé : s'il est vide (<reg/>),
      il reste vide ; s'il est déjà rempli, il est conservé tel quel.
    """

    # --- 1) Bloc <head> : tout sur une seule ligne ---
    head_pattern = re.compile(
        r'<head>\s*<choice>\s*<orig>(.*?)</orig>\s*'
        r'(?:<reg\s*/>|<reg>(.*?)</reg>)\s*</choice>\s*</head>',
        re.DOTALL
    )

    def head_repl(m):
        orig, reg = m.group(1), m.group(2)
        reg_tag = f'<reg>{reg}</reg>' if reg else '<reg/>'
        return f'<head><choice><orig>{orig}</orig>{reg_tag}</choice></head>'

    text = head_pattern.sub(head_repl, text)

    # --- 2) Blocs <lb/><choice><orig>...</orig><reg/></choice> dans les <p> ---
    block_pattern = re.compile(
        r'^([ \t]*)<lb/>\s*<choice>\s*<orig>(.*?)</orig>\s*'
        r'(?:<reg\s*/>|<reg>(.*?)</reg>)\s*</choice>',
        re.DOTALL | re.MULTILINE
    )

    def block_repl(m):
        indent, orig, reg = m.group(1), m.group(2), m.group(3)
        reg_tag = f'<reg>{reg}</reg>' if reg else '<reg/>'
        inner = indent + '  '
        return (f'{indent}<lb/><choice>\n'
                f'{inner}<orig>{orig}</orig>\n'
                f'{inner}{reg_tag}</choice>')

    text = block_pattern.sub(block_repl, text)

    return text


if __name__ == '__main__':
    import sys

    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.xml'
    outfile = sys.argv[2] if len(sys.argv) > 2 else 'output.xml'

    with open(infile, encoding='utf-8') as f:
        content = f.read()

    result = reformat_tei(content)

    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Fichier reformaté écrit dans : {outfile}")
