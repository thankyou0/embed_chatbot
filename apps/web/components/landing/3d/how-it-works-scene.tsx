"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Html, MeshDistortMaterial } from "@react-three/drei";
import * as THREE from "three";

/* ═══════════════════════════════════════════════════════════════
   Step colours
   ═══════════════════════════════════════════════════════════════ */
const STEP_COLORS = ["#10b981", "#14b8a6", "#06b6d4", "#a855f7"];

/* ═══════════════════════════════════════════════════════════════
   Ambient floating particles
   ═══════════════════════════════════════════════════════════════ */
function AmbientParticles({ count = 50 }: { count?: number }) {
  const ref = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 8;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 6;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 3 - 2;
    }
    return arr;
  }, [count]);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.rotation.y = Math.sin(clock.elapsedTime * 0.04) * 0.12;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.025} color="#34d399" transparent opacity={0.2} sizeAttenuation blending={THREE.AdditiveBlending} depthWrite={false} />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Step 1: Documents flying into knowledge orb — BIG
   ═══════════════════════════════════════════════════════════════ */
function UploadVisual() {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.3) * 0.12;
  });

  return (
    <group ref={groupRef}>
      {/* Central knowledge orb */}
      <mesh>
        <sphereGeometry args={[0.6, 32, 32]} />
        <MeshDistortMaterial
          color="#10b981"
          distort={0.3}
          speed={3}
          roughness={0.2}
          metalness={0.8}
          transparent
          opacity={0.85}
          emissive={new THREE.Color("#10b981")}
          emissiveIntensity={0.4}
        />
      </mesh>
      <mesh>
        <sphereGeometry args={[0.75, 16, 16]} />
        <meshBasicMaterial color="#10b981" transparent opacity={0.06} />
      </mesh>

      {/* Floating doc cards — large and spread */}
      {[
        { pos: [-1.3, 0.6, 0.2], type: "PDF", color: "#ef4444" },
        { pos: [1.2, -0.4, 0.5], type: "WEB", color: "#3b82f6" },
        { pos: [-0.8, -0.9, -0.3], type: "Q&A", color: "#10b981" },
        { pos: [0.9, 0.8, -0.4], type: "TXT", color: "#f59e0b" },
        { pos: [-1.5, -0.2, -0.5], type: "CSV", color: "#8b5cf6" },
      ].map((doc, i) => (
        <Float key={i} speed={1.5 + i * 0.3} rotationIntensity={0.25} floatIntensity={0.35}>
          <group position={doc.pos as [number, number, number]}>
            <mesh>
              <boxGeometry args={[0.38, 0.48, 0.02]} />
              <meshStandardMaterial
                color="#1e1e30"
                emissive={new THREE.Color(doc.color)}
                emissiveIntensity={0.25}
                metalness={0.3}
                roughness={0.7}
                transparent
                opacity={0.85}
              />
            </mesh>
            <Html center position={[0, 0, 0.015]} style={{ pointerEvents: "none" }}>
              <div style={{
                fontSize: "10px", fontWeight: 700, color: doc.color,
                fontFamily: "monospace", textShadow: `0 0 6px ${doc.color}`,
              }}>
                {doc.type}
              </div>
            </Html>
          </group>
        </Float>
      ))}

      {/* Absorption particle ring */}
      <AbsorptionRing />
    </group>
  );
}

/* Particles spiralling inward */
function AbsorptionRing() {
  const ref = useRef<THREE.Points>(null);
  const count = 30;

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const a = (i / count) * Math.PI * 2;
      const r = 1.5 + Math.random() * 0.5;
      arr[i * 3] = Math.cos(a) * r;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 0.8;
      arr[i * 3 + 2] = Math.sin(a) * r;
    }
    return arr;
  }, []);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.rotation.y = clock.elapsedTime * 0.3;
    const arr = (ref.current.geometry.attributes.position as THREE.BufferAttribute).array as Float32Array;
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      const dist = Math.sqrt(arr[i3] ** 2 + arr[i3 + 2] ** 2);
      if (dist > 0.15) {
        arr[i3] *= 0.998;
        arr[i3 + 2] *= 0.998;
      } else {
        const a = Math.random() * Math.PI * 2;
        const r = 1.5 + Math.random() * 0.5;
        arr[i3] = Math.cos(a) * r;
        arr[i3 + 2] = Math.sin(a) * r;
      }
    }
    (ref.current.geometry.attributes.position as THREE.BufferAttribute).needsUpdate = true;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.04} color="#34d399" transparent opacity={0.6} sizeAttenuation blending={THREE.AdditiveBlending} depthWrite={false} />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Step 2: Customization panel — BIG
   ═══════════════════════════════════════════════════════════════ */
