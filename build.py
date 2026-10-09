"""Genera index.html (archivo que se publica) a partir de src.html y valida la sintaxis JS.
Si existe docs/original_Pieza.html, verifica además que el texto de la instrucción (#restoPrompt)
y buildPrompt() sigan idénticos al HTML original.
Uso:  python build.py
"""
import pathlib, re, subprocess, sys
raiz = pathlib.Path(__file__).parent
s = (raiz / 'src.html').read_text(encoding='utf-8')

def partes(t):
    resto = re.search(r'<script type="text/plain" id="restoPrompt">.*?</script>', t, re.S).group(0)
    build = re.search(r'  /\* -+ Textos derivados -+ \*/.*?\n  \}\n(?=\n  /\*)', t, re.S).group(0)
    return resto, build

orig = raiz / 'docs' / 'original_Pieza.html'
if orig.exists():
    if partes(s) != partes(orig.read_text(encoding='utf-8')):
        print('ERROR: la instrucción o buildPrompt() ya no son idénticos al original'); sys.exit(1)
    nota = ' · instrucción idéntica al original'
else:
    nota = ''
(raiz / 'index.html').write_text(s, encoding='utf-8')
js = re.findall(r'<script>(.*?)</script>', s, re.S)[-1]
tmp = raiz / 'tests' / '.check.js'; tmp.write_text(js, encoding='utf-8')
r = subprocess.run(['node', '--check', str(tmp)], capture_output=True, text=True); tmp.unlink()
if r.returncode: print(r.stderr); sys.exit(1)
print(f'index.html generado ({len(s)//1024} KB) · sintaxis JS OK{nota}')
