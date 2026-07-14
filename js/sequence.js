async function createSequenceFromSelectedClips() {
  const project = await getActiveProject();

  let selection;
  try {
    selection = await project.getSelection();
  } catch (err) {
    throw new Error(
      "선택된 클립을 읽지 못했습니다. Project 패널에서 클립을 선택한 뒤 다시 시도해주세요. " +
        `(원인: ${err.message})`
    );
  }

  if (!selection || selection.length === 0) {
    throw new Error("Project 패널에서 클립을 하나 이상 선택해주세요.");
  }

  const sequenceName = `Auto Sequence ${new Date().toLocaleTimeString()}`;
  const rootItem = await project.getRootItem();

  const newSequence = await project.createSequenceFromClips(
    sequenceName,
    selection,
    rootItem
  );

  log(`시퀀스 "${sequenceName}" 생성 완료 (클립 ${selection.length}개).`);
  return newSequence;
}
