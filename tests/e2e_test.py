"""Prueba de punta a punta de la app (v2: subir la pieza terminada) con un Apps Script simulado.
NUNCA toca el servidor real: todas las llamadas a script.google.com se interceptan.
Requisitos: pip install playwright pillow && playwright install chromium
Uso: python tests/e2e_test.py        (capturas en tests/shots/)
"""
import asyncio, base64, io, json, os, pathlib
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SHOTS = RAIZ / 'tests' / 'shots'; SHOTS.mkdir(exist_ok=True)
TMP = SHOTS / 'archivos'; TMP.mkdir(exist_ok=True)
API = 'https://script.google.com/macros/s/TESTID/exec'
DRIVE = {}           # id → payload recibido
CAIDO = {'on': False}

def preparar_archivos():
    im = Image.new('RGB', (1080, 1350), '#FFD84D'); d = ImageDraw.Draw(im)
    d.rectangle([60, 220, 1020, 1000], fill='#C81E63'); d.ellipse([800, 40, 1040, 280], fill='#5B2A86')
    d.rounded_rectangle([60, 1100, 1020, 1220], 60, fill='#3A0B2A')
    im.save(TMP / '06_Pieza_comercial.png')
    im.save(TMP / 'pieza_v2.png')
    Image.frombytes('RGB', (2600, 2000), os.urandom(2600 * 2000 * 3)).save(TMP / 'foto_producto.jpg', quality=90)   # foto «pesada»
    (TMP / '06_Pieza_comercial.pptx').write_bytes(b'PK\x03\x04' + b'\0' * 2000)
    (TMP / 'programa.exe').write_bytes(b'MZ\x90\x00' + b'\0' * 500)
    b = io.BytesIO(); im.save(b, 'PDF'); (TMP / 'pieza.pdf').write_bytes(b.getvalue())

async def backend(route, req):
    if CAIDO['on']: return await route.abort()
    q = parse_qs(urlparse(req.url).query)
    if req.method == 'POST':
        d = json.loads(req.post_data)['data']
        raw = base64.b64decode(d.get('archivo') or d.get('pdf'))
        ok = raw[:4] in (b'%PDF', b'\x89PNG', b'PK\x03\x04') or raw[:3] == b'\xff\xd8\xff'
        out = {'ok': True, 'id': d['id']} if ok else {'ok': False, 'codigo': 'invalido'}
        if ok: DRIVE[d['id']] = dict(d, bytes=len(raw))
        return await route.fulfill(status=200, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}, body=json.dumps(out))
    a, cb = q.get('action', ['ping'])[0], q.get('callback', [''])[0]
    out = {'ok': True, 'existe': q.get('id', [''])[0] in DRIVE} if a == 'verificar' else {'ok': True, 'abierta': True}
    await route.fulfill(status=200, headers={'Content-Type': 'application/javascript'}, body=f'{cb}({json.dumps(out)});')

async def sig(pg, ms=600):
    await pg.click('#sig'); await pg.wait_for_timeout(ms)

async def sin_desborde(pg):
    w = await pg.evaluate('document.documentElement.scrollWidth')
    assert w <= await pg.evaluate('innerWidth'), f'la página se desborda a lo ancho: {w}px'

async def paso_actual(pg):
    return await pg.evaluate("document.querySelector('.step.active').dataset.id")

async def recorrido(pg, ancho):
    await pg.screenshot(path=str(SHOTS / f'{ancho}_00_bienvenida.png'))
    await sig(pg)
    # IA y nombre obligatorios
    await sig(pg, 300)
    assert 'Elige tu IA' in await pg.inner_text('#errIa')
    assert 'nombre de tu negocio' in await pg.inner_text('#errNombre')
    await pg.click('.opt[data-v="Gemini"]'); await pg.fill('#nombre', 'Delicias del Valle')
    assert await pg.inner_text('#errNombre') == ''
    assert 'Delicias del Valle' in await pg.text_content('#cinta1'), 'la cinta no muestra el negocio'
    await pg.click('.opt[data-v="Alimentos"]')
    await sig(pg)
    await pg.fill('#prod', 'Mermelada de durazno de 250 g'); await pg.fill('#cliente', 'Oficinas que piden refrigerios')
    await pg.fill('#benef', 'Un refrigerio rico y listo para llevar')
    await pg.fill('#cliente', 'Llamar al 71234567'); await pg.wait_for_timeout(100)
    assert await pg.is_visible('#priv-cliente'), 'debe avisar si escribe un número de teléfono'
    await pg.fill('#cliente', 'Oficinas que piden refrigerios')
    await sig(pg)
    await pg.fill('#pos', 'Ayudo a oficinas a tener refrigerios ricos mediante mermelada casera, destacándome por la fruta del valle')
    await pg.fill('#evid', 'Comentarios de clientes en WhatsApp')
    await pg.click('.chip[data-fill="msg"]')
    await sig(pg)
    await pg.fill('#precio', '25'); await pg.click('.chip[data-text="2x1"]'); await pg.click('.chip[data-fill="sost"][data-text="ninguna"]')
    await sig(pg)
    await pg.click('.opt[data-f="canal"][data-v="Instagram"]'); await pg.click('.opt[data-f="contacto"][data-v="WhatsApp"]')
    await pg.click('.chip[data-text="Quillacollo, Cochabamba"]')
    for e in ['divertido', 'cercano', 'elegante']: await pg.click(f'.est[data-v="{e}"]')
    await pg.click('.est[data-v="juvenil"]')
    assert 'hasta tres' in await pg.inner_text('#errEst')
    bg = await pg.evaluate("getComputedStyle(document.querySelector('.screen')).getPropertyValue('--bg').trim()")
    assert bg.upper() == '#FFD84D', bg
    if ancho == 390:
        await pg.click('#btnVer'); await pg.wait_for_timeout(600)
        assert 'Delicias del Valle' in await pg.inner_text('#hoja .screen')
        await pg.click('#cerrarHoja')
    else:
        assert await pg.is_visible('.vitrina .screen') and await pg.is_hidden('#btnVer')
    await sig(pg)
    for t in ['luz', 'fondo']: await pg.click(f'.opt[data-v="{t}"]')
    await pg.fill('#foto', 'Frasco sobre mantel blanco junto a duraznos'); await pg.click('.opt[data-f="subir"][data-v="si"]')
    assert await pg.inner_text('#sig') == 'Armar mi instrucción'
    await sig(pg, 2200)
    assert await paso_actual(pg) == 'listo'
    assert await pg.is_visible('#btnCopiar'), 'copiar debe estar disponible sin enviar nada'
    assert await pg.inner_text('#sig') == 'Ya terminé: subir mi pieza'
    await sin_desborde(pg)
    await pg.screenshot(path=str(SHOTS / f'{ancho}_07_final.png'), full_page=True)

