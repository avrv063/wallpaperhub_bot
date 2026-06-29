SCAN_CANCEL_REQUESTED = False


def request_scan_cancel():
    global SCAN_CANCEL_REQUESTED
    SCAN_CANCEL_REQUESTED = True


def reset_scan_cancel():
    global SCAN_CANCEL_REQUESTED
    SCAN_CANCEL_REQUESTED = False


def is_scan_cancelled() -> bool:
    return SCAN_CANCEL_REQUESTED