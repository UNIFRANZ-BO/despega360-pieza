"""Prueba de punta a punta de la app con un Apps Script simulado (no toca Drive).
Requisitos: pip install playwright && playwright install chromium
Uso: python tests/e2e_test.py        (genera capturas en tests/shots/)
"""
import asyncio, base64, json, pathlib
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SHOTS = RAIZ / 'tests' / 'shots'; SHOTS.mkdir(exist_ok=True)
API = 'https://script.google.com/macros/s/TESTID/exec'
DRIVE = {}           # id → payload recibido
CAIDO = {'on': False}

async def backend(route, req):
    if CAIDO['on']: return await route.abort()
    q = parse_qs(urlparse(req.url).query)
    if req.method == 'POST':
        d = json.loads(req.post_data)['data']
        assert base64.b64decode(d['pdf'])[:4] == b'%PDF', 'no es PDF'
        DRIVE[d['id']] = d
        return await route.fulfill(status=200, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                                   body=json.dumps({'ok': True, 'id': d['id']}))
    a, cb = q.get('action', ['ping'])[0], q.get('callback', [''])[0]
    out = {'ok': True, 'existe': q.get('id', [''])[0] in DRIVE} if a == 'verificar' else {'ok': True, 'abierta': True}
    await route.fulfill(status=200, headers={'Content-Type': 'application/javascript'}, body=f'{cb}({json.dumps(out)});')

async def sig(pg, ms=600):
    await pg.click('#sig'); await pg.wait_for_timeout(ms)

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
    await pg.screenshot(path=str(SHOTS / f'{ancho}_01_negocio.png'))
    await sig(pg)
    await pg.fill('#prod', 'Mermelada de durazno de 250 g'); await pg.fill('#cliente', 'Oficinas que piden refrigerios')
    await pg.fill('#benef', 'Un refrigerio rico y listo para llevar')
    # privacidad: un número largo avisa
    await pg.fill('#cliente', 'Llamar al 71234567'); await pg.wait_for_timeout(100)
    assert await pg.is_visible('#priv-cliente')
    await pg.fill('#cliente', 'Oficinas que piden refrigerios')
    await sig(pg)
    await pg.fill('#pos', 'Ayudo a oficinas a tener refrigerios ricos mediante mermelada casera, destacándome por la fruta del valle')
    await pg.fill('#evid', 'Comentarios de clientes en WhatsApp')
    await pg.click('.chip[data-fill="msg"]')
    await sig(pg)
    await pg.fill('#precio', '25'); await pg.click('.chip[data-text="2x1"]'); await pg.click('.chip[data-fill="sost"][data-text="ninguna"]')
    await pg.screenshot(path=str(SHOTS / f'{ancho}_04_precio.png'))
    await sig(pg)
    await pg.click('.opt[data-f="canal"][data-v="Instagram"]'); await pg.click('.opt[data-f="contacto"][data-v="WhatsApp"]')
    await pg.click('.chip[data-text="Quillacollo, Cochabamba"]')
    for e in ['divertido', 'cercano', 'elegante']: await pg.click(f'.est[data-v="{e}"]')
    await pg.click('.est[data-v="juvenil"]')
    assert 'hasta tres' in await pg.inner_text('#errEst')
    assert await pg.get_attribute('.est[data-v="divertido"]', 'data-n') == '1'
    # el boceto toma la paleta del primer estilo y el formato del canal
    bg = await pg.evaluate("getComputedStyle(document.querySelector('.screen')).getPropertyValue('--bg').trim()")
    assert bg.upper() == '#FFD84D', bg
    assert await pg.evaluate("document.querySelector('.screen').style.aspectRatio") in ('4 / 5', '4/5')
    await pg.screenshot(path=str(SHOTS / f'{ancho}_05_canal.png'), full_page=True)
    if ancho == 390:
        await pg.click('#btnVer'); await pg.wait_for_timeout(600)
        assert await pg.is_visible('#hoja .screen')
        assert 'Delicias del Valle' in await pg.inner_text('#hoja .screen')
        await pg.screenshot(path=str(SHOTS / f'{ancho}_05b_hoja.png'))
        await pg.click('#cerrarHoja')
    else:
        assert await pg.is_visible('.vitrina .screen') and await pg.is_hidden('#btnVer')
    await sig(pg)
    for t in ['luz', 'fondo']: await pg.click(f'.opt[data-v="{t}"]')
    await pg.fill('#foto', 'Frasco sobre mantel blanco junto a duraznos'); await pg.click('.opt[data-f="subir"][data-v="si"]')
    assert await pg.inner_text('#sig') == 'Armar mi instrucción'
    await sig(pg, 2200)
    assert await pg.is_hidden('#trasEnvio'), 'la instrucción no debe verse antes de enviar'
    assert '100%' in await pg.inner_text('.pct >> nth=0')
    await pg.screenshot(path=str(SHOTS / f'{ancho}_07_final_antes.png'), full_page=True)
    w = await pg.evaluate('document.documentElement.scrollWidth')
    assert w <= await pg.evaluate('innerWidth'), f'la página se desborda a lo ancho: {w}px'