function CustomizeVisual() {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.2) * 0.06;
  });

  return (
    <group ref={groupRef}>
      {/* Panel bg */}
      <mesh>
        <boxGeometry args={[2.6, 1.8, 0.04]} />
        <meshStandardMaterial color="#1a1a2e" metalness={0.4} roughness={0.6} transparent opacity={0.92} />
      </mesh>
      <mesh>
        <boxGeometry args={[2.64, 1.84, 0.035]} />
        <meshBasicMaterial color="#14b8a6" transparent opacity={0.04} />
      </mesh>

      {/* Rich UI */}
      <Html transform position={[0, 0, 0.025]} scale={0.055} style={{ pointerEvents: "none" }}>
        <div style={{
          width: "600px", padding: "20px", fontFamily: "system-ui, sans-serif",
        }}>
          <div style={{ fontSize: "15px", fontWeight: 700, color: "rgba(255,255,255,0.85)", marginBottom: "14px" }}>Customize Your Bot</div>
          {/* Color picker */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
            <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.45)", width: "55px" }}>Theme</span>
            <div style={{ display: "flex", gap: "8px" }}>
              {["#10b981", "#14b8a6", "#ec4899", "#f59e0b", "#3b82f6"].map((c, i) => (
                <div key={c} style={{
                  width: "24px", height: "24px", borderRadius: "50%", background: c,
                  border: i === 0 ? "2px solid rgba(255,255,255,0.6)" : "2px solid transparent",
                  boxShadow: i === 0 ? `0 0 8px ${c}` : "none",
                }} />
              ))}
            </div>
          </div>
          {/* Position */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
            <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.45)", width: "55px" }}>Position</span>
            <div style={{ padding: "4px 12px", borderRadius: "6px", background: "#059669", fontSize: "10px", color: "white" }}>Bottom Right</div>
            <div style={{ padding: "4px 12px", borderRadius: "6px", background: "rgba(255,255,255,0.05)", fontSize: "10px", color: "rgba(255,255,255,0.35)" }}>Bottom Left</div>
          </div>
          {/* Name */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
            <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.45)", width: "55px" }}>Name</span>
            <div style={{ padding: "5px 12px", borderRadius: "6px", background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", fontSize: "11px", color: "rgba(255,255,255,0.6)", flex: 1 }}>AI Assistant</div>
          </div>
          {/* Tone */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.45)", width: "55px" }}>Tone</span>
            <div style={{ display: "flex", gap: "6px" }}>
              {["Friendly", "Professional", "Casual"].map((t, i) => (
                <div key={t} style={{
                  padding: "4px 12px", borderRadius: "6px",
                  background: i === 0 ? "#059669" : "rgba(255,255,255,0.05)",
                  fontSize: "10px", color: i === 0 ? "white" : "rgba(255,255,255,0.35)",
                }}>{t}</div>
              ))}
            </div>
          </div>
        </div>
      </Html>
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Step 3: Code embed block — BIG
   ═══════════════════════════════════════════════════════════════ */
function EmbedVisual() {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.15) * 0.04;
    groupRef.current.position.y = Math.sin(clock.elapsedTime * 0.3) * 0.03;
  });

  return (
    <group ref={groupRef}>
      <mesh>
        <boxGeometry args={[2.6, 1.6, 0.035]} />
        <meshStandardMaterial color="#0d0d17" metalness={0.5} roughness={0.5} transparent opacity={0.92} />
      </mesh>
      <Html transform position={[0, 0, 0.02]} scale={0.05} style={{ pointerEvents: "none" }}>
        <div style={{
          width: "640px", padding: "20px",
          fontFamily: "'Fira Code', 'Consolas', monospace",
          border: "1px solid rgba(6,182,212,0.2)", borderRadius: "10px",
        }}>
          <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.25)", marginBottom: "10px" }}>{"<!-- Add to your HTML -->"}</div>
          <div style={{ fontSize: "13px", lineHeight: 1.8 }}>
            <span style={{ color: "#ec4899" }}>{"<script"}</span><br />
            <span style={{ paddingLeft: "16px" }}>
              <span style={{ color: "#06b6d4" }}>src</span>
              <span style={{ color: "rgba(255,255,255,0.4)" }}>=</span>
              <span style={{ color: "#22c55e" }}>{'"https://embed.chat/w.js"'}</span>
            </span><br />
            <span style={{ paddingLeft: "16px" }}>
              <span style={{ color: "#06b6d4" }}>data-bot-id</span>
              <span style={{ color: "rgba(255,255,255,0.4)" }}>=</span>
              <span style={{ color: "#22c55e" }}>{'"your-bot-id"'}</span>
            </span><br />
            <span style={{ color: "#ec4899" }}>{"></script>"}</span>
          </div>
          <div style={{
            marginTop: "16px", display: "inline-block",
            padding: "6px 16px", borderRadius: "6px",
            background: "#059669",
            fontSize: "11px", fontWeight: 600, color: "white",
            fontFamily: "system-ui, sans-serif",
          }}>
            📋 Copy to Clipboard
          </div>
        </div>
      </Html>
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Step 4: Live chat widget — BIG
   ═══════════════════════════════════════════════════════════════ */
function GoLiveVisual() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    meshRef.current.position.y = Math.sin(clock.elapsedTime * 0.5) * 0.05;
  });

  return (
    <group>
      <mesh ref={meshRef}>
        <boxGeometry args={[1.8, 2.4, 0.035]} />
        <meshStandardMaterial color="#1a1a2e" metalness={0.4} roughness={0.6} transparent opacity={0.92} />
      </mesh>
      <Html transform position={[0, 0.05, 0.02]} scale={0.048} style={{ pointerEvents: "none" }}>
        <div style={{
          width: "580px", overflow: "hidden", borderRadius: "14px",
          border: "1px solid rgba(16,185,129,0.15)",
          boxShadow: "0 20px 40px rgba(16,185,129,0.12)",
        }}>
          {/* Header */}
          <div style={{
            background: "linear-gradient(90deg, #059669, #0d9488)",
            padding: "14px 16px", display: "flex", alignItems: "center", gap: "10px",
          }}>
            <div style={{ width: "28px", height: "28px", borderRadius: "50%", background: "rgba(255,255,255,0.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "13px" }}>💬</div>
            <div>
              <div style={{ color: "white", fontSize: "13px", fontWeight: 600 }}>AI Assistant</div>
              <div style={{ color: "rgba(255,255,255,0.7)", fontSize: "9px", display: "flex", alignItems: "center", gap: "4px" }}>
                <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#4ade80", display: "inline-block" }} />
                Online — Live
              </div>
            </div>
          </div>
          {/* Chat body */}
          <div style={{ padding: "14px", background: "#1a1a2e" }}>
            {/* Bot message */}
            <div style={{ display: "flex", gap: "8px", marginBottom: "10px" }}>
              <div style={{ width: "20px", height: "20px", borderRadius: "50%", background: "rgba(16,185,129,0.2)", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "9px" }}>🤖</div>
              <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: "10px 10px 10px 2px", padding: "10px 14px", fontSize: "11px", color: "rgba(255,255,255,0.8)", lineHeight: 1.5 }}>
                Welcome! We offer three plans: Free, Pro ($29/mo), and Enterprise. The Pro plan includes 5 chatbots and unlimited messages. How can I help?
              </div>
            </div>
            {/* User message */}
            <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end", marginBottom: "12px" }}>
              <div style={{ background: "#059669", borderRadius: "10px 10px 2px 10px", padding: "10px 14px", fontSize: "11px", color: "white", lineHeight: 1.5 }}>
                What&apos;s included in the Pro plan?
              </div>
            </div>
            {/* Status badges */}
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              <div style={{ padding: "3px 8px", borderRadius: "12px", background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)", fontSize: "9px", color: "#10b981" }}>🟢 Live</div>
              <div style={{ padding: "3px 8px", borderRadius: "12px", background: "rgba(59,130,246,0.1)", border: "1px solid rgba(59,130,246,0.2)", fontSize: "9px", color: "#3b82f6" }}>📊 247 chats today</div>
              <div style={{ padding: "3px 8px", borderRadius: "12px", background: "rgba(249,115,22,0.1)", border: "1px solid rgba(249,115,22,0.2)", fontSize: "9px", color: "#f97316" }}>⚡ 0.8s avg</div>
              <div style={{ padding: "3px 8px", borderRadius: "12px", background: "rgba(168,85,247,0.1)", border: "1px solid rgba(168,85,247,0.2)", fontSize: "9px", color: "#a855f7" }}>😊 94% satisfaction</div>
            </div>
          </div>
        </div>
      </Html>

      {/* Confetti celebration */}
      <ConfettiParticles />
    </group>
  );
}

