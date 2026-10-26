# Brief de Branding — Punto Hogar Juguetería

**Versión:** 1.0 — Implementada en la tienda (26-10-2026)
**Marca:** Punto Hogar Juguetería · **Firma:** by Fredy Henao
**Uso principal:** WhatsApp Business, catálogo virtual (esta tienda), redes
sociales y piezas promocionales.

---

## 1. Esencia de la marca

- **Nombre comercial:** Punto Hogar Juguetería
- **Categoría:** Juguetes, juegos y regalos
- **Concepto:** Un punto de encuentro para regalar diversión
- **Eslogan:** *¡Diversión para cada momento!*
- **Personalidad:** alegre, cercana, confiable, moderna y divertida

Punto Hogar Juguetería combina la identidad moderna de Punto Hogar con una
expresión visual más colorida y juguetona: el nombre principal, la forma
circular, los grises tecnológicos y el acento verde lima, con juguetes y
colores vivos que comunican diversión, imaginación y regalos para
diferentes edades.

## 2. Paleta de colores

| Color | HEX | Uso | Token CSS |
|---|---|---|---|
| Gris carbón | `#27313B` | Textos, titulares, confianza | `--text-dark` |
| Gris acero | `#7D858D` | Textos secundarios, bordes | `--text-light` |
| Verde lima | `#A6C83A` | Acento de marca, botones, CTAs | `--primary-color` |
| Blanco | `#FFFFFF` | Fondo principal y descanso visual | `--white` |
| Rojo juguetón | `#F52F35` | Promociones y acentos puntuales | `--secondary-color` |
| Amarillo alegre | `#FFC928` | Estrellas, regalos, destacados | `--accent-color` |
| Azul brillante | `#1689E8` | Elementos lúdicos secundarios | — (confeti) |
| Naranja | `#FF861B` | Acentos cálidos promocionales | `--coral-color` |
| Violeta | `#8B35DB` | Detalles multicolores de campaña | `--purple-color` |

**Proporción orientativa:** 50% blanco · 25% grises · 10% verde lima ·
15% colores juguetones (ilustraciones y promociones).

Los colores viven en `:root` de `index.html`. El confeti del pedido usa
verde lima, rojo, amarillo, azul, naranja y violeta.

## 3. Tipografía

| Rol | Familia | Pesos | Dónde |
|---|---|---|---|
| Titulares y precios destacados | **Poppins** | 600/700/800 (ExtraBold) | `h1-h5`, `.font-display` |
| Descripciones y textos | **Montserrat** | 400-700 (Medium/SemiBold) | `body` |

Se cargan por Google Fonts en el `<head>` (no bloquean el primer render).

Reglas: títulos cortos, sin efectos volumétricos en todos los textos,
buen contraste (gris carbón sobre blanco), verde lima nunca como texto
pequeño sobre blanco.

## 4. Logo

- **Archivo:** `assets/logo-circular.png` (512×512) — oso de peluche,
  cohete, camión, pelota y estrellas dentro del aro gris con línea verde.
- Derivados: `assets/og-compartir.png` (512, para compartir), 
  `assets/apple-touch-icon.png` (180), `assets/favicon-32.png` (32).
- Se usa el logo completo en fondos blancos o claros; proporción
  intacta (no estirar ni recortar el círculo).
- Si se cambia desde el panel, aplicarIdentidad actualiza favicon,
  og:image y encabezado en vivo.

## 5. Tono de comunicación

| Atributo | Cómo se expresa |
|---|---|
| Alegre | Mensajes positivos, lenguaje amable |
| Confiable | Precios claros, condiciones transparentes |
| Cercana | Atención cordial, respuestas sencillas |
| Práctica | Edades recomendadas, uso y características |
| Divertida | Jugar, imaginar, compartir y regalar |

Ejemplo para WhatsApp Business:

> 🧸 **¡Bienvenido a Punto Hogar Juguetería!**
> ¡Diversión para cada momento! 🎁
> Encuentra juguetes y regalos para sorprender, compartir y crear
> recuerdos.
> 🚀 Mira nuestro catálogo y pregúntanos por disponibilidad, precios y
> opciones de entrega.
> **Punto Hogar Juguetería — by Fredy Henao**

Afirmaciones como "apto para todas las edades", "educativo" o "seguro"
solo cuando estén respaldadas por la información del producto.

## 6. Canales y contacto

- **WhatsApp (pedidos e información):** +57 314 724 7260 — único canal
  de cierre del checkout; configurable desde el panel.
- **Instagram / TikTok:** `@puntohogar` (placeholders configurables
  desde el panel).
- **Tienda física:** no hay — la atención es por WhatsApp con envíos a
  domicilio. Si algún día se configura `direccion` en el panel, el sitio
  vuelve a mostrar tienda física y mapas automáticamente.
- **Sitio:** https://puntohogarjugueteria.github.io

## 7. Resumen ejecutivo

| Elemento | Definición |
|---|---|
| Marca | Punto Hogar Juguetería |
| Firma | by Fredy Henao |
| Sector | Juguetes, juegos y regalos |
| Concepto | Un punto de encuentro para regalar diversión |
| Eslogan | ¡Diversión para cada momento! |
| Colores base | Gris carbón, gris acero, verde lima y blanco |
| Colores complementarios | Rojo, amarillo, azul, naranja y violeta |
| Tipografía principal | Poppins ExtraBold |
| Tipografía secundaria | Montserrat Medium / SemiBold |
| Estilo | Moderno, circular, alegre y lúdico |
| Canal prioritario | WhatsApp Business y catálogo digital |
