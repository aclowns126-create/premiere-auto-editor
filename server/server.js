require("dotenv").config();
const express = require("express");
const cors = require("cors");
const { spawn } = require("child_process");
const path = require("path");
const crypto = require("crypto");
const fs = require("fs");

const PORT = process.env.PORT || 8787;
const PYTHON_BIN = process.env.PYTHON_BIN || "python";
const ENGINE_DIR = path.join(__dirname, "..", "engine");
const JOBS_DIR = path.join(__dirname, "jobs");

const app = express();
app.use(cors());
app.use(express.json());

const jobs = new Map();

function ensureJobsDir() {
  if (!fs.existsSync(JOBS_DIR)) {
    fs.mkdirSync(JOBS_DIR, { recursive: true });
  }
}

app.post("/jobs", (req, res) => {
  const { videoPath, instruction } = req.body || {};
  if (!videoPath || !instruction) {
    return res.status(400).json({ error: "videoPath와 instruction이 필요합니다." });
  }
  if (!fs.existsSync(videoPath)) {
    return res.status(400).json({ error: `영상 파일을 찾을 수 없습니다: ${videoPath}` });
  }

  ensureJobsDir();
  const jobId = crypto.randomUUID();
  const outDir = path.join(JOBS_DIR, jobId);
  fs.mkdirSync(outDir, { recursive: true });

  const job = { id: jobId, status: "running", log: [], result: null, error: null };
  jobs.set(jobId, job);

  const child = spawn(
    PYTHON_BIN,
    ["main.py", "--video", videoPath, "--instruction", instruction, "--out", outDir],
    { cwd: ENGINE_DIR }
  );

  const handleLine = (line) => {
    if (!line) return;
    if (line.startsWith("RESULT:")) {
      job.result = JSON.parse(line.slice("RESULT:".length));
    } else if (line.startsWith("ERROR:")) {
      job.error = line.slice("ERROR:".length);
    } else {
      job.log.push(line);
    }
  };

  const attach = (stream) => {
    let buffer = "";
    stream.on("data", (chunk) => {
      buffer += chunk.toString();
      const lines = buffer.split("\n");
      buffer = lines.pop();
      lines.forEach(handleLine);
    });
  };
  attach(child.stdout);
  attach(child.stderr);

  child.on("close", (code) => {
    job.status = code === 0 && job.result ? "done" : "failed";
    if (job.status === "failed" && !job.error) {
      job.error = `엔진 프로세스가 코드 ${code}로 종료되었습니다.`;
    }
  });

  res.json({ jobId });
});

app.get("/jobs/:id", (req, res) => {
  const job = jobs.get(req.params.id);
  if (!job) {
    return res.status(404).json({ error: "해당 작업을 찾을 수 없습니다." });
  }
  res.json(job);
});

app.listen(PORT, () => {
  console.log(`Premiere Auto Editor server listening on http://localhost:${PORT}`);
});
