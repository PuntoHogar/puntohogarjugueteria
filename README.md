# Juguetería Taiwan — Tienda al detal

Tienda en línea de **Juguetería Taiwan** (Cali, Colombia): juguetería, piñatería,
didácticos, cubos Rubik, cacharros y más, al detal con envíos a toda Colombia.
Se sirve por GitHub Pages desde este repositorio:
**[saldosjugueteriataiwan.com](https://saldosjugueteriataiwan.com/)**

Todo el frente vive en **`index.html`** (HTML + CSS + JS en un solo archivo) y el
catálogo se sincroniza solo, 4 veces al día, desde el sistema POSGold de la tienda.

---

## Arquitectura

| Archivo / carpeta | Qué es |
|---|---|
| `index.html` | La tienda completa: vitrina, carruseles, lightbox, carrito, checkout por WhatsApp y panel de administración |
| `catalogo.js` | Catálogo generado automáticamente (1.911 productos). **No se edita a mano**: el cron lo regenera en cada corrida |
| `data/configuracion.js` | Configuración publicada desde el panel: la que ven **todos** los visitantes. La mantiene el botón "Publicar para todos" del panel vía la API de GitHub — nadie la edita a mano |
| `assets/fotos/` | Miniaturas WebP (~25 KB) de cada foto de producto, generadas por el cron desde POSGold y servidas por el CDN de GitHub Pages |
| `data/mapa_imagenes.json` | Cache de la relación SKU ↔ slug ↔ foto |
| `sync_posgold.py` | Sincronizador: POSGold → filtros de la tienda → miniaturas → `catalogo.js` |
| `.github/workflows/sync-top300.yml` | Cron en GitHub Actions (07:15, 08:15, 19:15 y 20:15, hora Colombia) |
| `costos.posgold.enc` | Excel de costos de POSGold **cifrado** (AES-256-CBC + PBKDF2) — el repo es público y los costos jamás viajan en claro |
| `assets/` (favicon, og) | Iconos de la marca |

Archivos **locales** (excluidos del repo por `.gitignore`): `.env` (credenciales
POSGold y llave de cifrado), `*.xlsx` (exportes con costos), `qa_e2e.py` (suite QA
completa; contiene la clave del panel en su escenario de admin),
`reportes/` (CSVs con costos y márgenes) y `generar_enlace_config.py` (arma el
enlace de configuración de un solo toque para cargar llave y tokens en el
navegador de la administración). `qa_carrito.py` sí vive en el repo: no toca
el panel y no lleva secretos.

## El catálogo automático

En cada corrida, `sync_posgold.py`:

1. Genera un JWT fresco de la API de POSGold (`/apiGold`).
2. Descarga el inventario de la bodega 2 y lo cruza con los costos del Excel cifrado.
   El precio detal sale del **Precio 2** del sistema; el tachado (`comparePrice`),
   del Precio 1 cuando queda por encima.
3. Aplica los **filtros duros de la tienda**: activo + existencias + foto real +
   categoría vendible + costo conocido + rentabilidad positiva.
4. Ordena por margen y resuelve cada producto:
   - **Slug**: el conocido del cache o, para productos nuevos, el derivado del
     nombre en POSGold.
   - **Fotos**: descarga las de POSGold (`Files/Images/`), genera UNA miniatura
     WebP por foto (el servidor de POSGold tarda ~2 s por foto: la vitrina usa
     las miniaturas del repo y el lightbox sube al original bajo demanda).
5. Regenera `catalogo.js` (con el top de utilidad para "Los imperdibles") y
   publica: GitHub Pages republica solo. **Conciliación dura con POSGold**: antes
   y después de generar verifica que el catálogo quede 100 % con productos
   activos y con existencias; si algo no cuadra, aborta sin tocar lo publicado.
6. Deja `reportes/novedades_*.xlsx`: el Excel de la tienda con todo lo que NO
   publica y por qué (inactivos, agotados, duplicados, sin precio, sin foto, sin
   costo, rentabilidad negativa), marcando los que estaban publicados. El cron lo
   sube como artefacto descargable en la pestaña Actions.

Los pedidos no tienen backend: el checkout arma el mensaje de WhatsApp con la
referencia de cada producto y su enlace directo a la ficha en esta misma tienda
(`?producto={slug}`), que al abrirse resalta el juguete con su panel de cantidades.

### Productos nuevos: qué entra solo y qué necesita la tienda

Un juguete recién creado en POSGold entra **solo** en la próxima corrida si
cumple los filtros: el cron le genera automáticamente la miniatura WebP, el
slug, la categoría web, el precio con margen y redondeo a $1.000, el tachado
y el enlace de ficha. Lo único que el cron no puede inventar es el **costo**:
un producto sin costo en el Excel queda oculto con el motivo
"sin costo en Excel" hasta que alguien refresque los costos (abajo).

La vitrina no tiene tope práctico de productos: el grid pagina de 60 en 60
con scroll infinito y los carruseles muestran máximo 32 por categoría, así
que el inventario puede crecer sin congelar el navegador. Lo que sí crece es
el peso: `catalogo.js` (~0,5 KB por producto) y las miniaturas (~25 KB por
foto) viven en el repo.

### Costos: por qué van por Excel y no por API

El API de POSGold **no expone los costos** (verificado contra
`GetProduct_V6`: 34 campos y ninguno de costos; su login web tiene captcha),
y este repo es público: el Excel con costos y márgenes nunca puede subir en
claro. Por eso el flujo es: exportar → cifrar → commitear cifrado
(`costos.posgold.enc`, solo 4 columnas, ~115 KB).

El formato es **el que POSGold genera tal cual** (una hoja "Productos",
86 columnas, 6.000+ filas, encabezados en minúscula: `productoid`, `costo`,
`costopromedio`, `costoultimo`): exportar y subir, sin prepararlo. Y es a
prueba de error:

- El **panel** valida el archivo antes de cifrarlo: rechaza uno incompleto,
  sin columnas de costo o con menos de 1.000 filas (export filtrado).
- `actualizar_costos.py` verifica el roundtrip SHA-256 antes de commitear.
- El **cron** lee por nombre de columna (el orden y las otras 82 columnas no
  importan). Si POSGold renombrara un encabezado en el futuro, el script
  aborta **antes de tocar `catalogo.js`**: la tienda publicada queda
  intacta con los costos anteriores hasta corregir. Un producto sin costo
  válido queda oculto, nunca rompe la vitrina.

La frecuencia correcta es semanal o mensual: los costos solo cambian cuando
compran inventario; stock, precios y fotos se refrescan solos en cada
corrida. El panel avisa "⚠️ Costos desactualizados" cuando el archivo pasa
de 15 días. Si POSGold algún día agrega el campo de costo al API, el
workflow documenta cómo retirar la dependencia del Excel.

## Características de la tienda

- Vitrina con grid paginado, carruseles por categoría y lightbox tipo Amazon.
- Precios calculados con margen y **redondeados a múltiplos de $1.000**
  (1000, 2000, 3000…): configurable desde el panel ("Sin redondeo" a
  "1.000").
- Efecto de compra: al agregar al carrito, la foto del juguete vuela hasta
  el icono y el contador rebota; al enviar el pedido, un confeti breve
  celebra el cierre (sin librerías: reusa la miniatura en cache, respeta
  `prefers-reduced-motion` y se omite si el checkout ya está abierto).
- Checkout por WhatsApp estilo COD en 5 fases (pedido → datos → entrega → pago → notas).
- Pago a crédito en cuotas (Addi / Sistecrédito) con simulador en tarjetas,
  carrito y checkout — configurable desde el panel.
- Panel de administración (enlace "Administración" del pie, `?admin=1` o
  Ctrl+Shift+A): precios y márgenes, producto en tendencia, favoritos,
  ocultar categorías y productos, temporada (Navidad), analítica
  (Pixel de Meta, GA4, Clarity) y actualización de costos cifrando el
  Excel del navegador.
- **Publicación autónoma**: el botón "Publicar para todos" del panel sube
  la configuración vigente al proyecto de GitHub (API de Contents, el
  mismo token de los costos) y todos los visitantes la ven en ~1 minuto
  — sin editar archivos ni pedirle nada a nadie. "Guardar en MI
  computador" previsualiza solo en ese navegador; lo publicado manda
  sobre la fábrica y sobre lo guardado cuando su versión es más nueva.
  La clave del panel nunca se publica.
- Ocultamiento reversible de categorías y productos individuales.
- Analítica con píxeles activables por ID, sin código adicional.

## Panel de administración (el día a día de la tienda)

Se abre con el enlace "Administración" del pie, `?admin=1` o Ctrl+Shift+A
(clave de `TIENDA_DEFECTO.claveAdmin`).

- **Una sola vez**: la persona de confianza corre `python generar_enlace_config.py`
  y envía por WhatsApp el enlace de configuración; al abrirlo, la llave de cifrado
  y los tokens de GitHub quedan cargados en ese navegador para siempre (nunca van
  escritos en el archivo de la página: el repo es público).
- **Guardar en MI computador** — previsualiza solo en ese navegador.
- **Publicar para todos** — sube la configuración al proyecto (API de GitHub) y
  todos los visitantes la ven en ~1 minuto. Es el botón normal: nadie edita
  archivos ni publica por ella.
- **Actualizar costos** — exporta el Excel de PRODUCTOS de POSGold (todo el
  inventario, sin filtros) y súbelo en el panel: se cifra en el navegador y el
  cron lo aplica al ranking.
- **Sincronizar ahora** — lanza la corrida del catálogo al instante (o espera al
  cron de las 07:15, 08:15, 19:15 y 20:15).

Si una corrida del cron termina con "AVISO git push" (el panel publicó algo a
media corrida), no es un error: la siguiente corrida lo publica todo.

## Seguridad

- El repositorio es **público**: las credenciales viven en `.env` (local) y en
  los *secrets* de GitHub Actions. **Nunca** se suben tokens, llaves ni costos en claro.
- Los costos viajan cifrados (`costos.posgold.enc`) y la llave solo existe en
  `.env` y en el secret `COSTOS_KEY`.
- El panel de administración es una barrera de conveniencia del lado del
  cliente, no seguridad real: quien tenga acceso al archivo puede ver su clave.

## Desarrollo local

```bash
# suite QA completa (Playwright): 42 pruebas en Chrome y WebKit/Safari,
# escritorio y móvil — debe pasar 42/42 antes de publicar
python qa_e2e.py

# suite del carrito (38/38): identidad de los productos agregados,
# aritmetica exacta (totales, cantidades, fusion de lineas, persistencia),
# mensaje de WhatsApp, vuelo al carrito y confeti — sin secretos, vive en el repo
python qa_carrito.py

# sincronización de prueba (no toca catalogo.js ni publica)
python sync_posgold.py --dry-run

# regenerar TODAS las miniaturas desde POSGold (migraciones / auditorías)
python sync_posgold.py --verificar-todas

# enlace de configuración de un solo toque (llave + tokens para un navegador)
python generar_enlace_config.py

# verificar sintaxis JS del index (bloques <script> sin src)
node -e "const h=require('fs').readFileSync('index.html','utf8');const re=/<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>([\s\S]*?)<\/script>/gi;let m;while((m=re.exec(h))!==null){if(m[1].trim())new Function(m[1]);}console.log('OK')"
```

Publicar = `git push origin main` (GitHub Pages reconstruye en ~1 minuto).

## Checkpoint — octubre de 2026

Estado del proyecto tras la última tanda de mejoras (20 de octubre de 2026):

| Área | Estado |
|---|---|
| Precios | Redondeados a múltiplos de **$1.000** (fábrica en `PRECIOS_DEFECTO` y publicado en `data/configuracion.js`, sincronizados) |
| Efecto de compra | **Vuelo al carrito** + pop del badge al agregar; **confeti** al enviar el pedido — sin librerías, respetan `prefers-reduced-motion` |
| QA | `qa_e2e.py` **42/42** y `qa_carrito.py` **38/38** (verde antes de publicar) |
| Costos | Documentado: el API de POSGold no trae costos (verificado); el Excel de PRODUCTOS es el contrato de formato y el pipeline falla seguro en cada etapa |
| Catálogo | 1.911 productos publicados; los nuevos de POSGold entran solos en la próxima corrida si cumplen los filtros (incluido costo en el Excel) |
| Panel | Publica configuración y costos solo (API de GitHub); nada se edita a mano |
| Dopamina descartada | Urgencia artificial y metas falsas: probadas/evaluadas y rechazadas (la urgencia ya costó pedidos una vez) |
