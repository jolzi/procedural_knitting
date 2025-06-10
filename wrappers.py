from knitout import Writer
from knitout_kniterate_3D.knit3D import closedTubeCaston, openTubeCaston, singleBedCaston, bindoff

def cast_on(w: Writer, left: int, right: int, carrier: str, style="closed", gauge=2):
    """One-line wrapper around knitout-kniterate-3D’s cast-ons."""
    if style == "closed":
        # closed tube, single pass, carrier flips sides
        closedTubeCaston(w, startN=right, endN=left, c=carrier, gauge=gauge)
    elif style == "open":
        # 4-pass zig-zag, carrier ends where it started
        openTubeCaston(w, startN=left, endN=right, c=carrier, gauge=gauge)
    elif style == "flat":
        # single-bed alternating-tuck cast-on on the front bed
        # reuse their singleBedCaston helper
        singleBedCaston(w, startN=left, endN=right, c=carrier, bed='f', gauge=gauge)
    else:
        raise ValueError("style must be 'closed', 'open', or 'flat'")

def cast_off(w: Writer, left: int, right: int, carrier: str, side="l"):
    """Bind off all live loops in a single pass."""
    count = right - left + 1
    # bindoff() wants the *edge* needle on the side you’re binding toward
    edge = left if side == "l" else right
    bindoff(w, count=count, xferNeedle=edge, c=carrier, side=side)
