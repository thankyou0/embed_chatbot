"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { MeshDistortMaterial } from "@react-three/drei";
import * as THREE from "three";

/* ═══════════════════════════════════════════════════════════════
   Swirling Tunnel Rings — create a portal/vortex effect
   ═══════════════════════════════════════════════════════════════ */
function TunnelRings() {
  const groupRef = useRef<THREE.Group>(null);
  const ringCount = 16;

  const rings = useMemo(() => {
    return Array.from({ length: ringCount }, (_, i) => ({
      z: -i * 0.8,
      radius: 1.2 + Math.sin(i * 0.5) * 0.3,
      speed: 0.3 + i * 0.05,
      offset: i * 0.4,
    }));
  }, []);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.children.forEach((child, i) => {
      const ring = rings[i];
      if (ring) {
        child.rotation.z = clock.elapsedTime * ring.speed + ring.offset;
        const scale = 1 + Math.sin(clock.elapsedTime * 0.5 + i * 0.3) * 0.1;
        child.scale.setScalar(scale);
      }
    });
  });

  return (
    <group ref={groupRef}>
      {rings.map((ring, i) => {
        const t = i / ringCount;
        const color = new THREE.Color().lerpColors(
          new THREE.Color("#10b981"), // emerald
          new THREE.Color("#06b6d4"), // cyan
          t
        );
        return (
          <mesh key={i} position={[0, 0, ring.z]}>
            <torusGeometry args={[ring.radius, 0.02, 8, 48]} />
            <meshBasicMaterial
              color={color}
              transparent
              opacity={0.15 + (1 - t) * 0.25}
              blending={THREE.AdditiveBlending}
              depthWrite={false}
            />
          </mesh>
        );
      })}
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Portal Orb — central glowing attraction point
   ═══════════════════════════════════════════════════════════════ */
function PortalOrb() {
  const meshRef = useRef<THREE.Mesh>(null);
  const outerRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = clock.elapsedTime * 0.5;
      meshRef.current.rotation.x = Math.sin(clock.elapsedTime * 0.3) * 0.2;
    }
    if (outerRef.current) {
      const pulse = 1 + Math.sin(clock.elapsedTime * 1.5) * 0.1;
      outerRef.current.scale.setScalar(pulse);
    }
  });

  return (
    <group position={[0, 0, -8]}>
      {/* Core orb */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <MeshDistortMaterial
          color="#10b981"
          distort={0.4}
          speed={3}
          roughness={0.1}
          metalness={0.9}
        />
      </mesh>

      {/* Outer glow shell */}
      <mesh ref={outerRef}>
        <sphereGeometry args={[0.8, 16, 16]} />
        <meshBasicMaterial color="#10b981" transparent opacity={0.05} />
      </mesh>

      {/* Point light inside */}
      <pointLight intensity={0.8} color="#10b981" distance={6} />
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Speed Lines — particles flying toward center
   ═══════════════════════════════════════════════════════════════ */
function SpeedLines() {
  const ref = useRef<THREE.Points>(null);
  const count = 150;

  const { positions, velocities } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const vel = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      const angle = Math.random() * Math.PI * 2;
      const r = 0.5 + Math.random() * 2;
      pos[i3] = Math.cos(angle) * r;
      pos[i3 + 1] = Math.sin(angle) * r;
      pos[i3 + 2] = Math.random() * 12 - 2;
      vel[i] = 0.02 + Math.random() * 0.04;
    }
    return { positions: pos, velocities: vel };
  }, []);

  useFrame(() => {
    if (!ref.current) return;
    const posAttr = ref.current.geometry.attributes.position as THREE.BufferAttribute;
    const arr = posAttr.array as Float32Array;
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      arr[i3 + 2] -= velocities[i]; // fly toward portal
      if (arr[i3 + 2] < -10) {
        const angle = Math.random() * Math.PI * 2;
        const r = 0.5 + Math.random() * 2;
        arr[i3] = Math.cos(angle) * r;
        arr[i3 + 1] = Math.sin(angle) * r;
        arr[i3 + 2] = 10;
      }
    }
    posAttr.needsUpdate = true;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={0.03}
        color="#34d399"
        transparent
        opacity={0.6}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Main CTA Scene
   ═══════════════════════════════════════════════════════════════ */
export default function CTAScene() {
  return (
    <Canvas
      camera={{ position: [0, 0, 4], fov: 50 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      dpr={[1, 1.5]}
      style={{ background: "transparent" }}
    >
      <ambientLight intensity={0.15} />

      <TunnelRings />
      <PortalOrb />
      <SpeedLines />

    </Canvas>
  );
}
