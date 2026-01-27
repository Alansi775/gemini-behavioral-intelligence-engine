# Gemini 3 Hackathon Backend

A clean, production-ready Node.js backend for testing Google Gemini 3 API integration.

## Project Structure

```
gemini3-hackathon/
└── backend/
    ├── src/
    │   ├── index.js       # Express server & endpoints
    │   └── gemini.js      # Gemini API integration
    ├── package.json       # Dependencies
    ├── .env              # Environment variables
    └── README.md         # This file
```

## Installation

1. **Navigate to the backend directory:**
   ```bash
   cd ~/Desktop/gemini3-hackathon/backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API Key:**
   - Open `.env` file
   - Replace `your_api_key_here` with your actual Google Gemini 3 API key
   ```
   GEMINI_API_KEY=sk-your-actual-api-key-here
   ```

## Running the Server

### Development Mode (with auto-reload)
```bash
npm run dev
```

### Production Mode
```bash
npm start
```

The server will start on `http://localhost:3000`

## Testing the API

### Health Check
```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "OK",
  "message": "Server is running"
}
```

### Test Gemini 3 Connection

**Using default prompt:**
```bash
curl -X POST http://localhost:3000/test \
  -H "Content-Type: application/json"
```

**With custom prompt:**
```bash
curl -X POST http://localhost:3000/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2+2?"}'
```

Example response:
```json
{
  "success": true,
  "prompt": "Confirm Gemini 3 is working",
  "response": "Gemini 3 is working correctly!",
  "timestamp": "2026-01-02T10:30:00.000Z"
}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health check |
| POST | `/test` | Test Gemini 3 API (accepts optional `prompt` in body) |

## Error Handling

The API includes comprehensive error handling:
- Missing API key validation
- Gemini API failures
- Invalid requests
- 404 for undefined endpoints

## Technologies Used

- **Node.js** - JavaScript runtime
- **Express.js** - Web framework
- **@google/generative-ai** - Official Gemini API client
- **dotenv** - Environment variable management
- **nodemon** - Development auto-reload

## Next Steps

This is the foundation for your Gemini 3 hackathon project. From here you can:
1. Add more sophisticated prompts and logic
2. Build additional endpoints for your specific use case
3. Add a frontend when ready
4. Integrate with a database
5. Deploy to production (Vercel, Railway, Heroku, etc.)

## Important Notes

-  Uses ES Modules (type: "module")
-  No hardcoded secrets
-  Clean, minimal codebase
-  Production-ready error handling
-  Ready for scaling