async def main():
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

            # Enviar y guardar en PDF
            async with pg.expect_download() as dl:
                await pg.click('#btnPdf')
            d = await dl.value
            assert d.suggested_filename == 'Despega360_Pieza_Alimentos_Delicias_del_Valle.pdf', d.suggested_filename
            await pg.wait_for_selector('#trasEnvio:not([hidden])', timeout=8000); await pg.wait_for_timeout(700)
            assert len(DRIVE) == 1, 'el PDF no llegó al servidor'
            env = list(DRIVE.values())[0]
            assert env['id'].startswith('D360P-'), env['id']
            assert env['nombre'] == 'Delicias del Valle' and env['rubro'] == 'Alimentos' and env['canal'] == 'Instagram', env
            assert env['municipio'] == 'Quillacollo, Cochabamba' and env['producto'].startswith('Mermelada'), env
            assert 'llegó al equipo' in await pg.inner_text('#estadoPdf')
            assert await pg.is_visible('#sello')
            pdf = base64.b64decode(env['pdf']); (SHOTS / f'{ancho}_constancia.pdf').write_bytes(pdf)
            await pg.screenshot(path=str(SHOTS / f'{ancho}_08_final_enviado.png'))

            # Copiar: la instrucción es la del original
            await pg.click('#btnCopiar'); await pg.wait_for_timeout(300)
            clip = await pg.evaluate('navigator.clipboard.readText()')
            assert clip.startswith('Actúa como especialista en marketing') and 'Delicias del Valle' in clip and 'Quillacollo' in clip
            assert '- Precio en Bs: 25' in clip and 'Instagram (tamaño 1080 × 1350 px)' in clip and 'REGLAS' in clip

            # Segunda vez sin cambios: solo descarga, no reenvía
            async with pg.expect_download():
                await pg.click('#btnPdf')
            await pg.wait_for_timeout(500)
            assert len(DRIVE) == 1, 'no debe reenviar si no cambió nada'

            # Cambia algo → hay que volver a enviar
            await pg.click('[data-goto="4"]'); await pg.wait_for_timeout(400)
            await pg.click('.chip[data-text="Envío gratis"]')
            for _ in range(3): await sig(pg, 400)
            await pg.wait_for_timeout(1200)
            assert await pg.is_hidden('#trasEnvio') and 'Cambiaste algo' in await pg.inner_text('#estadoPdf')

            # Sin internet: descarga igual, queda en cola y se envía al volver a abrir
            CAIDO['on'] = True
            async with pg.expect_download():
                await pg.click('#btnPdf')
            await pg.wait_for_selector('#trasEnvio:not([hidden])', timeout=30000)
            assert 'se enviará sola' in await pg.inner_text('#estadoPdf')
            assert await pg.evaluate("JSON.parse(localStorage.getItem('despega360-pieza-cola1')).length") == 1
            CAIDO['on'] = False
            await pg.reload(); await pg.wait_for_timeout(3500)
            assert len(DRIVE) == 2, 'la cola no se reenvió'
            assert await pg.evaluate("JSON.parse(localStorage.getItem('despega360-pieza-cola1')).length") == 0
            await pg.screenshot(path=str(SHOTS / f'{ancho}_09_cola_enviada.png'))

            # Panel técnico
            await pg.goto(url + '&admin=1'); await pg.wait_for_timeout(900)
            await pg.click('#admin [data-a="ping"]'); await pg.wait_for_timeout(800)
            assert '"abierta":true' in await pg.inner_text('#admLog')
            await pg.click('#admin [data-a="prueba"]'); await pg.wait_for_timeout(1200)
            assert any(k.startswith('PRUEBA-') for k in DRIVE)
            await pg.click('#admin [data-a="close"]')

            # Borrar todo
            pg.once('dialog', lambda dg: asyncio.ensure_future(dg.accept()))
            await pg.click('#reiniciar'); await pg.wait_for_timeout(800)
            assert await pg.inner_text('#sig') == 'Empezar'

            ancho_doc = await pg.evaluate('document.documentElement.scrollWidth')
            assert ancho_doc <= ancho, f'scroll horizontal: {ancho_doc}px'
            assert not errs, errs
            print(f'OK {ancho}px · envíos recibidos: {len(DRIVE)}')
            await ctx.close()

        # Modo de prueba (?api=sin-url → URL no válida): descarga y desbloquea, sin enviar
        ctx = await b.new_context(accept_downloads=True); pg = await ctx.new_page()
        await pg.route('https://script.google.com/**', lambda r: r.abort())   # nunca tocar el servidor real
        await pg.goto((RAIZ / 'index.html').as_uri() + '?api=sin-url'); await pg.wait_for_timeout(800)
        await recorrido(pg, 'demo')
        async with pg.expect_download():
            await pg.click('#btnPdf')
        await pg.wait_for_selector('#trasEnvio:not([hidden])', timeout=8000)
        assert 'Modo de prueba' in await pg.inner_text('#estadoPdf')
        print('OK modo de prueba')

        # Movimiento reducido: sin errores y sin animaciones
        ctx = await b.new_context(reduced_motion='reduce'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('https://script.google.com/**', lambda r: r.abort())
        await pg.goto((RAIZ / 'index.html').as_uri() + '?api=sin-url'); await pg.wait_for_timeout(600)
        await sig(pg); assert not errs, errs
        print('OK movimiento reducido')
        await b.close()

asyncio.run(main())
