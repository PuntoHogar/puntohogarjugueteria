# -*- coding: utf-8 -*-
"""QA del CARRITO: identidad de los productos agregados, aritmetica exacta
(totales, cantidades, fusion de lineas, persistencia) y operacion completa
hasta el mensaje de WhatsApp. Complementa a qa_e2e.py (que sigue siendo la
suite general 42/42): esta suite se concentra en que NADA se sume mal."""
import asyncio
import re
import urllib.parse
from playwright.async_api import async_playwright

URL = "file:///C:/Users/User/JUGUETERIA_TAIWAN/index.html"
ERRORES = []
RESULTADOS = []


def ok(fase, etiqueta, cond, extra=""):
    estado = "OK " if cond else "FAIL"
    RESULTADOS.append(f"F{fase}: [{estado}] {etiqueta}" + (f" ({extra})" if extra else ""))
    print(f"  [{estado}] {etiqueta}" + (f" ({extra})" if extra else ""))


def pesos(texto):
    """'$69.000' -> 69000 (cop() usa es-CO: punto de miles)."""
    digitos = re.sub(r"[^0-9]", "", str(texto))
    return int(digitos) if digitos else 0


async def cerrar_checkout(page):
    await page.evaluate("() => { try { closeOrderForm(); } catch (e) {} }")
    await page.wait_for_timeout(200)


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: ERRORES.append("F0: " + str(e)[:180]))

        # localStorage limpio para arrancar de cero como cliente nuevo
        await page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        await page.evaluate("() => localStorage.clear()")
        await page.reload(wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(3500)

        # ============ FASE 1: IDENTIDAD DE LOS PRODUCTOS ============
        print("== FASE 1: EL CARRITO AGREGA LOS PRODUCTOS CORRECTOS ==")
        base = await page.evaluate("""() => ({
            productos: products.length,
            carrito: cart.length,
        })""")
        ok(1, "carrito inicia vacio", base["carrito"] == 0, str(base))

        # elegir: el mas barato, el mas caro y uno medio del catalogo visible
        eleccion = await page.evaluate("""() => {
            const orden = products.slice().sort((a, b) => a.price - b.price);
            const barato = orden[0];
            const caro = orden[orden.length - 1];
            const medio = orden[Math.floor(orden.length / 2)];
            return {
                barato: { id: barato.id, name: barato.name, sku: barato.sku || '',
                          price: barato.price, opt: flattenSizeOptions(barato)[0].price },
                medio: { id: medio.id, name: medio.name, price: medio.price,
                         opt: flattenSizeOptions(medio)[0].price },
                caro: { id: caro.id, name: caro.name, price: caro.price,
                        opt: flattenSizeOptions(caro)[0].price },
            };
        }""")

        # 1 unidad del mas barato
        await page.evaluate("(id) => quickAddDefault(id)", eleccion["barato"]["id"])
        await page.wait_for_timeout(500)
        await cerrar_checkout(page)
        l1 = await page.evaluate("() => cart")
        b = eleccion["barato"]
        ok(1, "linea con el id del producto correcto",
           len(l1) == 1 and l1[0]["productId"] == b["id"], l1[0]["productId"] if l1 else "vacio")
        ok(1, "nombre y SKU exactos del catalogo",
           len(l1) == 1 and l1[0]["name"] == b["name"] and l1[0]["sku"] == b["sku"],
           (l1[0]["name"] if l1 else "")[:40])
        ok(1, "precio de linea = precio detal vigente (exacto)",
           len(l1) == 1 and l1[0]["price"] == b["opt"],
           str(l1[0]["price"] if l1 else 0))
        ok(1, "talla y cantidad correctas (Unidad x 1)",
           len(l1) == 1 and l1[0]["sizeLabel"] == "Unidad" and l1[0]["quantity"] == 1,
           f"{l1[0]['sizeLabel']} x{l1[0]['quantity']}" if l1 else "vacio")

        badge1 = await page.evaluate(
            "() => [document.getElementById('cartCount'), document.getElementById('floatingCartCount')]"
            ".map(e => e ? Number(e.textContent) : null)")
        ok(1, "badge del carrito = 1 en ambos contadores",
           badge1[0] == 1 and badge1[1] == 1, str(badge1))

        # agregar el mas caro: dos lineas, identidades independientes
        await page.evaluate("(id) => quickAddDefault(id)", eleccion["caro"]["id"])
        await page.wait_for_timeout(500)
        await cerrar_checkout(page)
        l2 = await page.evaluate(
            "() => cart.map(i => ({ id: i.productId, name: i.name, qty: i.quantity, price: i.price }))")
        ok(1, "dos productos distintos = dos lineas distintas",
           len(l2) == 2 and l2[0]["id"] != l2[1]["id"], str(len(l2)))
        ok(1, "cada linea conserva SU precio (barato != caro)",
           l2[0]["price"] != l2[1]["price"]
           and l2[0]["price"] == b["opt"] and l2[1]["price"] == eleccion["caro"]["opt"],
           f"{l2[0]['price']} / {l2[1]['price']}")

        # mismo producto otra vez: fusion, no duplicado
        await page.evaluate("(id) => quickAddDefault(id)", eleccion["barato"]["id"])
        await page.wait_for_timeout(500)
        await cerrar_checkout(page)
        l3 = await page.evaluate(
            "() => ({ lineas: cart.length, barato: cart.find(i => i.productId === '%s') })" % eleccion["barato"]["id"])
        ok(1, "re-agregar el mismo producto FUSIONA la linea (no la duplica)",
           l3["lineas"] == 2 and l3["barato"]["quantity"] == 2,
           f"{l3['lineas']} lineas, qty={l3['barato']['quantity'] if l3['barato'] else 0}")

        # el precio que ve el cliente en la TARJETA es el mismo que entra al carrito
        tarjeta = await page.evaluate("""() => {
            const card = document.querySelector('#productsGrid .product-card');
            const id = card ? card.id.replace('product-', '') : null;
            const priceEl = card ? card.querySelector('.current-price') : null;
            return { id: id, texto: priceEl ? priceEl.textContent.trim() : '' };
        }""")
        if tarjeta["id"]:
            await page.evaluate("(id) => quickAddDefault(id)", tarjeta["id"])
            await page.wait_for_timeout(500)
            await cerrar_checkout(page)
            linea_tarjeta = await page.evaluate(
                "(id) => cart.find(i => i.productId === id)", tarjeta["id"])
            ok(1, "precio de la TARJETA = precio de la linea del carrito",
               linea_tarjeta and pesos(tarjeta["texto"]) == linea_tarjeta["price"],
               f"tarjeta {tarjeta['texto']} vs carrito {linea_tarjeta['price'] if linea_tarjeta else 0}")
        else:
            ok(1, "precio de la TARJETA = precio de la linea del carrito", False, "sin tarjetas en el grid")

        # ============ FASE 2: MATEMATICAS DEL CARRITO ============
        print("== FASE 2: LA CUENTA ES EXACTA ==")
        await page.evaluate("() => vaciarCarrito()")
        await page.wait_for_timeout(300)

        # carrito de precision: barato x2, medio x3, caro x1
        plan = [(eleccion["barato"], 2), (eleccion["medio"], 3), (eleccion["caro"], 1)]
        for prod, qty in plan:
            for _ in range(qty):
                await page.evaluate("(id) => quickAddDefault(id)", prod["id"])
                await page.wait_for_timeout(120)
            await cerrar_checkout(page)
        await page.evaluate("() => toggleCart()")
        await page.wait_for_timeout(600)

        esperado = sum(p["opt"] * q for p, q in plan)
        unidades = sum(q for _, q in plan)

        m1 = await page.evaluate("""() => {
            const s = getCartSummary();
            const manual = cart.reduce((acc, i) => acc + i.price * i.quantity, 0);
            return { total: s.total, count: s.count, manual: manual,
                     dom: (document.getElementById('cartTotal') || {}).textContent,
                     lineas: cart.map(i => ({ id: i.productId, qty: i.quantity,
                                              price: i.price, sub: i.price * i.quantity })) };
        }""")
        ok(2, "getCartSummary.total = suma manual precio x cantidad (exacto)",
           m1["total"] == m1["manual"] == esperado,
           f"total={m1['total']} manual={m1['manual']} esperado={esperado}")
        ok(2, "unidades contadas = plan (2+3+1=6)",
           m1["count"] == unidades, str(m1["count"]))
        ok(2, "total del DOM (#cartTotal) = total calculado",
           pesos(m1["dom"]) == esperado, m1["dom"].strip())

        # subtotales por linea en el sidebar
        dom_lineas = await page.evaluate(
            "() => [...document.querySelectorAll('#cartItems .cart-item')].map(el => ({"
            "  titulo: el.querySelector('.cart-item-title').textContent,"
            "  sub: el.querySelector('.cart-item-price').textContent,"
            "  info: el.querySelector('.cart-item-info:nth-of-type(2)').textContent }))")
        subs_ok = all(pesos(d["sub"]) == l["sub"] for l, d in zip(m1["lineas"], dom_lineas))
        ok(2, "subtotal por linea en pantalla = precio x cantidad",
           subs_ok and len(dom_lineas) == len(plan),
           " / ".join(l["sub"].strip() for l in dom_lineas))

        # +1 al barato: el total sube EXACTO el precio del barato
        idx_barato = next(i for i, l in enumerate(m1["lineas"]) if l["id"] == eleccion["barato"]["id"])
        antes = await page.evaluate("() => getCartSummary().total")
        await page.evaluate("(i) => updateQuantity(i, 1)", idx_barato)
        await page.wait_for_timeout(400)
        despues = await page.evaluate("() => getCartSummary().total")
        ok(2, "+1 unidad sube el total exactamente el precio de la linea",
           despues - antes == eleccion["barato"]["opt"],
           f"{antes} -> {despues} (+{despues - antes})")

        # -1 tres veces: la linea desaparece al llegar a 0 y el total baja exacto
        for _ in range(3):
            await page.evaluate("(i) => updateQuantity(i, -1)", idx_barato)
            await page.wait_for_timeout(150)
        m2 = await page.evaluate(
            "() => ({ n: cart.length, total: getCartSummary().total, ids: cart.map(i => i.productId) })")
        ok(2, "-1 tres veces elimina la linea (2+1+1-3) y el total baja exacto",
           m2["n"] == 2 and eleccion["barato"]["id"] not in m2["ids"]
           and m2["total"] == esperado - 2 * eleccion["barato"]["opt"],
           f"total={m2['total']} esperado={esperado - 2 * eleccion['barato']['opt']}")

        # eliminar una linea suelta con el tacho
        total_antes = m2["total"]
        await page.evaluate("() => removeFromCart(0)")
        await page.wait_for_timeout(400)
        m3 = await page.evaluate("() => ({ n: cart.length, total: getCartSummary().total, precio: cart[0].price, qty: cart[0].quantity })")
        ok(2, "tacho elimina la linea y el total queda solo con la restante",
           m3["n"] == 1 and m3["total"] == m3["precio"] * m3["qty"] and m3["total"] != total_antes,
           str(m3["total"]))

        # TODO el catalogo: la tienda vende al Precio 2 exacto de POSGold
        # (margen 0 y sin redondeo) y el tachado, si existe, es real
        m4 = await page.evaluate("""() => {
            let malExacto = 0, malCompare = 0;
            const base = new Map(CATALOGO_BASE.map(p => [p.id, p]));
            products.forEach(p => {
                const b = base.get(p.id);
                if (b && p.price !== b.price) malExacto++;
                if (p.comparePrice && p.comparePrice <= p.price) malCompare++;
                flattenSizeOptions(p).forEach(o => { if (b && o.price !== b.price) malExacto++; });
            });
            return { malExacto: malExacto, malCompare: malCompare, n: products.length };
        }""")
        ok(2, f"los {m4['n']} productos se venden al Precio 2 exacto de POSGold",
           m4["malExacto"] == 0, f"{m4['malExacto']} precios alterados")
        ok(2, "ningun tachado es menor o igual al precio de venta",
           m4["malCompare"] == 0, str(m4["malCompare"]))

        # persistencia: el carrito sobrevive una recarga intacto
        antes_json = await page.evaluate("() => JSON.stringify(cart)")
        await page.reload(wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(3500)
        m5 = await page.evaluate(
            "() => ({ json: JSON.stringify(cart), total: getCartSummary().total })")
        ok(2, "el carrito sobrevive la recarga con las mismas lineas y precios",
           m5["json"] == antes_json, f"total tras recarga={m5['total']}")

        # vaciar: queda en cero real
        await page.evaluate("() => vaciarCarrito()")
        await page.wait_for_timeout(500)
        m6 = await page.evaluate("""() => ({
            n: cart.length, total: getCartSummary().total,
            dom: (document.getElementById('cartTotal') || {}).textContent,
            vacio: !!document.querySelector('#cartItems .empty-cart'),
        })""")
        ok(2, "vaciar carrito deja count 0, total $0 y pantalla de vacio",
           m6["n"] == 0 and m6["total"] == 0 and pesos(m6["dom"]) == 0 and m6["vacio"],
           f"n={m6['n']} dom={m6['dom'].strip()}")

        # ============ FASE 3: OPERACION COMPLETA (MENSAJE WHATSAPP) ============
        print("== FASE 3: EL PEDIDO QUE LLEGA POR WHATSAPP ES EXACTO ==")
        for prod, qty in plan:
            for _ in range(qty):
                await page.evaluate("(id) => quickAddDefault(id)", prod["id"])
                await page.wait_for_timeout(120)
        # el ultimo quickAdd dejo el checkout abierto: completar el formulario
        await page.wait_for_timeout(600)
        total_dom = await page.evaluate("() => getCartSummary().total")

        await page.fill("#customerFullName", "Laura Prueba QA")
        await page.fill("#customerPhone", "3101234567")
        await page.fill("#customerEmail", "qa@prueba.com")
        await page.select_option("#customerDepartment", label="Valle del Cauca")
        await page.fill("#customerCity", "Cali")
        await page.fill("#customerNeighborhood", "Barrio Centro")
        await page.fill("#customerAddress", "Calle 45 # 23-15")
        await page.evaluate("""() => {
            const t = document.querySelector('.payment-method-toggle [type=radio], .payment-method-toggle button, .payment-method-toggle label');
            if (t) t.click();
        }""")
        await page.wait_for_timeout(600)
        await page.evaluate("""() => {
            window.__captura = null;
            window.open = (u) => { window.__captura = u; return null; };
        }""")
        await page.evaluate("() => document.getElementById('whatsappBtn').click()")
        await page.wait_for_timeout(300)
        confeti_vivo = await page.evaluate(
            "() => document.querySelectorAll('.jt-confeti').length")
        ok(3, "el pedido enviado celebra con confeti", confeti_vivo > 20, str(confeti_vivo))
        await page.wait_for_timeout(900)
        enlace = await page.evaluate("() => window.__captura")
        ok(3, "se genera el enlace del pedido", bool(enlace and "wa.me" in enlace),
           (enlace or "")[:50])

        msg = urllib.parse.unquote_plus(enlace.split("text=")[1]) if enlace else ""

        # cada producto con SU nombre, cantidad, precio y subtotal
        lineas_msg = re.findall(r"• (.+?)\n.*?(\d+) x \$([\d.]+) = \$([\d.]+)", msg, re.S)
        ok(3, "el mensaje lista las 3 referencias del carrito",
           len(lineas_msg) == 3, str([l[0][:30] for l in lineas_msg]))

        nombres_ok = all(p["name"] in [l[0] for l in lineas_msg] for p, _ in plan)
        ok(3, "los nombres del mensaje son EXACTAMENTE los del carrito", nombres_ok,
           " / ".join(l[0][:28] for l in lineas_msg))

        aritmetica = []
        for (prod, qty), (_, qty_msg, precio_msg, sub_msg) in zip(plan, lineas_msg):
            igual = (int(qty_msg) == qty and pesos(precio_msg) == prod["opt"]
                     and pesos(sub_msg) == prod["opt"] * qty)
            aritmetica.append(igual)
        ok(3, "cantidad x precio = subtotal en cada linea del mensaje",
           all(aritmetica), str(aritmetica))

        suma_msg = sum(pesos(l[3]) for l in lineas_msg)
        m_total = re.search(r"TOTAL PRODUCTOS: \$([\d.]+)", msg)
        total_msg = pesos(m_total.group(1)) if m_total else 0
        ok(3, "la suma de subtotales del mensaje = TOTAL del mensaje",
           suma_msg == total_msg, f"{suma_msg} vs {total_msg}")

        ok(3, "el TOTAL del mensaje = total vivo del carrito",
           total_msg == total_dom, f"msg={total_msg} carrito={total_dom}")

        unidades_msg = sum(int(l[1]) for l in lineas_msg)
        ok(3, "las unidades del mensaje (2+3+1=6) = unidades del carrito",
           unidades_msg == 6, str(unidades_msg))

        # despues del pedido: el carrito se vacia solo (CONFIG.vaciarCarritoTrasPedido)
        # y el confeti termina de caer y desaparece
        limpio = False
        for _ in range(14):
            n_confeti = await page.evaluate(
                "() => document.querySelectorAll('.jt-confeti').length")
            if n_confeti == 0:
                limpio = True
                break
            await page.wait_for_timeout(250)
        ok(3, "el confeti se autolimpia al caer", limpio, str(n_confeti))
        m7 = await page.evaluate("() => ({ n: cart.length, ls: localStorage.getItem('taiwanCart') })")
        ok(3, "tras enviar el pedido el carrito se reinicia", m7["n"] == 0,
           f"carrito={m7['n']} ls={m7['ls']}")

        # ============ FASE 4: EFECTO VUELO AL CARRITO ============
        print("== FASE 4: DOPAMINA (la foto vuela al carrito) ==")
        # cargar una tarjeta del grid con su miniatura lista (nadie agrega
        # una foto que todavia no ve)
        lista_img = False
        for _ in range(40):
            lista_img = await page.evaluate(
                "() => { const im = document.querySelector('#productsGrid .card-gallery img');"
                " return !!(im && im.complete && im.naturalWidth > 0); }")
            if lista_img:
                break
            await page.wait_for_timeout(500)

        # el vuelo nace y muere solo, y el checkout sigue abriendo
        v1 = await page.evaluate("""() => {
            const card = document.querySelector('#productsGrid .card-gallery');
            const id = card.id.replace('gal-', '');
            const src = card.querySelector('img').src;
            try { closeOrderForm(); } catch (e) {}
            vaciarCarrito();
            quickAddDefault(id);
            const fly = document.querySelector('.jt-fly');
            return { id: id, vuelos: document.querySelectorAll('.jt-fly').length,
                     mismoSrc: !!(fly && fly.src === src),
                     badge: document.getElementById('cartCount').classList.contains('bump') };
        }""")
        ok(4, "al agregar, la foto de la tarjeta vuela al carrito (.jt-fly)",
           v1["vuelos"] == 1, str(v1["vuelos"]))
        ok(4, "el vuelo reusa la miniatura de la tarjeta (misma foto)",
           v1["vuelos"] == 1 and v1["mismoSrc"], "")
        ok(4, "el badge del carrito hace pop (clase bump)", v1["badge"])

        modal_abrio = False
        for _ in range(10):
            modal_abrio = await page.evaluate(
                "() => document.getElementById('orderModal').classList.contains('show')")
            if modal_abrio:
                break
            await page.wait_for_timeout(200)
        ok(4, "el checkout abre tras el vuelo (~0.3s de espera)", modal_abrio)

        await page.wait_for_timeout(900)
        restantes = await page.evaluate("() => document.querySelectorAll('.jt-fly').length")
        ok(4, "el clon volador se autolimpia al aterrizar", restantes == 0, str(restantes))

        # agregar un sugerido DESDE el checkout ya abierto: sin vuelo
        v2 = await page.evaluate("""() => {
            const card = document.querySelector('#productsGrid .card-gallery');
            const id = card.id.replace('gal-', '');
            quickAddDefault(id);
            return { vuelos: document.querySelectorAll('.jt-fly').length };
        }""")
        ok(4, "agregar con el checkout abierto NO lanza otro vuelo",
           v2["vuelos"] == 0, str(v2["vuelos"]))
        await cerrar_checkout(page)

        # usuarios con "reducir movimiento": sin vuelo, flujo intacto
        await page.emulate_media(reduced_motion="reduce")
        v3 = await page.evaluate("""() => {
            const card = document.querySelector('#productsGrid .card-gallery');
            const id = card.id.replace('gal-', '');
            vaciarCarrito();
            const t0 = performance.now();
            quickAddDefault(id);
            return { vuelos: document.querySelectorAll('.jt-fly').length,
                     modal: document.getElementById('orderModal').classList.contains('show'),
                     dt: Math.round(performance.now() - t0) };
        }""")
        ok(4, "prefers-reduced-motion: sin vuelo y checkout inmediato",
           v3["vuelos"] == 0 and v3["modal"], f"vuelos={v3['vuelos']} dt={v3['dt']}ms")
        await page.emulate_media(reduced_motion="no-preference")

        await browser.close()

        print()
        total = len(RESULTADOS)
        fallos = sum(1 for r in RESULTADOS if "FAIL" in r)
        print(f"== RESUMEN CARRITO: {total} pruebas | OK: {total - fallos} | FAIL: {fallos} ==")
        if ERRORES:
            print("errores JS:")
            for e in ERRORES:
                print("  " + e)
        else:
            print("errores JS: (ninguno)")
        return 1 if (fallos or ERRORES) else 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
