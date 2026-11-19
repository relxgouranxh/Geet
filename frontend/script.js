const $ = (s) => document.querySelector(s);
const state = { industry: "Both" };
const EMOJI = { happy: "😄", calm: "😌", sad: "😢", party: "🎉", romantic: "💖" };
let file = null;

// ---------- Upload ----------
const drop = $("#drop"), input = $("#file");
drop.onclick = () => input.click();
input.onchange = () => setFile(input.files[0]);
drop.ondragover = (e) => { e.preventDefault(); drop.classList.add("over"); };
drop.ondragleave = () => drop.classList.remove("over");
drop.ondrop = (e) => {
  e.preventDefault(); drop.classList.remove("over");
  setFile(e.dataTransfer.files[0]);
};

function setFile(f) {
  if (!f || !f.type.startsWith("image/")) return;
  file = f;
  $("#preview").src = URL.createObjectURL(f);
  $("#preview").hidden = false;
  $("#hint").hidden = true;
  $("#go").disabled = false;
}

// ---------- Filters ----------
document.querySelectorAll(".pills").forEach((group) => {
  group.onclick = (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    group.querySelectorAll("button").forEach((x) => x.classList.remove("on"));
    b.classList.add("on");
    state[group.dataset.key] = b.dataset.v;
  };
});

// ---------- Request ----------
async function run() {
  if (!file) return;
  const panel = document.querySelector(".panel");
  const err = $("#error"), status = $("#status");
  err.hidden = true;
  panel.classList.add("loading");
  $("#drop").classList.add("scanning");
  $("#go").textContent = "Searching...";
  status.textContent = "Reading the mood of your photo...";
  status.hidden = false;

  try {
    const fd = new FormData();
    fd.append("image", file);
    fd.append("industry", state.industry);

    const res = await fetch("/recommend", { method: "POST", body: fd });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Server error");

    renderMoods(json.moods);
    renderSongs(json.songs);
    $("#results").hidden = false;
    $("#shuffle").hidden = false;
    $("#results").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    err.textContent = "Error: " + (e.message || "Something went wrong");
    err.hidden = false;
  } finally {
    status.hidden = true;
    panel.classList.remove("loading");
    $("#drop").classList.remove("scanning");
    $("#go").textContent = "Find songs";
  }
}

$("#go").onclick = run;
$("#shuffle").onclick = run;   // same photo, naye random songs

// ---------- Render ----------
function renderMoods(moods) {
  const box = $("#moods");
  box.innerHTML = "";
  Object.entries(moods).sort((a, b) => b[1] - a[1]).forEach(([name, p]) => {
    const row = document.createElement("div");
    row.className = "mood-row";
    row.innerHTML = `<span>${EMOJI[name] || ""} ${name}</span>
                     <div class="bar"><i></i></div><span>${Math.round(p * 100)}%</span>`;
    box.appendChild(row);
    requestAnimationFrame(() => (row.querySelector("i").style.width = p * 100 + "%"));
  });
}

function renderSongs(songs) {
  const box = $("#songs");
  box.innerHTML = "";
  songs.forEach((s, i) => {
    const div = document.createElement("div");
    div.className = "song";
    div.style.animationDelay = `${i * 70}ms`;
    const label = document.createElement("small");
    label.textContent = `${s.track_name} · ${s.artist_name} · ${s.industry}`;
    const frame = document.createElement("iframe");
    frame.src = `https://open.spotify.com/embed/track/${s.track_id}`;
    frame.loading = "lazy";
    frame.allow = "encrypted-media";
    div.append(label, frame);
    box.appendChild(div);
  });
}