async def main():
    preparar_archivos()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for ancho, alto, movil in [(390, 844, True), (1366, 900, False)]:
            DRIVE.clear(); CAIDO['on'] = False
            ctx = await b.new_context(viewport={'width': ancho, 'height': alto}, is_mobile=movil, has_touch=movil, accept_downloads=True)
            await ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
            pg = await ctx.new_page()
            errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.route('https://script.google.com/**', backend)
            url = (RAIZ / 'index.html').as_uri() + '?api=' + API
            await pg.goto(url); await pg.wait_for_timeout(1200)
            await recorrido(pg, ancho)

            # Copiar: la instrucción es la del original
            await pg.click('#btnCopiar'); await pg.wait_for_timeout(300)
            clip = await pg.evaluate('navigator.clipboard.readText()')
            assert clip.startswith('Actúa como especialista en marketing') and 'Delicias del Valle' in clip and 'Quillacollo' in clip
            assert '- Precio en Bs: 25' in clip and 'Instagram (tamaño 1080 × 1350 px)' in clip and 'REGLAS' in clip

            # Constancia local: se descarga y NO se envía
            async with pg.expect_download() as dl:
                await pg.click('#btnPdf')
            assert (await dl.value).suggested_filename == 'Despega360_Pieza_Alimentos_Delicias_del_Valle.pdf'
            await (await dl.value).save_as(str(SHOTS / f'{ancho}_constancia.pdf'))
            await pg.wait_for_timeout(400)
            assert not DRIVE, 'la constancia local no debe enviarse'

            # Paso «Sube tu pieza»
            await sig(pg, 900)
            assert await paso_actual(pg) == 'subir'
            assert await pg.input_value('#nombre3') == 'Delicias del Valle'
            assert 'Canva' in await pg.text_content('#tips')
            await pg.click('#btnSubir'); await pg.wait_for_timeout(300)
            assert 'Primero elige' in await pg.inner_text('#errArch')
            await pg.set_input_files('#archivos', [str(TMP / n) for n in ['06_Pieza_comercial.png', 'foto_producto.jpg', '06_Pieza_comercial.pptx', 'programa.exe']])
            await pg.wait_for_timeout(1500)
            assert 'programa.exe' in await pg.inner_text('#errArch')
            assert await pg.locator('#lista li').count() == 3
            await pg.click('#lista li:nth-child(3) .quitar'); await pg.wait_for_timeout(200)
            assert await pg.locator('#lista li').count() == 2
            assert await pg.inner_text('#txtSubir') == 'Enviar mis 2 archivos'
            # la pieza real aparece en el celular, con su proporción
            assert await pg.evaluate("!!document.querySelector('.screen .m-real')"), 'la pieza real no aparece en el celular'
            assert (await pg.evaluate("document.querySelector('.screen').style.aspectRatio")).replace(' ', '') == '1080/1350'
            await sin_desborde(pg)
            await pg.screenshot(path=str(SHOTS / f'{ancho}_08_subir_lista.png'))
            if ancho == 390:
                await pg.click('#btnVer'); await pg.wait_for_timeout(700)
                await pg.screenshot(path=str(SHOTS / f'{ancho}_08b_hoja_real.png'))
                await pg.click('#cerrarHoja')
            await pg.click('#btnSubir')
            await pg.wait_for_selector('#exito:not([hidden])', timeout=20000); await pg.wait_for_timeout(700)
            env = sorted(DRIVE.values(), key=lambda d: d['parte'])
            assert len(env) == 2 and [d['parte'] for d in env] == [1, 2] and all(d['total'] == 2 for d in env), env
            assert all(d['id'].startswith('D360P-') for d in env)
            assert env[0]['ts'] == env[1]['ts'] and env[0]['nombre'] == 'Delicias del Valle'
            assert env[0]['municipio'] == 'Quillacollo, Cochabamba' and env[0]['canal'] == 'Instagram' and env[0]['producto'].startswith('Mermelada'), env[0]
            assert env[0]['nombre_original'] == '06_Pieza_comercial.png', 'el PNG de la pieza no se convierte'
            assert env[0]['bytes'] == (TMP / '06_Pieza_comercial.png').stat().st_size
            orig = (TMP / 'foto_producto.jpg').stat().st_size
            assert env[1]['bytes'] < orig, f'la foto debía achicarse ({env[1]["bytes"]} ≥ {orig})'
            print(f'   foto: {orig // 1024} KB → {env[1]["bytes"] // 1024} KB')
            assert '¡Tu pieza llegó!' in await pg.inner_text('#exito')
            await pg.screenshot(path=str(SHOTS / f'{ancho}_09_subido.png'))

            # Sin internet: falla, se reintenta y no se duplica
            await pg.click('#otraVez'); await pg.wait_for_timeout(300)
            await pg.set_input_files('#archivos', str(TMP / 'pieza_v2.png')); await pg.wait_for_timeout(500)
            CAIDO['on'] = True
            await pg.click('#btnSubir')
            await pg.wait_for_function("document.querySelector('#txtSubir').textContent === 'Reintentar el envío'", timeout=60000)
            assert 'conexión' in await pg.inner_text('#estadoSubir')
            await pg.screenshot(path=str(SHOTS / f'{ancho}_10_error.png'))
            CAIDO['on'] = False
            await pg.click('#btnSubir')
            await pg.wait_for_selector('#exito:not([hidden])', timeout=20000)
            assert len(DRIVE) == 3

            # Panel técnico
            await pg.goto(url + '&admin=1'); await pg.wait_for_timeout(900)
            await pg.click('#admin [data-a="ping"]'); await pg.wait_for_timeout(800)
            assert '"abierta":true' in await pg.inner_text('#admLog')
            await pg.click('#admin [data-a="prueba"]'); await pg.wait_for_timeout(1500)
            assert any(k.startswith('PRUEBA-') for k in DRIVE)
            await pg.click('#admin [data-a="close"]')

            # Atajo desde la bienvenida (otra emprendedora, sin datos)
            await pg.evaluate("localStorage.clear()"); await pg.goto(url); await pg.wait_for_timeout(900)
            await pg.click('.atajo'); await pg.wait_for_timeout(900)
            assert await paso_actual(pg) == 'subir'
            await pg.set_input_files('#archivos', str(TMP / 'pieza.pdf')); await pg.wait_for_timeout(400)
            await pg.click('#btnSubir'); await pg.wait_for_timeout(300)
            assert 'nombre de tu negocio' in await pg.inner_text('#errNombre3')
            await pg.fill('#nombre3', 'Tejidos Sur'); await pg.click('#btnSubir')
            await pg.wait_for_selector('#exito:not([hidden])', timeout=20000)
            ult = [d for d in DRIVE.values() if d['nombre'] == 'Tejidos Sur']
            assert len(ult) == 1 and ult[0]['nombre_original'] == 'pieza.pdf' and ult[0]['total'] == 1
            await pg.click('#atras'); await pg.wait_for_timeout(500)
            assert await paso_actual(pg) == 'inicio', 'desde el atajo, Atrás vuelve a la bienvenida'

            await sin_desborde(pg)
            assert not errs, errs
            print(f'OK {ancho}px · archivos recibidos: {len(DRIVE)}')
            await ctx.close()

        # Modo de prueba (?api=sin-url): no envía nada
        ctx = await b.new_context(); pg = await ctx.new_page()
        await pg.route('https://script.google.com/**', lambda r: r.abort())   # nunca tocar el servidor real
        await pg.goto((RAIZ / 'index.html').as_uri() + '?api=sin-url'); await pg.wait_for_timeout(800)
        await pg.click('.atajo'); await pg.wait_for_timeout(600)
        await pg.fill('#nombre3', 'Demo'); await pg.set_input_files('#archivos', str(TMP / '06_Pieza_comercial.png'))
        await pg.wait_for_timeout(300); await pg.click('#btnSubir')
        await pg.wait_for_selector('#exito:not([hidden])', timeout=8000)
        assert 'Modo de prueba' in await pg.inner_text('#exito')
        print('OK modo de prueba')

        # Movimiento reducido: sin errores
        ctx = await b.new_context(reduced_motion='reduce'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('https://script.google.com/**', lambda r: r.abort())
        await pg.goto((RAIZ / 'index.html').as_uri() + '?api=sin-url'); await pg.wait_for_timeout(600)
        await sig(pg); assert not errs, errs
        print('OK movimiento reducido')
        await b.close()

asyncio.run(main())
