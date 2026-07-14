// Thin wrapper around Adobe's Premiere Pro UXP scripting module.
// NOTE: the exact method names on Project/Sequence/TrackItem have changed
// across Premiere Pro releases. If a call here throws "is not a function",
// use the "현재 설치된 API 구조 살펴보기" button in the panel to inspect
// what your installed version actually exposes, then adjust the call below.
const ppro = require("premierepro");

async function getActiveProject() {
  const project = await ppro.Project.getActiveProject();
  if (!project) {
    throw new Error("열려 있는 프로젝트가 없습니다.");
  }
  return project;
}

async function getActiveSequence() {
  const project = await getActiveProject();
  const sequence = await project.getActiveSequence();
  if (!sequence) {
    throw new Error("활성 시퀀스가 없습니다. 타임라인을 하나 열어주세요.");
  }
  return { project, sequence };
}
