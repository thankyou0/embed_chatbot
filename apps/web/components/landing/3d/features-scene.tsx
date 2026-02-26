"use client";

import { useRef, useMemo, useState, useCallback } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Html } from "@react-three/drei";
import * as THREE from "three";

/* ═══════════════════════════════════════════════════════════════
   Feature Data — matches your actual chatbot features
   ═══════════════════════════════════════════════════════════════ */
const features = [
  {
    id: "train",
    label: "Train on Data",
    description:
      "Upload PDFs, crawl websites, add Q&A pairs. Your chatbot learns your business.",
    icon: "🧠",
    color: "#3b82f6",
    position: [-3.5, 1.5, 0] as [number, number, number],
  },
  {
    id: "embed",
    label: "One-Line Embed",
    description:
      "Copy a single script tag — works with React, WordPress, Shopify, or plain HTML.",
    icon: "⚡",
    color: "#10b981",
    position: [0, 2.5, 0] as [number, number, number],
  },
  {
    id: "customize",
    label: "Fully Customizable",
    description:
      "Custom colors, logo, welcome messages, position. Match your brand perfectly.",
    icon: "🎨",
    color: "#8b5cf6",
    position: [3.5, 1.5, 0] as [number, number, number],
  },
  {
    id: "smart",
    label: "Smart RAG Chat",
    description:
      "Hybrid search with BM25 + vectors, cross-encoder re-ranking for precise answers.",
    icon: "💬",
    color: "#ec4899",
    position: [-4.2, -0.5, 0] as [number, number, number],
  },
  {
    id: "multilang",
    label: "Multi-Language",
    description:
      "English, Hindi, Gujarati with romanized script detection and auto-translation.",
    icon: "🌍",
    color: "#06b6d4",
    position: [-1.8, -0.8, 0] as [number, number, number],
  },
  {
    id: "ecommerce",
    label: "E-Commerce AI",
    description:
      "Product carousels, price/color filtering, visual search from images.",
    icon: "🛒",
    color: "#f59e0b",
    position: [1.8, -0.8, 0] as [number, number, number],
  },
  {
    id: "analytics",
    label: "Analytics",
    description:
      "Track conversations, unanswered queries, satisfaction rates in real-time.",
    icon: "📊",
    color: "#f97316",
    position: [4.2, -0.5, 0] as [number, number, number],
  },
  {
    id: "vision",
    label: "Vision & Image",
    description:
      "Upload images into chat — AI extracts product attributes for visual search.",
    icon: "👁️",
    color: "#14b8a6",
    position: [-2.5, -2.5, 0] as [number, number, number],
  },
  {
    id: "security",
    label: "Secure & RBAC",
    description:
      "Enterprise security with per-chatbot permissions, granular team roles.",
    icon: "🛡️",
    color: "#22c55e",
    position: [0, -2.8, 0] as [number, number, number],
  },
  {
    id: "deploy",
    label: "Instant Deploy",
    description:
      "Go live in minutes. No complex setup, no server management needed.",
    icon: "🚀",
    color: "#eab308",
    position: [2.5, -2.5, 0] as [number, number, number],
  },
];

/* ═══════════════════════════════════════════════════════════════
   Connection edges between features
   ═══════════════════════════════════════════════════════════════ */
const connections: [number, number][] = [
  [0, 1],
  [1, 2], // top row
  [0, 3],
  [0, 4], // train connects down
  [1, 4],
  [1, 5], // embed connects down
  [2, 5],
  [2, 6], // customize connects down
  [3, 4],
  [4, 5],
  [5, 6], // middle row
  [3, 7],
  [4, 8],
  [5, 8],
  [6, 9], // to bottom
  [7, 8],
  [8, 9], // bottom row
];

/* ═══════════════════════════════════════════════════════════════
   Modern Feature Node — shiny sphere + orbital ring
   ═══════════════════════════════════════════════════════════════ */
