# Despega 360 · Arma tu pieza publicitaria (constancias en PDF) — emprendedoras

Proyecto de Rafael Aramayo (UNIFRANZ Cochabamba) para el programa Despega 360 (IFFI – UNIFRANZ/IPEE, apoyo UE).
App de un solo HTML que arma la instrucción (prompt) para que cada emprendedora pida a una IA los textos de su
pieza publicitaria para redes. Viene de un HTML de Rafael (copia intacta en `docs/original_Pieza.html`).
Proyecto hermano de `../Emprendedoras` («Arma tu guía IA»): **misma receta** (sin Sheets ni base de datos; PDF que
se descarga y una copia que va a una carpeta de Drive). Resumen de esa receta: `../Emprendedoras/docs/Chat_Despega360_resumen.md`.

## Cómo trabaja Rafael
- No es programador: pasos numerados con rutas de menú exactas y qué NO tocar. Ejecución directa, poco ida y vuelta.
- Castellano neutro (tú), nunca voseo. Textos para emprendedoras: simples y cálidos.

## Decisiones (09-oct-2026)
- **Botón final «Enviar y guardar en PDF»:** PDF una vez → cola local → descarga → subida al script → progreso de 3 pasos.
  «Copiar mi instrucción» aparece solo después de enviar (candado 🔒). Si cambia algo, debe enviar de nuevo; sin cambios
  el botón solo descarga otra copia.
- **Nombre del negocio obligatorio** (paso «Tu IA y tu negocio», junto con la IA). Nombra el archivo en Drive:
  `AAAA-MM-DD HH.MM – Nombre del negocio.pdf`. En la descripción: rubro, producto, canal, zona, IA, hora y código.
- **Script propio** (no el de la guía IA): otra carpeta («Despega 360 · Piezas publicitarias de las emprendedoras») y otra
  URL, en la misma cuenta dedicada. IDs `D360P-…` (el script rechaza los `D360-` de la otra app).
- PDF: datos + **boceto** con la paleta del primer estilo y el formato del canal + siguiente paso + anexo con la instrucción.
- **`#restoPrompt` y `buildPrompt()` (con precioTxt, difTxt, punto, FALTA) no se tocan.** `build.py` verifica que sigan
  idénticos al original cuando existe `docs/original_Pieza.html`.
- La nota de bienvenida ya no dice «No se envía a nadie» (ahora sí va una copia).
- **Interfaz «gran estreno» (v1.0):** pedido de Rafael: «muy llamativa». Tema oscuro tipo escenario: reflectores que barren,
  piso de neón en perspectiva, manchas de color, canvas con destellos, rombos de aguayo y reacciones (❤️👍⭐) flotando;
  megáfono con ondas; título con degradado; **dos cintas publicitarias cruzadas** que muestran el nombre, el producto y
  el precio de la emprendedora; aguayo de 7 hileras que se teje por paso. **Pieza en vivo:** celular con el boceto que se
  actualiza mientras escribe (columna fija a la derecha desde 1100 px; en celular, botón con anillo de avance en la barra
  inferior que abre una hoja). Anillo de avance %, reacciones que salen del celular al completar datos, estilos con su
  paleta, canales con su proporción dibujada, precio en etiqueta. Al enviar: destello, sello «Enviada», notificación en
  el celular y confeti. Vidrio solo en computadoras; canvas ~30 fps, pausa con pestaña oculta; `prefers-reduced-motion`.
  Lecciones heredadas: `body` sin fondo (va en `html`); `main`/`header`/`.cinta` sin desborde horizontal (la e2e lo mide).

## Estructura
| Ruta | Qué es |
|---|---|
| `src.html` | Fuente. Se edita aquí. |
| `build.py` | Copia a `index.html`, valida el JS con `node --check` y que la instrucción siga igual al original. |
| `index.html` | Lo que se publica. No editar a mano. |
| `apps-script/Codigo.gs` | Backend: Apps Script **independiente** en la cuenta dedicada. |
| `tests/backend.test.js` | Script con Drive simulado. |
| `tests/e2e_test.py` | Recorrido completo con Playwright (390 y 1366 px, cola sin internet, panel, modo de prueba, movimiento reducido). Bloquea `script.google.com`: **nunca** usa el servidor real. |

## Contrato app ↔ script
- `GET ?action=ping` → `{ok, servicio, version_app, abierta}` (JSONP con `&callback=`). `GET ?action=verificar&id=` → `{ok, existe}`.
- `POST {action:'subir', data:{id, nombre, rubro, producto, canal, municipio(zona), ia, ts, fecha_local, version, pdf}}`
  → `{ok,id}` · `{ok,id,repetido:true}` · `{ok:false, codigo:'cerrada'|'invalido'|'limite'|'error'}`.
- Claves locales: borrador `despega360-pieza-v1` (la misma del original), cola `despega360-pieza-cola1`.
- Panel técnico: `?admin=1` o tres toques en «v1.0». `?api=<url>` prueba otra URL; `?api=sin-url` fuerza modo de prueba.

## Estado (09-oct-2026)
- [x] App, script y pruebas locales en verde.
- [x] Repo `UNIFRANZ-BO/despega360-pieza` + GitHub Pages → https://unifranz-bo.github.io/despega360-pieza/?v=1
      (por ahora en **modo de prueba**: `API_URL_DEFECTO = 'PEGA_AQUI_LA_URL_EXEC'`).
- [ ] Rafael crea el script en la cuenta dedicada y pasa la URL `/exec` → verificar ping, incrustar, publicar `?v=2`.
- [ ] Prueba real desde el celular; luego `borrarPruebas`.

## Comandos
```bash
export PATH="/c/Program Files/nodejs:/c/Program Files/GitHub CLI:$PATH"; export PYTHONIOENCODING=utf-8
python build.py
node tests/backend.test.js
python tests/e2e_test.py
```
