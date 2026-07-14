async function importSubtitles() {
  const { localFileSystem } = require("uxp").storage;

  const file = await localFileSystem.getFileForOpening({
    types: ["srt", "vtt"],
  });
  if (!file) {
    log("자막 파일 선택이 취소되었습니다.");
    return;
  }

  const project = await getActiveProject();
  const rootItem = await project.getRootItem();

  const imported = await project.importFiles(
    [file.nativePath],
    true,
    rootItem,
    false
  );

  log(`자막 파일을 프로젝트로 가져왔습니다: ${file.name}`);
  log("Project 패널에서 자막 클립을 확인한 뒤, 타임라인의 자막 트랙으로 드래그해주세요.");
  return imported;
}
