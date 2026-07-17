# HDE somatic mandala asset fix — 2026-07-17

## Scope

`public/somatic_mandala.png` was checkpointed separately from the theme and runtime commits because it is a binary asset change.

## Change

The tracked file path is a `.png` asset. The prior blob at that path was JPEG-encoded data despite the `.png` filename. The replacement is a valid 1024×1024 PNG with RGBA channels.

## Verification

```bash
file public/somatic_mandala.png
git show HEAD:public/somatic_mandala.png | file -
sha256sum public/somatic_mandala.png
```

Expected result after this checkpoint: the working asset reports `PNG image data, 1024 x 1024, 8-bit/color RGBA, non-interlaced`.
