# AGENTS.md — Guía para trabajar en este repositorio

Tienda al detal de Juguetería Taiwan (Cali): un `index.html` monolítico publicado
por GitHub Pages en saldosjugueteriataiwan.com, con catálogo sincronizado 4×/día
desde POSGold por un cron de GitHub Actions. Ver `README.md` para la
arquitectura completa.

## Reglas de oro

1. **El repo es público.** Nada de tokens, llaves, contraseñas ni costos en claro.
   Las credenciales viven en `.env` (local, gitignored) y en los *secrets* de
   GitHub Actions. Los `.txt` están TODOS en `.gitignore` precisamente porque
   guardan material privado.
2. **`catalogo.js` y `assets/fotos/` son generados** por `sync_posgold.py`:
   jamás se editan a mano. El historial de git es su respaldo.
   `data/configuracion.js` lo escribe el PANEL (API de GitHub), no el cron
   ni personas; tampoco se edita a mano.
3. Al publicar, `index.html` es lo único que se suele tocar a mano; el cron
   commitea `catalogo.js`, `data/mapa_imagenes.json` y `assets/fotos`.
4. Textos de la tienda: español de Colombia, tuteo, tono cálido. Los mensajes
   de commit del repo no llevan tildes (estilo histórico).
5. Nunca commitear sin que pase el QA (regla 42/42 de `qa_e2e.py` y 38/38 de
   `qa_carrito.py`, abajo).

## Comandos de verificación

```bash
python qa_e2e.py            # suite completa: 42/42 esperado (Playwright + WebKit)
python qa_carrito.py        # carrito: identidad, aritmetica exacta, mensaje WhatsApp, vuelo y confeti (38/38)
python sync_posgold.py --dry-run   # sync de prueba sin tocar catalogo.js
python sync_posgold.py --verificar-todas   # auditar/regenerar miniaturas
python generar_enlace_config.py    # enlace de config (llave+tokens) para un navegador
```

Verificación de sintaxis JS del index (los dos primeros `<script>` son JSON-LD,
no JavaScript):

```bash
node -e "const h=require('fs').readFileSync('index.html','utf8');const re=/<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>([\s\S]*?)<\/script>/gi;let m;while((m=re.exec(h))!==null){if(m[1].trim())new Function(m[1]);}console.log('OK')"
```

Publicar: `git push origin main`. GitHub Pages republica en ~1 min. Si el push
es rechazado, el cron movió el remoto: `git pull --rebase origin main` y de nuevo.

## Mapa del código (index.html)

- **Configuración editable** (todo lo que cambia la dueña va aquí):
  `TIENDA_DEFECTO` y `PRECIOS_DEFECTO` son la FÁBRICA; `data/configuracion.js`
  es lo PUBLICADO desde el panel (botón "Publicar para todos", vía API de
  GitHub con el token Contents) y **manda sobre la fábrica**. Si cambias
  TIENDA_DEFECTO o PRECIOS_DEFECTO a mano, actualiza o borra también
  `data/configuracion.js` o tu cambio será invisible. "Guardar en MI
  computador" queda en localStorage del navegador (con marca de versión
  `jt_config_base`: lo publicado más nuevo lo reemplaza al recargar).
  `CONFIG` → valores de fábrica en ejecución.
- **Publicación del panel**: `publicarConfigNavegador()` sube TIENDA+PRECIOS a
  `data/configuracion.js` con versión siempre creciente (`Math.max(Date.now(),
  publicada+1)`) y SIN `claveAdmin` (la clave nunca se publica). La absorción
  vive arriba de `cargarTienda` (`CONFIG_PUBLICA`, `TIENDA_FABRICA`,
  `PRECIOS_FABRICA`, `BASE_CONFIG_KEY`).
- **Panel de administración**: login con `TIENDA_DEFECTO.claveAdmin`, abre con
  el enlace del pie, `?admin=1` o Ctrl+Shift+A. Sus secciones se pintan desde
  funciones `pintar*Admin()`.
- **Visibilidad**: `catalogoVisible()` filtra categorías/productos ocultos
  (`TIENDA.categoriasOcultas` / `productosOcultos`); el panel siempre ve
  `CATALOGO_BASE` completo. La clave `"navidad"` esconde la sección de
  temporada, no sus productos.
- **Precios**: `precioDetal()` = base × multiplicador × (1+margen) y
  `redondearPrecio()` al múltiplo de `PRECIOS.redondeo` (**1000** hoy: la
  fábrica en `PRECIOS_DEFECTO` y lo publicado en `data/configuracion.js`
  deben llevar el mismo valor o lo publicado tapa a la fábrica). El
  tachado (`compareDetal`) se acota a un descuento creíble de 20–30%.
