"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, MeshDistortMaterial } from "@react-three/drei";
import * as THREE from "three";

/* ═══════════════════════════════════════════════════════════════
   Tier Pedestal — a glowing 3D tower for each plan
   ═══════════════════════════════════════════════════════════════ */
function TierPedestal({
  position,
  height,
  color,
  glowIntensity,
  isPro,
}: {
  position: [number, number, number];
  height: number;
  color: string;
  glowIntensity: number;
  isPro: boolean;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.position.y = Math.sin(clock.elapsedTime * 0.5 + position[0]) * 0.05;
    }
    if (ringRef.current) {
      ringRef.current.rotation.y = clock.elapsedTime * (isPro ? 0.8 : 0.3);
      ringRef.current.rotation.x = Math.sin(clock.elapsedTime * 0.3) * 0.2;
    }
  });

  return (
    <group position={position}>
      {/* Main pedestal */}
      <mesh ref={meshRef}>
        <cylinderGeometry args={[0.6, 0.8, height, 6]} />
        <meshStandardMaterial
          color={color}
          metalness={0.7}
          roughness={0.2}
          transparent
          opacity={0.85}
        />
      </mesh>

      {/* Top cap — sphere */}
      <Float speed={isPro ? 2 : 1} floatIntensity={isPro ? 0.3 : 0.15}>
        <mesh position={[0, height / 2 + 0.4, 0]}>
          <sphereGeometry args={[0.25, 16, 16]} />
          <MeshDistortMaterial
            color={color}
            distort={isPro ? 0.35 : 0.15}
            speed={isPro ? 3 : 1.5}
            roughness={0.1}
            metalness={0.9}
          />
        </mesh>
      </Float>

      {/* Orbiting ring */}
      <mesh ref={ringRef} position={[0, height / 2 + 0.4, 0]}>
        <torusGeometry args={[0.5, 0.015, 8, 32]} />
        <meshBasicMaterial color={color} transparent opacity={isPro ? 0.6 : 0.2} />
      </mesh>

      {/* Pro plan crown — extra ring + glow */}
      {isPro && (
        <>
          <mesh position={[0, height / 2 + 0.4, 0]} rotation={[Math.PI / 2, 0, 0]}>
            <torusGeometry args={[0.65, 0.01, 8, 32]} />
            <meshBasicMaterial color={color} transparent opacity={0.3} />
          </mesh>
          <pointLight
            position={[0, height / 2 + 0.5, 0.5]}
            intensity={glowIntensity}
            color={color}
            distance={3}
          />
        </>
      )}

      {/* Base glow ring */}
      <mesh position={[0, -height / 2 + 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.75, 1.0, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.06} side={THREE.DoubleSide} />
      </mesh>

      {/* Vertical glow beam */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.02, 0.02, height + 1, 8]} />
        <meshBasicMaterial color={color} transparent opacity={isPro ? 0.15 : 0.05} />
      </mesh>
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Floating price particles
   ═══════════════════════════════════════════════════════════════ */
function PricingParticles() {
  const ref = useRef<THREE.Points>(null);
  const count = 100;

  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      pos[i3] = (Math.random() - 0.5) * 14;
      pos[i3 + 1] = (Math.random() - 0.5) * 8;
      pos[i3 + 2] = (Math.random() - 0.5) * 8;
    }
    return pos;
  }, []);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.rotation.y = clock.elapsedTime * 0.015;
    ref.current.rotation.x = Math.sin(clock.elapsedTime * 0.1) * 0.02;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={0.025}
        color="#10b981"
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
   Grid floor
   ═══════════════════════════════════════════════════════════════ */
function GridFloor() {
  return (
    <gridHelper
      args={[20, 30, "#10b981", "#10b981"]}
      position={[0, -2.5, 0]}
      // @ts-ignore gridHelper material
      material-transparent={true}
      material-opacity={0.04}
    />
  );
}

/* ═══════════════════════════════════════════════════════════════
   Main Pricing Scene
   ═══════════════════════════════════════════════════════════════ */
export default function PricingScene() {
  return (
    <Canvas
      camera={{ position: [0, 1.5, 7], fov: 42 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      dpr={[1, 1.5]}
      style={{ background: "transparent" }}
    >
      <ambientLight intensity={0.25} />
      <directionalLight position={[5, 8, 5]} intensity={0.4} />
      <pointLight position={[-4, 3, 3]} intensity={0.3} color="#10b981" />
      <pointLight position={[4, 3, 3]} intensity={0.3} color="#06b6d4" />
      <pointLight position={[0, 3, 3]} intensity={0.2} color="#14b8a6" />

      {/* Free tier — left, short */}
      <TierPedestal
        position={[-3.2, -0.5, 0]}
        height={1.8}
        color="#6b7280"
        glowIntensity={0.2}
        isPro={false}
      />

      {/* Pro tier — center, tall (featured) */}
      <TierPedestal
        position={[0, 0, 0.5]}
        height={3}
        color="#10b981"
        glowIntensity={0.5}
        isPro={true}
      />

      {/* Enterprise tier — right, medium */}
      <TierPedestal
        position={[3.2, -0.3, 0]}
        height={2.3}
        color="#8b5cf6"
        glowIntensity={0.3}
        isPro={false}
      />

      <GridFloor />
      <PricingParticles />

    </Canvas>
  );
}