/* Confetti around the widget */
function ConfettiParticles() {
  const ref = useRef<THREE.Points>(null);
  const count = 30;

  const { positions, colors } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    const palette = [[0.06, 0.72, 0.51], [0.08, 0.72, 0.65], [0.93, 0.33, 0.6], [0.96, 0.62, 0.04], [0.23, 0.51, 0.96]];
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      pos[i3] = (Math.random() - 0.5) * 3;
      pos[i3 + 1] = Math.random() * 2.5;
      pos[i3 + 2] = (Math.random() - 0.5) * 1.5;
      const c = palette[Math.floor(Math.random() * palette.length)];
      col[i3] = c[0]; col[i3 + 1] = c[1]; col[i3 + 2] = c[2];
    }
    return { positions: pos, colors: col };
  }, []);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    const arr = (ref.current.geometry.attributes.position as THREE.BufferAttribute).array as Float32Array;
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      arr[i3 + 1] -= 0.006;
      arr[i3] += Math.sin(clock.elapsedTime + i) * 0.002;
      if (arr[i3 + 1] < -1.5) { arr[i3 + 1] = 2.5; arr[i3] = (Math.random() - 0.5) * 3; }
    }
    (ref.current.geometry.attributes.position as THREE.BufferAttribute).needsUpdate = true;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={count} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.06} vertexColors transparent opacity={0.7} sizeAttenuation blending={THREE.AdditiveBlending} depthWrite={false} />
    </points>
  );
}

