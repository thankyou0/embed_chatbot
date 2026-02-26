"use client";

import { useRef, useMemo, useCallback, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Float, Html, MeshDistortMaterial, Stars } from "@react-three/drei";
import * as THREE from "three";

/* ═══════════════════════════════════════════════════════════════
   Data Particle System — particles flowing INTO the laptop
   representing websites, PDFs, Q&As being ingested
   ═══════════════════════════════════════════════════════════════ */
function DataParticles({ count = 120 }: { count?: number }) {
  const mesh = useRef<THREE.Points>(null);

  const { positions, velocities, colors, sizes } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const vel = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    const sz = new Float32Array(count);

    // Target center: the laptop area
    const targetX = 0;
    const targetY = 0;
    const targetZ = 0;

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      // Spawn on a sphere around the laptop
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 4 + Math.random() * 3;

      pos[i3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i3 + 2] = r * Math.cos(phi);

      // Velocity toward center
      const dx = targetX - pos[i3];
      const dy = targetY - pos[i3 + 1];
      const dz = targetZ - pos[i3 + 2];
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
      const speed = 0.003 + Math.random() * 0.005;
      vel[i3] = (dx / dist) * speed;
      vel[i3 + 1] = (dy / dist) * speed;
      vel[i3 + 2] = (dz / dist) * speed;

      // Emerald/teal/cyan colors
      const colorChoice = Math.random();
      if (colorChoice < 0.4) {
        // Emerald
        col[i3] = 0.2;
        col[i3 + 1] = 0.85;
        col[i3 + 2] = 0.5;
      } else if (colorChoice < 0.7) {
        // Teal
        col[i3] = 0.15;
        col[i3 + 1] = 0.7;
        col[i3 + 2] = 0.7;
      } else {
        // Cyan
        col[i3] = 0.2;
        col[i3 + 1] = 0.8;
        col[i3 + 2] = 0.9;
      }

      sz[i] = 0.02 + Math.random() * 0.04;
    }
    return { positions: pos, velocities: vel, colors: col, sizes: sz };
  }, [count]);

  useFrame(() => {
    if (!mesh.current) return;
    const posAttr = mesh.current.geometry.attributes.position as THREE.BufferAttribute;
    const arr = posAttr.array as Float32Array;

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      arr[i3] += velocities[i3];
      arr[i3 + 1] += velocities[i3 + 1];
      arr[i3 + 2] += velocities[i3 + 2];

      // Reset when close to center
      const dist = Math.sqrt(arr[i3] ** 2 + arr[i3 + 1] ** 2 + arr[i3 + 2] ** 2);
      if (dist < 0.8) {
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        const r = 4 + Math.random() * 3;
        arr[i3] = r * Math.sin(phi) * Math.cos(theta);
        arr[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        arr[i3 + 2] = r * Math.cos(phi);

        const dx = -arr[i3];
        const dy = -arr[i3 + 1];
        const dz = -arr[i3 + 2];
        const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        const speed = 0.003 + Math.random() * 0.005;
        velocities[i3] = (dx / d) * speed;
        velocities[i3 + 1] = (dy / d) * speed;
        velocities[i3 + 2] = (dz / d) * speed;
      }
    }
    posAttr.needsUpdate = true;
  });

  return (
    <points ref={mesh}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={count} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.05} vertexColors transparent opacity={0.8} sizeAttenuation blending={THREE.AdditiveBlending} depthWrite={false} />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Neural Network Lines — connections between floating nodes
   ═══════════════════════════════════════════════════════════════ */