function FeatureNode({
  feature,
  index,
  activeIndex,
  hoveredIndex,
  onHover,
  onLeave,
}: {
  feature: (typeof features)[0];
  index: number;
  activeIndex: number;
  hoveredIndex: number | null;
  onHover: (i: number) => void;
  onLeave: () => void;
}) {
  const coreRef = useRef<THREE.Mesh>(null);
  const outerRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const isHovered = hoveredIndex === index;
  const isActive = index <= activeIndex;

  useFrame(({ clock }) => {
    if (!coreRef.current || !outerRef.current || !ringRef.current) return;

    const t = clock.elapsedTime;

    if (isActive) {
      const pulse = Math.sin(t * 2.5 + index * 0.7) * 0.04;
      const s = isHovered ? 1.25 : 1 + pulse;
      coreRef.current.scale.setScalar(s);
      outerRef.current.scale.setScalar(s * 1.6);
      ringRef.current.scale.setScalar(s * 1.8);
    } else {
      coreRef.current.scale.setScalar(0.5);
      outerRef.current.scale.setScalar(0.7);
      ringRef.current.scale.setScalar(0.8);
    }

    // Spin the orbital ring
    ringRef.current.rotation.x = Math.PI / 3 + Math.sin(t * 0.5 + index) * 0.15;
    ringRef.current.rotation.z = t * 0.6 + index * 0.8;
  });

  const color = new THREE.Color(feature.color);

  return (
    <Float speed={1.2} rotationIntensity={0.08} floatIntensity={0.12}>
      <group position={feature.position}>
        {/* Outer glow sphere */}
        <mesh ref={outerRef}>
          <sphereGeometry args={[0.22, 24, 24]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={isActive ? (isHovered ? 0.18 : 0.07) : 0.015}
          />
        </mesh>

        {/* Core sphere — shiny modern look */}
        <mesh
          ref={coreRef}
          onPointerEnter={() => onHover(index)}
          onPointerLeave={onLeave}
        >
          <sphereGeometry args={[0.18, 32, 32]} />
          <meshStandardMaterial
            color={isActive ? color : "#333344"}
            emissive={color}
            emissiveIntensity={isActive ? (isHovered ? 1.2 : 0.5) : 0.03}
            metalness={0.85}
            roughness={0.15}
            transparent
            opacity={isActive ? 1 : 0.35}
            envMapIntensity={1.5}
          />
        </mesh>

        {/* Orbital ring */}
        <mesh ref={ringRef}>
          <torusGeometry args={[0.28, 0.012, 8, 48]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={isActive ? 0.6 : 0.02}
            metalness={0.9}
            roughness={0.2}
            transparent
            opacity={isActive ? 0.7 : 0.1}
          />
        </mesh>

        {/* Small orbiting dot on the ring */}
        {isActive && <OrbitingDot color={feature.color} index={index} />}

        {/* Icon */}
        <Html center position={[0, 0, 0.28]} style={{ pointerEvents: "none" }}>
          <div
            style={{
              fontSize: isHovered ? "22px" : "16px",
              transition: "all 0.3s ease",
              filter: isActive ? "none" : "grayscale(100%) opacity(0.25)",
              textShadow: isActive ? `0 0 12px ${feature.color}` : "none",
            }}
          >
            {feature.icon}
          </div>
        </Html>

        {/* Label below node */}
        <Html
          center
          position={[0, -0.48, 0]}
          style={{ pointerEvents: "none" }}
        >
          <div
            style={{
              fontSize: isHovered ? "13px" : "11px",
              fontWeight: isHovered ? 700 : 600,
              color: isActive ? "white" : "rgba(255,255,255,0.2)",
              whiteSpace: "nowrap",
              transition: "all 0.3s ease",
              textShadow:
                isActive && isHovered
                  ? `0 0 20px ${feature.color}`
                  : "none",
              fontFamily: "system-ui, sans-serif",
            }}
          >
            {feature.label}
          </div>
        </Html>

        {/* Description tooltip on hover — always above, with enough space */}
        {isHovered && isActive && (
          <Html
            center
            position={[0, 0.55, 0.5]}
            style={{ pointerEvents: "none" }}
            zIndexRange={[100, 0]}
          >
            <div
              style={{
                width: "280px",
                padding: "14px 18px",
                background: "rgba(8, 8, 14, 0.97)",
                borderRadius: "14px",
                border: `1px solid ${feature.color}50`,
                boxShadow: `0 12px 40px rgba(0,0,0,0.6), 0 0 20px ${feature.color}20`,
                backdropFilter: "blur(16px)",
                fontFamily: "system-ui, sans-serif",
                transform: "translateY(-8px)",
              }}
            >
              <div
                style={{
                  fontSize: "13px",
                  fontWeight: 600,
                  color: feature.color,
                  marginBottom: "6px",
                  letterSpacing: "0.02em",
                }}
              >
                {feature.label}
              </div>
              <div
                style={{
                  fontSize: "12px",
                  color: "rgba(255,255,255,0.75)",
                  lineHeight: 1.6,
                  wordBreak: "break-word",
                }}
              >
                {feature.description}
              </div>
            </div>
          </Html>
        )}
      </group>
    </Float>
  );
}

/* Small glowing dot orbiting the ring */
function OrbitingDot({ color, index }: { color: string; index: number }) {
  const ref = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    const t = clock.elapsedTime * 1.5 + index * 1.2;
    ref.current.position.x = Math.cos(t) * 0.28;
    ref.current.position.y = Math.sin(t) * 0.28 * Math.cos(Math.PI / 3);
    ref.current.position.z = Math.sin(t) * 0.28 * Math.sin(Math.PI / 3);
  });

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.025, 8, 8]} />
      <meshBasicMaterial color={color} />
    </mesh>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Connection Edge — animated line between nodes
   ═══════════════════════════════════════════════════════════════ */
