# primitives.py
# ----------
# tiny helpers for a Kniterate v-bed, assuming one yarn carrier (default '3')

# Constants for Kniterate machine constraints
KNITERATE_MAX_NEEDLES = 252  # Maximum number of needles on the bed
VALID_BEDS = {'f', 'b', 'fs', 'bs'}  # Valid bed positions

def validate_bed(bed):
    """Validate that a bed position is valid for Kniterate"""
    if bed not in VALID_BEDS:
        raise ValueError(f"Invalid bed '{bed}'. Must be one of {VALID_BEDS}")
    return bed

def validate_needle(n):
    """Validate that a needle position is valid for Kniterate"""
    if not isinstance(n, int):
        raise ValueError(f"Needle position must be an integer, got {n}")
    if n < 0 or n >= KNITERATE_MAX_NEEDLES:
        raise ValueError(f"Needle position {n} out of range [0, {KNITERATE_MAX_NEEDLES})")
    return n

def validate_direction(direction):
    """Validate that a direction is valid for Kniterate"""
    if direction not in {'+', '-'}:
        raise ValueError(f"Invalid direction '{direction}'. Must be '+' or '-'")
    return direction

def tuck_on_empty(w, n, direction, carrier='3'):
    """
    +1 loop, hole-free.  Ensure needle n is empty, then tuck.
    """
    n = validate_needle(n)
    direction = validate_direction(direction)
    w.xfer(('f', n), ('b', n))           # frees front needle if occupied
    w.tuck(direction, ('f', n), carrier) # new loop appears on front


def yarn_over_eyelet(w, n, direction, carrier='3'):
    """
    +1 loop *with* eyelet.  Needle keeps its old stitch and gains one tuck loop.
    """
    n = validate_needle(n)
    direction = validate_direction(direction)
    w.tuck(direction, ('f', n), carrier) # no transfer → hole remains


def miss_float(w, n, direction, carrier='3'):
    """
    –1 loop: skip the hook so no new stitch is formed (creates a float behind).
    """
    n = validate_needle(n)
    direction = validate_direction(direction)
    w.miss(direction, ('f', n), carrier)


def gather_back_to_front(w, n, carrier='3'):
    """
    –1 loop per call (collapse).  Moves the back-bed stitch onto the front
    so the *next* knit will knit two loops together.
    Caller must issue that knit instruction in the same direction.
    """
    n = validate_needle(n)
    w.xfer(('b', n), ('f', n))           # stack loops; knit-together happens later


def validate_rack_position(pos):
    """Validate that a rack position is valid for Kniterate (integer or integer+0.25)"""
    fractional = pos % 1
    if fractional != 0 and fractional != 0.25:
        raise ValueError(f"Invalid rack position {pos}. Must be an integer or integer+0.25")
    return pos


def cable_2x2_RC(w, n_left, carrier='3'):
    """
    2×2 right-cross (front pair crosses in front of back pair).
    Needles involved: n_left … n_left+3
    No change in loop count, lateral Δ = +2 (moves two sts right).
    Uses only valid racking values for Kniterate.
    """
    a, b, c, d = n_left, n_left+1, n_left+2, n_left+3
    
    # First move all stitches to back bed
    for n in [a, b, c, d]:
        w.xfer(('f', n), ('b', n))
    
    # Move right pair of stitches with rack = 2
    w.rack(validate_rack_position(2))  # rack to the right by 2 needles
    w.xfer(('b', c), ('f', a))  # move rightmost stitch
    w.xfer(('b', d), ('f', b))  # move second rightmost stitch
    
    # Reset rack and transfer remaining stitches
    w.rack(validate_rack_position(0))  # return to neutral position
    w.xfer(('b', a), ('f', c))  # move original left stitches
    w.xfer(('b', b), ('f', d))  # to their new positions


def short_row_wedge(w, col0, col1, rows, carrier='3'):
    """
    +area: hold outside [col0, col1] and knit partial rows inside the window.
    Very small, naïve implementation (no wraps, no racking).
    """
    # Validate input parameters
    col0 = validate_needle(col0)
    col1 = validate_needle(col1)
    if col1 < col0:
        raise ValueError(f"col1 ({col1}) must be greater than col0 ({col0})")
    if rows < 1:
        raise ValueError(f"rows must be positive, got {rows}")
        
    # put needles outside the window on hold
    for n in range(col0):
        n = validate_needle(n)
        w.xfer(('f', n), ('b', n))       # held on back bed
    for n in range(col1+1, col1+rows+1): # crude safety margin
        n = validate_needle(n)
        w.xfer(('f', n), ('b', n))

    # knit `rows` short rows back and forth inside the window
    for i in range(rows):
        direction = '+' if i % 2 == 0 else '-'
        r = range(col0, col1+1)
        r = r if direction == '+' else reversed(r)
        for n in r:
            w.knit(direction, ('f', n), carrier)

    # release held stitches (transfer them back)
    for n in range(col0):
        w.xfer(('b', n), ('f', n))
    for n in range(col1+1, col1+rows+1):
        w.xfer(('b', n), ('f', n))
