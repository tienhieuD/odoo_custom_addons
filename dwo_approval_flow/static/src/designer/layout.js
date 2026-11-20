/**
 * Geometry of the diagram: curved arrows that go around the boxes and labels that do not overlap.
 * Pure functions, no Owl. Quadratic Bezier curves: P(t) = (1-t)^2 P1 + 2(1-t)t C + t^2 P2.
 */
export const NW = 150;
export const NH = 52;
const GAP = 8; // free space kept around a box
const LABEL_H = 22;
const SAMPLES = 16;
const BENDS = [0, 36, -36, 72, -72, 110, -110, 150, -150];
const LABEL_T = [0.5, 0.42, 0.58, 0.34, 0.66, 0.26, 0.74, 0.18, 0.82];

const center = (s) => ({ x: s.x + NW / 2, y: s.y + NH / 2 });

function clip(c, to) {
    const dx = to.x - c.x;
    const dy = to.y - c.y;
    if (!dx && !dy) {
        return c;
    }
    const k = Math.min(dx ? NW / 2 / Math.abs(dx) : 1e9, dy ? NH / 2 / Math.abs(dy) : 1e9);
    return { x: c.x + dx * k, y: c.y + dy * k };
}

export function pointAt(curve, t) {
    const u = 1 - t;
    return {
        x: u * u * curve.p1.x + 2 * u * t * curve.c.x + t * t * curve.p2.x,
        y: u * u * curve.p1.y + 2 * u * t * curve.c.y + t * t * curve.p2.y,
    };
}

const inside = (p, s, pad) =>
    p.x > s.x - pad && p.x < s.x + NW + pad && p.y > s.y - pad && p.y < s.y + NH + pad;

function hits(curve, obstacles) {
    let n = 0;
    for (let i = 1; i < SAMPLES; i++) {
        const p = pointAt(curve, i / SAMPLES);
        if (obstacles.some((s) => inside(p, s, GAP))) {
            n++;
        }
    }
    return n;
}

/** A curve from box a to box b that bows ``bend`` pixels away from the straight line. */
function curveBetween(a, b, bend) {
    const ca = center(a);
    const cb = center(b);
    const dx = cb.x - ca.x;
    const dy = cb.y - ca.y;
    const len = Math.hypot(dx, dy) || 1;
    const nx = -dy / len;
    const ny = dx / len;
    const c = { x: (ca.x + cb.x) / 2 + nx * bend * 2, y: (ca.y + cb.y) / 2 + ny * bend * 2 };
    const p1 = clip(ca, c);
    const p2 = clip(cb, c);
    return { p1, c, p2 };
}

const overlap = (r, q) => r.x < q.x + q.w && r.x + r.w > q.x && r.y < q.y + q.h && r.y + r.h > q.y;

/**
 * @param states      [{key, x, y}]
 * @param transitions [{cid, from, to, name}]   (from empty = every state)
 * @returns {cid: {d, mx, my, width, any, x1, y1}}
 */
export function computeLayout(states, transitions) {
    const byKey = Object.fromEntries(states.map((s) => [s.key, s]));
    const result = {};
    const curves = [];
    // arrows between the same two boxes are spread on both sides of the line
    const groups = {};
    const spreadOf = new Map();
    for (const t of transitions) {
        if (t.from && byKey[t.from] && byKey[t.to]) {
            const key = [t.from, t.to].sort().join("|");
            (groups[key] = groups[key] || []).push(t);
        }
    }
    for (const list of Object.values(groups)) {
        list.forEach((t, i) => {
            const spread = (i - (list.length - 1) / 2) * 34;
            const canonical = t.from < t.to ? 1 : -1;
            spreadOf.set(t.cid, spread * canonical);
        });
    }
    for (const t of transitions) {
        const b = byKey[t.to];
        if (!b) {
            continue;
        }
        const label = t.name || "?";
        const width = Math.max(40, label.length * 6.4 + 14);
        if (!t.from || !byKey[t.from]) {
            const cy = b.y + NH / 2;
            const curve = { p1: { x: b.x - 90, y: cy }, c: { x: b.x - 45, y: cy }, p2: { x: b.x, y: cy } };
            curves.push({ t, curve, width, any: true });
            continue;
        }
        const a = byKey[t.from];
        const spread = spreadOf.get(t.cid) || 0;
        const others = states.filter((s) => s !== a && s !== b);
        let best = null;
        for (const extra of BENDS) {
            // keep the side of the pair spread, add the detour on top of it
            const sign = spread < 0 ? -1 : 1;
            const bend = spread + (spread ? sign * Math.abs(extra) : extra);
            const curve = curveBetween(a, b, bend);
            const n = hits(curve, others);
            if (!best || n < best.n) {
                best = { curve, n };
            }
            if (!n) {
                break;
            }
        }
        curves.push({ t, curve: best.curve, width, any: false });
    }
    // labels: keep the first spot that touches neither another label nor a box
    const placed = [];
    const boxes = states.map((s) => ({ x: s.x - 2, y: s.y - 2, w: NW + 4, h: NH + 4 }));
    for (const { t, curve, width, any } of curves) {
        let choice = null;
        for (const at of LABEL_T) {
            const p = pointAt(curve, at);
            const rect = { x: p.x - width / 2, y: p.y - LABEL_H / 2, w: width, h: LABEL_H };
            const score = placed.filter((q) => overlap(rect, q)).length * 2 + boxes.filter((q) => overlap(rect, q)).length;
            if (!choice || score < choice.score) {
                choice = { score, p, rect };
            }
            if (!score) {
                break;
            }
        }
        placed.push(choice.rect);
        result[t.cid] = {
            d: `M${curve.p1.x} ${curve.p1.y}Q${curve.c.x} ${curve.c.y} ${curve.p2.x} ${curve.p2.y}`,
            mx: choice.p.x, my: choice.p.y, width, any, x1: curve.p1.x, y1: curve.p1.y,
        };
    }
    return result;
}

/** Does box (x, y) overlap another box (with a margin)? */
export function collides(states, moving, x, y, margin = 14) {
    return states.some(
        (o) => o !== moving && x < o.x + NW + margin && x + NW + margin > o.x && y < o.y + NH + margin && y + NH + margin > o.y
    );
}

/** First free place for a new box, scanning the grid left to right, top to bottom. */
export function freeSpot(states) {
    for (let row = 0; row < 40; row++) {
        for (let col = 0; col < 5; col++) {
            const x = 30 + col * 220;
            const y = 30 + row * 110;
            if (!collides(states, null, x, y)) {
                return { x, y };
            }
        }
    }
    return { x: 30, y: 30 };
}
