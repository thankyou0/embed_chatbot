"use client";

import { useRef, useMemo, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Html, RoundedBox, MeshDistortMaterial } from "@react-three/drei";
import * as THREE from "three";

/* ═══════════════════════════════════════════════════════════════
   Demo Conversations Data
   ═══════════════════════════════════════════════════════════════ */
const conversations = [
  {
    question: "What pricing plans do you offer?",
    answer: "We have three plans:\n• Free — 1 bot, 50 msgs/mo\n• Pro ($29/mo) — 5 bots, unlimited msgs, analytics\n• Enterprise — custom limits, SSO, dedicated support\n\nAll plans include our core AI engine!",
    tag: "💰 Pricing",
  },
  {
    question: "How do I embed the chatbot?",
    answer: "Super easy! Just 3 steps:\n1. Copy your unique script tag\n2. Paste it before </body>\n3. Done! Works with React, WordPress, Shopify — any platform.\n\nNo npm packages needed.",
    tag: "🔧 Setup",
  },
  {
    question: "What data sources can I use?",
    answer: "You can train your bot on:\n• PDF documents & text files\n• Website URLs (we crawl them)\n• Q&A pairs for precise answers\n• Product catalogs\n\nOur RAG engine retrieves the most relevant context for every query.",
    tag: "📚 Data",
  },
];

/* ═══════════════════════════════════════════════════════════════
   Procedural Phone in 3D
   ═══════════════════════════════════════════════════════════════ */
function Phone3D({ activeConvo, isTyping }: { activeConvo: number; isTyping: boolean }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.3) * 0.06;
    groupRef.current.position.y = Math.sin(clock.elapsedTime * 0.5) * 0.04;
  });

  const convo = conversations[activeConvo];

  return (
    <group ref={groupRef} position={[-2, 0, 0]}>
      {/* Phone body */}
      <RoundedBox args={[1.6, 2.8, 0.08]} radius={0.12} smoothness={4}>
        <meshStandardMaterial color="#1a1a2e" metalness={0.7} roughness={0.3} />
      </RoundedBox>

      {/* Screen bezel inner glow */}
      <RoundedBox args={[1.45, 2.6, 0.09]} radius={0.1} smoothness={4} position={[0, 0, 0.005]}>
        <meshStandardMaterial color="#0d0d17" metalness={0.3} roughness={0.5} />
      </RoundedBox>

      {/* Screen content */}
      <Html
        transform
        position={[0, 0, 0.05]}
        scale={0.065}
        style={{ pointerEvents: "none" }}
      >
        <div style={{
          width: "680px",
          height: "1200px",
          background: "#0d0d17",
          borderRadius: "16px",
          overflow: "hidden",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}>
          {/* Status bar */}
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "8px 20px",
            fontSize: "10px",
            color: "rgba(255,255,255,0.4)",
          }}>
            <span>9:41</span>
            <span>📶 🔋</span>
          </div>

          {/* Chat header */}
          <div style={{
            background: "linear-gradient(90deg, #059669, #0d9488)",
            padding: "16px 20px",
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}>
            <div style={{
              width: "36px", height: "36px", borderRadius: "50%",
              background: "rgba(255,255,255,0.2)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "16px",
            }}>🤖</div>
            <div>
              <div style={{ color: "white", fontSize: "14px", fontWeight: 600 }}>AI Assistant</div>
              <div style={{ color: "rgba(255,255,255,0.7)", fontSize: "10px" }}>Online now</div>
            </div>
          </div>

          {/* Messages */}
          <div style={{ padding: "16px", display: "flex", flexDirection: "column", gap: "12px" }}>
            {/* User question */}
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <div style={{
                background: "#059669",
                borderRadius: "16px 16px 4px 16px",
                padding: "12px 16px",
                maxWidth: "480px",
                fontSize: "12px",
                color: "white",
                lineHeight: 1.5,
              }}>
                {convo.question}
              </div>
            </div>

            {/* Bot answer */}
            <div style={{ display: "flex", gap: "8px", alignItems: "flex-start" }}>
              <div style={{
                width: "24px", height: "24px", borderRadius: "50%",
                background: "rgba(16,185,129,0.2)", flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "11px",
              }}>🤖</div>
              <div style={{
                background: "rgba(255,255,255,0.06)",
                borderRadius: "4px 16px 16px 16px",
                padding: "12px 16px",
                maxWidth: "480px",
                fontSize: "12px",
                color: "rgba(255,255,255,0.85)",
                lineHeight: 1.6,
                whiteSpace: "pre-line",
              }}>
                {isTyping ? (
                  <span style={{ display: "flex", gap: "4px" }}>
                    <span style={{ animation: "pulse 1s infinite 0s", width: "6px", height: "6px", borderRadius: "50%", background: "rgba(255,255,255,0.3)", display: "inline-block" }}>·</span>
                    <span style={{ animation: "pulse 1s infinite 0.2s", width: "6px", height: "6px", borderRadius: "50%", background: "rgba(255,255,255,0.3)", display: "inline-block" }}>·</span>
                    <span style={{ animation: "pulse 1s infinite 0.4s", width: "6px", height: "6px", borderRadius: "50%", background: "rgba(255,255,255,0.3)", display: "inline-block" }}>·</span>
                  </span>
                ) : (
                  convo.answer
                )}
              </div>
            </div>
          </div>

          {/* Input bar */}
          <div style={{
            position: "absolute", bottom: "20px", left: "16px", right: "16px",
            background: "rgba(255,255,255,0.05)",
            borderRadius: "24px",
            padding: "12px 16px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            border: "1px solid rgba(255,255,255,0.08)",
          }}>
            <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.25)" }}>Ask anything...</span>
            <div style={{
              width: "28px", height: "28px", borderRadius: "50%",
              background: "#059669",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "12px",
            }}>↑</div>
          </div>
        </div>
      </Html>

      {/* Phone glow */}
      <pointLight position={[0, 0, 0.5]} intensity={0.3} color="#10b981" distance={3} />
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Procedural Laptop in 3D
   ═══════════════════════════════════════════════════════════════ */
