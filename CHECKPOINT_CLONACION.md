# Checkpoint de clonación — 26-10-2026

Clonación completa del sistema de jugueteriataiwan
(`github.com/jugueteriataiwanoficial/jugueteriataiwan`) hacia este repo
(`github.com/PuntoHogar/puntohogarjugueteria`), siguiendo el mismo patrón
que se aplicó con **Lunaria**: sistema heredado + rebranding completo al
brief oficial de la marca.

## Cambios aplicados

### Identidad (brief de branding)

| Qué | Antes (Taiwan) | Ahora (Punto Hogar) |
|---|---|---|
| Nombre | Juguetería Taiwan | **Punto Hogar Juguetería — by Fredy Henao** |
| Eslogan | — | ¡Diversión para cada momento! (héroe, metas, compartir) |
| Colores | Cian `#00bcd4` / rosa `#e91e63` | Verde lima `#A6C83A`, gris carbón `#27313B`, gris acero `#7D858D` + rojo/amarillo/azul/naranja/violeta |
| Tipografías | Fredoka + Outfit | **Poppins** (titulares) + **Montserrat** (cuerpo) |
| Logo | PNG externo (jugueteriataiwan.com) | `assets/logo-circular.png` (nuevo) + favicon/og/apple-touch regenerados |
| theme-color | `#00bcd4` | `#A6C83A` |

### Contacto y operation

| Qué | Antes | Ahora |
|---|---|---|
| WhatsApp pedidos | 573106988465 | **573137203136** (+57 313 720 31 36) |
| WhatsApp contacto | 573138786096 | **573137203136** (mismo número) |
| Dirección física | CC Taiwan, Local 27 | **Vacía** (sin tienda física) |
| Instagram / TikTok | @jugueteriataiwan / @jugueteria.taiwan | @puntohogar / @puntohogar (placeholders) |
| Retiro en tienda | Sí (checkout, FAQ, mapas) | **Eliminado**; solo entrega a domicilio |
| Enlaces de ficha (catalogo.js) | saldosjugueteriataiwan.com/?producto= | **puntohogarjugueteria.github.io/?producto=** (1.938 URLs) |
| SYNC_API / REPO_API (panel) | jugueteriataiwanoficial/… | **PuntoHogar/puntohogarjugueteria** |
| Pixel de Meta | 3678555472322858 (activo) | **Retirado** (vacío = apagado; se pega el propio ID desde el panel) |
| cantidadProductos | +22.000 | **+1.900** (1.938 productos en la foto del catálogo) |

### Precios (regla de la tienda)

| Parámetro | Valor | Nota |
|---|---|---|
| margenGlobal | **0.30** | 30% de ganancia sobre el **Precio 2** del sistema (base de catalogo.js) |
| redondeo | 0 | Precio exacto: Precio 2 × 1.3 (ej. $15.000 → $19.500) |
| multiplicadorBase | 1 | Sin ajuste adicional |
| margenesPorCategoria | {} | Ninguna categoría con margen propio |
| preciosPersonalizados | {} | Ningún precio fijo |

Configurado en **fábrica** (`PRECIOS_DEFECTO` en index.html) y en lo
**publicado** (`data/configuracion.js`, versión 1792710000000) — lo
publicado manda sobre la fábrica, por eso ambos deben llevar 0.30.
Cambiable en cualquier momento desde el panel ("¿Cuánto quieres ganar?")
sin tocar código.

El tachado sigue siendo honesto: solo si el sistema trae un Precio 1 real
por encima (hoy ningún producto lo trae → 0 badges de descuento).

### Infraestructura

| Qué | Decisión | Motivo |
|---|---|---|
| CNAME (saldosjugueteriataiwan.com) | **Eliminado** | Dominio del sistema original; la tienda sirve de github.io |
| costos.posgold.enc | **Eliminado** | Material cifrado de costos de OTRO negocio; sin POSGold es inútil y no debe vivir aquí |
| Workflow sync-top300.yml | **Dispatch-only** (sin schedule) | Punto Hogar no tiene POSGold: el cron fallaría 4×/día sin secrets |
| sync_posgold.py | Conservado | Inerte hasta que exista POSGold propio (DETAL_URL por defecto ya apunta a github.io) |
| catalogo.js | Foto estática (1.938 productos) | Sin cron no se regenera; los enlaces ya apuntan al dominio propio |

## Verificación (26-10-2026)

| Prueba | Resultado |
|---|---|
| Sintaxis JS de index.html (node) | OK |
| Sintaxis catalogo.js y configuracion.js (node) | OK |
| `qa_carrito.py` | **38/38 OK** (regla de precios actualizada a Precio 2 +30%) |
| Productos fuera de Precio 2 × 1.3 | **0 de 1.552** visibles (desvío máximo $0) |
| Tachados inventados | **0** |
| Enlace del pedido WhatsApp | wa.me/573137203136 con precios +30% correctos |

Precios de muestra verificados en vivo:

| Producto | Precio 2 | Venta (+30%) |
|---|---|---|
| Pista neón carro (héroe) | $100.000 | $130.000 |
| Mesa fútbol de madera | $240.000 | $312.000 |
| Burbujero burbuja gun | $24.000 | $31.200 |
| Más barato (bolsa carro) | $200 | $260 |
| Más caro (caja armable Harry) | $500.000 | $650.000 |

## Pendientes manuales

1. **Activar GitHub Pages**: Settings → Pages → Deploy from branch →
   `main` / `(root)`. Sitio: https://puntohogarjugueteria.github.io
2. **Panel de administración**: crear fine-grained token sobre
   `PuntoHogar/puntohogarjugueteria` (Actions y Contents Read+write),
   cargarlo en el panel y usar "Publicar para todos". Clave de fábrica:
   `Walter123*` (cambiable desde el panel).
3. **Analítica**: pegar los IDs propios de Pixel de Meta / GA4 / Clarity
   en el panel (hoy todo viene apagado).
4. **Futuro POSGold** (si algún día se contrata): definir `POSGOLD_BASE`
   en el workflow, agregar secrets (POSGOLD_TOKEN_USER,
   POSGOLD_TOKEN_PASS, COSTOS_KEY), subir el `costos.posgold.enc` propio
   y reactivar el `schedule:`.
5. **Dominio propio** (opcional): al comprarlo, agregar el CNAME y ajustar
   `sitioWeb`, `canonical`, `og:url` y las URLs de `catalogo.js`.