function NeuralNetwork() {
  const groupRef = useRef<THREE.Group>(null);

  const { nodes, connections } = useMemo(() => {
    const n: THREE.Vector3[] = [];
    const c: [number, number][] = [];

    // Create nodes in a spread formation
    for (let i = 0; i < 20; i++) {
      n.push(
        new THREE.Vector3(
          (Math.random() - 0.5) * 10,
          (Math.random() - 0.5) * 6,
          (Math.random() - 0.5) * 4 - 2
        )
      );
    }

    // Connect nearby nodes
    for (let i = 0; i < n.length; i++) {
      for (let j = i + 1; j < n.length; j++) {
        if (n[i].distanceTo(n[j]) < 3.5) {
          c.push([i, j]);
        }
      }
    }
    return { nodes: n, connections: c };
  }, []);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.05) * 0.1;
    groupRef.current.rotation.x = Math.cos(clock.elapsedTime * 0.03) * 0.05;
  });

  return (
    <group ref={groupRef} position={[0, 0, -3]}>
      {/* Nodes */}
      {nodes.map((pos, i) => (
        <mesh key={i} position={pos}>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshBasicMaterial color="#34d399" transparent opacity={0.5} />
        </mesh>
      ))}
      {/* Connections */}
      {connections.map(([a, b], i) => {
        const points = [nodes[a], nodes[b]];
        const geo = new THREE.BufferGeometry().setFromPoints(points);
        return (
          <line key={i} geometry={geo}>
            <lineBasicMaterial color="#34d399" transparent opacity={0.08} />
          </line>
        );
      })}
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Procedural Laptop — wireframe/stylized laptop model
   ═══════════════════════════════════════════════════════════════ */
function ProceduralLaptop({ mouseX, mouseY }: { mouseX: number; mouseY: number }) {
  const groupRef = useRef<THREE.Group>(null);
  const screenRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    // Subtle float animation
    groupRef.current.position.y = Math.sin(clock.elapsedTime * 0.5) * 0.08;
    // Mouse follow
    groupRef.current.rotation.y = THREE.MathUtils.lerp(
      groupRef.current.rotation.y,
      mouseX * 0.15,
      0.05
    );
    groupRef.current.rotation.x = THREE.MathUtils.lerp(
      groupRef.current.rotation.x,
      -0.2 + mouseY * 0.08,
      0.05
    );
  });

  return (
    <group ref={groupRef} position={[0, -0.3, 0]} rotation={[-0.2, 0, 0]}>
      {/* ── Screen (lid) ── */}
      <group position={[0, 1.05, -0.05]} rotation={[-0.1, 0, 0]}>
        {/* Screen bezel */}
        <mesh>
          <boxGeometry args={[3.2, 2.1, 0.06]} />
          <meshStandardMaterial
            color="#111118"
            metalness={0.8}
            roughness={0.3}
          />
        </mesh>

        {/* Screen display area */}
        <mesh ref={screenRef} position={[0, 0, 0.035]}>
          <planeGeometry args={[2.9, 1.85]} />
          <meshBasicMaterial color="#0d0d17" />
        </mesh>

        {/* Embedded HTML widget on the screen */}
        <Html
          transform
          occlude
          position={[0, 0, 0.04]}
          scale={0.18}
          style={{
            width: "960px",
            height: "600px",
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              width: "960px",
              height: "600px",
              background: "linear-gradient(135deg, #0d0d17 0%, #111118 100%)",
              borderRadius: "0",
              overflow: "hidden",
              position: "relative",
              fontFamily: "system-ui, -apple-system, sans-serif",
            }}
          >
            {/* Fake website content */}
            <div style={{ padding: "24px", position: "relative", height: "100%" }}>
              {/* Header bar */}
              <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "20px" }}>
                <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "linear-gradient(135deg, #10b981, #14b8a6)" }} />
                <div style={{ height: "10px", width: "80px", background: "rgba(255,255,255,0.08)", borderRadius: "4px" }} />
                <div style={{ flex: 1 }} />
                <div style={{ height: "10px", width: "50px", background: "rgba(255,255,255,0.05)", borderRadius: "4px" }} />
                <div style={{ height: "10px", width: "50px", background: "rgba(255,255,255,0.05)", borderRadius: "4px" }} />
                <div style={{ height: "10px", width: "50px", background: "rgba(255,255,255,0.05)", borderRadius: "4px" }} />
              </div>
              {/* Content lines */}
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxWidth: "400px" }}>
                <div style={{ height: "14px", width: "70%", background: "rgba(255,255,255,0.06)", borderRadius: "4px" }} />
                <div style={{ height: "14px", width: "50%", background: "rgba(255,255,255,0.06)", borderRadius: "4px" }} />
                <div style={{ height: "10px", width: "90%", background: "rgba(255,255,255,0.03)", borderRadius: "4px", marginTop: "8px" }} />
                <div style={{ height: "10px", width: "75%", background: "rgba(255,255,255,0.03)", borderRadius: "4px" }} />
                <div style={{ height: "10px", width: "60%", background: "rgba(255,255,255,0.03)", borderRadius: "4px" }} />
                <div style={{ height: "80px", width: "100%", background: "rgba(255,255,255,0.02)", borderRadius: "8px", marginTop: "12px", border: "1px solid rgba(255,255,255,0.05)" }} />
              </div>

              {/* Chat Widget — bottom-right */}
              <div
                style={{
                  position: "absolute",
                  bottom: "16px",
                  right: "16px",
                  width: "260px",
                }}
              >
                {/* Chat Window */}
                <div
                  style={{
                    background: "#1a1a2e",
                    borderRadius: "16px",
                    border: "1px solid rgba(255,255,255,0.1)",
                    overflow: "hidden",
                    boxShadow: "0 25px 50px -12px rgba(16,185,129,0.15)",
                    marginBottom: "8px",
                  }}
                >
                  {/* Header */}
                  <div
                    style={{
                      background: "linear-gradient(90deg, #059669, #0d9488)",
                      padding: "10px 14px",
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                    }}
                  >
                    <div
                      style={{
                        width: "28px",
                        height: "28px",
                        borderRadius: "50%",
                        background: "rgba(255,255,255,0.2)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "12px",
                      }}
                    >
                      💬
                    </div>
                    <div>
                      <div style={{ color: "white", fontSize: "12px", fontWeight: 600 }}>AI Assistant</div>
                      <div style={{ color: "rgba(255,255,255,0.7)", fontSize: "9px", display: "flex", alignItems: "center", gap: "4px" }}>
                        <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#4ade80", display: "inline-block" }} />
                        Online
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div style={{ padding: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
                    {/* Bot message */}
                    <div style={{ display: "flex", gap: "6px", alignItems: "flex-start" }}>
                      <div style={{ width: "20px", height: "20px", borderRadius: "50%", background: "rgba(16,185,129,0.2)", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "8px" }}>💬</div>
                      <div style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px 12px 12px 4px", padding: "8px 10px", fontSize: "10px", color: "rgba(255,255,255,0.8)", maxWidth: "180px" }}>
                        Hi! 👋 How can I help you today?
                      </div>
                    </div>

                    {/* User message */}
                    <div style={{ display: "flex", justifyContent: "flex-end" }}>
                      <div style={{ background: "#059669", borderRadius: "12px 12px 4px 12px", padding: "8px 10px", fontSize: "10px", color: "white", maxWidth: "180px" }}>
                        What are your pricing plans?
                      </div>
                    </div>

                    {/* Bot typing */}
                    <div style={{ display: "flex", gap: "6px", alignItems: "flex-start" }}>
                      <div style={{ width: "20px", height: "20px", borderRadius: "50%", background: "rgba(16,185,129,0.2)", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "8px" }}>💬</div>
                      <div style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px 12px 12px 4px", padding: "8px 12px", display: "flex", gap: "3px", alignItems: "center" }}>
                        <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "rgba(52,211,153,0.6)", animation: "dotPulse 1.2s ease-in-out infinite" }} />
                        <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "rgba(52,211,153,0.6)", animation: "dotPulse 1.2s ease-in-out infinite 0.2s" }} />
                        <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "rgba(52,211,153,0.6)", animation: "dotPulse 1.2s ease-in-out infinite 0.4s" }} />
                      </div>
                    </div>
                  </div>

                  {/* Input */}
                  <div style={{ padding: "0 12px 12px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", padding: "6px 10px", background: "rgba(255,255,255,0.03)" }}>
                      <span style={{ fontSize: "10px", color: "rgba(255,255,255,0.3)", flex: 1 }}>Type a message...</span>
                      <div style={{ width: "20px", height: "20px", borderRadius: "4px", background: "#059669", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "10px", color: "white" }}>→</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <style>{`
              @keyframes dotPulse {
                0%, 100% { opacity: 0.3; transform: scale(0.8); }
                50% { opacity: 1; transform: scale(1); }
              }
            `}</style>
          </div>
        </Html>

        {/* Screen edge glow */}
        <mesh position={[0, 0, 0.04]}>
          <planeGeometry args={[3.0, 1.95]} />
          <meshBasicMaterial color="#10b981" transparent opacity={0.02} />
        </mesh>
      </group>

      {/* ── Base (keyboard area) ── */}
      <group position={[0, -0.02, 0.7]}>
        <mesh>
          <boxGeometry args={[3.2, 0.08, 2.0]} />
          <meshStandardMaterial
            color="#111118"
            metalness={0.8}
            roughness={0.3}
          />
        </mesh>

        {/* Keyboard area (subtle glow) */}
        <mesh position={[0, 0.045, -0.1]}>
          <planeGeometry args={[2.6, 1.2]} />
          <meshBasicMaterial color="#0d0d17" transparent opacity={0.8} />
        </mesh>

        {/* Keyboard grid (procedural) */}
        {Array.from({ length: 4 }).map((_, row) =>
          Array.from({ length: 12 }).map((_, col) => (
            <mesh
              key={`${row}-${col}`}
              position={[
                -1.2 + col * 0.2 + (row % 2 ? 0.05 : 0),
                0.045,
                -0.55 + row * 0.25,
              ]}
            >
              <planeGeometry args={[0.16, 0.18]} />
              <meshBasicMaterial color="#1a1a2e" transparent opacity={0.6} />
            </mesh>
          ))
        )}

        {/* Trackpad */}
        <mesh position={[0, 0.045, 0.55]}>
          <planeGeometry args={[1.0, 0.6]} />
          <meshBasicMaterial color="#151520" transparent opacity={0.7} />
        </mesh>
      </group>

      {/* ── Hinge ── */}
      <mesh position={[0, 0, -0.3]}>
        <boxGeometry args={[2.8, 0.05, 0.06]} />
        <meshStandardMaterial color="#1a1a2e" metalness={0.9} roughness={0.2} />
      </mesh>

      {/* ── Glow underneath laptop ── */}
      <mesh position={[0, -0.15, 0.4]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[2, 32]} />
        <meshBasicMaterial color="#10b981" transparent opacity={0.04} />
      </mesh>
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Floating Data Icons — small 3D shapes representing data types
   ═══════════════════════════════════════════════════════════════ */
