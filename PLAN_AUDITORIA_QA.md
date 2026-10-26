# Plan de auditoría y QA — Punto Hogar Juguetería

Qué se prueba, cómo y cuándo, para publicar sin miedo. Regla de oro del
repo: **no se commitea nada sin que el QA esté en verde**.

## Niveles de verificación

### L0 — Sintaxis (antes de cada commit)

Los bloques `<script>` inline de `index.html` (los dos primeros son
JSON-LD y no cuentan):

```bash
node -e "const h=require('fs').readFileSync('index.html','utf8');const re=/<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>([\s\S]*?)<\/script>/gi;let m;while((m=re.exec(h))!==null){if(m[1].trim())new Function(m[1]);}console.log('OK')"
```

También vale para `catalogo.js` y `data/configuracion.js`:

```bash
node -e "new Function(require('fs').readFileSync('catalogo.js','utf8'));console.log('OK')"
```

### L1 — Suite del carrito (antes de cada push)

`qa_carrito.py` — **38/38 esperado**, Playwright sobre el archivo local.
Cubre 4 fases:

| Fase | Qué vigila |
|---|---|
| 1 | El carrito agrega los productos CORRECTOS: id, nombre, SKU, precio, talla, fusión de líneas, badge |
| 2 | La cuenta es EXACTA: totales (cálculo y DOM), subtotales, +1/−1, tacho, persistencia tras recarga, vaciado |
| 3 | El pedido de WhatsApp es EXACTO: enlace al 573137203136, referencias, subtotales, TOTAL, unidades, confeti, reinicio del carrito |
| 4 | Dopamina: vuelo de la foto al carrito, reuso de la miniatura, pop del badge, guardas (checkout abierto, `prefers-reduced-motion`) |

Incluye la **regla de precios de la tienda**: los 1.552 productos
visibles deben venderse a `Precio 2 × 1.30` (margenGlobal 0.30, redondeo
0) — si se toca `PRECIOS_DEFECTO`, `data/configuracion.js` o la lógica de
`precioDetal()`, esta prueba es la que lo caza.

```bash
python qa_carrito.py
```

### L2 — Revisión visual (tras publicar)

Contra el sitio publicado (GitHub Pages), no contra `file://`:

1. Logo circular en header y favicon; nombre "Punto Hogar Juguetería"
   en pestaña, héroe, menú móvil y pie (con firma "by Fredy Henao").
2. Esquema de colores del brief (verde lima como acento, grises de
   Punto Hogar) y tipografías Poppins/Montserrat cargadas.
3. Un paseo completo: buscar un producto, agregarlo, ver el vuelo al
   carrito, abrir checkout, elegir A domicilio y pagar contra entrega.
4. NO debe aparecer: opción "Retiro en tienda", enlaces "Cómo llegar",
   dirección física, ni mención alguna de Taiwan.
5. Compartir el enlace en WhatsApp: debe verse el og con el logo
   circular (los mensajeros cachean; usar el inspector de
   https://developers.facebook.com/tools/debug/ si no).

### L3 — Pedido real de prueba (tras publicar)

1. Agregar 2-3 productos variados (barato + caro).
2. Completar el checkout con datos de prueba y enviar el pedido.
3. Verificar en el WhatsApp +57 313 720 31 36: llega con
   "*NUEVO PEDIDO — PUNTO HOGAR JUGUETERÍA*", precios con el +30%
   correcto, enlaces de ficha que abren la tarjeta resaltada en ESTA
   tienda, y el envío cotizado por WhatsApp.
4. Probar también desde el celular (Safari iOS incluido si hay).

### L4 — Suite E2E completa (futura)

El sistema original tenía `qa_e2e.py` (42/42) con escenarios de panel,
lightbox y filtros; NO vive en este repo (contiene la clave del panel en
sus escenarios y por eso estaba gitignored). Si se necesita, reconstruirla
siguiendo el estilo de `qa_carrito.py` y manteniéndola fuera del repo.

## Calendario sugerido

| Momento | Nivel |
|---|---|
| Cada commit local | L0 |
| Cada push a main | L1 (38/38) |
| Tras activar Pages o cambiar branding/precios | L2 + L3 |
| Cambios grandes (checkout, precios, panel) | L1 + L2 + L3 |

## Gotchas de QA

- Playwright sobre `file://` no registra Resource Timing de imágenes:
  el rendimiento se mide contra el sitio publicado.
- Las fotos ORIGINALES del lightbox tardan ~2 s cada una (viven en el
  servidor del sistema original): no es un bug del sitio.
- Si se cambia el margen desde el panel en vivo, L1 sigue probando el
  30% de fábrica: actualizar la regla en `qa_carrito.py` si se cambia el
  margen de forma permanente.
- El QA de WebKit/Safari puede fallar por red lenta al tocar fotos del
  lightbox: solo tocarlas cuando la miniatura ya cargó.
