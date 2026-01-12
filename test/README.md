# Chatbot Widget Test Site

This is a test website running on port 3005 to test your chatbot widget embed code.

## Setup Instructions

### 1. Get Your Chatbot ID

1. Open your chatbot dashboard: http://localhost:3000
2. Navigate to your chatbot → **Install** tab
3. Copy the `chatbotId` from the embed code shown there

### 2. Update the Embed Code

Open `test/index.html` and replace `YOUR_CHATBOT_ID_HERE` with your actual chatbot ID:

```html
<script src="http://localhost:3001/widget.umd.js"></script>
<script>
  ChatbotWidget.init({
    chatbotId: "your-actual-chatbot-id-here",  // ← Replace this
    apiUrl: "http://localhost:8000"
  });
</script>
```

### 3. Make Sure Services Are Running

```bash
# Check if services are running
docker-compose ps

# If not running, start them:
docker-compose up -d

# Make sure these services are up:
# - api (port 8000)
# - widget (port 3001)
```

### 4. Build the Widget (if needed)

If the widget hasn't been built yet:

```bash
# Build the widget
docker-compose exec widget pnpm run build

# Or build locally
cd apps/widget
pnpm install
pnpm run build
```

### 5. Start the Test Site

```bash
cd test
pnpm install
pnpm run dev
```

The test site will be available at: **http://localhost:3005**

### 6. Test the Widget

1. Open http://localhost:3005 in your browser
2. The chatbot widget should appear in the bottom-right corner
3. Click it to open and test the chat functionality

## Troubleshooting

### Widget not appearing?

1. **Check browser console** for errors
2. **Verify widget is accessible**: Open http://localhost:3001/widget.umd.js in browser
3. **Check API is running**: Open http://localhost:8000/health
4. **Verify chatbot ID**: Make sure the ID exists in your database

### CORS errors?

Make sure your API has CORS configured to allow requests from localhost:3005

### Widget file not found?

The widget needs to be built first. Run:
```bash
docker-compose exec widget pnpm run build
```

## Embed Code Format

The embed code matches the format shown in the Install tab:

```html
<script src="http://localhost:3001/widget.umd.js"></script>
<script>
  ChatbotWidget.init({
    chatbotId: "your-chatbot-id",
    apiUrl: "http://localhost:8000"
  });
</script>
```

**Note:** In production, replace `localhost` URLs with your actual domain.
