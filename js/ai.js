const AI_SERVER_URL = "http://localhost:8787";

let pickedVideoPath = null;

async function pickVideoFile() {
  const { localFileSystem } = require("uxp").storage;
  const file = await localFileSystem.getFileForOpening({
    types: ["mp4", "mov", "mxf", "avi"],
  });
  if (!file) {
    log("영상 파일 선택이 취소되었습니다.");
    return;
  }
  pickedVideoPath = file.nativePath;
  document.getElementById("videoStatus").textContent = `선택됨: ${file.name}`;
  log(`영상 파일 선택: ${file.name}`);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pollJob(jobId) {
  let seenLogLines = 0;
  while (true) {
    const res = await fetch(`${AI_SERVER_URL}/jobs/${jobId}`);
    if (!res.ok) {
      throw new Error(`작업 상태 조회 실패 (${res.status})`);
    }
    const job = await res.json();

    for (let i = seenLogLines; i < job.log.length; i++) {
      log(job.log[i]);
    }
    seenLogLines = job.log.length;

    if (job.status === "done") {
      return job.result;
    }
    if (job.status === "failed") {
      throw new Error(job.error || "작업이 실패했습니다.");
    }

    await sleep(2000);
  }
}

async function runAiAutoEdit() {
  if (!pickedVideoPath) {
    throw new Error("먼저 원본 영상 파일을 선택해주세요.");
  }
  const instruction = document.getElementById("instructionInput").value.trim();
  if (!instruction) {
    throw new Error("어떤 편집을 원하는지 지시 문장을 입력해주세요.");
  }

  log("보조 서버(localhost:8787)에 자동 편집 작업을 요청합니다...");
  const startRes = await fetch(`${AI_SERVER_URL}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ videoPath: pickedVideoPath, instruction }),
  });
  if (!startRes.ok) {
    const text = await startRes.text();
    throw new Error(`작업 시작 실패 (${startRes.status}): ${text}`);
  }
  const { jobId } = await startRes.json();
  log(`작업 시작됨 (id: ${jobId}). 음성 인식/분석에 시간이 걸릴 수 있습니다.`);

  const result = await pollJob(jobId);
  log(`엔진 완료: 컷 ${result.cutCount}개 제거, 유지 구간 ${result.keepSegmentCount}개, 자막 ${result.subtitleCount}개.`);

  const project = await getActiveProject();
  const rootItem = await project.getRootItem();
  await project.importFiles([result.xmlPath], true, rootItem, false);

  log("시퀀스 XML을 프로젝트로 가져왔습니다. Project 패널에서 새 시퀀스를 확인해주세요.");
  log(`자막 파일은 ${result.srtPath} 에 저장되어 있습니다. 필요하면 '.srt 자막 파일 가져오기'로 별도 임포트하세요.`);
}
