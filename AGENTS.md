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
  `CONFIG` → valores de fábrica en ejecución; `TIENDA_DEFECTO` → identidad,
  contacto, analítica, crédito, visibilidad (se sobreescribe con localStorage y
  se exporta con "Guardar para TODOS"); `PRECIOS_DEFECTO` → márgenes, temporada
  y precios fijos.
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
  los valores de fábrica se publican editando `TIENDA_DEFECTO`.
- QA de WebKit: tocar una foto del lightbox solo cuando la miniatura de la
  tarjeta ya cargó (nadie toca una foto que no ve); si el QA de WebKit móvil
  falla por tiempo, revisar primero si es la red, no el código.
