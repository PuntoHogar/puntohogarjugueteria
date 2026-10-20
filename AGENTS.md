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
5. Nunca commitear sin que pase el QA (regla 42/42, abajo).

## Comandos de verificación

```bash
python qa_e2e.py            # suite completa: 42/42 esperado (Playwright + WebKit)
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
- **ScrollLock**: congela el scroll del body conservando la posición (menú,
  carrito, lightbox y checkout). Toda pantalla completa debe usarlo, nunca
  toggles directos de `body-no-scroll`.
- **Lightbox**: muestra la miniatura del repo al instante y sube al original de
  POSGold con `imgFullUrl()` (usa `fulls[]` del catálogo, mismo índice que
  `images[]`).
- **Pedidos**: `sendWhatsAppOrder()` arma el mensaje de WhatsApp; el enlace de
  cada producto apunta a `?producto={slug}` de esta misma tienda (deep link que
  resalta la tarjeta con `scrollToProduct`).

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
