# HD Engine social image strategy

## Default image

All Astro pages that use `src/layouts/Layout.astro` now emit a complete Open Graph and Twitter card image set. The fallback image is `/somatic_mandala.png`, resolved to an absolute URL from `Astro.site` with `https://humandesignengine.com` as the runtime fallback.

Generated tags include:

- `og:image`
- `og:image:secure_url`
- `og:image:alt`
- `og:image:type`
- `og:image:width`
- `og:image:height`
- `twitter:card`
- `twitter:title`
- `twitter:description`
- `twitter:image`
- `twitter:image:alt`

## Section overrides

Pages can select a section-specific social preview by passing `section` into `Layout`:

| Section | Intended pages | Current image |
| --- | --- | --- |
| `home` | Site homepage and generic pages | `/somatic_mandala.png` |
| `free-reading` | Free calculator / reading generator | `/somatic_mandala.png` |
| `reports` | Paid report purchase flow | `/somatic_mandala.png` |
| `sanctuary` | Somatic Sanctuary / deconditioning flow | `/somatic_mandala.png` |
| `developers` | API documentation | `/somatic_mandala.png` |
| `checkout` | Checkout/payment pages | `/somatic_mandala.png` |

The image map lives in `src/layouts/Layout.astro` so future branded section images can be swapped in one place without touching every page.

## Page-level override

If a page needs a unique preview, pass `ogImage` and `ogImageAlt` directly:

```astro
<Layout
  title="Example | Human Design Engine"
  description="Example page description."
  section="reports"
  ogImage="/custom-social-preview.png"
  ogImageAlt="Custom Human Design Engine report preview"
>
```

`ogType` defaults to `website`; product/report pages can pass `ogType="product"`.
