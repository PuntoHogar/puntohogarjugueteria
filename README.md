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
POSGold y llave de cifrado), `*.xlsx` (exportes con costos), `qa_e2e.py` (suite QA),
`reportes/` (CSVs con costos y márgenes), scripts de la persona de confianza.

## El catálogo automático

En cada corrida, `sync_posgold.py`:

1. Genera un JWT fresco de la API de POSGold (`/apiGold`).
2. Descarga el inventario de la bodega 2 y lo cruza con los costos del Excel cifrado.
3. Aplica los **filtros duros de la tienda**: activo + existencias + foto real +
   categoría vendible + costo conocido + rentabilidad positiva.
4. Ordena por margen y resuelve cada producto:
   - **Slug**: el conocido del cache o, para productos nuevos, el derivado del
     nombre en POSGold.
   - **Fotos**: descarga las de POSGold (`Files/Images/`), genera UNA miniatura
     WebP por foto (el servidor de POSGold tarda ~2 s por foto: la vitrina usa
     las miniaturas del repo y el lightbox sube al original bajo demanda).
5. Regenera `catalogo.js` (con el top de utilidad para "Los imperdibles") y
   publica: GitHub Pages republica solo.

Los pedidos no tienen backend: el checkout arma el mensaje de WhatsApp con la
referencia de cada producto y su enlace directo a la ficha en esta misma tienda
(`?producto={slug}`), que al abrirse resalta el juguete con su panel de cantidades.

## Características de la tienda

- Vitrina con grid paginado, carruseles por categoría y lightbox tipo Amazon.
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

# sincronización de prueba (no toca catalogo.js ni publica)
python sync_posgold.py --dry-run

# regenerar TODAS las miniaturas desde POSGold (migraciones / auditorías)
python sync_posgold.py --verificar-todas

# verificar sintaxis JS del index (bloques <script> sin src)
node -e "const h=require('fs').readFileSync('index.html','utf8');const re=/<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>([\s\S]*?)<\/script>/gi;let m;while((m=re.exec(h))!==null){if(m[1].trim())new Function(m[1]);}console.log('OK')"
```

Publicar = `git push origin main` (GitHub Pages reconstruye en ~1 minuto).
