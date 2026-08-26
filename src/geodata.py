"""Country boundaries for the maps, fetched once and cached.

make_maps.py needs Natural Earth 50m admin-0 boundaries. Rather than expect a
3 MB file to be in the working tree, fetch it on first run and cache it next to
the source. The pinned tag matters: the index's maps should not change because
upstream edited a border on master.
"""
import pathlib, urllib.request, sys

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "data" / "ne_50m.geojson"
TAG = "v5.1.2"
URLS = [
    f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{TAG}"
    "/geojson/ne_50m_admin_0_countries.geojson",
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master"
    "/geojson/ne_50m_admin_0_countries.geojson",
]
MIN_BYTES = 1_000_000          # a truncated download is worse than none


def path():
    """Local path to the boundary file, downloading it if we do not have it."""
    if CACHE.exists() and CACHE.stat().st_size > MIN_BYTES:
        return CACHE
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    for url in URLS:
        try:
            print(f"  fetching Natural Earth boundaries ({TAG if TAG in url else 'master'}) ...",
                  file=sys.stderr)
            with urllib.request.urlopen(url, timeout=120) as r:
                data = r.read()
            if len(data) < MIN_BYTES:
                errors.append(f"{url} returned only {len(data)} bytes")
                continue
            tmp = CACHE.with_suffix(".part")
            tmp.write_bytes(data)
            tmp.replace(CACHE)
            print(f"  cached {len(data)/1e6:.1f} MB at {CACHE}", file=sys.stderr)
            return CACHE
        except Exception as e:                       # noqa: BLE001
            errors.append(f"{url}: {e}")
    raise SystemExit(
        "Could not fetch Natural Earth 50m admin-0 boundaries.\n  "
        + "\n  ".join(errors)
        + f"\nDownload ne_50m_admin_0_countries.geojson by hand and save it as\n  {CACHE}")


if __name__ == "__main__":
    print(path())
