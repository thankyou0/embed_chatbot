# Chatbot Widget

Preact-based embeddable chat widget (<50KB gzipped).

## Development

```bash
pnpm dev
```

## Build

```bash
pnpm build
```

The built widget will be in `dist/` directory.

## Usage

### Auto-initialization

Add the script tag with data attributes:

```html
<script
  src="path/to/chatbot-widget.js"
  data-auto-init="true"
  data-api-url="http://localhost:8000"
  data-tenant-id="your-tenant-id"
></script>
```

### Manual initialization

```javascript
ChatbotWidget.init({
  apiUrl: 'http://localhost:8000',
  tenantId: 'your-tenant-id',
  theme: {
    primaryColor: '#007bff',
    position: 'bottom-right'
  }
})
```

