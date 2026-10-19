/* Scientific citation links aligned with the contained Manim video. */
(() => {
  const data = JSON.parse(document.getElementById('paper-link-data').textContent);
  const layer = document.createElement('div');
  layer.className = 'paper-links-layer';
  layer.setAttribute('aria-label', 'Scientific references');
  document.body.append(layer);
  const style = document.createElement('style');
  style.textContent = `
    .paper-links-layer { position:fixed; inset:0; pointer-events:none; z-index:20; }
    .paper-links-layer a { position:absolute; color:transparent; overflow:hidden;
      pointer-events:auto; cursor:pointer; font-size:1px; border-radius:2px; }
    .paper-links-layer a:hover { box-shadow:0 1px #245774; }
    .paper-links-layer a:focus-visible { outline:2px solid #245774; outline-offset:4px; }
  `;
  document.head.append(style);

  function update() {
    layer.replaceChildren();
    if (Reveal.isOverview()) return;
    const index = Reveal.getIndices().h;
    const section = document.querySelectorAll('.slides > section')[index];
    const source = section?.getAttribute('data-background-video');
    const video = [...document.querySelectorAll('video')].find(v =>
      source && v.currentSrc.endsWith(source.split('/').pop()));
    if (!video || !Number.isFinite(video.duration) || video.currentTime < video.duration - .07) return;
    const box = video.getBoundingClientRect();
    const scale = Math.min(box.width / video.videoWidth, box.height / video.videoHeight);
    const width = video.videoWidth * scale, height = video.videoHeight * scale;
    const left = box.left + (box.width - width) / 2;
    const top = box.top + (box.height - height) / 2;
    for (const ref of data[index] || []) {
      const link = document.createElement('a');
      link.href = ref.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = ref.label;
      link.setAttribute('aria-label', ref.label);
      link.title = ref.label;
      Object.assign(link.style, {
        left: `${left + ref.x * width}px`, top: `${top + ref.y * height}px`,
        width: `${ref.width * width}px`, height: `${ref.height * height}px`,
      });
      link.addEventListener('click', event => event.stopPropagation());
      layer.append(link);
    }
  }
  Reveal.on('ready', update);
  Reveal.on('slidechanged', update);
  Reveal.on('overviewshown', update);
  Reveal.on('overviewhidden', update);
  window.addEventListener('resize', update);
  document.addEventListener('ended', update, true);
  document.addEventListener('loadeddata', update, true);
  document.addEventListener('timeupdate', update, true);
  update();
})();