function FloatingDataIcon({
  position,
  color,
  shape,
  delay,
}: {
  position: [number, number, number];
  color: string;
  shape: "box" | "sphere" | "octahedron" | "torus";
  delay: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.x = clock.elapsedTime * 0.3 + delay;
    meshRef.current.rotation.y = clock.elapsedTime * 0.5 + delay;
  });

  return (
    <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.8} floatingRange={[-0.2, 0.2]}>
      <mesh ref={meshRef} position={position} scale={0.15}>
        {shape === "box" && <boxGeometry args={[1, 1, 1]} />}
        {shape === "sphere" && <sphereGeometry args={[0.6, 16, 16]} />}
        {shape === "octahedron" && <octahedronGeometry args={[0.7]} />}
        {shape === "torus" && <torusGeometry args={[0.5, 0.2, 8, 16]} />}
        <MeshDistortMaterial
          color={color}
          transparent
          opacity={0.6}
          distort={0.2}
          speed={2}
          roughness={0.4}
          metalness={0.8}
        />
      </mesh>
    </Float>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Camera Controller — responds to mouse movement
   ═══════════════════════════════════════════════════════════════ */
function CameraController({ mouseX, mouseY }: { mouseX: number; mouseY: number }) {
  useFrame(({ camera }) => {
    camera.position.x = THREE.MathUtils.lerp(camera.position.x, mouseX * 0.3, 0.05);
    camera.position.y = THREE.MathUtils.lerp(camera.position.y, 2.3 + mouseY * 0.15, 0.05);
  });
  return null;
}

