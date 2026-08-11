"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import sceneData from "./scenes.json";

type Mode = "sync" | "boards" | "script";
type ScriptBlock = { type: "action" | "character" | "parenthetical" | "dialogue"; text: string };
type Scene = { number: number; title: string; blocks: ScriptBlock[]; images: string[] };

const scenes = sceneData as Scene[];
const APP_VERSION = "v1.2.0";

export default function Home() {
  const [mode, setMode] = useState<Mode>("sync");
  const [sceneIndex, setSceneIndex] = useState(0);
  const [boardIndex, setBoardIndex] = useState(0);
  const [query, setQuery] = useState("");
  const [offlineStatus, setOfflineStatus] = useState("Offline");
  const [menuOpen, setMenuOpen] = useState(false);
  const [portraitSplit, setPortraitSplit] = useState(58);
  const [landscapeSplit, setLandscapeSplit] = useState(56);
  const scriptRef = useRef<HTMLDivElement>(null);
  const splitRef = useRef<HTMLDivElement>(null);
  const sceneRefs = useRef<Record<number, HTMLElement | null>>({});
  const programmaticScroll = useRef(false);
  const releaseScrollTimer = useRef<number | null>(null);
  const scene = scenes[sceneIndex];

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase().replace(/^s(?:cene)?\s*/, "");
    if (!q) return [];
    return scenes.filter((item) =>
      String(item.number).startsWith(q) || item.title.toLowerCase().includes(q)
    ).slice(0, 8);
  }, [query]);

  const jumpTo = (index: number, scrollText = true, targetBoard = 0) => {
    const safe = Math.max(0, Math.min(scenes.length - 1, index));
    setSceneIndex(safe);
    setBoardIndex(Math.max(0, Math.min(targetBoard, scenes[safe].images.length - 1)));
    setQuery("");
    if (scrollText) {
      programmaticScroll.current = true;
      if (releaseScrollTimer.current) window.clearTimeout(releaseScrollTimer.current);
      requestAnimationFrame(() => {
        const panel = scriptRef.current;
        const target = sceneRefs.current[scenes[safe].number];
        if (panel && target) {
          panel.scrollTop += target.getBoundingClientRect().top - panel.getBoundingClientRect().top;
        }
        releaseScrollTimer.current = window.setTimeout(() => {
          programmaticScroll.current = false;
        }, 40);
      });
    }
  };

  const stepBoard = (direction: -1 | 1) => {
    const nextBoard = boardIndex + direction;
    if (nextBoard >= 0 && nextBoard < scene.images.length) {
      setBoardIndex(nextBoard);
      return;
    }
    let nextScene = sceneIndex + direction;
    while (nextScene >= 0 && nextScene < scenes.length && scenes[nextScene].images.length === 0) nextScene += direction;
    if (nextScene >= 0 && nextScene < scenes.length) {
      const target = direction > 0 ? 0 : scenes[nextScene].images.length - 1;
      jumpTo(nextScene, true, target);
    }
  };

  const submitSearch = () => {
    const exact = scenes.findIndex((item) => item.number === Number(query.replace(/\D/g, "")));
    if (exact >= 0) jumpTo(exact);
    else if (matches[0]) jumpTo(scenes.indexOf(matches[0]));
  };

  const onScriptScroll = () => {
    if (programmaticScroll.current) return;
    const panel = scriptRef.current;
    if (!panel) return;
    // A scene changes only when its heading reaches the first line of the script pane.
    // A larger marker skips very short scenes.
    const marker = panel.scrollTop + 3;
    let active = 0;
    for (let i = 0; i < scenes.length; i += 1) {
      const node = sceneRefs.current[scenes[i].number];
      if (node && node.offsetTop <= marker) active = i;
      else break;
    }
    if (active !== sceneIndex) {
      setSceneIndex(active);
      setBoardIndex(0);
    }
  };

  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js");
      const onMessage = (event: MessageEvent) => {
        if (event.data?.type === "CACHE_PROGRESS") setOfflineStatus(`${event.data.done}/${event.data.total}`);
        if (event.data?.type === "CACHE_COMPLETE") setOfflineStatus("Ready offline");
      };
      navigator.serviceWorker.addEventListener("message", onMessage);
      return () => navigator.serviceWorker.removeEventListener("message", onMessage);
    }
  }, []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.target as HTMLElement)?.tagName === "INPUT") return;
      if (event.key === "ArrowUp") jumpTo(sceneIndex - 1);
      if (event.key === "ArrowDown") jumpTo(sceneIndex + 1);
      if (event.key === "ArrowLeft") stepBoard(-1);
      if (event.key === "ArrowRight") stepBoard(1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sceneIndex, scene.images.length]);

  const downloadOffline = async () => {
    if (!("serviceWorker" in navigator)) return setOfflineStatus("Not supported");
    setOfflineStatus("Preparing…");
    const registration = await navigator.serviceWorker.ready;
    const worker = registration.active;
    const urls = Array.from(new Set(scenes.flatMap(item => item.images)));
    worker?.postMessage({ type: "CACHE_ALL", urls });
  };

  const board = scene.images[boardIndex];

  const resizeSplit = (event: React.PointerEvent<HTMLDivElement>) => {
    const container = splitRef.current;
    if (!container) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    const update = (clientX: number, clientY: number) => {
      const rect = container.getBoundingClientRect();
      const landscape = window.matchMedia("(orientation: landscape) and (max-height: 650px)").matches;
      const raw = landscape
        ? ((clientX - rect.left) / rect.width) * 100
        : ((clientY - rect.top) / rect.height) * 100;
      const value = Math.round(Math.max(35, Math.min(70, raw)));
      if (landscape) setLandscapeSplit(value);
      else setPortraitSplit(value);
    };
    update(event.clientX, event.clientY);
    const move = (moveEvent: PointerEvent) => update(moveEvent.clientX, moveEvent.clientY);
    const end = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", end);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", end, { once: true });
  };

  return (
    <main className={`reader mode-${mode}`} style={{ "--portrait-split": `${portraitSplit}%`, "--landscape-split": `${landscapeSplit}%` } as React.CSSProperties}>
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">PC</span>
          <div><strong>Painting Christmas With You <em className="version">{APP_VERSION}</em></strong><small>Interactive storyboard reader</small></div>
        </div>

        <div className="scene-search">
          <span>⌕</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => event.key === "Enter" && submitSearch()}
            placeholder="Jump to scene…"
            aria-label="Search scenes"
          />
          {matches.length > 0 && (
            <div className="results">
              {matches.map((item) => <button key={item.number} onClick={() => jumpTo(scenes.indexOf(item))}><b>S{item.number}</b><span>{item.title}</span></button>)}
            </div>
          )}
        </div>

        <button className="mobile-menu-toggle" onClick={() => setMenuOpen(value => !value)} aria-expanded={menuOpen} aria-controls="view-menu">View <span>{menuOpen ? "▴" : "▾"}</span></button>
        <nav id="view-menu" className={`modes ${menuOpen ? "open" : ""}`} aria-label="View mode">
          <button className="offline-button" onClick={downloadOffline}>{offlineStatus}</button>
          <button className={mode === "sync" ? "active" : ""} onClick={() => { setMode("sync"); setMenuOpen(false); }}>Split</button>
          <button className={mode === "boards" ? "active" : ""} onClick={() => { setMode("boards"); setMenuOpen(false); }}>Boards</button>
          <button className={mode === "script" ? "active" : ""} onClick={() => { setMode("script"); setMenuOpen(false); }}>Script</button>
        </nav>
      </header>

      <section className="scene-bar">
        <button className="scene-arrow" onClick={() => jumpTo(sceneIndex - 1)} disabled={sceneIndex === 0} aria-label="Previous scene">←</button>
        <div className="scene-identity"><span>SCENE {scene.number}</span><strong>{scene.title}</strong></div>
        <div className="progress"><span>{sceneIndex + 1} / {scenes.length}</span><i style={{ width: `${((sceneIndex + 1) / scenes.length) * 100}%` }} /></div>
        <button className="scene-arrow" onClick={() => jumpTo(sceneIndex + 1)} disabled={sceneIndex === scenes.length - 1} aria-label="Next scene">→</button>
      </section>

      <div className="content-split" ref={splitRef}>
      {mode !== "script" && (
        <section className="board-stage">
          {board ? (
            <div className="board-frame">
              <img src={board} alt={`Storyboard for scene ${scene.number}, board ${boardIndex + 1}`} />
              <button className="board-arrow left" onClick={() => stepBoard(-1)} disabled={sceneIndex === 0 && boardIndex === 0}>‹</button>
              <button className="board-arrow right" onClick={() => stepBoard(1)} disabled={sceneIndex === scenes.length - 1 && boardIndex === scene.images.length - 1}>›</button>
              {scene.images.length > 1 && <div className="board-count">{boardIndex + 1} / {scene.images.length}</div>}
            </div>
          ) : <div className="no-board"><span>SCENE {scene.number}</span><p>No storyboard artwork for this scene.</p></div>}
          {scene.images.length > 1 && <div className="filmstrip">{scene.images.map((image, index) => <button key={image} className={index === boardIndex ? "selected" : ""} onClick={() => setBoardIndex(index)}><img src={image} alt="" /></button>)}</div>}
        </section>
      )}

      {mode === "sync" && <div className="split-handle" onPointerDown={resizeSplit} role="separator" aria-label="Resize storyboard and screenplay panes"><span /></div>}

      {mode !== "boards" && (
        <section className="script-panel" ref={scriptRef} onScroll={onScriptScroll}>
          <div className="script-page">
            {scenes.map((item) => (
              <article key={item.number} ref={(node) => { sceneRefs.current[item.number] = node; }} className={item.number === scene.number ? "current" : ""}>
                <div className="script-heading"><span>{item.number}</span><h2>{item.title}</h2><span>{item.number}</span></div>
                <div className="script-copy">
                  {item.blocks.map((block, index) => <div key={`${block.type}-${index}`} className={`screenplay-${block.type}`}>{block.text}</div>)}
                </div>
                <div className="scene-end">END SCENE {item.number}</div>
              </article>
            ))}
          </div>
        </section>
      )}
      </div>
    </main>
  );
}
