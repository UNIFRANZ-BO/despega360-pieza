# Despega 360 · Arma tu pieza publicitaria (subida de la pieza terminada) — emprendedoras

Proyecto de Rafael Aramayo (UNIFRANZ Cochabamba) para el programa Despega 360 (IFFI – UNIFRANZ/IPEE, apoyo UE).
App de un solo HTML que arma la instrucción (prompt) para que cada emprendedora pida a una IA los textos de su
pieza publicitaria para redes. Viene de un HTML de Rafael (copia intacta en `docs/original_Pieza.html`).
Proyecto hermano de `../Emprendedoras` («Arma tu guía IA»): **misma receta** (sin Sheets ni base de datos; lo que
suben las emprendedoras va a una carpeta de Drive, con una subcarpeta por negocio). Resumen de esa receta: `../Emprendedoras/docs/Chat_Despega360_resumen.md`.

## Cómo trabaja Rafael
- No es programador: pasos numerados con rutas de menú exactas y qué NO tocar. Ejecución directa, poco ida y vuelta.
- Castellano neutro (tú), nunca voseo. Textos para emprendedoras: simples y cálidos.

## Decisiones
- **v2.0 (09-oct-2026), receta v2.1 de la guía IA:** lo que llega a Drive es la **pieza terminada**, no una constancia.
  Paso final **«Sube tu pieza terminada»** (+ atajo en la bienvenida «¿Ya terminaste tu pieza? Súbela aquí» y botón
  «Ya terminé: subir mi pieza» en la pantalla final). PNG/JPG/WebP/GIF/HEIC, PDF, PowerPoint, Word; **5 archivos × 15 MB**.
  Fotos JPG/WebP de más de 1,2 MB se achican (2400 px, JPEG 0,85); **un PNG solo si pasa de 4 MB** (la pieza diseñada se
  respeta). La primera imagen elegida **reemplaza el boceto en el celular** («Tu pieza real»). Si falla: «Reintentar el
  envío» con el mismo código (no se duplica). Sin cola en `localStorage`.
- «Copiar mi instrucción» está disponible de inmediato. La constancia PDF quedó como **descarga local opcional** (no se envía).
- Textos: llega «al equipo de Despega 360» (nunca «a tu mentora»; la instrucción para la IA no se toca).
- **Nombre del negocio obligatorio** (paso «Tu IA y tu negocio» y prellenado al subir). Nombra la **subcarpeta** y los
  archivos: `AAAA-MM-DD HH.MM – Nombre del negocio.ext`, varios a la vez `… (1 de 2).png`. En la descripción: rubro,
  producto, canal, zona, IA, nombre original, hora y código.
- **Script propio** (no el de la guía IA): otra carpeta («Despega 360 · Piezas publicitarias de las emprendedoras») y otra
  URL, en la misma cuenta dedicada. IDs `D360P-…` (el script rechaza los `D360-` de la otra app).
- PDF: datos + **boceto** con la paleta del primer estilo y el formato del canal + siguiente paso + anexo con la instrucción.
- **`#restoPrompt` y `buildPrompt()` (con precioTxt, difTxt, punto, FALTA) no se tocan.** `build.py` verifica que sigan
  idénticos al original cuando existe `docs/original_Pieza.html`.
- La nota de bienvenida dice que lo único que llega al equipo es la pieza que ella suba al final.
- **Interfaz «gran estreno» (v1.0):** pedido de Rafael: «muy llamativa». Tema oscuro tipo escenario: reflectores que barren,
  piso de neón en perspectiva, manchas de color, canvas con destellos, rombos de aguayo y reacciones (❤️👍⭐) flotando;
  megáfono con ondas; título con degradado; **dos cintas publicitarias cruzadas** que muestran el nombre, el producto y
  el precio de la emprendedora; aguayo de 7 hileras que se teje por paso. **Pieza en vivo:** celular con el boceto que se
  actualiza mientras escribe (columna fija a la derecha desde 1100 px; en celular, botón con anillo de avance en la barra
  inferior que abre una hoja). Anillo de avance %, reacciones que salen del celular al completar datos, estilos con su
  paleta, canales con su proporción dibujada, precio en etiqueta. Al subir: destello, notificación «Tu pieza llegó» en
  el celular, reacciones y confeti. Vidrio solo en computadoras; canvas ~30 fps, pausa con pestaña oculta; `prefers-reduced-motion`.
  Lecciones heredadas: `body` sin fondo (va en `html`); `main`/`header`/`.cinta` sin desborde horizontal (la e2e lo mide).

## Estructura
| Ruta | Qué es |
|---|---|
| `src.html` | Fuente. Se edita aquí. |
| `build.py` | Copia a `index.html`, valida el JS con `node --check` y que la instrucción siga igual al original. |
| `index.html` | Lo que se publica. No editar a mano. |
| `apps-script/Codigo.gs` | Backend: Apps Script **independiente** en la cuenta dedicada. |
| `tests/backend.test.js` | Script con Drive simulado: formatos, archivos disfrazados, subcarpetas, tope. |
| `tests/e2e_test.py` | Recorrido completo con Playwright (390 y 1366 px, subida de varios archivos, error y reintento, atajo, panel, modo de prueba, movimiento reducido). Bloquea `script.google.com`: **nunca** usa el servidor real. |

## Contrato app ↔ script
- `GET ?action=ping` → `{ok, servicio, version_app, abierta}` (JSONP con `&callback=`). `GET ?action=verificar&id=` → `{ok, existe}`.
- `POST {action:'subir', data:{id, nombre, rubro, producto, canal, municipio(zona), ia, ts, fecha_local, version, parte, total, nombre_original, archivo}}`
  (el script v2 sigue aceptando `pdf` de la app v1)
  → `{ok,id}` · `{ok,id,repetido:true}` · `{ok:false, codigo:'cerrada'|'invalido'|'limite'|'error'}`.
- Clave local: borrador `despega360-pieza-v1` (la misma del original). Los `PRUEBA-…` quedan sueltos en la carpeta principal.
- Panel técnico: `?admin=1` o tres toques en «v2.0». `?api=<url>` prueba otra URL; `?api=sin-url` fuerza modo de prueba.

## Estado (09-oct-2026)
- [x] App, script y pruebas locales en verde.
- [x] Repo `UNIFRANZ-BO/despega360-pieza` + GitHub Pages (publicado el 09-oct-2026 con confirmación de Rafael).
- [x] Script «Despega 360 · Piezas» implementado en la cuenta dedicada (09-oct-2026): `AKfycbwNm7JM…0whICJXGWRv/exec`.
      Ping anónimo OK; URL incrustada en `API_URL_DEFECTO`. **Enlace vigente: https://unifranz-bo.github.io/despega360-pieza/?v=2**
- [x] v2.0 (subida de la pieza) escrita y probada en local; commit hecho, **sin publicar**.
- [ ] Rafael actualiza el script a v2.0 (Administrar implementaciones → ✏️ → **Nueva versión**) → `ping` debe decir
      `version_app: "2.0"` → recién entonces push de la app y repartir **`?v=3`** (orden: script → app).
- [ ] Prueba real desde el celular; luego `borrarPruebas` y borrar a mano subcarpetas de prueba.

## Comandos
```bash
export PATH="/c/Program Files/nodejs:/c/Program Files/GitHub CLI:$PATH"; export PYTHONIOENCODING=utf-8
python build.py
node tests/backend.test.js
python tests/e2e_test.py
```
