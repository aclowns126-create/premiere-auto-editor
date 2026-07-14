const CUT_MARKER_PREFIX = "CUT";

async function collectCutRanges(sequence) {
  const markers = await sequence.getMarkers();
  const ranges = [];

  let marker = await markers.getFirstMarker();
  while (marker) {
    const name = (await marker.getName()) || "";
    if (name.toUpperCase().startsWith(CUT_MARKER_PREFIX)) {
      const start = await marker.getStart();
      const end = await marker.getEnd();
      ranges.push({ startSeconds: start.seconds, endSeconds: end.seconds });
    }
    marker = await markers.getNextMarker(marker);
  }

  return ranges;
}

function overlaps(itemStart, itemEnd, rangeStart, rangeEnd) {
  return itemStart < rangeEnd && itemEnd > rangeStart;
}

async function cutAtMarkers() {
  const { project, sequence } = await getActiveSequence();

  const ranges = await collectCutRanges(sequence);
  if (ranges.length === 0) {
    throw new Error(
      `"${CUT_MARKER_PREFIX}"로 시작하는 마커를 찾지 못했습니다. 타임라인에 마커를 먼저 찍어주세요.`
    );
  }

  const videoTracks = await sequence.getVideoTracks();
  const audioTracks = await sequence.getAudioTracks();
  const allTracks = [...videoTracks, ...audioTracks];

  const itemsToRemove = [];
  for (const track of allTracks) {
    const trackItems = await track.getTrackItems();
    for (const item of trackItems) {
      const start = await item.getStartTime();
      const end = await item.getEndTime();
      const hit = ranges.some((r) =>
        overlaps(start.seconds, end.seconds, r.startSeconds, r.endSeconds)
      );
      if (hit) {
        itemsToRemove.push(item);
      }
    }
  }

  if (itemsToRemove.length === 0) {
    throw new Error("마커 구간과 겹치는 클립을 찾지 못했습니다.");
  }

  await project.lockedAccess(async () => {
    await project.executeTransaction((compoundAction) => {
      for (const item of itemsToRemove) {
        const action = sequence.createRemoveItemAction(item, true);
        compoundAction.addAction(action);
      }
    }, "CUT 마커 구간 삭제");
  });

  log(`마커 ${ranges.length}개 구간, 클립 ${itemsToRemove.length}개 리플 삭제 완료.`);
}