/* Map step index to visual component */
const StepVisuals = [UploadVisual, CustomizeVisual, EmbedVisual, GoLiveVisual];

/* ═══════════════════════════════════════════════════════════════
   Glowing ring around the active visual
   ═══════════════════════════════════════════════════════════════ */
function GlowRing({ color }: { color: string }) {
  const ref = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.rotation.z = clock.elapsedTime * 0.3;
    ref.current.rotation.x = Math.PI / 4 + Math.sin(clock.elapsedTime * 0.25) * 0.15;
  });

  const col = new THREE.Color(color);

  return (
    <mesh ref={ref}>
      <torusGeometry args={[1.6, 0.01, 8, 64]} />
      <meshStandardMaterial
        color={col}
        emissive={col}
        emissiveIntensity={0.5}
        metalness={0.9}
        roughness={0.2}
        transparent
        opacity={0.35}
      />
    </mesh>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Main Scene — shows ONE big visual at a time
   ═══════════════════════════════════════════════════════════════ */
export default function HowItWorksScene({
  activeStep,
}: {
  activeStep: number;
}) {
  const Visual = StepVisuals[activeStep];

  return (
    <Canvas
      camera={{ position: [0, 0, 4.5], fov: 42 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      dpr={[1, 1.5]}
      style={{ background: "transparent" }}
    >
      <ambientLight intensity={0.35} />
      <directionalLight position={[3, 4, 5]} intensity={0.5} />
      <pointLight position={[-2, 1, 3]} intensity={0.5} color={STEP_COLORS[activeStep]} />
      <pointLight position={[2, -1, 3]} intensity={0.3} color={STEP_COLORS[activeStep]} />

      {/* Active step visual — centered and large */}
      <Visual />

      {/* Encompassing glow ring */}
      <GlowRing color={STEP_COLORS[activeStep]} />

      {/* Background particles */}
      <AmbientParticles />
    </Canvas>
  );
}