- **Carrito**: `cart` fusiona líneas por `lineId` (`id::talla`), el total
  sale de `getCartSummary()` (Σ precio×cantidad) y `qa_carrito.py` (36/36)
  vigila identidad de líneas, aritmética exacta hasta el mensaje de
  WhatsApp, persistencia y vuelo.
- **Vuelo al carrito**: `volarAlCarrito(product)` clona la miniatura de la
  tarjeta (`.jt-fly`) y la anima con Web Animations hasta el icono; abre el
  checkout ~300 ms después para que el ojo siga el recorrido. Guardas: no
  vuela con el checkout abierto (sugeridos), con
  `prefers-reduced-motion`, sin Web Animations ni sin foto cargada.
- **Confeti del pedido**: `lanzarConfeti()` celebra el envío del pedido
  (`.jt-confeti`, ~70 partículas, ~1,4 s) con las mismas guardas; NUNCA debe
  romper el pedido (try/catch total).
- **ScrollLock**: congela el scroll del body conservando la posición (menú,
  carrito, lightbox y checkout). Toda pantalla completa debe usarlo, nunca
  toggles directos de `body-no-scroll`.
- **Lightbox**: muestra la miniatura del repo al instante y sube al original de
  POSGold con `imgFullUrl()` (usa `fulls[]` del catálogo, mismo índice que
  `images[]`).
- **Pedidos**: `sendWhatsAppOrder()` arma el mensaje de WhatsApp; el enlace de
  cada producto apunta a `?producto={slug}` de esta misma tienda (deep link que
  resalta la tarjeta con `scrollToProduct`).
- **Sincronización (`sync_posgold.py`)**: el detal sale del **Precio 2** del
  sistema (el tachado, del Precio 1 cuando queda encima) y los filtros duros son
  activo + existencias + foto + categoría + costo + rentabilidad. Conciliación
  dura con POSGold en 3 puertas (pre-generación, contenido y archivo escrito):
  si el catálogo quedara con UN solo producto inactivo o sin existencias, aborta
  SIN tocar lo publicado. Cada corrida deja `reportes/sync_*.csv` (con costos:
  nunca publicar) y `reportes/novedades_*.xlsx` para la tienda (lo que no
  publica y por qué, marcando lo que estaba publicado); el cron sube ese Excel
  como artefacto de Actions.

## Gotchas conocidos

- Playwright sobre `file://` no registra Resource Timing de imágenes ni descarga
  en frío: para medir rendimiento real, probar contra el sitio publicado.
- El servidor de fotos de POSGold tarda ~2 s por archivo: la vitrina NUNCA debe
  cargar originales (usa las miniaturas del repo; el original es solo para el
  lightbox, bajo demanda).
- Los carruseles muestran máximo 32 productos por fila: renderizar más avalancha
  peticiones (pasamos de 562 `<img>` a 72 y el arranque bajó de 12 s a ~2 s).
- El filtro de categorías del panel se guarda por navegador (localStorage);
  para que lo vean TODOS, la administración usa "Publicar para todos" (o se
  edita `data/configuracion.js`, nunca a mano: se publica desde el panel).
- El push del cron puede ser rechazado si el panel publicó algo a media
  corrida (el remoto se movió entre el checkout y el push del runner): la
  corrida avisa "AVISO git push" y la siguiente lo publica todo. No es error.
- QA de WebKit: tocar una foto del lightbox solo cuando la miniatura de la
  tarjeta ya cargó (nadie toca una foto que no ve); si el QA de WebKit móvil
  falla por tiempo, revisar primero si es la red, no el código.
- **El API de POSGold no trae costos** (verificado contra `GetProduct_V6`:
  34 campos, ninguno de costo; el login web tiene captcha): no intentar
  automatizar el refresco de costos. El plan B si POSGold algún día expone
  el campo está documentado en `.github/workflows/sync-top300.yml`.
- **El Excel de costos es un contrato de formato**: el export de PRODUCTOS
  de POSGold trae 86 columnas y encabezados en minúscula
  (`productoid`, `costo`, `costopromedio`, `costoultimo`); el pipeline lee
  por NOMBRE de columna (el orden y las columnas extra no importan) y falla
  seguro: el panel rechaza el archivo antes de cifrar (columnas faltantes o
  <1.000 filas = export filtrado) y el cron aborta antes de tocar
  `catalogo.js` si los encabezados cambian. Un producto nuevo sin costo en
  el Excel queda oculto ("sin costo en Excel"): no es un bug, es la regla.
- Un producto nuevo en POSGold entra solo en la próxima corrida si cumple
  los filtros (activo + existencias + foto + precio + costo + rentabilidad);
  fotos, slug, categoría y precios son automáticos. Temporada navideña y
  destacados del héroe se curan a mano (panel / workflow).
