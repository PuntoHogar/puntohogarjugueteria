# AGENTS.md — Guía para trabajar en este repositorio

Tienda al detal de Punto Hogar Juguetería — by Fredy Henao: un `index.html`
monolítico publicado por GitHub Pages en puntohogar.github.io/puntohogarjugueteria, con
checkout por WhatsApp (+57 314 724 7260). Clonado y rebrandeado del sistema
original de Juguetería Taiwan (26-10-2026) siguiendo el patrón de Lunaria:
sistema heredado + rebranding completo al brief. Ver `README.md` para la
arquitectura completa.

## Reglas de oro

1. **El repo es público.** Nada de tokens, llaves, contraseñas ni costos en
   claro. Las credenciales viven en `.env` (local, gitignored) y en los
   *secrets* de GitHub Actions. Los `.txt` están TODOS en `.gitignore`
   precisamente porque guardan material privado.
2. **`catalogo.js` y `assets/fotos/`** en este repo son una FOTO ESTÁTICA
   del sistema original: Punto Hogar no tiene POSGold y no hay cron que los
   regenere. Si se editan, el historial de git es el respaldo.
   `data/configuracion.js` lo escribe el PANEL (API de GitHub), no personas;
   tampoco se edita a mano.
3. Al publicar, `index.html` es lo único que se suele tocar a mano.
4. Textos de la tienda: español de Colombia, tuteo, tono cálido y alegre
   (¡Diversión para cada momento!). Los mensajes de commit del repo no
   llevan tildes (estilo histórico).
5. Nunca commitear sin que pase el QA (`qa_carrito.py` 38/38, abajo) y la
   verificación de sintaxis JS.

## Identidad de marca (brief)

- Nombre: **Punto Hogar Juguetería** · Firma: **by Fredy Henao**.
- Eslogan: **¡Diversión para cada momento!**
- Colores (`:root` de index.html): verde lima `#A6C83A` (primario),
  gris carbón `#27313B` (texto), gris acero `#7D858D`, y acentos rojo
  `#F52F35`, amarillo `#FFC928`, azul `#1689E8`, naranja `#FF861B`,
  violeta `#8B35DB`.
- Tipografías: **Poppins** (titulares, 600/700/800) + **Montserrat** (cuerpo,
  400-700). Se cargan por Google Fonts en el `<head>`.
- Logo circular: `assets/logo-circular.png` (512). Favicons y og derivan del
  mismo.
- WhatsApp pedidos e información: `573147247260` (314 724 7260).
- **Sin tienda física**: no hay dirección, retiro en tienda, ni enlaces de
  mapa. Si algún día se configura `direccion` en el panel, el sitio vuelve a
  mostrar tienda física y mapas automáticamente (ver `aplicarIdentidad` y
  `renderMobileMenu`).

## Comandos de verificación

```bash
python qa_carrito.py        # carrito: identidad, aritmetica exacta, mensaje WhatsApp, vuelo y confeti (38/38)
```

Verificación de sintaxis JS del index (los dos primeros `<script>` son
JSON-LD, no JavaScript):

```bash
node -e "const h=require('fs').readFileSync('index.html','utf8');const re=/<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>([\s\S]*?)<\/script>/gi;let m;while((m=re.exec(h))!==null){if(m[1].trim())new Function(m[1]);}console.log('OK')"
```

Publicar: `git push origin main`. GitHub Pages republica en ~1 min.

## Mapa del código (index.html)

- **Configuración editable**: `TIENDA_DEFECTO` y `PRECIOS_DEFECTO` son la
  FÁBRICA; `data/configuracion.js` es lo PUBLICADO desde el panel (botón
  "Publicar para todos", vía API de GitHub con el token Contents) y **manda
  sobre la fábrica**. Si cambias TIENDA_DEFECTO o PRECIOS_DEFECTO a mano,
  actualiza también `data/configuracion.js` o tu cambio será invisible.
  "Guardar en MI computador" queda en localStorage del navegador.
