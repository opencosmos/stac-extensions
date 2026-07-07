# OpenCosmos STAC Extensions

Custom [STAC](https://stacspec.org/) extensions that formalise the `opencosmos:` metadata
properties DataCosmos stores on its collections and items. Each extension owns a distinct
property namespace so they can be **combined** on a per-collection basis (a collection can
declare the general extension plus the QA extension plus the payload extension that applies
to it).

These schemas were derived from the properties actually present on production items
(`https://app.open-cosmos.com/api/data/v0/stac`), see [Known data mismatches](#known-data-mismatches).

## Extension catalog

| Extension | Namespace(s) owned | Applies to | Schema |
|-----------|--------------------|------------|--------|
| `opencosmos` (general) | `opencosmos:<field>` (single segment) | Item, Collection, Catalog | [opencosmos/v1.0.0/schema.json](opencosmos/v1.0.0/schema.json) |
| `opencosmos-qa` | `opencosmos:qa:*` | Item | [opencosmos-qa/v1.0.0/schema.json](opencosmos-qa/v1.0.0/schema.json) |
| `opencosmos-simera` | `opencosmos:simera:*` | Item | [opencosmos-simera/v1.0.0/schema.json](opencosmos-simera/v1.0.0/schema.json) |
| `opencosmos-processing` | `opencosmos:calibration:*`, `opencosmos:georeference:*`, `opencosmos:process:*` | Item | [opencosmos-processing/v1.0.0/schema.json](opencosmos-processing/v1.0.0/schema.json) |
| `opencosmos-isim90` | `opencosmos:isim90:*` | Item | [opencosmos-isim90/v1.0.0/schema.json](opencosmos-isim90/v1.0.0/schema.json) |
| `opencosmos-alisio` | `opencosmos:alisio:*` | Item | [opencosmos-alisio/v1.0.0/schema.json](opencosmos-alisio/v1.0.0/schema.json) |

`opencosmos-simera`, `opencosmos-isim90` and `opencosmos-alisio` are examples of
**payload-specific** extensions. Add one per payload family as new payloads appear.

## Design conventions

- **Namespacing.** The general extension defines the common single-segment fields
  (`opencosmos:copyright`, `opencosmos:data_area_km2`, ...). Every sub-namespaced key
  (`opencosmos:<group>:...`) is owned by a dedicated companion extension. A few single-segment
  fields that are specific to processing or a payload (e.g. `opencosmos:session_id`,
  `opencosmos:calibration_site_type`, `opencosmos:per_payload_time_sync_s`) are defined in the
  relevant companion extension rather than in the general one.
- **Combinability.** Extensions are designed to be applied together without rejecting each
  other's properties. The payload and processing extensions (`opencosmos-simera`,
  `opencosmos-processing`, `opencosmos-isim90`, `opencosmos-alisio`) are strict *within their own
  namespace*: they set `additionalProperties: false` and use a negative-lookahead
  `patternProperties` so keys outside their namespace pass through untouched. The general
  (`opencosmos`) and `opencosmos-qa` extensions are intentionally **permissive**
  (`additionalProperties: true`): they type-check only the common fields they define and allow
  any other `opencosmos:*` property, so new fields can be introduced while the spec matures and
  so items carrying not-yet-modelled fields remain valid.
- **Canonical types.** Schemas describe the *intended* type of each field (e.g. booleans as
  `boolean`, IDs as `string`). Some production data currently serialises values differently
  (e.g. `"true"` strings), those are tracked in [Known data mismatches](#known-data-mismatches)
  and should be migrated rather than reflected in the schema.
- **Item vs collection fields.** The general extension defines its fields separately for items
  and collections. `opencosmos:resolution` and `opencosmos:high_resolution_read_permission` are
  modelled as **collection-level** fields; the remaining common fields are item-level. On
  collections these values usually appear under `summaries` as STAC summary structures (an array
  of values, e.g. `opencosmos:resolution: ["full", "limited"]`, or a `{"minimum", "maximum"}`
  range). Summary contents are intentionally left permissive and not constrained by the schemas.

## Attaching an extension

Add the schema `$id` URL(s) to the `stac_extensions` array of the collection and/or item.

Collection:

```json
{
  "type": "Collection",
  "id": "menut-l1c-cogs",
  "stac_extensions": [
    "https://opencosmos.github.io/stac-extensions/opencosmos/v1.0.0/schema.json",
    "https://opencosmos.github.io/stac-extensions/opencosmos-qa/v1.0.0/schema.json",
    "https://opencosmos.github.io/stac-extensions/opencosmos-simera/v1.0.0/schema.json"
  ]
}
```

Item:

```json
{
  "type": "Feature",
  "stac_extensions": [
    "https://opencosmos.github.io/stac-extensions/opencosmos/v1.0.0/schema.json",
    "https://opencosmos.github.io/stac-extensions/opencosmos-simera/v1.0.0/schema.json"
  ],
  "properties": {
    "opencosmos:data_area_km2": 1234.5,
    "opencosmos:simera:compression": 0
  }
}
```

## Hosting

The schemas are published with **GitHub Pages** from the `opencosmos/stac-extensions`
repository, so each `$id` resolves at:

```
https://opencosmos.github.io/stac-extensions/<extension>/<version>/schema.json
```

Publishing is automated by [.github/workflows/pages.yml](.github/workflows/pages.yml), which
validates the schemas and checks every `$id` against its served path
([scripts/verify_ids.py](scripts/verify_ids.py)) before deploying on push to `main`.

Keep the directory layout `<extension>/<version>/schema.json`; the `$id` inside each file must
match its public URL. If the repository or host ever changes, update every `$id` and the
`BASE_URL` in `scripts/verify_ids.py` accordingly.

## Versioning

Extensions are versioned in the URL (`v1.0.0`). Make backwards-incompatible changes under a new
version directory and leave existing versions in place, since already-published items reference
them by URL.

## Known data mismatches

The following fields fail validation against the canonical schemas because production currently
stores them in a different (legacy) representation. Counts were confirmed against a full scan of
all 399 production collections (~4,800 items, up to 60 items paginated per collection). These are
data-cleanup targets, not schema bugs.

| Extension | Field | Canonical type | Production deviation |
|-----------|-------|----------------|----------------------|
| `opencosmos-simera` | `opencosmos:simera:compression` | integer | string, e.g. `"0"` |
| `opencosmos-simera` | `opencosmos:simera:absolute_correction` | boolean | string `"true"`/`"false"` |
| `opencosmos-simera` | `opencosmos:simera:band_alignment_correction` | boolean | string `"true"`/`"false"` |
| `opencosmos-simera` | `opencosmos:simera:geometric_correction` | boolean | string `"true"`/`"false"` |
| `opencosmos-simera` | `opencosmos:simera:orthorectification` | boolean | string `"true"`/`"false"` |
| `opencosmos-simera` | `opencosmos:simera:real_gcps_used` | boolean | string `"true"`/`"false"` |
| `opencosmos-simera` | `opencosmos:simera:relative_correction` | boolean | mixed boolean and string |
| `opencosmos-simera` / `-processing` / `-isim90` / `-alisio` | `opencosmos:session_id` | string | integer for some payload families (e.g. `heleo-*`) |
| `opencosmos-qa` | `opencosmos:qa:rejected` | boolean | string `"true"` in some items |
| `opencosmos-processing` | `opencosmos:calibration:georeference` | object | integer sentinel (`0`) in some items |

## Regenerating / validating

The discovery and validation scripts used to build these schemas query the production STAC API
read-only. To re-check the schemas against live data, meta-validate each `schema.json` with a
Draft-07 validator and validate item `properties` against each extension's item fields
definition (`#/definitions/item_fields` for the general extension, `#/definitions/fields` for the
companions), grouping by the namespace each extension owns.
