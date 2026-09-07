"""Small two-layer grid router for the compact macros (M2 vertical/M3 horizontal)."""
import heapq
import random


def route(terminals, nx, ny, reservations=None):
    """Connect each net's grid terminals; reserve all terminals before routing.

    Node coordinates are (x, y, layer), with layer 0=M2 and 1=M3.
    Vertical pitch is 0.7 um; horizontal pitch is 0.51 um. Different M3
    nets must leave a vacant horizontal grid point for 0.3 um clearance.
    Retry net ordering, not geometry or electrical constraints.
    """
    reserved = dict(reservations or {})
    for net, points in terminals.items():
        for point in points:
            assert point not in reserved or reserved[point] == net
            reserved[point] = net
    rng = random.Random(130)
    nets = sorted(terminals, key=lambda n: -len(terminals[n]))
    for attempt in range(300):
        occupied = dict(reserved)
        edges = {n: set() for n in nets}
        failed = False
        for net in nets:
            pending = set(terminals[net])
            tree = {min(pending)}
            pending -= tree
            while pending:
                queue = [(0, p) for p in sorted(tree)]
                heapq.heapify(queue)
                cost = {p: 0 for p in tree}
                previous = {}
                found = None
                while queue:
                    distance, p = heapq.heappop(queue)
                    if distance != cost[p]:
                        continue
                    if p in pending:
                        found = p
                        break
                    x, y, layer = p
                    neighbors = [(x, y, 1-layer)]
                    neighbors += ([(x, y-1, layer), (x, y+1, layer)] if layer == 0
                                  else [(x-1, y, layer), (x+1, y, layer)])
                    for q in neighbors:
                        if not (0 <= q[0] < nx and 0 <= q[1] < ny):
                            continue
                        if occupied.get(q, net) != net:
                            continue
                        if q[2] == 1 and any(occupied.get((q[0]+dx,q[1],1),net) != net
                                             for dx in (-1,1)):
                            continue
                        new_cost = distance + (3 if q[2] != layer else 1)
                        if new_cost < cost.get(q, float('inf')):
                            cost[q] = new_cost
                            previous[q] = p
                            heapq.heappush(queue, (new_cost, q))
                if found is None:
                    failed = True
                    break
                pending.remove(found)
                p = found
                while p not in tree:
                    q = previous[p]
                    edges[net].add(tuple(sorted((p, q))))
                    occupied[p] = net
                    tree.add(p)
                    p = q
            if failed:
                break
        if not failed:
            return edges
        rng.shuffle(nets)
    raise RuntimeError('Compact routing grid is congested; no route found')
