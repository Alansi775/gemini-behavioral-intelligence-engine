import express from "express";
import dotenv from "dotenv";

// Load environment variables FIRST
dotenv.config();

console.log(".env loaded successfully");
console.log("PORT:", process.env.PORT);
console.log("GEMINI_API_KEY:", process.env.GEMINI_API_KEY ? "✓ Loaded" : "✗ Missing");

// Dynamic import after dotenv.config()
const { geminiModel } = await import("./gemini.js");

const app = express();
app.use(express.json());

app.post("/test", async (req, res) => {
  try {
    const result = await geminiModel.generateContent(
      "Say hello and confirm Gemini 3 is working"
    );

    res.json({
      success: true,
      reply: result.response.text()
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(process.env.PORT || 3000, () => {
  console.log("Server running on port", process.env.PORT || 3000);
});
