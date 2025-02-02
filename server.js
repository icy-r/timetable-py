const express = require("express");
const http = require("http");
const fs = require("fs");
const path = require("path");

const app = express();
const server = http.createServer(app);
const PORT = 3001;

// Serve static files
app.use(express.static("public"));

// GET /list returns available video files in the current directory
app.get("/list", (req, res) => {
  const videos = fs
    .readdirSync(__dirname)
    .filter((file) =>
      [".mkv", ".mp4", ".avi", ".mov", ".wmv"].some((ext) =>
        file.toLowerCase().endsWith(ext)
      )
    );
  res.json({ files: videos });
});

// GET /video/:filename streams the video with range support
app.get("/video/:filename", (req, res) => {
  const filePath = path.join(__dirname, req.params.filename);
  if (!fs.existsSync(filePath)) {
    return res.sendStatus(404);
  }

  // If file is .mkv, transmux using ffmpeg on-the-fly with improved error handling
  if (path.extname(filePath).toLowerCase() === ".mkv") {
    res.writeHead(200, {
      "Content-Type": "video/mp4",
    });
    const ffmpeg = require("child_process").spawn("ffmpeg", [
      "-err_detect",
      "ignore_err", // ignore minor errors
      "-i",
      filePath,
      "-c:v",
      "copy", // copy video stream if possible (transmuxing)
      "-c:a",
      "copy", // copy audio stream
      "-f",
      "mp4",
      "-movflags",
      "frag_keyframe+empty_moov",
      "pipe:1",
    ]);
    ffmpeg.stdout.pipe(res);
    ffmpeg.stderr.on("data", (data) => console.error(`ffmpeg: ${data}`));
    ffmpeg.on("close", (code) => {
      if (code !== 0) console.error("ffmpeg exited with code", code);
    });
  } else {
    // Existing range-based streaming for supported formats (like .mp4)
    const stat = fs.statSync(filePath);
    const fileSize = stat.size;
    const range = req.headers.range;

    if (range) {
      const parts = range.replace(/bytes=/, "").split("-");
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
      const chunkSize = end - start + 1;

      const file = fs.createReadStream(filePath, { start, end });
      res.writeHead(206, {
        "Content-Range": `bytes ${start}-${end}/${fileSize}`,
        "Accept-Ranges": "bytes",
        "Content-Length": chunkSize,
        "Content-Type": "video/mp4",
      });
      file.pipe(res);
    } else {
      res.writeHead(200, {
        "Content-Length": fileSize,
        "Content-Type": "video/mp4",
      });
      fs.createReadStream(filePath).pipe(res);
    }
  }
});

// Create public directory if it doesn't exist
if (!fs.existsSync("public")) {
  fs.mkdirSync("public");
}

// Start the server
server.listen(PORT, () => {
  console.log(`Server started at http://localhost:${PORT}`);
  console.log("Current time (UTC):", new Date().toISOString());
  console.log(
    "Current user:",
    process.env.USER || process.env.USERNAME || "unknown"
  );
});
