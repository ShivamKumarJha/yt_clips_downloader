(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  let lastHeight = 0;
  let sameCount = 0;

  console.log("Starting auto-scroll...");

  while (sameCount < 3) {
    window.scrollTo(0, document.documentElement.scrollHeight);

    await sleep(3000);

    const newHeight = document.documentElement.scrollHeight;

    console.log("Scrolled:", newHeight);

    if (newHeight === lastHeight) {
      sameCount++;
      console.log(`No new content (${sameCount}/5)`);
    } else {
      sameCount = 0;
      lastHeight = newHeight;
    }
  }

  console.log("Finished loading clips.");

  const clips = [...document.querySelectorAll('a')]
    .map(a => a.href)
    .filter(h => h && h.includes('/clip/'));

  const uniqueClips = [...new Set(clips)];

  const data = {
    exportedAt: new Date().toISOString(),
    total: uniqueClips.length,
    clips: uniqueClips
  };

  const blob = new Blob(
    [JSON.stringify(data, null, 2)],
    { type: 'application/json' }
  );

  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = `youtube-clips-${Date.now()}.json`;

  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  URL.revokeObjectURL(url);

  console.log(`Saved ${uniqueClips.length} clips.`);
})();