- **Precios**: `precioDetal()` = base × multiplicador × (1+margen). **Punto
  Hogar vende con 30% de ganancia global sobre el Precio 2 del sistema**
  (`margenGlobal: 0.30`, `redondeo: 0`, exacto; fábrica y publicado llevan
  los mismos valores). La base llega en `catalogo.js` (el Precio 2 de la
  foto estática). El tachado (`compareDetal`) es honesto: solo si hay un
  Precio 1 real por encima.
- **Carrito**: `cart` fusiona líneas por `lineId` (`id::talla`), el total
  sale de `getCartSummary()` y `qa_carrito.py` vigila identidad, aritmética
  hasta el mensaje de WhatsApp, persistencia y vuelo.
- **Pedidos**: `sendWhatsAppOrder()` arma el mensaje al +57 314 724 7260;
  el enlace de cada producto apunta a `?producto={slug}` de esta misma
   tienda (los `url` de catalogo.js ya apuntan a puntohogar.github.io/puntohogarjugueteria).
- **Entrega**: solo "A domicilio" (no hay opción de retiro en tienda ni
  bloque de dirección en el checkout). El JS conserva la rama `tienda` por
  si algún día se configura dirección, pero no es alcanzable desde la UI.
- **Panel de administración**: login con `TIENDA_DEFECTO.claveAdmin`
  (fábrica `PUNTOHOGAR123*`, cambiada el 29-10-2026 desde la de clonado),
  abre con el enlace "Administración" del pie,
  `?admin=1` o Ctrl+Shift+A. Publica TIENDA+PRECIOS a
  `data/configuracion.js` SIN `claveAdmin` (la clave nunca se publica).
  Los tokens deben crearse contra `PuntoHogar/puntohogarjugueteria`
  (`SYNC_API` y `REPO_API` ya apuntan ahí). Los 3 botones de GitHub del
  panel (Sincronizar ahora, Cifrar y subir costos, Publicar para todos)
  aceptan el token de CUALQUIERA de los dos campos: si el campo propio
  está vacío hacen fallback al del otro (30-10-2026).
- **Analítica**: Pixel de Meta, GA4 y Clarity vienen VACÍOS de fábrica (los
  IDs del sistema original se retiraron en el clonado); se activan pegando
  el ID en el panel.
- **Sincronización**: desactivada. `sync-top300.yml` es dispatch-only y
  `sync_posgold.py` solo correría si Punto Hogar conecta su propio POSGold
  (definir `POSGOLD_BASE`, secrets y `costos.posgold.enc` propio; el del
  sistema original se retiró del repo por ser material de otro negocio).
  El paso "Verificar que POSGold esta conectado" (30-10-2026) hace que una
  corrida sin POSGold termine en VERDE con aviso (`::warning::`) de lo que
  falta — el catálogo no se toca y la pestaña Actions no queda en rojo.

## Gotchas conocidos

- **`catalogo.js` es una foto estática**: sin cron, ni `stock` ni precios se
  refrescan solos. Cualquier cambio de inventario/precios requiere editar
  el archivo (con cuidado) o conectar POSGold.
- Las fotos ORIGINALES del lightbox (`fulls[]`) siguen en el servidor de
  imágenes del sistema original: la vitrina usa las miniaturas del repo
  (los originales solo se suben bajo demanda, como en el sistema original).
- El servidor de fotos del sistema original tarda ~2 s por archivo: la
  vitrina NUNCA debe cargar originales.
- Los carruseles muestran máximo 32 productos por fila.
- Si el API de GitHub del panel falla (token vencido/permisos), "Publicar
  para todos" avisa: nunca silencia el error.
- Playwright sobre `file://` no registra Resource Timing: para medir
  rendimiento real, probar contra el sitio publicado.
- El Excel de costos del sistema original es un contrato de formato (86
  columnas, encabezados en minúscula); si Punto Hogar algún día exporta el
  suyo de POSGold, debe respetar ese formato.
- GitHub Pages debe activarse a mano (Settings → Pages → main / root) la
  primera vez: el push solo publica el código.
