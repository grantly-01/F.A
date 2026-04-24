/**
 * Funding Aggregator — Animated Stars Background
 * Creates a parallax star field on canvas
 */
(function() {
  const canvas = document.getElementById('starsCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let stars = [];
  let shootingStars = [];
  let w, h;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }

  function createStars(count) {
    stars = [];
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * 1.5 + 0.3,
        speed: Math.random() * 0.3 + 0.05,
        opacity: Math.random() * 0.8 + 0.2,
        twinkleSpeed: Math.random() * 0.02 + 0.005,
        twinkleDir: Math.random() > 0.5 ? 1 : -1,
      });
    }
  }

  function createShootingStar() {
    if (Math.random() > 0.997) {
      shootingStars.push({
        x: Math.random() * w,
        y: Math.random() * h * 0.5,
        len: Math.random() * 80 + 40,
        speed: Math.random() * 8 + 6,
        angle: Math.PI / 4 + Math.random() * 0.3,
        opacity: 1,
      });
    }
  }

  function drawStars() {
    for (const s of stars) {
      s.opacity += s.twinkleSpeed * s.twinkleDir;
      if (s.opacity >= 1 || s.opacity <= 0.2) s.twinkleDir *= -1;
      s.y += s.speed;
      if (s.y > h) { s.y = 0; s.x = Math.random() * w; }

      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200, 210, 255, ${s.opacity})`;
      ctx.fill();
    }
  }

  function drawShootingStars() {
    for (let i = shootingStars.length - 1; i >= 0; i--) {
      const ss = shootingStars[i];
      const endX = ss.x + Math.cos(ss.angle) * ss.len;
      const endY = ss.y + Math.sin(ss.angle) * ss.len;

      const gradient = ctx.createLinearGradient(ss.x, ss.y, endX, endY);
      gradient.addColorStop(0, `rgba(167, 139, 250, ${ss.opacity})`);
      gradient.addColorStop(1, 'rgba(167, 139, 250, 0)');

      ctx.beginPath();
      ctx.moveTo(ss.x, ss.y);
      ctx.lineTo(endX, endY);
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 2;
      ctx.stroke();

      ss.x += Math.cos(ss.angle) * ss.speed;
      ss.y += Math.sin(ss.angle) * ss.speed;
      ss.opacity -= 0.015;

      if (ss.opacity <= 0 || ss.x > w || ss.y > h) {
        shootingStars.splice(i, 1);
      }
    }
  }

  // Nebula glow spots
  function drawNebula() {
    const spots = [
      { x: w * 0.2, y: h * 0.3, r: 200, color: 'rgba(139, 92, 246, 0.03)' },
      { x: w * 0.8, y: h * 0.6, r: 250, color: 'rgba(59, 130, 246, 0.02)' },
      { x: w * 0.5, y: h * 0.8, r: 180, color: 'rgba(6, 182, 212, 0.02)' },
    ];
    for (const spot of spots) {
      const g = ctx.createRadialGradient(spot.x, spot.y, 0, spot.x, spot.y, spot.r);
      g.addColorStop(0, spot.color);
      g.addColorStop(1, 'transparent');
      ctx.fillStyle = g;
      ctx.fillRect(spot.x - spot.r, spot.y - spot.r, spot.r * 2, spot.r * 2);
    }
  }

  function animate() {
    ctx.clearRect(0, 0, w, h);
    drawNebula();
    drawStars();
    createShootingStar();
    drawShootingStars();
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', () => { resize(); createStars(250); });
  resize();
  createStars(250);
  animate();
})();
