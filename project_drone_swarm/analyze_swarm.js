import fs from "fs";
import readline from "readline";
import { GoogleGenerativeAI } from "@google/generative-ai";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

const CHUNK_SIZE = 100; // lines per request
const SYSTEM_PROMPT = `You are analyzing logs from a multi-agent drone simulation.

Context:
- 5 autonomous drones
- Simple local rules only
- No global coordination
- No learning or optimization

Your task:
1. Infer behavioral patterns ONLY from the logs provided.
2. Identify any emergent group behavior.
3. Detect correlations between:
   - battery level
   - proximity to other drones
   - movement decisions
4. Describe behaviors that were NOT explicitly programmed.
5. Formulate any discovered behavior as a hypothesis or informal rule.

Constraints:
- Do NOT assume intent or purposeful behavior.
- Do NOT suggest improvements.
- Act as a scientific observer only.`;

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) {
  console.error("ERROR: GEMINI_API_KEY not found in .env file!");
  process.exit(1);
}

const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

class SwarmAnalyzer {
  constructor() {
    this.logFile = "swarm_log.jsonl";
    this.reportFile = "emergent_report.md";
    this.analysisHistory = [];
    this.observations = [];
  }

  async analyzeChunk(lines, chunkNum) {
    /**
     * Send a chunk of log lines to Gemini for analysis
     */
    if (lines.length === 0) return;

    const userPrompt = `Analyze this chunk of drone simulation logs (${lines.length} entries, chunk ${chunkNum}):

${lines.slice(0, Math.min(20, lines.length)).join("\n")}
... (${lines.length} total lines) ...

Focus on: What patterns do you see in drone positions, movements, battery levels, and proximity behaviors?`;

    try {
      console.log(`[Chunk ${chunkNum}] Analyzing ${lines.length} lines...`);

      const response = await model.generateContent({
        contents: [
          {
            role: "user",
            parts: [{ text: userPrompt }],
          },
        ],
        systemInstruction: SYSTEM_PROMPT,
      });

      const analysis = response.response.text();
      this.observations.push({
        chunk: chunkNum,
        lines: lines.length,
        analysis,
      });

      console.log(`[Chunk ${chunkNum}] ✓ Analysis received.`);
    } catch (error) {
      console.error(`[Chunk ${chunkNum}] Error:`, error.message);
    }
  }

  async readAndAnalyze() {
    /**
     * Stream the JSONL file in chunks
     */
    return new Promise((resolve) => {
      const rl = readline.createInterface({
        input: fs.createReadStream(this.logFile),
        crlfDelay: Infinity,
      });

      let chunk = [];
      let chunkCount = 0;
      let pendingRequests = 0;

      rl.on("line", (line) => {
        chunk.push(line);

        if (chunk.length >= CHUNK_SIZE) {
          pendingRequests++;
          const currentChunk = chunk;
          const currentNum = chunkCount;
          
          (async () => {
            await this.analyzeChunk(currentChunk, currentNum);
            pendingRequests--;
          })();
          
          chunk = [];
          chunkCount++;
        }
      });

      rl.on("close", async () => {
        // Process remaining lines
        if (chunk.length > 0) {
          pendingRequests++;
          await this.analyzeChunk(chunk, chunkCount);
          pendingRequests--;
        }
        
        // Wait for all pending requests to complete
        while (pendingRequests > 0) {
          await new Promise(r => setTimeout(r, 100));
        }
        
        resolve();
      });

      rl.on("error", (err) => {
        console.error("File read error:", err);
        resolve();
      });
    });
  }

  async generateReport() {
    /**
     * Generate final markdown report
     */
    const timestamp = new Date().toISOString();

    const report = `# Drone Swarm Emergent Behavior Analysis Report

**Generated:** ${timestamp}

**Data Source:** swarm_log.jsonl (5 drones, 1000 timesteps, 5000 log entries)

**Analysis Method:** Gemini AI behavioral observer (no rules provided to model)

---

## Chunk-by-Chunk Observations

${this.observations.map((obs) => `### Chunk ${obs.chunk} (${obs.lines} lines)\n\n${obs.analysis}`).join("\n\n---\n\n")}

---

**End of Report**`;

    fs.writeFileSync(this.reportFile, report, "utf8");
    console.log(`\n Report generated: ${this.reportFile}`);
  }

  async run() {
    /**
     * Main analysis pipeline
     */
    console.log("🤖 Drone Swarm Behavioral Analysis Pipeline");
    console.log("==========================================\n");

    if (!fs.existsSync(this.logFile)) {
      console.error(`Error: ${this.logFile} not found!`);
      process.exit(1);
    }

    console.log(` Analyzing ${this.logFile}...`);
    console.log(`🔄 Processing in chunks of ${CHUNK_SIZE} lines...\n`);

    // Stream and analyze chunks
    await this.readAndAnalyze();

    console.log("\n All chunks analyzed.");

    // Generate final report
    await this.generateReport();

    console.log("\n📋 Analysis complete!");
  }
}

// Main execution
const analyzer = new SwarmAnalyzer();
analyzer.run().catch(console.error);
