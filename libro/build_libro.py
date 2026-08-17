import math

V = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
E = [(0,1),(0,2),(0,4),(1,3),(1,5),(2,3),(2,6),(3,7),(4,5),(4,6),(5,7),(6,7)]

def proj(v, ang, tilt, esc, cx, cy):
    x, y, z = v
    ca, sa = math.cos(ang), math.sin(ang)
    x1, z1 = x*ca - z*sa, x*sa + z*ca
    cb, sb = math.cos(tilt), math.sin(tilt)
    y1, z2 = y*cb - z1*sb, y*sb + z1*cb
    d = 3.6
    f = d / (d - z2)
    return (cx + x1*esc*f, cy + y1*esc*f, f)

def cubo_svg(size, esc_out, esc_in, ang=0.62, tilt=0.42):
    cx = cy = size / 2
    partes = []
    # halo
    partes.append(
        f'<defs><radialGradient id="halo{size}" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#3B6CF6" stop-opacity=".3"/>'
        '<stop offset="60%" stop-color="#3B6CF6" stop-opacity=".08"/>'
        '<stop offset="100%" stop-color="#3B6CF6" stop-opacity="0"/>'
        f'</radialGradient></defs>'
        f'<circle cx="{cx}" cy="{cy}" r="{size*0.48}" fill="url(#halo{size})"/>'
    )
    # cubo interior violeta
    p_in = [proj(v, -ang*1.7, tilt, esc_in, cx, cy) for v in V]
    for a, b in E:
        partes.append(f'<line x1="{p_in[a][0]:.1f}" y1="{p_in[a][1]:.1f}" x2="{p_in[b][0]:.1f}" y2="{p_in[b][1]:.1f}" stroke="#A78BFA" stroke-width="1.1" opacity=".55"/>')
    # cubo principal azul: glow + nítido
    p = [proj(v, ang, tilt, esc_out, cx, cy) for v in V]
    for w, op in ((7, .16), (3.5, .3), (1.7, 1)):
        col = '#3B6CF6' if op < 1 else '#6E92FF'
        for a, b in E:
            partes.append(f'<line x1="{p[a][0]:.1f}" y1="{p[a][1]:.1f}" x2="{p[b][0]:.1f}" y2="{p[b][1]:.1f}" stroke="{col}" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>')
    for q in p:
        partes.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="{2.4*q[2]/1.25:.1f}" fill="#6E92FF" opacity=".95"/>')
    return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">' + ''.join(partes) + '</svg>'

b64 = open('archivo-latin.b64').read().strip()
tpl = open('libro.template.html').read()
page = (tpl
    .replace('@@FONT@@', b64)
    .replace('@@CUBE@@', cubo_svg(430, 92, 40))
    .replace('@@CUBE2@@', '<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)">' + cubo_svg(330, 72, 32, ang=0.5) + '</div>'))
open('libro.html', 'w').write(page)
print('libro.html listo:', len(page), 'bytes')