/* ═══════════════════════════════════════════════════════════════
   Main Scene — Composed together
   ═══════════════════════════════════════════════════════════════ */
export default function HeroScene() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePos({
      x: ((e.clientX - rect.left) / rect.width - 0.5) * 2,
      y: ((e.clientY - rect.top) / rect.height - 0.5) * 2,
    });
  }, []);

  return (
    <div
      onMouseMove={handleMouseMove}
      className="w-full h-full"
      style={{ position: "absolute", inset: 0 }}
    >
      <Canvas
        camera={{ position: [0, 2.3, 5.5], fov: 45 }}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
        }}
        dpr={[1, 1.5]}
        style={{ background: "transparent" }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.3} />
        <directionalLight position={[5, 5, 5]} intensity={0.5} color="#ffffff" />
        <pointLight position={[-3, 2, 3]} intensity={0.3} color="#10b981" />
        <pointLight position={[3, 1, 2]} intensity={0.2} color="#14b8a6" />

        {/* Camera controller */}
        <CameraController mouseX={mousePos.x} mouseY={mousePos.y} />

        {/* Stars background */}
        <Stars radius={15} depth={30} count={800} factor={3} saturation={0} fade speed={0.5} />

        {/* Neural network background mesh */}
        <NeuralNetwork />

        {/* Data particles flowing inward */}
        <DataParticles count={100} />

        {/* Main laptop */}
        <ProceduralLaptop mouseX={mousePos.x} mouseY={mousePos.y} />

        {/* Floating data type icons around the laptop */}
        <FloatingDataIcon position={[-2.5, 1.5, 1]} color="#10b981" shape="box" delay={0} />
        <FloatingDataIcon position={[2.8, 2, 0.5]} color="#14b8a6" shape="octahedron" delay={1} />
        <FloatingDataIcon position={[-3, 0.5, -1]} color="#06b6d4" shape="sphere" delay={2} />
        <FloatingDataIcon position={[2.5, 0, 1.5]} color="#34d399" shape="torus" delay={3} />
        <FloatingDataIcon position={[-1.5, 2.5, -0.5]} color="#2dd4bf" shape="box" delay={1.5} />
        <FloatingDataIcon position={[1.8, 2.8, 0]} color="#10b981" shape="octahedron" delay={0.5} />

      </Canvas>
    </div>
  );
}
