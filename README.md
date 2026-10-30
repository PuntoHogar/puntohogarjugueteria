# Punto Hogar Juguetería — Tienda al detal

Tienda en línea de **Punto Hogar Juguetería — by Fredy Henao**: juguetes,
juegos y regalos para sorprender, compartir y crear recuerdos. Al detal con
envíos a toda Colombia y atención por WhatsApp.
Se sirve por GitHub Pages desde este repositorio:
**[puntohogar.github.io/puntohogarjugueteria](https://puntohogar.github.io/puntohogarjugueteria/)**

Todo el frente vive en **`index.html`** (HTML + CSS + JS en un solo archivo).
El catálogo (`catalogo.js`, 1.938 productos) es una **foto estática del
sistema POSGold original**: Punto Hogar aún no tiene POSGold, así que el cron
de sincronización está desactivado (ver "El catálogo", abajo).

---

## Identidad (Brief de Branding)

| Elemento | Definición |
|---|---|
| Marca | Punto Hogar Juguetería |
| Firma | by Fredy Henao |
| Concepto | Un punto de encuentro para regalar diversión |
| Eslogan | ¡Diversión para cada momento! |
| Colores base | Gris carbón `#27313B`, gris acero `#7D858D`, verde lima `#A6C83A`, blanco |
| Colores juguetones | Rojo `#F52F35`, amarillo `#FFC928`, azul `#1689E8`, naranja `#FF861B`, violeta `#8B35DB` |
| Tipografía principal | Poppins ExtraBold (titulares, precios destacados) |
| Tipografía secundaria | Montserrat Medium/SemiBold (descripciones y textos) |
| Logo | Circular (`assets/logo-circular.png`), oso, cohete, camión, pelota y estrellas |
| WhatsApp | **+57 314 724 7260** (pedidos e información) |
| Tienda física | No: atención por WhatsApp y envíos a domicilio |

Los tokens viven en `:root` de `index.html` (`--primary-color` = verde lima,
`--secondary-color` = rojo juguetón, etc.).

## Arquitectura

| Archivo / carpeta | Qué es |
|---|---|
| `index.html` | La tienda completa: vitrina, carruseles, lightbox, carrito, checkout por WhatsApp y panel de administración |
| `catalogo.js` | Catálogo publicado. En el sistema original lo regenera el cron; aquí es una foto estática (los enlaces de ficha apuntan a `puntohogar.github.io/puntohogarjugueteria`) |
| `data/configuracion.js` | Configuración publicada desde el panel: la que ven **todos** los visitantes. La mantiene el botón "Publicar para todos" vía la API de GitHub — nadie la edita a mano |
| `assets/fotos/` | Miniaturas WebP (~25 KB) de cada foto de producto, servidas por el CDN de GitHub Pages |
| `assets/logo-circular.png` | Logo circular de la marca (512×512); `og-compartir.png`, `favicon-32.png` y `apple-touch-icon.png` derivan del mismo |
| `data/mapa_imagenes.json` | Cache de la relación SKU ↔ slug ↔ foto |
| `sync_posgold.py` | Sincronizador: POSGold → filtros de la tienda → miniaturas → `catalogo.js` (inactivo mientras Punto Hogar no tenga POSGold) |
| `.github/workflows/sync-top300.yml` | Cron en GitHub Actions — **desactivado** (solo `workflow_dispatch`) |

## Precios: 30% de ganancia sobre el Precio 2

El precio que ve el cliente se calcula en `precioDetal()`:

```
precio detal = precio base (Precio 2 del sistema) × multiplicador × (1 + margen)
```

**Punto Hogar Juguetería vende con 30% de ganancia global sobre el Precio 2**
(decisión de la tienda, 26-10-2026): `margenGlobal: 0.30`, `redondeo: 0`
(precio exacto, sin redondeo). Ejemplo: Precio 2 de $15.000 → se vende a
$19.500. La fábrica (`PRECIOS_DEFECTO` en `index.html`) y lo publicado
(`data/configuracion.js`) llevan los mismos valores (lo publicado manda).
El margen se puede cambiar en cualquier momento desde el panel de
administración ("¿Cuánto quieres ganar?").

El tachado (`comparePrice`) es honesto: solo aparece si el sistema trae un
Precio 1 real por encima del precio de venta. No se inventan rebajas.

## El catálogo (foto estática, sin POSGold)

Punto Hogar Juguetería **no tiene POSGold** (26-10-2026). El catálogo
publicado (1.938 productos, todos activos y con existencias al momento del
clonado) es una foto estática del sistema original:

- El **cron está desactivado**: el workflow solo corre a mano
  (`workflow_dispatch`). No lo actives hasta que Punto Hogar conecte su
  propio POSGold.
- Las **fotos originales del lightbox** siguen servidas desde el servidor de
  imágenes del sistema original (`fulls[]` de `catalogo.js`); la vitrina usa
  las miniaturas WebP de este repo.
- Cuando Punto Hogar tenga POSGold: definir `POSGOLD_BASE` en
  `sync-top300.yml`, agregar los secrets (`POSGOLD_TOKEN_USER`,
  `POSGOLD_TOKEN_PASS`, `COSTOS_KEY`), subir su propio `costos.posgold.enc`
  y reactivar el `schedule:`.

Los pedidos no tienen backend: el checkout arma el mensaje de WhatsApp con
la referencia de cada producto y su enlace directo a la ficha en esta misma
tienda (`?producto={slug}`), al **+57 314 724 7260**.

## Características de la tienda

- Vitrina con grid paginado, carruseles por categoría y lightbox tipo Amazon.
- **+30% de ganancia global sobre el Precio 2** del sistema, exacto.
- Reglas de la tienda activables desde el panel, reversibles al instante:
  *Un solo ejemplar de cada juguete* (activa) y *Ocultar juguetes agotados*
  (opción disponible, inactiva).
- Efecto de compra: vuelo al carrito + confeti al enviar el pedido (sin
  librerías, respeta `prefers-reduced-motion`).
- Checkout por WhatsApp estilo COD en 5 fases (pedido → datos → entrega → pago → notas).
- Entrega **a domicilio** (sin retiro en tienda: Punto Hogar no tiene local).
- Pago a crédito en cuotas (Addi / Sistecrédito) con simulador — configurable
  desde el panel.
- Panel de administración (enlace "Administración" del pie, `?admin=1` o
  Ctrl+Shift+A): precios y márgenes, reglas, tendencia, favoritos, ocultar
  categorías y productos, temporada (Navidad), analítica (Pixel de Meta,
  GA4, Clarity) y publicación para todos los visitantes.
- Publicación autónoma: el botón "Publicar para todos" del panel sube la
  configuración al proyecto de GitHub (API de Contents) y todos los
  visitantes la ven en ~1 minuto.

## Panel de administración

Se abre con el enlace "Administración" del pie, `?admin=1` o Ctrl+Shift+A
(clave de `TIENDA_DEFECTO.claveAdmin`, de fábrica `Walter123*`).

- **Una sola vez**: crear un fine-grained token sobre
  `PuntoHogar/puntohogarjugueteria` (permisos Actions:Read+write y
  Contents:Read+write), cargarlo en el panel y usar "Publicar para todos".
- **Guardar en MI computador** — previsualiza solo en ese navegador.
- **Publicar para todos** — sube la configuración al proyecto y la ven todos.
- **Sincronizar ahora** — lanza la corrida del catálogo al instante (solo
  aplica cuando Punto Hogar tenga POSGold y secrets configurados).

## Seguridad

- El repositorio es **público**: las credenciales viven en `.env` (local) y
  en los *secrets* de GitHub Actions. **Nunca** se suben tokens, llaves ni
  costos en claro.
- El panel de administración es una barrera de conveniencia del lado del
  cliente, no seguridad real: quien tenga acceso al archivo puede ver su clave.

## Desarrollo local

```bash
# suite del carrito (38/38): identidad de los productos agregados,
# aritmetica exacta, mensaje de WhatsApp, vuelo al carrito y confeti
python qa_carrito.py

# verificar sintaxis JS del index (bloques <script> sin src)
node -e "const h=require('fs').readFileSync('index.html','utf8');const re=/<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>([\s\S]*?)<\/script>/gi;let m;while((m=re.exec(h))!==null){if(m[1].trim())new Function(m[1]);}console.log('OK')"
```

Publicar = `git push origin main` (GitHub Pages reconstruye en ~1 minuto).

## Pendientes manuales (una sola vez en GitHub)

1. **Activar GitHub Pages**: Settings → Pages → Deploy from branch → `main` /
   `/ (root)`. Como el repo vive en la organización `PuntoHogar`, la URL del
   sitio es proyecto: **https://puntohogar.github.io/puntohogarjugueteria/**
   (el subdominio `puntohogarjugueteria.github.io` solo existiría en una
   organización con ese mismo nombre; si se quiere, mover el repo a una
   cuenta/organización con ese nombre o crear un dominio propio con CNAME).
2. Si se quiere dominio propio, crear el CNAME y ajustar `sitioWeb`,
   `canonical`, `og:url` y las URLs de `catalogo.js`.
3. Configurar los IDs de analítica (Pixel de Meta, GA4, Clarity) desde el
   panel — hoy vienen vacíos.