function ConnectionEdge({
  from,
  to,
  active,
}: {
  from: [number, number, number];
  to: [number, number, number];
  active: boolean;
}) {
  const positions = useMemo(() => {
    return new Float32Array([...from, ...to]);
  }, [from, to]);

  return (
    <line>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={2}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial
        color={active ? "#34d399" : "#1a1a2e"}
        transparent
        opacity={active ? 0.3 : 0.05}
        linewidth={1}
      />
    </line>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Traveling Pulse on active connections
   ═══════════════════════════════════════════════════════════════ */
function TravelingPulse({
  from,
  to,
  delay,
}: {
  from: [number, number, number];
  to: [number, number, number];
  delay: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = (clock.elapsedTime * 0.4 + delay) % 1;
    meshRef.current.position.x = from[0] + (to[0] - from[0]) * t;
    meshRef.current.position.y = from[1] + (to[1] - from[1]) * t;
    meshRef.current.position.z = from[2] + (to[2] - from[2]) * t;
    (meshRef.current.material as THREE.MeshBasicMaterial).opacity =
      Math.sin(t * Math.PI) * 0.9;
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.035, 8, 8]} />
      <meshBasicMaterial color="#34d399" transparent opacity={0} />
    </mesh>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Background ambient particles
   ═══════════════════════════════════════════════════════════════ */
function AmbientParticles({ count = 80 }: { count?: number }) {
  const ref = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 14;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 8;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 4 - 2;
    }
    return arr;
  }, [count]);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.rotation.y = Math.sin(clock.elapsedTime * 0.03) * 0.1;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        color="#34d399"
        transparent
        opacity={0.3}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Main Scene — scrollProgress 0→1 now activates ALL nodes by ~40%
   ═══════════════════════════════════════════════════════════════ */
export default function FeaturesScene({
  scrollProgress,
}: {
  scrollProgress: number;
}) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const handleHover = useCallback((i: number) => setHoveredIndex(i), []);
  const handleLeave = useCallback(() => setHoveredIndex(null), []);

  // Accelerated: all 10 nodes light up by scrollProgress ~0.4 instead of 1.0
  const activeIndex = Math.min(
    features.length - 1,
    Math.floor(scrollProgress * features.length * 2.5)
  );

  return (
    <Canvas
      camera={{ position: [0, 0, 9.5], fov: 45 }}
      gl={{
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
      }}
      dpr={[1, 1.5]}
      style={{ background: "transparent" }}
    >
      <ambientLight intensity={0.4} />
      <pointLight position={[0, 3, 5]} intensity={0.6} color="#10b981" />
      <pointLight position={[-5, -2, 3]} intensity={0.35} color="#06b6d4" />
      <pointLight position={[5, -2, 3]} intensity={0.35} color="#8b5cf6" />

      {/* Connection edges */}
      {connections.map(([a, b], i) => {
        const bothActive = a <= activeIndex && b <= activeIndex;
        return (
          <group key={`edge-${i}`}>
            <ConnectionEdge
              from={features[a].position}
              to={features[b].position}
              active={bothActive}
            />
            {bothActive && (
              <TravelingPulse
                from={features[a].position}
                to={features[b].position}
                delay={i * 0.25}
              />
            )}
          </group>
        );
      })}

      {/* Feature nodes */}
      {features.map((feature, i) => (
        <FeatureNode
          key={feature.id}
          feature={feature}
          index={i}
          activeIndex={activeIndex}
          hoveredIndex={hoveredIndex}
          onHover={handleHover}
          onLeave={handleLeave}
        />
      ))}

      {/* Background particles */}
      <AmbientParticles />
    </Canvas>
  );
}
