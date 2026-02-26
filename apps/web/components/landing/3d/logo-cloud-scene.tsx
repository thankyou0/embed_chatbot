"use client";

import { useRef, useMemo, useState, useCallback } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Html, MeshDistortMaterial } from "@react-three/drei";
import * as THREE from "three";

const platforms = [
  { name: "React", icon: "⚛️", color: "#61dafb" },
  { name: "WordPress", icon: "📝", color: "#21759b" },
  { name: "Shopify", icon: "🛍️", color: "#96bf48" },
  { name: "Webflow", icon: "🌊", color: "#4353ff" },
  { name: "Wix", icon: "✨", color: "#faad4d" },
  { name: "Squarespace", icon: "◼️", color: "#ffffff" },
  { name: "HTML/JS", icon: "🌐", color: "#f06529" },
  { name: "Next.js", icon: "▲", color: "#ffffff" },
  { name: "Vue", icon: "💚", color: "#42b883" },
  { name: "Angular", icon: "🔺", color: "#dd0031" },
];

/* ═══════════════════════════════════════════════════════════════
   Central EmbedChat Logo Orb
   ═══════════════════════════════════════════════════════════════ */
function CenterOrb() {
  const meshRef = useRef<THREE.Mesh>(null);
  const pulseRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y = clock.elapsedTime * 0.3;
    // Pulse the outer glow
    if (pulseRef.current) {
      const s = 1 + Math.sin(clock.elapsedTime * 1.5) * 0.08;
      pulseRef.current.scale.set(s, s, s);
      (pulseRef.current.material as THREE.MeshBasicMaterial).opacity =
        0.06 + Math.sin(clock.elapsedTime * 1.5) * 0.03;
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Glowing core sphere */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[0.55, 32, 32]} />
        <MeshDistortMaterial
          color="#10b981"
          distort={0.3}
          speed={2}
          roughness={0.2}
          metalness={0.8}
          transparent
          opacity={0.85}
        />
      </mesh>
      {/* Inner glow */}
      <mesh>
        <sphereGeometry args={[0.62, 16, 16]} />
        <meshBasicMaterial color="#34d399" transparent opacity={0.12} />
      </mesh>
      {/* Pulsing outer halo */}
      <mesh ref={pulseRef}>
        <sphereGeometry args={[0.82, 16, 16]} />
        <meshBasicMaterial color="#10b981" transparent opacity={0.06} side={THREE.BackSide} />
      </mesh>
      {/* Orbiting ring */}
      <mesh rotation={[Math.PI / 2.5, 0, 0]}>
        <torusGeometry args={[0.78, 0.008, 8, 64]} />
        <meshBasicMaterial color="#34d399" transparent opacity={0.25} />
      </mesh>
      {/* Label */}
      <Html center position={[0, -1, 0]} style={{ pointerEvents: "none" }}>
        <div style={{
          fontSize: "14px",
          fontWeight: 700,
          color: "#10b981",
          whiteSpace: "nowrap",
          textShadow: "0 0 20px rgba(16,185,129,0.5)",
          fontFamily: "system-ui, sans-serif",
        }}>
          EmbedChat
        </div>
      </Html>
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Orbiting Platform Orb — enhanced with glow ring & mini particles
   ═══════════════════════════════════════════════════════════════ */
function PlatformOrb({
  platform,
  index,
  total,
  hoveredIndex,
  onHover,
  onLeave,
}: {
  platform: typeof platforms[0];
  index: number;
  total: number;
  hoveredIndex: number | null;
  onHover: (i: number) => void;
  onLeave: () => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const groupRef = useRef<THREE.Group>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const isHovered = hoveredIndex === index;

  const angle = (index / total) * Math.PI * 2;
  const radius = 2.8;

  useFrame(({ clock }) => {
    if (!groupRef.current || !meshRef.current) return;
    const t = clock.elapsedTime * 0.15;
    const currentAngle = angle + t;

    // Orbit position
    const targetX = Math.cos(currentAngle) * radius;
    const targetZ = Math.sin(currentAngle) * radius;
    const targetY = Math.sin(currentAngle * 2 + index) * 0.3;

    groupRef.current.position.x = THREE.MathUtils.lerp(groupRef.current.position.x, targetX, 0.05);
    groupRef.current.position.z = THREE.MathUtils.lerp(groupRef.current.position.z, targetZ, 0.05);
    groupRef.current.position.y = THREE.MathUtils.lerp(groupRef.current.position.y, targetY, 0.05);

    // Scale on hover
    const targetScale = isHovered ? 1.5 : 1;
    meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);

    // Slow rotation
    meshRef.current.rotation.y += 0.01;

    // Always-visible outer glow pulsing
    if (glowRef.current) {
      const glowScale = isHovered ? 1.8 : 1 + Math.sin(clock.elapsedTime * 2 + index) * 0.1;
      glowRef.current.scale.set(glowScale, glowScale, glowScale);
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity = isHovered ? 0.15 : 0.05;
    }

    // Spinning ring
    if (ringRef.current) {
      ringRef.current.rotation.z = clock.elapsedTime * 0.8 + index;
      ringRef.current.rotation.x = Math.PI / 3;
      (ringRef.current.material as THREE.MeshBasicMaterial).opacity = isHovered ? 0.4 : 0.1;
    }
  });

  const color = new THREE.Color(platform.color);

  return (
    <group ref={groupRef}>
      <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.3}>
        {/* Main orb */}
        <mesh
          ref={meshRef}
          onPointerEnter={() => onHover(index)}
          onPointerLeave={onLeave}
        >
          <sphereGeometry args={[0.32, 24, 24]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={isHovered ? 0.7 : 0.2}
            metalness={0.7}
            roughness={0.3}
            transparent
            opacity={isHovered ? 1 : 0.8}
          />
        </mesh>

        {/* Always-visible outer glow sphere */}
        <mesh ref={glowRef}>
          <sphereGeometry args={[0.4, 12, 12]} />
          <meshBasicMaterial color={platform.color} transparent opacity={0.05} side={THREE.BackSide} />
        </mesh>

        {/* Orbiting mini ring around each node */}
        <mesh ref={ringRef}>
          <torusGeometry args={[0.44, 0.006, 8, 32]} />
          <meshBasicMaterial color={platform.color} transparent opacity={0.1} />
        </mesh>

        {/* Platform label */}
        <Html center position={[0, -0.6, 0]} style={{ pointerEvents: "none" }}>
          <div
            style={{
              fontSize: isHovered ? "13px" : "10px",
              fontWeight: isHovered ? 700 : 500,
              color: isHovered ? "white" : "rgba(255,255,255,0.5)",
              whiteSpace: "nowrap",
              transition: "all 0.3s ease",
              textShadow: isHovered ? `0 0 15px ${platform.color}` : "none",
              fontFamily: "system-ui, sans-serif",
            }}
          >
            <span style={{ marginRight: "4px" }}>{platform.icon}</span>
            {platform.name}
          </div>
        </Html>

        {/* Expanded glow ring on hover */}
        {isHovered && (
          <mesh rotation={[Math.PI / 2, 0, 0]}>
            <ringGeometry args={[0.45, 0.52, 32]} />
            <meshBasicMaterial color={platform.color} transparent opacity={0.25} side={THREE.DoubleSide} />
          </mesh>
        )}
      </Float>

      {/* Connection line to center */}
      <ConnectionLine
        start={groupRef.current?.position || new THREE.Vector3(0, 0, 0)}
        end={new THREE.Vector3(0, 0, 0)}
        color={platform.color}
        hovered={isHovered}
      />
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Connection Line between orb and center
   ═══════════════════════════════════════════════════════════════ */
function ConnectionLine({
  start,
  end,
  color,
  hovered,
}: {
  start: THREE.Vector3;
  end: THREE.Vector3;
  color: string;
  hovered: boolean;
}) {
  const lineRef = useRef<THREE.Line>(null);

  useFrame(() => {
    if (!lineRef.current) return;
    const geo = lineRef.current.geometry;
    const positions = geo.attributes.position as THREE.BufferAttribute;
    const arr = positions.array as Float32Array;
    arr[0] = start.x;
    arr[1] = start.y;
    arr[2] = start.z;
    arr[3] = end.x;
    arr[4] = end.y;
    arr[5] = end.z;
    positions.needsUpdate = true;
  });

  const points = useMemo(() => {
    return new Float32Array([0, 0, 0, 0, 0, 0]);
  }, []);

  return (
    <line ref={lineRef as any}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={2}
          array={points}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial
        color={color}
        transparent
        opacity={hovered ? 0.35 : 0.08}
        linewidth={1}
      />
    </line>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Star-like particles — dense field of twinkling stars
   ═══════════════════════════════════════════════════════════════ */
function StarField({ count = 300 }: { count?: number }) {
  const meshRef = useRef<THREE.Points>(null);

  const { positions, sizes } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const sz = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 1.5 + Math.random() * 4.5;
      pos[i3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i3 + 1] = (Math.random() - 0.5) * 3;
      pos[i3 + 2] = r * Math.sin(phi) * Math.sin(theta);
      sz[i] = 0.008 + Math.random() * 0.015;
    }
    return { positions: pos, sizes: sz };
  }, [count]);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y = clock.elapsedTime * 0.015;
    // Gentle twinkle via material opacity cycling
    const mat = meshRef.current.material as THREE.PointsMaterial;
    mat.opacity = 0.35 + Math.sin(clock.elapsedTime * 0.5) * 0.1;
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={0.018}
        color="#ffffff"
        transparent
        opacity={0.35}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Emerald accent particles — galaxy feel
   ═══════════════════════════════════════════════════════════════ */
function GalaxyParticles({ count = 150 }: { count?: number }) {
  const meshRef = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 1 + Math.random() * 4;
      arr[i3] = r * Math.sin(phi) * Math.cos(theta);
      arr[i3 + 1] = (Math.random() - 0.5) * 2;
      arr[i3 + 2] = r * Math.sin(phi) * Math.sin(theta);
    }
    return arr;
  }, [count]);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y = clock.elapsedTime * 0.025;
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        color="#34d399"
        transparent
        opacity={0.45}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Main Scene
   ═══════════════════════════════════════════════════════════════ */
export default function LogoCloudScene() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const handleHover = useCallback((i: number) => setHoveredIndex(i), []);
  const handleLeave = useCallback(() => setHoveredIndex(null), []);

  return (
    <Canvas
      camera={{ position: [0, 2.5, 6], fov: 40 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      dpr={[1, 1.5]}
      style={{ background: "transparent" }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} intensity={0.3} />
      <pointLight position={[0, 0, 0]} intensity={1} color="#10b981" distance={6} />
      {/* Secondary faint lights for depth */}
      <pointLight position={[3, 1, 2]} intensity={0.15} color="#61dafb" distance={5} />
      <pointLight position={[-3, -1, 2]} intensity={0.15} color="#f06529" distance={5} />

      {/* Central EmbedChat orb */}
      <CenterOrb />

      {/* Orbiting platform orbs */}
      {platforms.map((p, i) => (
        <PlatformOrb
          key={p.name}
          platform={p}
          index={i}
          total={platforms.length}
          hoveredIndex={hoveredIndex}
          onHover={handleHover}
          onLeave={handleLeave}
        />
      ))}

      {/* Star field — white twinkling stars */}
      <StarField count={250} />

      {/* Emerald accent galaxy particles */}
      <GalaxyParticles count={120} />
    </Canvas>
  );
}