function Laptop3D({ activeConvo, isTyping }: { activeConvo: number; isTyping: boolean }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.25) * -0.05;
    groupRef.current.position.y = Math.sin(clock.elapsedTime * 0.4 + 1) * 0.04;
  });

  const convo = conversations[activeConvo];

  return (
    <group ref={groupRef} position={[2, -0.3, 0]}>
      {/* Base / keyboard */}
      <RoundedBox args={[3, 0.08, 2]} radius={0.03} smoothness={4} position={[0, -1.1, 0.5]}>
        <meshStandardMaterial color="#1a1a2e" metalness={0.6} roughness={0.3} />
      </RoundedBox>

      {/* Screen back */}
      <RoundedBox args={[3, 2, 0.06]} radius={0.04} smoothness={4} position={[0, 0, 0]}>
        <meshStandardMaterial color="#1a1a2e" metalness={0.7} roughness={0.3} />
      </RoundedBox>

      {/* Screen inner */}
      <RoundedBox args={[2.8, 1.8, 0.065]} radius={0.02} smoothness={4} position={[0, 0, 0.005]}>
        <meshStandardMaterial color="#0d0d17" metalness={0.2} roughness={0.6} />
      </RoundedBox>

      {/* Website content with widget overlay */}
      <Html
        transform
        position={[0, 0, 0.04]}
        scale={0.056}
        style={{ pointerEvents: "none" }}
      >
        <div style={{
          width: "1500px",
          height: "960px",
          background: "#0d0d17",
          borderRadius: "8px",
          position: "relative",
          overflow: "hidden",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}>
          {/* Fake website content */}
          <div style={{ padding: "24px" }}>
            {/* Nav */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "40px" }}>
              <div style={{ fontSize: "16px", fontWeight: 700, color: "rgba(255,255,255,0.6)" }}>acme.com</div>
              <div style={{ display: "flex", gap: "16px" }}>
                {["Products", "Pricing", "Docs", "Blog"].map((item) => (
                  <span key={item} style={{ fontSize: "11px", color: "rgba(255,255,255,0.3)" }}>{item}</span>
                ))}
              </div>
            </div>
            {/* Hero content placeholder */}
            <div style={{ maxWidth: "600px" }}>
              <div style={{ width: "200px", height: "12px", background: "rgba(255,255,255,0.06)", borderRadius: "6px", marginBottom: "12px" }} />
              <div style={{ width: "350px", height: "20px", background: "rgba(255,255,255,0.04)", borderRadius: "6px", marginBottom: "8px" }} />
              <div style={{ width: "280px", height: "20px", background: "rgba(255,255,255,0.04)", borderRadius: "6px", marginBottom: "24px" }} />
              <div style={{ width: "120px", height: "32px", background: "rgba(16,185,129,0.15)", borderRadius: "6px", border: "1px solid rgba(16,185,129,0.2)" }} />
            </div>
          </div>

          {/* EmbedChat Widget in bottom-right */}
          <div style={{
            position: "absolute",
            bottom: "16px",
            right: "16px",
            width: "340px",
            background: "#1a1a2e",
            borderRadius: "16px",
            overflow: "hidden",
            border: "1px solid rgba(16,185,129,0.15)",
            boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
          }}>
            {/* Widget header */}
            <div style={{
              background: "linear-gradient(90deg, #059669, #0d9488)",
              padding: "10px 14px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}>
              <div style={{ width: "24px", height: "24px", borderRadius: "50%", background: "rgba(255,255,255,0.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "11px" }}>🤖</div>
              <div style={{ color: "white", fontSize: "11px", fontWeight: 600 }}>AI Assistant</div>
            </div>

            {/* Messages */}
            <div style={{ padding: "12px", display: "flex", flexDirection: "column", gap: "8px", maxHeight: "360px" }}>
              {/* User question */}
              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <div style={{
                  background: "#059669",
                  borderRadius: "12px 12px 2px 12px",
                  padding: "8px 12px",
                  maxWidth: "260px",
                  fontSize: "10px",
                  color: "white",
                  lineHeight: 1.5,
                }}>
                  {convo.question}
                </div>
              </div>
              {/* Bot answer */}
              <div style={{ display: "flex", gap: "6px", alignItems: "flex-start" }}>
                <div style={{
                  width: "18px", height: "18px", borderRadius: "50%",
                  background: "rgba(16,185,129,0.2)", flexShrink: 0,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "8px",
                }}>🤖</div>
                <div style={{
                  background: "rgba(255,255,255,0.05)",
                  borderRadius: "2px 12px 12px 12px",
                  padding: "8px 12px",
                  maxWidth: "260px",
                  fontSize: "10px",
                  color: "rgba(255,255,255,0.8)",
                  lineHeight: 1.5,
                  whiteSpace: "pre-line",
                }}>
                  {isTyping ? "●●●" : convo.answer}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Html>

      {/* Local glow */}
      <pointLight position={[0, 0, 1]} intensity={0.25} color="#14b8a6" distance={3} />
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Ambient particles
   ═══════════════════════════════════════════════════════════════ */
function AmbientParticles() {
  const ref = useRef<THREE.Points>(null);
  const count = 80;

  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      pos[i3] = (Math.random() - 0.5) * 15;
      pos[i3 + 1] = (Math.random() - 0.5) * 8;
      pos[i3 + 2] = (Math.random() - 0.5) * 10;
    }
    return pos;
  }, []);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.rotation.y = clock.elapsedTime * 0.02;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={0.03}
        color="#10b981"
        transparent
        opacity={0.4}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Main Demo Scene
   ═══════════════════════════════════════════════════════════════ */
export default function DemoScene({
  activeConvo,
  isTyping,
}: {
  activeConvo: number;
  isTyping: boolean;
}) {
  return (
    <Canvas
      camera={{ position: [0, 0.5, 6], fov: 45 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      dpr={[1, 1.5]}
      style={{ background: "transparent" }}
    >
      <ambientLight intensity={0.3} />
      <directionalLight position={[5, 5, 5]} intensity={0.4} />
      <pointLight position={[-3, 2, 4]} intensity={0.3} color="#10b981" />
      <pointLight position={[3, 2, 4]} intensity={0.3} color="#14b8a6" />

      {/* Phone (left) */}
      <Float speed={0.8} rotationIntensity={0.1} floatIntensity={0.15}>
        <Phone3D activeConvo={activeConvo} isTyping={isTyping} />
      </Float>

      {/* Laptop (right) */}
      <Float speed={0.6} rotationIntensity={0.08} floatIntensity={0.12}>
        <Laptop3D activeConvo={activeConvo} isTyping={isTyping} />
      </Float>

      {/* Center energy orb connecting both devices */}
      <mesh position={[0, 0, -1]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <MeshDistortMaterial
          color="#10b981"
          distort={0.3}
          speed={2}
          transparent
          opacity={0.6}
        />
      </mesh>
      <mesh position={[0, 0, -1]}>
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshBasicMaterial color="#10b981" transparent opacity={0.05} />
      </mesh>

      <AmbientParticles />

    </Canvas>
  );
}
