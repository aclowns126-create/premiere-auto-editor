function wire(buttonId, handler) {
  document.getElementById(buttonId).addEventListener("click", async () => {
    try {
      await handler();
    } catch (err) {
      logError("오류", err);
    }
  });
}

async function exploreApi() {
  log(`premierepro 모듈 최상위 키: ${Object.keys(ppro).join(", ")}`);

  try {
    const project = await getActiveProject();
    log(`Project 인스턴스 메서드: ${Object.getOwnPropertyNames(Object.getPrototypeOf(project)).join(", ")}`);
    const sequence = await project.getActiveSequence();
    if (sequence) {
      log(`Sequence 인스턴스 메서드: ${Object.getOwnPropertyNames(Object.getPrototypeOf(sequence)).join(", ")}`);
    } else {
      log("활성 시퀀스가 없어 Sequence API는 건너뜁니다.");
    }
  } catch (err) {
    logError("API 탐색 중 오류", err);
  }
}

wire("btnCreateSequence", createSequenceFromSelectedClips);
wire("btnCutAtMarkers", cutAtMarkers);
wire("btnImportSubtitles", importSubtitles);
wire("btnExploreApi", exploreApi);
wire("btnPickVideo", pickVideoFile);
wire("btnRunAutoEdit", runAiAutoEdit);

log("Auto Editor 패널이 로드되었습니다.");
